# -*- coding: utf-8 -*-
"""
把 guide-v2/index.html 排成「正式讲义」PDF（白底学术版式）。

版式要点
  · 封面单页（信息表 + 标题层级 + 出处）
  · 目录用真实正文页码（正文页码从 1 起，与封面/目录分离）
  · 正文：宋体 10.5pt、首行缩进 2 字符、两端对齐、行距 1.72
  · 图编号「图 X-Y」、表编号「表 X-Y」（表题取自上文标题）、三线表
  · 公式改为真正的上下标排版（不再出现 Σ_{n=0}^{N-1} 这种 ASCII 写法）
  · 采样量化表由截图改为可排版的正文表格
  · 页眉书名 + 页脚页码 + PDF 书签 + 元数据

用法：python tools/build_pdf.py
"""
import csv
import io
import os
import re
import subprocess
import sys
from copy import deepcopy

from lxml import html as LH
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(HERE)
ROOT = os.path.dirname(GUIDE)

SRC = os.path.join(GUIDE, "index.html")
CSV_WAVE = os.path.join(ROOT, "acoustic-lab", "outputs", "waveform_data.csv")
BODY_HTML = os.path.join(GUIDE, "_build_body.html")
TOC_HTML = os.path.join(GUIDE, "_build_toc.html")
COVER_HTML = os.path.join(GUIDE, "_build_cover.html")
BODY_PDF = os.path.join(GUIDE, "_build_body.pdf")
TOC_PDF = os.path.join(GUIDE, "_build_toc.pdf")
COVER_PDF = os.path.join(GUIDE, "_build_cover.pdf")
FINAL = os.path.join(GUIDE, "声纹信号处理学习讲义.pdf")
FALLBACK = os.path.join(GUIDE, "声纹信号处理学习讲义（印刷版）.pdf")

CHROME = next((p for p in [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
] if os.path.exists(p)), None)

ACCENT = "#1f5fbf"

