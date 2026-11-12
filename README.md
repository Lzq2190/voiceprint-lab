# 声纹信号处理 · 从零开始的学习讲义

> 一份写给零基础读者的中文讲义，加上一个把讲义里每个算法都手写了一遍的可运行项目。
> 讲义主体部分的每一张图、每一个数字，都是这个仓库里的脚本跑出来的，不是示意图，也不是抄来的结论。
> 工程专题里引用的文献数据均明确标注出处，不冒充本项目实测。

**讲义（网页版）** → [`guide-v2/index.html`](guide-v2/index.html)　双击即可打开，**完全离线可用**（KaTeX 及字体已放进仓库），学习进度存在浏览器里
**讲义（打印版）** → [`guide-v2/pdf/声纹信号处理学习讲义.pdf`](guide-v2/pdf/声纹信号处理学习讲义.pdf)　A4、120 页、20 条书签，公式与网页版同一套排版
**交互实验台** → [`guide-v2/labs.html`](guide-v2/labs.html)　DFT 投影与反向传播链式分解，参数可拖
**复现项目** → [`acoustic-lab/`](acoustic-lab)　只需 `numpy` + `pillow`，其余全部手写

> **v3.0 公式版**：全部公式改用 KaTeX 排版并按「讲-序」编号，不再是 `Σ_{n=0}^{N-1}` 这类等宽 ASCII；
> 每讲末尾新增**推导详解**——符号对照表、不跳步的推导、手算到底的数值例、公式与代码的逐行对应、
> 边界与失效条件。网页版与 PDF 使用同一份源文件、同一套本地字体，不需要联网。
>
> **v3.1 资料补充版**：依据 `Desktop/SHUJI` 的 7 本教材 + 2 篇变压器声纹文献，新增 **3 个工程专题**
> （A 变压器声纹实战 / B 经典算法补遗 / C 动手实验与资料索引），共 29 个新编号公式、11 张新表、
> 14 条新自检项；全篇 90 个编号公式、1400 处数学排版、约 5.1 万中文字。

---

## 这套材料解决什么问题

市面上的语音/声纹教材大体有两个毛病：一是公式给全了但不告诉你**为什么这么做**，二是罗列一堆论文的准确率却不说**这些数字能不能横向比**。这份讲义按"依赖链"重排，正文每一讲固定六段结构（第 0 讲、附录与三个工程专题略有不同）：

| 段落 | 回答的问题 |
|---|---|
| 目标 | 学完这一讲，你能**做到**什么（可验证） |
| 产出 | 你要写出什么、跑出什么 |
| 怎么做 + 为什么 | 逐步操作，每一步都解释动机与原理；公式逐条编号、变量逐个定义 |
| 推导详解 | 符号对照表 → 不跳步的推导 → 手算数值例 → 公式↔代码逐行对应 → 边界与失效条件 |
| 误区与注意事项 | 这一步最容易错在哪，错了会看到什么现象 |
| 自检 | 勾得上的硬标准，勾不上就别往下走 |

配套项目 `acoustic-lab` 的作用是**当标准答案**：讲义让你先自己写，写完用 `python run.py --check` 跟手写实现逐项对拍，误差到 `1e-12` 才算过。这比"看懂了"可靠得多。

---

## 仓库里有什么

