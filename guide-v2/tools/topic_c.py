# -*- coding: utf-8 -*-
"""专题 C：动手实验清单与资料索引（完整 <section>）。

资料来源：
  梁瑞宇/赵力/魏昕《语音信号处理实验教程》（机械工业出版社，2016）13 章实验体系
  本仓库 SHUJI 目录下的 9 本教材 + 2 篇文献（原文与提取文本均不入库）
"""

TOPIC_C = r"""
<section id="sC">
  <h2><span class="no">专题 C</span>动手实验清单与资料索引</h2>

  <div class="goal">
    <div class="g">目标</div>
    <ul>
      <li>把前面 17 讲 + 专题 A/B/D/E 的每一条结论，都变成一条<strong>能自己跑、能判对错</strong>的实验。</li>
      <li>知道每本参考书各自贡献了什么，遇到卡点时能直接定位到该翻哪一本、哪一章。</li>
      <li>养成「先预测结果 → 再跑 → 对不上就找根因」的习惯，而不是把代码跑通就算学完。</li>
    </ul>
  </div>
  <div class="goal">
    <div class="g">产出</div>
    <ul><li>一张打了勾的实验记录表；一份自己写的「参数 → 现象」笔记；能说清每个验收标准的数字是怎么来的。</li></ul>
  </div>

  <h3>C.1　教材实验体系与本讲义的对应</h3>
  <p>梁瑞宇、赵力、魏昕《语音信号处理实验教程》是赵力《语音信号处理（第 3 版）》的配套实验教材，共 13 章、基于 MATLAB。它给的是<strong>实验编排</strong>，本讲义给的是<strong>为什么这么做 + 手写实现</strong>，两者正好互补：</p>
  <table class="sym">
    <tr><th>教程章节</th><th>实验内容</th><th>对应本讲义</th><th>本项目的替代做法</th></tr>
    <tr><td>第 1 章</td><td>MATLAB 基础教程</td><td>第 0 讲</td><td><code>python run.py --check</code> 取代 MATLAB 环境</td></tr>
    <tr><td>第 2 章</td><td>语音信号处理基础实验</td><td>第 1–2 讲</td><td><code>src/wav.py</code> 手写 WAV 读写与 6 类合成声纹</td></tr>
    <tr><td>第 3 章</td><td>语音信号分析实验</td><td>第 3–5 讲</td><td>能量 / 过零率 / 自相关 / STFT 全套手写</td></tr>
    <tr><td>第 4 章</td><td>语音信号特征提取实验</td><td>第 6–7 讲</td><td>MFCC(13/39)、Mel 滤波器组、小波与 EMD</td></tr>
    <tr><td>第 5 章</td><td>语音增强实验</td><td>专题 A.3 / B.5</td><td>谱减、维纳、小波阈值三种可对比实现</td></tr>
    <tr><td>第 6 章</td><td>语音编码实验</td><td>专题 B.1 / B.2</td><td>LPC / 反射系数 / LSP / VQ 码本</td></tr>
    <tr><td>第 7 章</td><td>语音合成与转换实验</td><td>专题 B.1（源–滤波器模型）</td><td>用全极点模型反过来合成，验证 \(H(z)\)</td></tr>
    <tr><td>第 8 章</td><td>语音隐藏实验</td><td>第 4 讲（频域）、第 5 讲（时频）</td><td>可作为拓展：在谱里嵌信息再看可恢复性</td></tr>
    <tr><td>第 9 章</td><td>声源定位实验</td><td>第 3 讲（互相关）</td><td>把自相关推广成互相关估时延 \(\tau\)</td></tr>
    <tr><td>第 10 章</td><td>语音识别实验</td><td>专题 B.3 / B.4 / B.6</td><td>DTW、Viterbi、WFST 概念验证</td></tr>
    <tr><td>第 11 章</td><td>说话人识别实验</td><td>第 11–14 讲</td><td>VQ / GMM-UBM / i-vector / embedding 四类打分对照</td></tr>
    <tr><td>第 12 章</td><td>语音情感识别实验</td><td>第 10 讲（特征与评估）</td><td>换标签重跑同一套特征 + BPNN/CNN</td></tr>
    <tr><td>第 13 章</td><td>实用语音信号处理平台</td><td>第 15 讲</td><td>把前面各模块串成一条命令行流水线</td></tr>
  </table>
  <div class="tip"><span class="t">怎么用这张表</span>教程用 MATLAB，本讲义用纯 Python + numpy + Pillow，<strong>没有第三方算法库</strong>。如果你的目的是「真正理解」，建议先按本讲义手搓一遍，再去对照教程里的 MATLAB 实现——两边结果应当一致，不一致就是最有价值的学习点。</div>

  <h3>C.2　15 个可自己跑的实验</h3>
  <p>每个实验都写清<strong>改什么、预期看到什么、怎么算通过</strong>。所有实验都在 <code>acoustic-lab/</code> 里做，先用 <code>python run.py --check</code> 确认基线，再单独改动一个参数——<b>一次只动一个变量</b>，否则现象无法归因。</p>

  <div class="mathbox">
    <div class="math">\[ \varepsilon_{\mathrm{rel}}=\frac{\big\|g_{\text{ours}}-g_{\text{ref}}\big\|}{\big\|g_{\text{ours}}\big\|+\big\|g_{\text{ref}}\big\|+\epsilon}\lt 10^{-10},\qquad
    \mathrm{macro}F_1=\frac{1}{C}\sum_{c=1}^{C}\frac{2P_cR_c}{P_c+R_c} \tag{C-1} \]</div>
    <div class="mathnote"><p>左边是所有「对拍类」实验的通用验收线（第 8 讲梯度检查、第 4 讲 DFT 对拍都用它）；右边是类别不平衡时必须补报的指标（第 10 讲、专题 A.5.4）。</p></div>
  </div>

  <h4>第一组：基础层（E1–E5）</h4>
  <table class="sym">
    <tr><th>编号</th><th>改动</th><th>预期现象</th><th>验收标准</th></tr>
    <tr><td>E1 混叠</td><td>把含 1000 Hz 分量的信号按 800 Hz 重采样</td><td>峰跑到 200 Hz，且再怎么增加采样点数也回不来</td><td>用 \(f_{\mathrm{alias}}=\min_k|f-kF_s|\) 手算得 200 Hz（第 2 讲式 2-3）</td></tr>
    <tr><td>E2 量化</td><td>量化位数 16 → 8 → 4 bit</td><td>波形出现台阶，底噪抬升</td><td>SNR 依 \(6.02B+1.76\) 约 98 / 50 / 26 dB（式 2-4、推导 2-11）</td></tr>
    <tr><td>E3 加窗</td><td>汉明窗 ↔ 矩形窗，对非整周期正弦做谱</td><td>矩形窗旁瓣约 −13 dB 且主峰降约 3.9 dB；汉明窗旁瓣约 −43 dB</td><td>量出两者旁瓣差 \(\ge 25\,\mathrm{dB}\)</td></tr>
    <tr><td>E4 DFT 对拍</td><td>自己写 \(X[k]=\sum_n x[n]W_N^{kn}\)，与 <code>np.fft.fft</code> 比</td><td>逐点几乎相同</td><td>最大绝对偏差 \(\lt 10^{-12}\)（本仓库实测 \(1.4\times10^{-12}\)）</td></tr>
    <tr><td>E5 补零</td><td>256 点补到 1024 点，信号含 100 Hz 与 120 Hz</td><td>谱线从 31.25 Hz 变「密」到 7.8 Hz，但两个峰仍糊在一起</td><td>能说出真实分辨率由 \(T_{\rm obs}\) 决定（式 4-6 / 4-13）</td></tr>
  </table>

  <h4>第二组：特征层（E6–E10）</h4>
  <table class="sym">
    <tr><th>编号</th><th>改动</th><th>预期现象</th><th>验收标准</th></tr>
    <tr><td>E6 预加重</td><td>\(\alpha:0\to0.97\)</td><td>100 Hz 基频被明显压低</td><td>按 \(|H|^2=(1-\alpha)^2+4\alpha\sin^2(\omega/2)\) 算出低频约 −26 dB（专题 A / 第 6 讲式 6-9）</td></tr>
    <tr><td>E7 Mel 通道账</td><td>打印 26 个滤波器中心频率，数 100–500 Hz 内有几个</td><td>只有 2–3 个通道覆盖最关键的谐波区</td><td>能复算 \(m(f)=2595\log_{10}(1+f/700)\) 与第 6 讲前 10 个中心频率表</td></tr>
    <tr><td>E8 差分 vs 维度</td><td>13 维静态 → 30 维静态 → 13+Δ+ΔΔ（39 维），各跑同一分类器</td><td>加维度收益很小，加差分明显变好</td><td>复现韩书表 3-3 的结论（加差分约降 20% 误识），并解释最小二乘斜率（式 6-15）</td></tr>
    <tr><td>E9 阈值函数</td><td>对同一含噪信号分别用硬 / 软 / 半软阈值</td><td>硬阈值重构有振荡；软阈值整体幅值偏低；半软两者都缓解</td><td>同时报 RMSE 与 LSD，说明为什么只看 SNR 会漏掉谱畸变（专题 A 式 A-7）</td></tr>
    <tr><td>E10 谱减法</td><td>调过减因子 \(\alpha=1.0\to2.0\)、谱下限 \(\beta\)</td><td>\(\alpha\) 太大出现音乐噪声、谱峰被削</td><td>画出「去噪后」与「原始」的谐波峰高对比，指出哪一列判别信息丢了</td></tr>
  </table>

  <h4>第三组：模型与经典算法（E11–E15）</h4>
  <table class="sym">
    <tr><th>编号</th><th>改动</th><th>预期现象</th><th>验收标准</th></tr>
    <tr><td>E11 学习率</td><td>\(\eta:0.1\to2.0\)，连点「下降一步」</td><td>先震荡、后发散甚至 NaN</td><td>能用 \(\eta\lt 2/\lambda_{\max}\) 解释（第 10 讲）；<code>labs.html</code> 第二个实验台可直接拖</td></tr>
    <tr><td>E12 梯度检查</td><td>关掉 dropout，对每个权重做中心差分</td><td>解析梯度与数值梯度一致</td><td>绝对误差 \(\lt 10^{-10}\)；近零元素要用式 C-1 的相对误差判据，别被 \(5\times10^{-6}\) 吓到</td></tr>
    <tr><td>E13 LPC 阶数</td><td>\(p=4,8,12,20\)，画 \(1/|A(e^{j\omega})|\) 与 MFCC 包络叠加</td><td>低阶平滑欠拟合，过高出现虚假谱峰</td><td>用 B-6 从根算出前 3 个共振峰频率，与谱峰位置对上</td></tr>
    <tr><td>E14 VQ 码本</td><td>码本大小 \(K=2,4,\dots,256\)，画平均失真 \(D\) 曲线</td><td>单调下降、边际收益递减；注意过拟合</td><td>每次 LBG 迭代 \(D\) 不增；报告每帧比特数 \(b=\log_2K\)</td></tr>
    <tr><td>E15 时间对齐</td><td>同一段语音快放/慢放，分别跑 DTW 与 Viterbi</td><td>得到可解释的对齐路径，快放版路径被压缩</td><td>手算一个 \(3\times3\) 的 DTW 网格，与代码输出逐格一致（式 B-10）</td></tr>
  </table>
  <div class="note"><span class="t">实验记录模板</span>每条实验记四行：<b>预测</b>（我以会看到什么）→ <b>实测</b>（实际数字/截图）→ <b>差异</b>（对不上的地方）→ <b>根因</b>（哪条公式或哪行代码）。第 0 讲说过「预测—打脸」的过程才是真正记住的地方；没有第一行的实验记录等于没做。</div>

  <h3>C.3　资料来源索引</h3>
  <p>本讲义的知识点来自下列资料。按仓库约定，<strong>原书全文与从电子书提取的文本均不入库</strong>（版权内容），仓库只包含自己撰写的讲义、自己手写的算法实现、以及由脚本实测生成的图表与数值。</p>
  <table class="sym">
    <tr><th>资料</th><th>形态</th><th>本次用于</th><th>对应章节</th></tr>
    <tr><td><strong>郑君里、应启珩、杨为理《信号与系统（第三版）》上、下册</strong></td><td>PDF 扫描版，160 条书签可作框架</td><td><strong>理论根基</strong>：LTI 与卷积、卷积定理、抽样与内插、拉普拉斯与零极点、无失真传输与希尔伯特、帕塞瓦尔/相关/匹配滤波/测不准、z 变换与 ROC、DFS→DFT、IIR/FIR 设计、反馈稳定性、状态变量</td><td>专题 D / E 全篇；第 1–14 讲的「理论桥接」；附录 12 章映射表</td></tr>
    <tr><td>韩纪庆、张磊、郑铁然《语音信号处理（第 3 版）》</td><td>EPUB，可提取全文</td><td>语音侧根基：产生模型、短时分析、同态解卷积、Mel 倒谱、线性预测、LPC 倒谱</td><td>第 1–7 讲、专题 B.1 / B.5</td></tr>
    <tr><td>王泉《声纹技术：从核心算法到工程实践》</td><td>MOBI，可提取全文</td><td>工程视角：预处理、评价指标、GMM-UBM、i-vector、深度学习声纹</td><td>第 11–14 讲</td></tr>
    <tr><td>赵力《语音信号处理（第三版）》</td><td>PDF 扫描版，仅目录可用</td><td><strong>知识地图</strong>：矢量量化、HMM、LPC/LSP、端点检测、基音/共振峰、语音增强、DTW、说话人识别各分支</td><td>专题 B 全篇、第 3/5 讲延伸</td></tr>
    <tr><td>梁瑞宇、赵力、魏昕《语音信号处理实验教程》</td><td>PDF，可提取</td><td>13 章实验体系与编排</td><td>专题 C.1、各讲「动手」部分</td></tr>
    <tr><td>柳若边《深度学习语音识别技术实践》</td><td>EPUB，可提取</td><td>Kaldi / WFST / FST、DTW、VAD、端到端、N-gram 与平滑、困惑度</td><td>专题 B.4 / B.6</td></tr>
    <tr><td>宋知用《MATLAB 语音信号分析与合成（第 2 版）》</td><td>PDF 扫描版</td><td>仅作「MATLAB 实现路线」的参照，未转录正文</td><td>专题 C.1 对照</td></tr>
    <tr><td>姜囡《语音信号识别技术与实践》</td><td>PDF 扫描版</td><td>识别系统结构的旁证，未转录正文</td><td>第 11 讲</td></tr>
    <tr><td>朱柯佳《高噪声环境下变压器声纹特征提取方法研究》（2021，硕士论文）</td><td>PDF，字符定位需重排</td><td><strong>专题 A 主体</strong>：三种去噪法对比、改进/分层阈值、小波包能量谱、TFCC、Laplacian/Fisher 选维、现场实测数字</td><td>专题 A.2–A.4、A.6</td></tr>
    <tr><td>陆云才等《基于声纹特征和集成学习的变压器缺陷诊断方法》（2023）</td><td>PDF，可提取</td><td><strong>专题 A 主体</strong>：19 类样本库、多通道时频输入、CNN+CBAM、stacking 二次诊断、单一/混合缺陷实测结果</td><td>专题 A.1 / A.5</td></tr>
  </table>
  <div class="warn inline"><span class="t">一句提醒</span>四本扫描版 PDF（郑君里上/下册、宋知用、姜囡）没有文本层，本次只用它们的目录做知识地图，正文公式全部按标准教材形式自行推导，没有从扫描件 OCR 后照抄。郑君里两册的价值在<strong>理论框架</strong>：专题 D/E 的章节顺序、定理编号与符号记法（\(\operatorname{Sa}(x)\)、\(\omega_s=2\pi/T_s\)、DFS 式 9-18/9-19、DTFT 式 8-82）都对照其书签目录与抽样页核对过，但推导文字是重写的。专题 A 里朱柯佳论文的「改进阈值函数」也一样：讲义给出的是同家族的<strong>半软阈值标准形式</strong>并说明思路，不是原论文图中分段公式的逐字转录。</div>

  <h3>C.4　从讲义到现场：十条检查清单</h3>
  <div class="defbox"><div class="dh">上线前逐条过</div>
  <ol>
    <li><b>采样率是不是任务定的？</b>局放要数 kHz 以上，8 kHz 不够（专题 A.2）。</li>
    <li><b>抗混叠滤波在 ADC 之前吗？</b>采样后再补已经晚了（第 2 讲式 2-10）。</li>
    <li><b>预处理有没有压掉判别频段？</b>预加重 \(\alpha=0.97\) 会把 100 Hz 压掉约 26 dB。</li>
    <li><b>分帧/帧移是否满足重叠相加？</b>无重叠会让重构失真（第 5 讲式 5-5）。</li>
    <li><b>特征是不是照搬语音配置？</b>Mel 在低频只给 2–3 个通道（第 6 讲、专题 A.4）。</li>
    <li><b>去噪有没有引入失真？</b>同时报 SNR、RMSE、LSD，不要只看波形像不像。</li>
    <li><b>划分是不是按「段/设备」分组？</b>按帧随机切会让指标虚高（第 10 讲）。</li>
    <li><b>类别不平衡有没有报宏 \(F_1\)？</b>960 : 100 的样本比会骗人（专题 A.5.4）。</li>
    <li><b>阈值是在开发集上选的吗？</b>在测试集上调阈值等于作弊（第 12 讲）。</li>
    <li><b>换设备/换工况后还稳吗？</b>CMN、z-norm、域适配至少做一个（第 6/12 讲）。</li>
  </ol></div>

  <h3>自检</h3>
  <div class="checklist">
    <label><input type="checkbox" data-k="qC-1"> 我能不看讲义，把 15 个实验里任意 5 个的「预期现象 + 验收数字」说出来。</label>
    <label><input type="checkbox" data-k="qC-2"> 我知道遇到「频谱突然多出不该有的峰」「换设备就崩」「指标虚高」分别该翻哪一讲。</label>
    <label><input type="checkbox" data-k="qC-3"> 我能说清哪些资料是扫描版、为什么讲义没有照抄它们的公式。</label>
    <label><input type="checkbox" data-k="qC-4"> 我已经真的跑过至少 5 个实验，并写下了「预测 / 实测 / 差异 / 根因」四行记录。</label>
  </div>
</section>
"""