CSS = r"""
@page { size: A4; margin: 21mm 21mm 19mm 21mm; }
* { box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
html, body { margin: 0; padding: 0; background: #fff; }
body {
  font-family: "Times New Roman", "SimSun", serif;
  font-size: 10.5pt; line-height: 1.72; color: #1a1a1a;
  text-align: justify; -webkit-font-smoothing: antialiased;
}
sub, sup { font-size: 68%; line-height: 0; }
sub { vertical-align: -0.28em; } sup { vertical-align: 0.42em; }

/* ---------- 封面 ---------- */
.cover { height: 242mm; display: flex; flex-direction: column; page-break-after: always; }
.cover .meta { width: 100%; border-collapse: collapse; font-size: 9pt; }
.cover .meta td { border: 0.6pt solid #9aa4b2; padding: 4pt 7pt; }
.cover .meta td.k { width: 26mm; color: #55606e; background: #f7f8fa; }
.cover .grow { flex: 1 1 auto; }
.cover .mid { text-align: center; }
.cover .kicker { font-family: "Microsoft YaHei"; font-size: 9.5pt; letter-spacing: .42em;
  color: #7a8492; margin-bottom: 7mm; }
.cover h1 { font-family: "Microsoft YaHei"; font-size: 31pt; font-weight: 700;
  letter-spacing: .10em; margin: 0 0 3.5mm; color: #10161f; line-height: 1.25; }
.cover .sub { font-family: "Microsoft YaHei"; font-size: 14.5pt; font-weight: 400;
  color: #37424f; letter-spacing: .10em; margin: 0; }
.cover .rule { width: 44mm; height: 2pt; background: %(accent)s; margin: 8mm auto; }
.cover .tag { font-size: 10.5pt; color: #4c5664; letter-spacing: .06em; }
.cover .foot { text-align: center; font-size: 9pt; color: #64707e; line-height: 1.95; }
.cover .foot .org { font-family: "Microsoft YaHei"; font-size: 10pt; color: #2c3542;
  letter-spacing: .06em; margin-bottom: 1.5mm; }

/* ---------- 目录 ---------- */
.toc { page-break-after: always; }
.toc h1 { font-family: "Microsoft YaHei"; font-size: 17pt; font-weight: 700; text-align: center;
  letter-spacing: .34em; margin: 0 0 3mm; color: #10161f; }
.toc .hint { text-align: center; font-size: 9pt; color: #77818f; margin-bottom: 10mm; }
.toc .item { display: flex; align-items: baseline; margin: 0 0 8pt; font-size: 10.5pt; }
.toc .item .no { flex: 0 0 18mm; font-family: "Microsoft YaHei"; font-size: 9.3pt;
  color: %(accent)s; font-weight: 600; }
.toc .item .ti { flex: 0 1 auto; }
.toc .item .dots { flex: 1 1 auto; border-bottom: 0.7pt dotted #b3bdc9; margin: 0 1.8mm 1.5mm; }
.toc .item .pg { flex: 0 0 7mm; text-align: right; font-variant-numeric: tabular-nums; }
.toc .tocfoot { margin-top: 14mm; padding-top: 4mm; border-top: 0.7pt solid #dfe4ea;
  font-size: 9pt; color: #6b7583; line-height: 1.95; }

/* ---------- 正文 ---------- */
.chap { page-break-before: always; }
.chap.first { page-break-before: auto; }
.chap .chapno { font-family: "Microsoft YaHei"; font-size: 9.3pt; letter-spacing: .32em;
  color: %(accent)s; text-align: center; margin: 0 0 3.5mm; }
.chap h2 { font-family: "Microsoft YaHei"; font-size: 17pt; font-weight: 700; line-height: 1.45;
  text-align: center; margin: 0 0 3.5mm; color: #10161f; break-after: avoid; }
.chap .rule { width: 100%; height: 0.9pt; background: #d8dee6; margin: 0 0 7mm; }

h3 { font-family: "Microsoft YaHei"; font-size: 11.4pt; font-weight: 700; color: #14213a;
  margin: 15pt 0 6pt; padding-left: 6pt; border-left: 3pt solid %(accent)s;
  line-height: 1.5; break-after: avoid; break-inside: avoid; }
h4 { font-family: "Microsoft YaHei"; font-size: 10.2pt; font-weight: 700; color: #22303f;
  margin: 11pt 0 4pt; break-after: avoid; }
p { margin: 0 0 5.5pt; text-indent: 2em; }
ul, ol { margin: 0 0 6pt; padding-left: 1.9em; }
li { margin: 0 0 3.2pt; text-indent: 0; }
b, strong { font-weight: 700; color: #10161f; }
code { font-family: "Consolas", "Courier New", monospace; font-size: 9pt;
  background: #eef1f5; color: #1f3f6b; padding: 0.5pt 2.6pt; border-radius: 2pt; }
pre { font-family: "Consolas", "Courier New", monospace; font-size: 8.6pt; line-height: 1.55;
  background: #f7f9fb; border: 0.7pt solid #e1e7ee; border-left: 2.6pt solid %(accent)s;
  border-radius: 2pt; padding: 7pt 9pt; margin: 6pt 0 8pt; white-space: pre-wrap;
  word-break: break-word; text-align: left; break-inside: avoid; }
pre code { background: none; color: #1a1a1a; padding: 0; font-size: inherit; }

/* 公式框 */
.eq { background: #f6f8fb; border-left: 2.6pt solid #9aa7b8; padding: 8pt 12pt;
  margin: 8pt 0 10pt; font-family: "Cambria", "Times New Roman", "SimSun", serif;
  font-size: 10.2pt; line-height: 2.0; text-indent: 0; text-align: left;
  white-space: pre-wrap; break-inside: avoid; }
.eq.one { text-align: center; }

/* 提示框 */
.note, .tip, .warn { padding: 6.5pt 9pt; margin: 7pt 0 9pt; font-size: 9.8pt;
  line-height: 1.72; border-radius: 2pt; text-indent: 0; break-inside: avoid; }
.note { background: #f3f7fc; border-left: 2.6pt solid #5a8fd0; }
.tip  { background: #f2faf6; border-left: 2.6pt solid #3f9e78; }
.warn { background: #fdf7f2; border-left: 2.6pt solid #cf8a3c; }
.note .t, .tip .t, .warn .t { font-family: "Microsoft YaHei"; font-weight: 700; font-size: 9.3pt;
  margin-right: 5pt; }
.note .t { color: #24527f; } .tip .t { color: #1f6b4e; } .warn .t { color: #8a5a20; }

/* 目标 / 产出 */
.goal { background: #f8fafc; border: 0.7pt solid #e1e7ee; border-radius: 2pt;
  padding: 7pt 10pt 4pt; margin: 7pt 0 9pt; break-inside: avoid; }
.goal .g { font-family: "Microsoft YaHei"; font-size: 8.8pt; font-weight: 700;
  letter-spacing: .16em; color: %(accent)s; margin-bottom: 3pt; }
.goal ul { margin: 0 0 2pt; padding-left: 0.3em; list-style-position: inside; }
.goal li { font-size: 9.9pt; margin-bottom: 2.2pt; }

/* 图表 */
figure { margin: 9pt 0 11pt; text-align: center; break-inside: avoid; }
figure img { max-width: 100%%; height: auto; border: 0.6pt solid #e1e7ee; }
figcaption, .tcap { font-size: 8.8pt; color: #4a5462; text-indent: 0; line-height: 1.55;
  text-align: center; }
figcaption { margin-top: 4pt; }
.tcap { margin: 9pt 0 3pt; font-family: "Microsoft YaHei"; font-weight: 600; color: #2c3542;
  break-after: avoid; }
.tblwrap { break-inside: avoid; }

/* 三线表 */
table { width: 100%%; border-collapse: collapse; font-size: 9.1pt; line-height: 1.6;
  margin: 0 0 10pt; break-inside: auto; }
table tr { break-inside: avoid; }
table th { font-family: "Microsoft YaHei"; font-weight: 700; font-size: 8.9pt; color: #14213a;
  text-align: left; padding: 5pt 6pt; border-top: 1.1pt solid #2b3440;
  border-bottom: 0.8pt solid #2b3440; background: #f7f9fb; }
table.ref th:first-child, table.ref td:first-child { white-space: nowrap; }
table td { padding: 4.5pt 6pt; border-bottom: 0.5pt solid #e3e8ee; vertical-align: top; }
table tr:last-child td { border-bottom: 1.1pt solid #2b3440; }
table.num td:first-child { font-variant-numeric: tabular-nums; color: #6b7583; }

/* 自检清单 */
.checklist { border: 0.7pt solid #e1e7ee; background: #fff; padding: 8pt 10pt 6pt;
  margin: 7pt 0 9pt; break-inside: avoid; }
.checklist label { break-inside: avoid; }
.checklist label:last-child { break-before: avoid; }   /* 不让最后一项单独掉到下一页 */
.checklist label { display: block; font-size: 9.9pt; line-height: 1.72; margin-bottom: 4pt;
  text-indent: 0; }
.checklist input { -webkit-appearance: none; appearance: none; width: 8.4pt; height: 8.4pt;
  border: 0.9pt solid #78838f; border-radius: 1.5pt; margin: 0 6pt 0 0; vertical-align: -0.6pt; }
.mk { color: #fff; font-size: 1pt; }
"""

