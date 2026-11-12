# -*- coding: utf-8 -*-
"""导出 index.html 中全部 KaTeX 定界符内容，交给 Node + KaTeX 逐条渲染校验。"""
import html
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(HERE)
SRC = os.path.join(GUIDE, "index.html")
JS = os.path.join(HERE, "check_math.js")
TMP = os.path.join(HERE, "_math_check.json")


def main():
    s = io.open(SRC, encoding="utf-8").read()
    # 去掉 <pre>/<code> 块（里面是代码，不参与公式渲染）
    s = re.sub(r"<pre\b.*?</pre>", "", s, flags=re.S | re.I)
    s = re.sub(r"<code\b.*?</code>", "", s, flags=re.S | re.I)
    s = re.sub(r"<script\b.*?</script>", "", s, flags=re.S | re.I)
    s = re.sub(r"<style\b.*?</style>", "", s, flags=re.S | re.I)

    items = []
    # 展示公式固定写成 "\[ ... \]"（前后各一个空格），避开 LaTeX 换行符 "\\[6pt]" 里的 "\["
    for tex in re.findall(r"\\\[ (.*?) \\\]", s, re.S):
        items.append({"display": True, "tex": html.unescape(tex)})
    for tex in re.findall(r"\\\((.*?)\\\)", s, re.S):
        items.append({"display": False, "tex": html.unescape(tex)})

    io.open(TMP, "w", encoding="utf-8").write(
        json.dumps(items, ensure_ascii=False))
    print("共提取 %d 条公式（display %d / inline %d）" % (
        len(items), sum(1 for x in items if x["display"]),
        sum(1 for x in items if not x["display"])))

    r = subprocess.run(["node", JS, TMP], capture_output=True, text=True,
                       encoding="utf-8", timeout=180)
    print(r.stdout)
    if r.stderr.strip():
        print("[stderr]", r.stderr[:2000])
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
