# -*- coding: utf-8 -*-
r"""
当本机代理把 github.com:443 挡掉、但 api.github.com 可直连时，
用 GitHub Git Data API 把本地最近一次 commit 推到远端 main。

原理：blob -> tree(基于远端 tree) -> commit -> PATCH ref，等价于一次 git push。
token 从 git credential 动态读取，绝不写进本文件，也不打印。
用本脚本推送后，远端 commit 的 sha 与本地不同（作者时间戳由 GitHub 生成），
但目录树完全相同；脚本会比较父提交的 tree sha 而不是 commit sha 来校验，
因此之后每次改动都能继续用本脚本推送。

用法：python tools/push_github_api.py [--dry-run]
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

OWNER = "Lzq2190"
REPO = "voiceprint-lab"
BRANCH = "main"
BASE = "https://api.github.com/repos/%s/%s" % (OWNER, REPO)

# 本机代理对 api.github.com 会返回 502；这里强制直连
for _k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
           "ALL_PROXY", "all_proxy"):
    os.environ.pop(_k, None)
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def git(*args, binary=False):
    # 关闭路径转义，否则中文文件名会变成 \345\243... 导致 git show 找不到
    r = subprocess.run(["git", "-c", "core.quotepath=false"] + list(args),
                       capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode("utf-8").strip()


def token():
    p = subprocess.run(["git", "credential", "fill"],
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True, check=True, timeout=30)
    kv = dict(l.split("=", 1) for l in p.stdout.strip().splitlines() if "=" in l)
    t = kv.get("password")
    if not t:
        raise RuntimeError("未找到 GitHub 凭据，请先登录")
    return t


TOKEN = None


def api(method, path, payload=None):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Authorization": "Bearer " + TOKEN,
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json",
                 "X-GitHub-Api-Version": "2022-11-28",
                 "User-Agent": "workbuddy-guide-push"})
    try:
        with OPENER.open(req, timeout=90) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:600]
        raise RuntimeError("API %s %s -> %d: %s" % (method, path, e.code, body))


def is_binary(b):
    if b"\x00" in b[:8000]:
        return True
    try:
        b.decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True


def main(dry=False, patch_only=None):
    global TOKEN
    TOKEN = token()
    if patch_only:
        api("PATCH", "/git/refs/heads/%s" % BRANCH, {"sha": patch_only})
        print("引用已更新：%s" % patch_only[:10])
        return
    head = git("rev-parse", "HEAD")
    parent = git("rev-parse", "HEAD^")
    msg = git("log", "-1", "--pretty=%B")
    changed = [l.split("\t", 1) for l in
               git("diff", "--name-status", parent, head).splitlines() if "\t" in l]

    print("本地 HEAD  %s" % head[:10])
    print("改动文件   %d 个" % len(changed))
    if dry:
        return

    ref = api("GET", "/git/ref/heads/%s" % BRANCH)
    remote_head = ref["object"]["sha"]
    print("远端 HEAD  %s" % remote_head[:10])
    remote_commit = api("GET", "/git/commits/" + remote_head)
    base_tree = remote_commit["tree"]["sha"]
    # 用 API 建出来的 commit 与本地 commit 的 sha 不同（作者时间戳由 GitHub 生成），
    # 但内容一致。因此比较「父提交目录树」而非 commit sha，后续推送也能直接续上。
    local_parent_tree = git("rev-parse", parent + "^{tree}")
    if remote_head != parent and local_parent_tree != base_tree:
        raise RuntimeError("远端 main 与本地父提交的目录树不一致，需先 pull/rebase")
    print("目录树一致  %s" % base_tree[:10])

    entries = []
    nblob = 0
    for status, path in changed:
        if status.startswith("D"):
            entries.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
            continue
        data = git("show", "HEAD:" + path, binary=True)
        mode = "100644"
        try:
            m = git("ls-tree", "HEAD", "--", path).split()[0]
            if m in ("100644", "100755"):
                mode = m
        except Exception:
            pass
        if is_binary(data):
            b = api("POST", "/git/blobs", {
                "content": base64.b64encode(data).decode("ascii"),
                "encoding": "base64"})
            entries.append({"path": path, "mode": mode, "type": "blob", "sha": b["sha"]})
            nblob += 1
        else:
            entries.append({"path": path, "mode": mode, "type": "blob",
                            "content": data.decode("utf-8")})
    print("已上传 %d 个二进制 blob，准备提交 %d 个 tree 条目" % (nblob, len(entries)))

    tree = api("POST", "/git/trees", {"base_tree": base_tree, "tree": entries})
    commit = api("POST", "/git/commits", {
        "message": msg, "tree": tree["sha"], "parents": [remote_head]})
    print("commit 已创建：%s（若下一步失败，可用 --patch-only 续跑）" % commit["sha"])
    api("PATCH", "/git/refs/heads/%s" % BRANCH, {"sha": commit["sha"]})
    print("推送完成：%s" % commit["sha"][:10])
    print("https://github.com/%s/%s/commit/%s" % (OWNER, REPO, commit["sha"]))


if __name__ == "__main__":
    _po = None
    if "--patch-only" in sys.argv:
        _i = sys.argv.index("--patch-only")
        _po = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        if not _po:
            raise SystemExit("用法：--patch-only <commit_sha>")
    main(dry="--dry-run" in sys.argv, patch_only=_po)