BAD_CAP = {"准备", "自检", "误区与注意事项", "怎么做 + 为什么", "怎么做+为什么"}


# --------------------------------------------------------------------------- 工具
def typeset(s: str) -> str:
    """把 ASCII 伪公式转成真正的上下标：_{..} ^(..) ^ {..} f_k μ_c 等。"""
    parts = re.split(r"(<[^>]+>)", s)
    for i, p in enumerate(parts):
        if not p or p.startswith("<"):
            continue
        p = re.sub(r"_\{([^{}]*)\}", r"<sub>\1</sub>", p)
        p = re.sub(r"\^\{([^{}]*)\}", r"<sup>\1</sup>", p)
        p = re.sub(r"\^\(([^()]*)\)", r"<sup>\1</sup>", p)
        p = re.sub(r"(?<=[A-Za-zΣπμσλτ])_([A-Za-z0-9]{1,4})(?![A-Za-z0-9])", r"<sub>\1</sub>", p)
        parts[i] = p
    return "".join(parts)


def has_tag(s: str) -> bool:
    return "<" in s


def xml(el) -> str:
    return LH.tostring(el, encoding="unicode")


# --------------------------------------------------------------------------- 数据
def read_sampling_rows(n=14):
    rows = []
    if not os.path.exists(CSV_WAVE):
        return rows
    with io.open(CSV_WAVE, encoding="utf-8-sig") as f:
        for i, r in enumerate(csv.DictReader(f)):
            if i >= n:
                break
            rows.append((r["n"], r["t_ms"], "%.6f" % float(r["x_n"]), r["int16"]))
    return rows