| 路径 | 内容 | 怎么用 |
|---|---|---|
| `acoustic-lab/src/dsp.py` | DFT / FFT（Cooley–Tukey 向量化蝶形）/ STFT、Mel 滤波器组 + MFCC(13/39 维)、gamma 校正、Gammatonegram、Haar 与 db4 小波、Morlet CWT、EMD（含自写三次样条与 Thomas 解三对角） | 逐行对照讲义第 3–7 讲 |
| `acoustic-lab/src/features.py` | 49 维时域/频域/时频特征 + Fisher 可分性排序 + PCA + 相关热力图 | 讲义第 7 讲 |
| `acoustic-lab/src/nn.py` | 手写 BPNN 与 CNN（im2col / col2im / 池化 mask / 反向传播 / 数值梯度检查）+ 全部分类曲线 | 讲义第 8–10 讲 |
| `acoustic-lab/src/plot.py` | 零依赖绘图引擎（只靠 Pillow）：折线、热力图、柱状、三线表、堆叠子图，深/浅两套主题 | 想改配色改这里 |
| `acoustic-lab/src/wav.py` | 16 bit WAV 读写 + 6 类变压器声纹合成（`x(t)` 磁致伸缩模型 + 扰动项） | 讲义第 2 讲 |
| `acoustic-lab/run.py` | 一键入口：全流程 / `--check` 只验证 / `--wav` 跑真实录音 | 见下 |
| `acoustic-lab/data/` | 6 段 8 kHz / 0.5 s 合成声纹：正常、铁芯松动、直流偏磁、局部放电、短路冲击、风机老化 | 可换成自己的录音 |
| `acoustic-lab/outputs/` | 57 张 PNG、7 个 CSV、`metrics.json` | 讲义里的图全部来自这里 |
| `guide-v2/index.html` | 讲义网页版：17 讲 + 3 个工程专题 + 附录，约 5.1 万中文字、71 张表、90 个 KaTeX 编号公式（1400 处数学排版）、18 个推导详解、14 张实测图、86 个自检项 | 双击打开，无需联网 |
| `guide-v2/assets/katex/` | 本地化的 KaTeX 0.16.11（CSS / JS / 60 个字体文件，约 600 KB） | 网页与 PDF 共用，保证离线渲染 |
| `guide-v2/tools/math_data.py`、`exp_a~c.py` | 公式数据层：70 个原 ASCII 公式块的 LaTeX 映射 + 16 讲的推导详解 HTML | 改公式/加推导改这里，然后跑 `rebuild_guide.py` |
| `guide-v2/tools/topic_a~c.py` | 3 个工程专题的完整 section：变压器声纹实战、经典算法补遗、动手实验与资料索引 | 改专题内容改这里，同样由 `rebuild_guide.py` 装配 |
| `tools/survey_shuji.py` | 盘点 `Desktop/SHUJI` 资料，把 PDF/EPUB 目录与正文提取到 `.workbuddy/sources/`（<b>不入库</b>，版权内容） | 换新资料时重跑 |
| `guide-v2/tools/rebuild_guide.py` | 幂等地重建 `index.html`（从 `tools/backup/index_v2.html` 原始版重新装配公式、推导、KaTeX 运行时） | 改了数据层后重跑 |
| `guide-v2/tools/check_math.py` + `check_math.js` | 用本地 Node + KaTeX 逐条渲染全部 1400 处公式，定位任何语法错误 | `python tools/check_math.py`，需 Node 18+ |
| `guide-v2/assets/`、`assets-print/` | 深色版（网页用）与浅色版（印刷用）两套插图 | 由脚本生成，勿手改 |
| `guide-v2/labs.html` | 两个可拖的实验台：DFT 的缠绕/质心可视化、反向传播的链式分解（9 个权重可拖，实时数值梯度校验） | 双击打开，先预测再拖 |
| `guide-v2/tools/render_light_figs.py` | 用浅色主题重绘全部插图（字号放大 1.3 倍，缩到 A4 后仍清晰） | 改了图之后重跑 |
| `guide-v2/tools/build_pdf.py` | 把 `index.html` 排成正式 PDF：封面、目录（真实页码）、三线表、图注编号、页眉页码、书签，并在打印前执行 KaTeX 渲染 | 改了正文之后重跑 |

---

## 快速开始

```bash
git clone https://github.com/Lzq2190/voiceprint-lab.git
cd voiceprint-lab

# 只需要两个库，其余算法全部手写
pip install numpy pillow

cd acoustic-lab
python run.py --check     # 约 10 秒：只跑数值验证，打印对拍误差
python run.py             # 约 3 分钟：全流程，生成 57 张图 + 7 个 CSV + metrics.json
python run.py --wav "data/3_局部放电.wav"   # 换成单条真实录音
```

