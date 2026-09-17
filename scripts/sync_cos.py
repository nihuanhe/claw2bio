#!/usr/bin/env python3
"""sync_cos.py — Incremental upload of cos-staging/ to Tencent COS.

Reads every manifest.csv under cos-staging/ (columns: file,md5,size,example,note),
verifies local files against the manifest (md5 + size), then uploads each object
to the bucket with simple (non-multipart) PUT so that COS ETag == md5.

Incremental / idempotent:
  - head_object first: if the remote ETag matches the local md5 and the size
    matches, the object is skipped.
  - a second run without local changes reports everything as SKIPPED.

Credentials come ONLY from environment variables (never hard-coded):
  COS_SECRET_ID, COS_SECRET_KEY

Optional env / args:
  COS_BUCKET   (default my-website-1358159656)
  COS_REGION   (default ap-guangzhou)

Usage:
  python scripts/sync_cos.py            # from anywhere; repo root auto-detected
  python scripts/sync_cos.py --dry-run  # verify manifests + report, upload nothing
"""

import csv
import hashlib
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STAGING = REPO_ROOT / "cos-staging"

BUCKET = os.environ.get("COS_BUCKET", "my-website-1358159656")
REGION = os.environ.get("COS_REGION", "ap-guangzhou")

MAX_SIMPLE_UPLOAD = 100 * 1024 * 1024  # well above our largest object (~30 MB)


def die(msg: str) -> None:
    print(f"[FATAL] {msg}", file=sys.stderr)
    sys.exit(1)


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifests():
    """Return [(skill_name, manifest_path, rows)] for every manifest.csv."""
    manifests = sorted(STAGING.glob("*/manifest.csv"))
    if not manifests:
        die(f"no manifest.csv found under {STAGING}")
    out = []
    for m in manifests:
        with m.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            die(f"manifest has no rows: {m}")
        out.append((m.parent.name, m, rows))
    return out