def build_sampling_table():
    rows = read_sampling_rows()
    if not rows:
        return None
    tr = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in rows)
    return ("<table class='num' data-cap='采样与量化的前 14 个点（fs = 8000 Hz，16 bit 量化）'>"
            "<tr><th>n</th><th>t = n·Ts / ms</th><th>x[n]（浮点）</th>"
            "<th>int16 量化</th></tr>" + tr + "</table>")


# --------------------------------------------------------------------------- 解析
def load_chapters():
    doc = LH.fromstring(io.open(SRC, encoding="utf-8").read())
    out = []
    for idx, sec in enumerate(doc.xpath("//section")):
        h2 = sec.xpath(".//h2")[0]
        no = h2.xpath(".//span[@class='no']")
        if no:
            label = no[0].text_content().strip()
        else:
            label = "附录"
        title = " ".join(h2.text_content().split())
        if no:
            title = title.replace(label, "", 1).strip()
        out.append({"idx": idx, "label": label, "title": title, "el": sec})
    return out


def chap_no(label: str) -> str:
    m = re.search(r"(\d+)", label)
    return m.group(1) if m else "A"


def transform_section(sec, ch_no):
    """返回该讲的正文 HTML。"""
    sec = deepcopy(sec)
    for h2 in sec.xpath(".//h2"):
        h2.getparent().remove(h2)

    # 图片指向印刷版资源
    for img in sec.xpath(".//img"):
        src = img.get("src", "")
        img.set("src", src.replace("assets/", "assets-print/"))

    # 采样量化表：截图 → 真正的表格
    table_html = build_sampling_table()
    if table_html:
        for fig in sec.xpath(".//figure"):
            img = fig.xpath(".//img")
            if img and "采样与量化" in (img[0].get("alt") or ""):
                wrap = LH.fragment_fromstring(
                    "<div class='tblwrap'>%s</div>" % table_html, create_parent=True)
                parent = fig.getparent()
                at = parent.index(fig)
                parent.remove(fig)
                for off, child in enumerate(list(wrap)):
                    parent.insert(at + off, child)
                break

    # 图编号
    k = 0
    for fig in sec.xpath(".//figure"):
        k += 1
        cap = fig.xpath(".//figcaption")
        if cap:
            c = cap[0]
            c.text = "图 %s-%d　%s" % (ch_no, k, (c.text or "").strip())

    # 长表跨页时重复表头：把首个含 th 的行放进 thead
    for tb in sec.xpath(".//table"):
        rows = tb.xpath("./tr")
        if rows and rows[0].xpath("./th"):
            thead = etree.Element("thead")
            tb.insert(0, thead)
            thead.append(rows[0])

    # 表编号（表题取自上文最近的标题）
    tk = 0
    for tb in sec.xpath(".//table"):
        cap_text = tb.get("data-cap") or ""
        prev = tb.getprevious()
        hop = 0
        while prev is not None and hop < 3 and not cap_text:
            if prev.tag in ("h4", "h3"):
                t = " ".join(prev.text_content().split())
                if prev.tag == "h4" and t not in BAD_CAP:
                    cap_text = t
                break
            if prev.tag == "p":
                t = " ".join(prev.text_content().split())
                t = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", "", t).rstrip("：: ")
                if 4 <= len(t) <= 34:
                    cap_text = t
                break
            prev = prev.getprevious()
            hop += 1
        if cap_text:
            tk += 1
            cap = LH.fromstring(
                "<div class='tcap'>表 %s-%d　%s</div>" % (ch_no, tk, cap_text))
            tb.addprevious(cap)

    # 公式排版
    for eq in sec.xpath(".//div[@class='eq']"):
        raw = "".join(eq.itertext())
        inner = "".join(xml(c) if isinstance(c, etree._Element) else (c or "")
                        for c in eq.xpath("child::node()")) or raw
        html_txt = typeset(inner)
        for c in list(eq):
            eq.remove(c)
        eq.text = ""
        frag = LH.fragment_fromstring("<div>%s</div>" % html_txt, create_parent=True)
        for c in list(frag):
            eq.append(c)
        if len([l for l in raw.split("\n") if l.strip()]) == 1:
            eq.set("class", "eq one")

    return "".join(xml(c) if isinstance(c, etree._Element) else (c or "")
                   for c in sec.xpath("child::node()"))


