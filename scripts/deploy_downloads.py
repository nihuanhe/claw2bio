#!/usr/bin/env python3
"""deploy_downloads.py — upload skill zip packages to the website's download area.

Packages come from .build/skill-zips/manifest.csv (built by build_skill_zips.py);
only entries whose size is <= SERVER_LIMIT are handled here — bigger ones are
served from COS instead (see scripts/sync_cos.py).

The remote directory is deliberately OUTSIDE the website root, so redeploying the
site never removes the downloads:

  /var/www/claw2bio-downloads/   ->   https://claw2bio.site/downloads/<file>

Idempotent: a file is skipped when its remote size AND md5 match the local file.

Credentials come ONLY from the environment:
  LH_SSH_PASSWORD   (required)
  LH_SSH_USER       (default ubuntu)

Usage:
  python scripts/deploy_downloads.py             # sync all server-bound packages
  python scripts/deploy_downloads.py --dry-run   # report only
"""

import csv
import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deploy_site import connect, run  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / ".build" / "skill-zips"
MANIFEST = BUILD / "manifest.csv"
REMOTE_DIR = "/var/www/claw2bio-downloads"
SERVER_LIMIT = 50 * 1024 * 1024


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    dry = "--dry-run" in sys.argv
    if not MANIFEST.exists():
        print(f"[FATAL] {MANIFEST} not found — run scripts/build_skill_zips.py first",
              file=sys.stderr)
        sys.exit(1)

    with MANIFEST.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if int(r["size"]) <= SERVER_LIMIT]
    if not rows:
        print("[done] nothing to upload (no server-bound packages)")
        return

    cli = connect()
    try:
        sftp = cli.open_sftp()
        try:
            try:
                sftp.stat(REMOTE_DIR)
            except FileNotFoundError:
                print(f"[init] creating {REMOTE_DIR}")
                if dry:
                    pass
                else:
                    rc, out, err = run(cli, f"sudo mkdir -p {REMOTE_DIR} && "
                                            f"sudo chown -R {os.environ.get('LH_SSH_USER', 'ubuntu')} "
                                            f"{REMOTE_DIR}")
                    if rc != 0:
                        print(f"[FATAL] cannot create {REMOTE_DIR}: {err.strip()}")
                        sys.exit(1)

            uploaded = skipped = failed = 0
            for row in rows:
                name = row["file"]
                local = BUILD / name
                if not local.is_file():
                    print(f"[FAIL]  {name}: local file missing")
                    failed += 1
                    continue
                expect_size, expect_md5 = int(row["size"]), row["md5"].lower()
                remote = f"{REMOTE_DIR}/{name}"

                try:
                    st = sftp.stat(remote)
                    if st.st_size == expect_size:
                        rc, out, _ = run(cli, f"md5sum {remote}")
                        remote_md5 = out.split()[0].lower() if rc == 0 and out else ""
                        if remote_md5 == expect_md5:
                            skipped += 1
                            print(f"[skip]  {name} (md5 verified)")
                            continue
                        print(f"[stale] {name}: md5 {remote_md5 or '?'} != {expect_md5}")
                except FileNotFoundError:
                    pass

                if dry:
                    print(f"[dry]   would upload {name} ({expect_size:,} B)")
                    continue
                try:
                    sftp.put(str(local), remote)
                    rc, out, _ = run(cli, f"md5sum {remote}")
                    remote_md5 = out.split()[0].lower() if rc == 0 and out else ""
                    if remote_md5 != expect_md5:
                        raise RuntimeError(f"post-upload md5 mismatch: {remote_md5}")
                    uploaded += 1
                    print(f"[up]    {name} ({expect_size:,} B)")
                except Exception as e:
                    failed += 1
                    print(f"[FAIL]  {name}: {e}")
        finally:
            sftp.close()
    finally:
        cli.close()

    print("=" * 60)
    print(f"uploaded: {uploaded}  skipped: {skipped}  failed: {failed}")
    print(f"[done] https://claw2bio.site/downloads/  <-  {REMOTE_DIR}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