不想装 git：在仓库页面点 `Code` → `Download ZIP`，解压后目录结构相同。

### 验证表（`run.py --check` 的实际输出）

手写实现跟"标准答案"逐项对拍，这是判断代码有没有被改坏的唯一依据：

| 项 | 实测误差 |
|---|---|
| DFT vs `numpy.fft` | `1.4e-12` |
| FFT（Cooley–Tukey）vs `numpy.fft` | `7.1e-14` |
| STFT vs `numpy.fft` | `5.4e-15` |
| Haar 小波重构 RMSE | `1.7e-16` |
| db4 小波重构 RMSE | `1.0e-12` |
| EMD 重构 RMSE / 正交指数 | `3.4e-17` / `0.074` |
| BPNN 梯度检查（绝对误差） | `3.4e-11` |
| CNN 梯度检查（绝对误差） | `1.5e-11` |
| 测试准确率 BPNN / CNN | `1.000` / `0.979`（宏 F1 `0.979`） |

> 合成且稳态的数据上跑到 100%，只证明**实现正确**，不证明现场性能。所以项目里另有一条噪声鲁棒性衰减曲线：噪声比 1.0 时 BPNN 95.8% / CNN 58.3%，2.0 时 75.0% / 39.6%。这条曲线比上面的准确率更有信息量。

---

## 四个真踩过的坑（讲义里都写明了）

1. **db4 小波重构要用分析算子的转置 `Aᵀ`**。写成另一套卷积相位时，重构 RMSE 是 `1.40` 而不是 `1e-12`——差九个数量级，但图上看不出来，只有对拍才发现。
2. **CWT 的尺度是对数分布的**。直接把对数频率轴按线性刻度标 y 轴，会把 100 Hz 的谐波带标成 `912 Hz`，看起来"高频能量异常"，其实是标注错。
3. **近零梯度会放大相对误差**。BPNN 梯度检查一开始报 `5.3e-6`，看着像反向传播写错了；查到那个探针的解析梯度只有 `-2.03e-6`，绝对误差 `1e-11`，属于数值微分的固有噪声。所以本项目同时报相对误差与绝对误差，不靠放宽阈值掩盖。
4. **HTML 会吞掉 LaTeX 里的裸 `<`**。把 `f_{m-1}\le k<f_m` 直接写进网页，浏览器把 `<f_m` 当成标签开始，
   公式内容凭空少一截、PDF 里甚至残留 `\[ ... \]` 源码。现在生成时自动把公式内部的 `<` / `>` 换成
   `\lt` / `\gt`，并用 Node + KaTeX 逐条渲染校验，才把 1400 处公式全部跑通。

---

## 重新生成讲义与 PDF

正文在 `guide-v2/index.html`，PDF 由它排版而来，**不要直接改 PDF**；公式与各讲推导详解的源文件在
`guide-v2/tools/math_data.py` 与 `exp_a~c.py`，三个工程专题在 `topic_a~c.py`，**也不要直接改 index.html 里的公式**：

```bash
cd guide-v2
python tools/rebuild_guide.py        # 从原始版幂等重建 index.html（公式 + 推导 + 3 专题 + KaTeX + 导航）
python tools/check_math.py           # 用本地 Node + KaTeX 逐条校验，必须 1400/1400 通过
python tools/render_light_figs.py    # 仅在改了插图配色/字号时：重绘 assets-print/
python tools/build_pdf.py            # 重新排版 PDF（封面/目录/书签/页码自动重建）
```

`rebuild_guide.py` 每次从 `tools/backup/index_v2.html`（改造前的原始讲义）重新装配，所以重复运行不会
重复注入内容。它还会把 LaTeX 里的裸 `<` / `>` 自动换成 `\lt` / `\gt`——否则 HTML 解析器会把
`k<f_m` 中的 `<f_m` 当成一个标签吃掉，公式就残缺了。

PDF 输出到 `guide-v2/pdf/声纹信号处理学习讲义.pdf`。脚本先写临时文件再原子替换正式名——
Windows 上 PDF 常被预览器占用，替换失败时它会明确提示并存成「（待替换）.pdf」，不会静默改出一堆副本。