def build_body(chapters):
    parts = []
    for i, ch in enumerate(chapters):
        body = transform_section(ch["el"], chap_no(ch["label"]))
        parts.append(
            '<div class="chap%s" id="ch%d"><div class="chapno">%s</div>'
            '<h2>%s</h2><div class="rule"></div>%s</div>'
            % (" first" if i == 0 else "", i, ch["label"], ch["title"], body))
    return "\n".join(parts)


CSS_READY = CSS.replace("%%", "%").replace("%(accent)s", ACCENT)


def page_html(title, inner):
    return ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<title>%s</title><style>%s</style></head><body>%s</body></html>'
            % (title, CSS_READY, inner))


def cover_html():
    inner = (
        '<div class="cover">'
        '<table class="meta">'
        '<tr><td class="k">文档类型</td><td>学习讲义（自学用）</td>'
        '<td class="k">版　　本</td><td>2.0</td></tr>'
        '<tr><td class="k">适用对象</td><td>零基础，需高中物理与基础代数</td>'
        '<td class="k">配套项目</td><td>acoustic-lab/（可运行代码）</td></tr>'
        '<tr><td class="k">内容来源</td><td colspan="3">韩纪庆等《语音信号处理（第 3 版）》；'
        '王泉《声纹技术：从核心算法到工程实践》；项目实测数据</td></tr>'
        '<tr><td class="k">在线仓库</td><td colspan="3">github.com/Lzq2190/voiceprint-lab'
        '（讲义、代码、图表与数据；仓库说明见第 0 讲）</td></tr>'
        '<tr><td class="k">说　　明</td><td colspan="3">书中公式按标准形式重写并标注出处；'
        '全部图表由配套脚本实测生成，非示意图</td></tr>'
        '</table>'
        '<div class="grow"></div>'
        '<div class="mid">'
        '<div class="kicker">信 号 处 理 与 识 别 系 列</div>'
        '<h1>声纹信号处理</h1>'
        '<p class="sub">从零开始的学习讲义</p>'
        '<div class="rule"></div>'
        '<div class="tag">信号 → 特征 → 神经网络 → 声纹识别</div>'
        '</div>'
        '<div class="grow"></div>'
        '<div class="foot">'
        '<div class="org">共 16 讲 · 每讲含目标、产出、做法、误区与自检</div>'
        '<div>配套复现项目 acoustic-lab　·　全部图表为脚本实测生成</div>'
        '<div>github.com/Lzq2190/voiceprint-lab</div>'
        '<div>2026 年 11 月</div>'
        '</div></div>')
    return page_html("封面", inner)


def toc_html(chapters, pages):
    rows = []
    for i, ch in enumerate(chapters):
        rows.append(
            '<div class="item"><div class="no">%s</div><div class="ti">%s</div>'
            '<div class="dots"></div><div class="pg">%d</div></div>'
            % (ch["label"], ch["title"], pages.get(i, 1)))
    inner = (
        '<div class="toc"><h1>目　录</h1>'
        '<div class="hint">共 %d 讲　·　页码为正文页码</div>%s'
        '<div class="tocfoot">每一讲均按「目标 → 产出 → 准备 → 怎么做 + 为什么 → '
        '误区与注意事项 → 自检」编排。自检项可直接勾选，用于确认是否真正掌握；'
        '配套可运行项目 acoustic-lab/ 中的脚本生成了本文全部图表与数值。</div></div>'
        % (len(chapters), "".join(rows)))
    return page_html("目录", inner)


# --------------------------------------------------------------------------- 渲染
def render(hpath, ppath):
    if os.path.exists(ppath):
        os.remove(ppath)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", "--print-to-pdf=" + ppath,
                    "--virtual-time-budget=20000",
                    "file:///" + hpath.replace("\\", "/")],
                   check=True, capture_output=True, timeout=240)
    if not os.path.exists(ppath):
        raise RuntimeError("渲染失败：" + ppath)


def locate(pdf_path, chapters):
    """章首页 = 该页第一行恰好是「第 X 讲」/「附录」。"""
    import pymupdf as fitz
    doc = fitz.open(pdf_path)
    labels = [c["label"] for c in chapters]
    pages = {}
    firsts = []
    for i, p in enumerate(doc):
        lines = [l.strip() for l in p.get_text("text").split("\n") if l.strip()]
        firsts.append(lines[0] if lines else "")
        for k, lab in enumerate(labels):
            if k not in pages and firsts[-1] == lab:
                pages[k] = i + 1
    # 兜底：按标题文字查找
    for k, ch in enumerate(chapters):
        if k in pages:
            continue
        for i, p in enumerate(doc):
            if ch["title"][:12] in p.get_text("text"):
                pages[k] = i + 1
                break
    total = len(doc)
    doc.close()
    return pages, total, [k for k in range(len(chapters)) if k not in pages]


