#!/usr/bin/env python3
"""deploy_site.py — Deploy the VitePress dist to the Lighthouse server via SSH.

Password comes ONLY from environment variable LH_SSH_PASSWORD (never stored).
Host/port/user via args below; defaults match the Claw2Bio Lighthouse server.

Subcommands:
  probe                       inspect server: nginx, webroot, existing config
  exec "<shell command>"      run one command on the server
  put <local> <remote>        sftp upload a single file
  deploy <dist_dir> <root>    tar dist -> upload -> backup old root -> extract
  deploy-file <local> <remote>  upload one file with parent-dir creation

Examples:
  python scripts/deploy_site.py probe
  python scripts/deploy_site.py exec "nginx -v"
  python scripts/deploy_site.py deploy website/.vitepress/dist /var/www/claw2bio
"""

import os
import stat as statmod
import sys
import tarfile
import tempfile
from pathlib import Path

import paramiko

HOST = "119.91.105.37"
PORT = 22
USER = os.environ.get("LH_SSH_USER", "ubuntu")
# Server public host key (ssh-ed25519) — pins the fingerprint; override via LH_SSH_HOSTKEY env
HOST_KEY = os.environ.get(
    "LH_SSH_HOSTKEY",
    "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKGE0rhS9O/l3mdDOcGSKcF+6SXiPknd8fJoeeHLox1p",
)


class PinnedKeyPolicy(paramiko.RejectPolicy):
    """Reject any host key that does not match the pinned fingerprint."""

    def missing_host_key(self, client, hostname, key):
        expected = HOST_KEY.split()[-1]
        import base64 as _b64
        actual = _b64.b64encode(key.asbytes()).decode()
        if actual == expected:
            client._host_keys.add(hostname, key.get_name(), key)  # accept: matches pin
            return
        raise paramiko.SSHException(
            f"host key mismatch for {hostname}: got {key.get_name()} {actual}, expected pin"
        )


def die(msg):
    print(f"[FATAL] {msg}", file=sys.stderr)
    sys.exit(1)


def connect():
    password = os.environ.get("LH_SSH_PASSWORD", "")
    if not password:
        die("LH_SSH_PASSWORD not set in environment")
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(PinnedKeyPolicy())
    cli.connect(HOST, port=PORT, username=USER, password=password, timeout=20,
                allow_agent=False, look_for_keys=False)
    return cli


def run(cli, cmd, timeout=120):
    _, stdout, stderr = cli.exec_command(cmd, timeout=timeout)
    rc = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    return rc, out, err


def cmd_probe(cli):
    cmds = [
        ("nginx version", "nginx -v 2>&1; which nginx"),
        ("port 80/443 listeners", "ss -tlnp | grep -E ':(80|443)\\b' || true"),
        ("nginx -T server blocks", "nginx -T 2>/dev/null | grep -nE 'server_name|root |listen|include' | head -40"),
        ("site-enabled files", "ls -la /etc/nginx/sites-enabled/ 2>/dev/null; ls -la /etc/nginx/conf.d/ 2>/dev/null"),
        ("webroot candidates", "ls -la /var/www/ 2>/dev/null; ls -la /usr/share/nginx/html 2>/dev/null"),
        ("os", "cat /etc/os-release | head -2"),
    ]
    for title, c in cmds:
        rc, out, err = run(cli, c)
        print(f"===== {title} (rc={rc}) =====")
        print(out.strip() or "(empty)")
        if err.strip() and rc != 0:
            print(f"[stderr] {err.strip()[:500]}")


def cmd_exec(cli, command):
    rc, out, err = run(cli, command, timeout=300)
    print(out)
    if err.strip():
        print(f"[stderr]\n{err}")
    sys.exit(rc)


def sftp_mkdirs(sftp, remote_dir):
    parts = remote_dir.strip("/").split("/")
    cur = ""
    for p in parts:
        cur += "/" + p
        try:
            sftp.stat(cur)
        except FileNotFoundError:
            sftp.mkdir(cur)


def cmd_put(cli, local, remote):
    sftp = cli.open_sftp()
    rdir = os.path.dirname(remote)
    if rdir:
        sftp_mkdirs(sftp, rdir)
    sftp.put(local, remote)
    st = sftp.stat(remote)
    print(f"[put] {local} -> {remote} ({st.st_size:,} B)")
    sftp.close()


def cmd_deploy(cli, dist_dir, remote_root):
    dist = Path(dist_dir).resolve()
    if not dist.is_dir():
        die(f"dist dir not found: {dist}")
    # 1) local tar
    tmp = Path(tempfile.mkdtemp(prefix="claw2bio-deploy-"))
    tar_path = tmp / "dist.tar.gz"
    print(f"[tar] {dist} -> {tar_path}")
    with tarfile.open(tar_path, "w:gz") as tf:
        for p in sorted(dist.rglob("*")):
            tf.add(p, arcname=p.relative_to(dist).as_posix())
    size = tar_path.stat().st_size
    print(f"[tar] done ({size:,} B)")

    remote_tar = f"/tmp/claw2bio-dist-{os.getpid()}.tar.gz"
    # 2) upload
    sftp = cli.open_sftp()
    sftp.put(str(tar_path), remote_tar)
    print(f"[put] -> {remote_tar}")
    # 3) backup old root (sudo: /var/www is root-owned), extract new
    ts = "pre-deploy"
    backup = f"{remote_root}.bak-{ts}"
    seq = [
        (f"if test -d {remote_root}; then sudo mv {remote_root} {backup} "
         f"&& echo 'MOVED old root -> {backup}'; else echo 'NO OLD ROOT'; fi"),
        f"sudo mkdir -p {remote_root} && sudo chown -R ubuntu:ubuntu {remote_root}",
        f"tar -xzf {remote_tar} -C {remote_root}",
        f"rm -f {remote_tar}",
        f"ls {remote_root} | head -20",
    ]
    backup_note = "no old root existed"
    for c in seq:
        rc, out, err = run(cli, c)
        print(f"$ {c}\n{out.strip() or err.strip()}")
        if rc != 0:
            die(f"remote command failed (rc={rc}): {c}")
        if out.strip().startswith("MOVED old root"):
            backup_note = f"old root preserved at {backup}"
    sftp.close()
    tar_path.unlink()
    tmp.rmdir()
    print(f"[deploy] OK — {backup_note}")


def cmd_deploy_file(cli, local, remote):
    cmd_put(cli, local, remote)
    # fix common case: certs uploaded too open — caller can chmod via exec
    rc, out, err = run(cli, f"chmod 600 {remote} 2>/dev/null; true")
    print(f"[chmod 600] {remote}")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(2)
    cmd, args = argv[0], argv[1:]
    cli = connect()
    try:
        if cmd == "probe":
            cmd_probe(cli)
        elif cmd == "exec" and args:
            cmd_exec(cli, args[0])
        elif cmd == "put" and len(args) == 2:
            cmd_put(cli, args[0], args[1])
        elif cmd == "deploy" and len(args) == 2:
            cmd_deploy(cli, args[0], args[1])
        elif cmd == "deploy-file" and len(args) == 2:
            cmd_deploy_file(cli, args[0], args[1])
        else:
            die(f"unknown subcommand/args: {argv}")
    finally:
        cli.close()


if __name__ == "__main__":
    main()