`build_pdf.py` 会自动：给每讲另起一页、把表格转三线表并按「表 X-Y」编号、给图注加「图 X-Y」、
**在打印前执行本地 KaTeX 渲染**（所以 PDF 里的 Σ / ∫ / 分式 / 上下标与网页版完全一致）、
生成带真实页码的目录和 20 条书签。PDF 生成需要 `lxml` + `pymupdf`，本机还要有 Chrome 或 Edge。

> 注意：`render_light_figs.py` 会直接 import 兄弟目录 `../acoustic-lab/src/`，
> `build_pdf.py` 会读 `../acoustic-lab/outputs/waveform_data.csv`。所以这两个目录必须保持同级。

**推送**：国内网络下 `git push` 常因本机代理挡住 `github.com:443` 而失败（`502` / SSL EOF），
但 `api.github.com` 通常可直连。此时用 `python tools/push_github_api.py`，它通过 Git Data API
把最近一次本地 commit 推到远端 `main`；token 从系统 Git 凭据动态读取，不写进文件也不打印。
脚本比较父提交的目录树而非 commit sha，因此用它推送之后仍可继续正常迭代。

---

## 关于参考教材与版权

讲义的知识点来自 7 本教材 + 2 篇变压器声纹文献，专题 C.3 有一张完整的「资料 → 知识点 → 章节」对照表：

- 韩纪庆、张磊、郑铁然《语音信号处理（第 3 版）》— 理论根基
- 王泉《声纹技术：从核心算法到工程实践》— 工程视角与声纹评价体系
- 赵力《语音信号处理（第三版）》— 经典算法知识地图（VQ / HMM / LPC / LSP / DTW / 语音增强）
- 梁瑞宇、赵力、魏昕《语音信号处理实验教程》— 13 章实验编排
- 柳若边《深度学习语音识别技术实践》— WFST / DTW / 端到端 / N-gram 与平滑
- 宋知用《MATLAB 语音信号分析与合成》、姜囡《语音信号识别技术与实践》— 实现与系统结构旁证
- 朱柯佳（2021，硕士论文）、陆云才等（2023）— **专题 A 的主体**：去噪、特征、诊断与实测数字

**这些资料的原文、以及从 PDF/EPUB/MOBI 提取的全文文本，都没有放进这个仓库**——那属于版权内容，提取结果只留在本地的 `.workbuddy/sources/`。仓库只包含：

- 自己手写的算法实现与绘图引擎（`acoustic-lab/`）
- 由脚本从合成数据生成的图表与数值
- 自己撰写的讲义正文与排版脚本（含 3 个专题）

公式按标准形式自行推导重写并标注出处；文献中的准确率一律注明「原作者样本库结果，非本项目实测」。
三本扫描版 PDF 没有文本层，本次只用其目录做知识地图，没有 OCR 后照抄。想深读原书请自备正版。

---

## 环境要求

| 项 | 要求 |
|---|---|
| Python | 3.9+（开发环境 3.13） |
| 运行项目 | `numpy`、`pillow` |
| 生成 PDF | `lxml`、`pymupdf`，以及本机安装 Chrome 或 Edge（无头打印） |
| 校验公式（开发时） | Node 18+；KaTeX 已本地化在 `guide-v2/assets/katex/`，无需联网 |
| 中文字体 | Windows 自带（宋体 / 微软雅黑 / 等线）；其他系统需自行替换 `plot.py` 里的字体路径 |
| 磁盘 | 约 18 MB（含 120 页 PDF 3.3 MB、71 张插图、本地 KaTeX 字体 1.5 MB） |

`numpy.fft` 只在验证时充当"标准答案"，项目里所有算法都是手写的，不调用 `scipy` 或 `librosa`。

---

## 许可

代码（`acoustic-lab/`、`guide-v2/tools/`）可自由使用与修改，保留出处即可。
讲义正文欢迎引用与转载，注明来源仓库。图表由本项目脚本生成，可随意复用。