def main():
    if not CHROME:
        print("未找到 Chrome / Edge")
        sys.exit(1)

    print("1/6 解析讲义结构 ...")
    chapters = load_chapters()
    print("    %d 节：%s … %s" % (len(chapters), chapters[0]["label"], chapters[-1]["label"]))

    print("2/6 排版并渲染正文 ...")
    io.open(BODY_HTML, "w", encoding="utf-8").write(page_html("正文", build_body(chapters)))
    render(BODY_HTML, BODY_PDF)

    print("3/6 定位每讲起始页 ...")
    pages, nb, missing = locate(BODY_PDF, chapters)
    if missing:
        print("    [警告] 未定位：", missing)
    print("    正文 %d 页" % nb)

    print("4/6 生成封面与目录 ...")
    io.open(COVER_HTML, "w", encoding="utf-8").write(cover_html())
    render(COVER_HTML, COVER_PDF)
    io.open(TOC_HTML, "w", encoding="utf-8").write(toc_html(chapters, pages))
    render(TOC_HTML, TOC_PDF)

    import pymupdf as fitz
    nt = len(fitz.open(TOC_PDF))
    nc = len(fitz.open(COVER_PDF))
    print("    封面 %d 页，目录 %d 页" % (nc, nt))

    print("5/6 合并 ...")
    out = fitz.open()
    for p in (COVER_PDF, TOC_PDF, BODY_PDF):
        d = fitz.open(p)
        out.insert_pdf(d)
        d.close()

    print("6/6 页眉页脚 / 书签 / 元数据 ...")
    offset = nc + nt
    gray = (0.42, 0.45, 0.50)
    head = "声纹信号处理 · 从零开始的学习讲义"
    for pi in range(len(out)):
        if pi < offset:
            continue
        pg = out[pi]
        body_pno = pi - offset + 1
        hw = fitz.get_text_length(head, fontname="china-s", fontsize=7.6)
        pg.insert_text((pg.rect.width / 2 - hw / 2, 34), head,
                       fontname="china-s", fontsize=7.6, color=gray)
        pg.draw_line((pg.rect.width * 0.10, 40),
                     (pg.rect.width * 0.90, 40),
                     color=(0.83, 0.86, 0.90), width=0.5)
        s = str(body_pno)
        pg.insert_text((pg.rect.width / 2 - fitz.get_text_length(s, "helv", 9) / 2,
                        pg.rect.height - 24), s, fontname="helv", fontsize=9, color=gray)

    out.set_toc([[1, "%s　%s" % (ch["label"], ch["title"]), offset + pages.get(i, 1)]
                 for i, ch in enumerate(chapters)])
    out.set_metadata({
        "title": "声纹信号处理·从零开始的学习讲义",
        "author": "WorkBuddy",
        "subject": "基于韩纪庆《语音信号处理》与王泉《声纹技术》编排的初学者讲义",
        "keywords": "声纹, 语音信号处理, MFCC, 小波, EMD, 神经网络, 声纹识别",
        "creator": "Chrome + PyMuPDF",
    })
    # 若同名文件被预览器占用，自动换一个可写的名字
    cands = [FINAL, FALLBACK,
             os.path.join(GUIDE, "声纹信号处理学习讲义（详版）.pdf"),
             os.path.join(GUIDE, "声纹信号处理学习讲义（详版2）.pdf")]
    target, last = None, None
    for c in cands:
        try:
            out.save(c, garbage=4, deflate=True)
            target = c
            break
        except Exception as e:
            last = e
    if target is None:
        raise RuntimeError("所有候选文件名都不可写：%s" % last)
    total = len(out)
    out.close()

    for f in (BODY_HTML, TOC_HTML, COVER_HTML, BODY_PDF, TOC_PDF, COVER_PDF):
        if os.path.exists(f):
            os.remove(f)

    print("完成：%s" % os.path.basename(target))
    print("  %d 页 = 封面 %d + 目录 %d + 正文 %d，书签 %d 条" % (
        total, nc, nt, nb, len(chapters)))


if __name__ == "__main__":
    main()