def main() -> None:
    dry = "--dry-run" in sys.argv

    secret_id = os.environ.get("COS_SECRET_ID", "")
    secret_key = os.environ.get("COS_SECRET_KEY", "")
    if not dry:
        if not secret_id or not secret_key:
            die("COS_SECRET_ID / COS_SECRET_KEY not set in environment")
    if len(sys.argv) > 1 and not dry:
        die(f"unknown args: {sys.argv[1:]}")

    from qcloud_cos import CosConfig, CosS3Client, CosServiceError  # noqa: E402

    client = CosS3Client(
        CosConfig(Region=REGION, SecretId=secret_id, SecretKey=secret_key, Scheme="https")
    )

    manifests = load_manifests()
    plan = []  # (skill, rel_file, expected_md5, expected_size, local_path)
    for skill, mpath, rows in manifests:
        for row in rows:
            rel = row["file"].strip()
            expect_md5 = row["md5"].strip().lower()
            expect_size = int(row["size"])
            local = mpath.parent / rel
            if not local.is_file():
                die(f"manifest lists missing file: {local}")
            actual_size = local.stat().st_size
            if actual_size != expect_size:
                die(f"size mismatch for {local}: manifest={expect_size} disk={actual_size}")
            if local.stat().st_size > MAX_SIMPLE_UPLOAD:
                die(f"file too large for simple upload (ETag!=md5): {local}")
            plan.append((skill, rel, expect_md5, expect_size, local))

    # cross-check disk md5 against manifest (abort on any mismatch before uploading)
    print(f"[plan] {len(plan)} objects, verifying local md5 against manifests ...")
    for skill, rel, expect_md5, expect_size, local in plan:
        actual = md5_of(local)
        if actual != expect_md5:
            die(f"md5 mismatch for {local}: manifest={expect_md5} disk={actual}")
    total_bytes = sum(p[3] for p in plan)
    print(f"[plan] all {len(plan)} files match manifests; total {total_bytes:,} bytes")

    if dry:
        print("[dry-run] nothing uploaded.")
        return

    uploaded, skipped, failed = [], [], []
    for skill, rel, expect_md5, expect_size, local in plan:
        key = f"{skill}/{rel}"
        try:
            head = client.head_object(Bucket=BUCKET, Key=key)
            etag = head.get("ETag", "").strip('"').lower()
            rsize = int(head.get("Content-Length", -1))
            if etag == expect_md5 and rsize == expect_size:
                skipped.append(key)
                continue
            reason = f"etag {etag} != {expect_md5}" if etag != expect_md5 else f"size {rsize} != {expect_size}"
            print(f"[stale] {key}: {reason} -> re-upload")
        except CosServiceError as e:
            if e.get_status_code() != 404:  # 404 = not exists (normal); anything else: warn, then re-upload
                print(f"[warn]  {key}: head failed (http {e.get_status_code()}); will re-upload")
        except Exception as e:
            print(f"[warn]  {key}: head failed ({e}); will re-upload")
        last_err = None
        for attempt in (1, 2):  # put + verify, one retry (plan A2)
            try:
                with local.open("rb") as f:
                    client.put_object(Bucket=BUCKET, Key=key, Body=f, EnableMD5=False)
                head = client.head_object(Bucket=BUCKET, Key=key)
                etag = head.get("ETag", "").strip('"').lower()
                rsize = int(head.get("Content-Length", -1))
                if etag != expect_md5 or rsize != expect_size:
                    raise RuntimeError(f"post-upload verify failed: etag={etag} size={rsize}")
                uploaded.append(key)
                print(f"[up]    {key} ({expect_size:,} B)" + (" [retry ok]" if attempt == 2 else ""))
                last_err = None
                break
            except Exception as e:
                last_err = e
                if attempt == 1:
                    print(f"[retry] {key}: {e}")
        if last_err is not None:
            failed.append((key, str(last_err)))
            print(f"[FAIL]  {key}: {last_err}")

    print("=" * 60)
    print(f"uploaded: {len(uploaded)}  skipped: {len(skipped)}  failed: {len(failed)}")
    if failed:
        for key, err in failed:
            print(f"  FAILED {key}: {err}")
        sys.exit(1)
    if len(uploaded) + len(skipped) != len(plan):
        print(f"[FATAL] accounting mismatch: {len(uploaded)}+{len(skipped)} != {len(plan)}")
        sys.exit(1)

    # independent remote census: list the bucket instead of trusting our own counters
    expect_sizes = {f"{skill}/{rel}": sz for skill, rel, _, sz, _ in plan}
    remote: dict[str, int] = {}
    for prefix in sorted({f"{m[0]}/" for m in manifests}):
        marker = ""
        while True:
            resp = client.list_objects(Bucket=BUCKET, Prefix=prefix, MaxKeys=1000, Marker=marker)
            for c in resp.get("Contents", []):
                remote[c["Key"]] = int(c["Size"])
            if resp.get("IsTruncated") == "true":
                marker = resp.get("NextMarker") or sorted(remote)[-1]
            else:
                break
    extra = sorted(set(remote) - set(expect_sizes))
    missing = sorted(set(expect_sizes) - set(remote))
    wrong = sorted(k for k in set(expect_sizes) & set(remote) if remote[k] != expect_sizes[k])
    if extra or missing or wrong:
        for k in extra:
            print(f"  EXTRA  {k} ({remote[k]:,} B) — not in any manifest")
        for k in missing:
            print(f"  MISSING {k}")
        for k in wrong:
            print(f"  SIZEDIFF {k}: remote={remote[k]:,} manifest={expect_sizes[k]:,}")
        print(f"[FATAL] remote census mismatch: extra={len(extra)} missing={len(missing)} sizediff={len(wrong)}")
        sys.exit(1)
    remote_bytes = sum(remote[k] for k in expect_sizes)
    if remote_bytes != total_bytes:
        print(f"[FATAL] remote bytes {remote_bytes:,} != manifest total {total_bytes:,}")
        sys.exit(1)
    print(f"[done] bucket {BUCKET} ({REGION}) census: {len(remote)} objects, "
          f"{remote_bytes:,} bytes — exactly matches manifests (no extra/missing)")
    print(f"[done] base URL: https://{BUCKET}.cos.{REGION}.myqcloud.com/")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
