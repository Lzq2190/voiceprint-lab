# -*- coding: utf-8 -*-
r"""
盘点 SHUJI 资料：把 PDF / EPUB 的目录与正文提取成可检索的纯文本。

输出放在 .workbuddy/sources/（项目数据目录，不进 git —— 电子书的提取全文属于版权内容，
仓库里只保留自己撰写的讲义）。
"""
import io
import os
import re
import zipfile

import pymupdf as fitz
from bs4 import BeautifulSoup
from lxml import etree

SHUJI = r"C:\Users\25451\Desktop\SHUJI"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  ".workbuddy", "sources")
os.makedirs(OUT, exist_ok=True)


def clean_html(raw):
    soup = BeautifulSoup(raw, "lxml")
    for t in soup(["script", "style", "head"]):
        t.decompose()
    for im in soup.find_all("img"):
        im.replace_with(" 〔图〕 ")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    return "\n".join(x.strip() for x in soup.get_text("\n").split("\n") if x.strip())


def parse_ncx(data):
    root = etree.fromstring(data, etree.XMLParser(recover=True))
    local = lambda t: etree.QName(t).localname
    out = []

    def walk(node, depth):
        for ch in node:
            if local(ch.tag) != "navPoint":
                continue
            label, src = "", ""
            for sub in ch:
                if local(sub.tag) == "navLabel":
                    label = " ".join("".join(sub.itertext()).split())
                elif local(sub.tag) == "content":
                    src = sub.get("src", "")
            out.append((depth, label, src))
            walk(ch, depth + 1)

    for n in root:
        if local(n.tag) == "navMap":
            walk(n, 1)
    return out


def do_pdf(path, stem, survey):
    doc = fitz.open(path)
    n = len(doc)
    toc = doc.get_toc()
    survey.append("\n### %s\n页数 %d，书签 %d 条" % (stem, n, len(toc)))
    if toc:
        for lv, title, pg in toc[:60]:
            survey.append("  " * (lv - 1) + "- " + title.strip() + "  `p%s`" % pg)
    else:
        survey.append("（无书签，前 12 页文本见下）")

    parts = []
    for i, p in enumerate(doc):
        try:
            t = p.get_text("text")
        except Exception:
            continue
        parts.append("\n\n===== PDF page %d =====\n%s" % (i + 1, t))
    txt = "".join(parts)
    io.open(os.path.join(OUT, stem + ".txt"), "w", encoding="utf-8").write(txt)
    survey.append("  正文字符 %d" % len(txt))
    if not toc:
        survey.append("  前 12 页摘录：\n" + "\n".join(txt.splitlines()[:60]))
    doc.close()


def do_epub(path, stem, survey):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    ncx = next((x for x in names if x.endswith("toc.ncx")), None)
    toc = []
    if ncx:
        toc = parse_ncx(z.read(ncx))
    survey.append("\n### %s\nEPUB，条目 %d 个" % (stem, len(toc)))
    for d, label, src in toc[:80]:
        survey.append("  " * (d - 1) + "- " + label)

    htmls = sorted(x for x in names if re.search(r"\.(x?html|htm)$", x, re.I)
                   and "toc" not in x.lower() and "nav" not in x.lower())
    parts = []
    for name in htmls:
        raw = z.read(name).decode("utf-8", errors="replace")
        parts.append("\n\n===== %s =====\n%s" % (name, clean_html(raw)))
    txt = "".join(parts)
    io.open(os.path.join(OUT, stem + ".txt"), "w", encoding="utf-8").write(txt)
    survey.append("  章节页 %d，正文字符 %d" % (len(htmls), len(txt)))


def main():
    survey = ["# SHUJI 资料盘点\n"]
    for name in sorted(os.listdir(SHUJI)):
        path = os.path.join(SHUJI, name)
        if os.path.isdir(path):
            for sub in sorted(os.listdir(path)):
                p2 = os.path.join(path, sub)
                stem = "文献_" + os.path.splitext(sub)[0][:24]
                if sub.lower().endswith(".pdf"):
                    do_pdf(p2, stem, survey)
            continue
        stem = os.path.splitext(name)[0][:28]
        low = name.lower()
        if low.endswith(".pdf"):
            do_pdf(path, stem, survey)
        elif low.endswith(".epub"):
            do_epub(path, stem, survey)
    io.open(os.path.join(OUT, "_survey.md"), "w", encoding="utf-8").write(
        "\n".join(survey))
    print("完成：", OUT)


if __name__ == "__main__":
    main()
