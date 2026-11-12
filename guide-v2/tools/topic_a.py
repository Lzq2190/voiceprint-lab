# -*- coding: utf-8 -*-
"""专题 A：变压器声纹 —— 从物理机理到故障诊断（完整 <section>）。

资料来源：
  朱柯佳《高噪声环境下变压器声纹特征提取方法研究》（华北电力大学硕士论文，2021）
  陆云才等《基于声纹特征和集成学习的变压器缺陷诊断方法》（电力工程技术，2023, 42(5)）
  韩纪庆《语音信号处理》第 2/3 章、赵力《语音信号处理（第三版）》第 4/6 章
文献中的准确率均为原作者在其自建样本库上的结果，不是本项目 acoustic-lab 的实测值。
"""

TOPIC_A = r"""
<section id="sA">
  <h2><span class="no">专题 A</span>变压器声纹：从物理机理到故障诊断</h2>

  <div class="goal">
    <div class="g">目标</div>
    <ul>
      <li>能推出「正常变压器为什么是 100 Hz 基频」，并说清各类缺陷怎样改变频谱。</li>
      <li>掌握现场抗噪的三条路线（小波阈值 / 谱减法 / FastICA）及各自的适用边界。</li>
      <li>理解小波包能量谱与 TFCC 为什么比照搬语音的 MFCC 更贴合设备声纹。</li>
      <li>能读懂多通道 CNN + 集成学习的诊断流水线，并复述其中的维度账与实测结果。</li>
    </ul>
  </div>
  <div class="goal">
    <div class="g">产出</div>
    <ul><li>一张「缺陷 → 物理机制 → 频域表现」对照表；一份可自己跑的去噪对比实验；一段能解释 (8, 96000) 输入怎么来的维度推导。</li></ul>
  </div>

  <div class="note"><span class="t">关于本专题的数字</span>下面标了出处的准确率（92.0% / 98.7% / 99.2% / 99.7% / 99.65% / 99.4% 等）来自上述两篇文献的<strong>自建样本库</strong>，样本数、采样率、噪声条件都和本讲义 <code>acoustic-lab</code> 的 8 kHz 合成数据不同，<b>不能当成本项目的实测结果</b>。讲义引用它们是为了说明「每一步改动带来了多少收益」以及「哪一步最容易翻车」，不是给自己的系统背书。</div>

  <h3>A.1　声音从哪来：先推出 100 Hz</h3>
  <p>变压器本体噪声不是「随机嗡嗡声」，而是有严格频率结构的确定性振动。主要来源是<strong>铁芯磁致伸缩</strong>：硅钢片在交变磁场中被周期性拉伸/压缩。关键在于磁致伸缩应变与磁感应强度的<strong>平方</strong>成正比，而电网工频是 50 Hz：</p>
  <div class="mathbox">
    <div class="math">\[ \varepsilon(t)\propto B^2(t)=B_m^2\sin^2(2\pi\cdot 50\,t)=\frac{B_m^2}{2}\Big[1-\cos\big(2\pi\cdot 100\,t\big)\Big] \tag{A-1} \]</div>
    <div class="mathnote"><p>用 \(\sin^2\theta=\frac{1-\cos2\theta}{2}\) 把平方展开，频率直接<strong>翻倍</strong>：50 Hz → <b>100 Hz</b>。绕组受到的洛伦兹力 \(F=BIL\propto i^2\) 同理也含 \(2f\) 分量。所以正常声纹是一组以 100 Hz 为基频的谐波串：100 / 200 / 300 / 400 Hz……这正是第 1 讲「谐波叠加」的物理实例。</p></div>
  </div>
  <p>非线性（磁化曲线弯曲、铁芯饱和）会让 \(B(t)\) 不再是纯正弦，于是平方后除了 \(2f\) 还会长出 \(4f,6f,\dots\) 等高次谐波；一旦<strong>直流偏磁</strong>让工作点偏移、正负半周不对称，还会出现 50 Hz 的<strong>奇次倍频</strong> 150 / 250 / 350 Hz——本讲义合成数据里「直流偏磁」类正是这么造的（第 1 讲式 1-3、第 6 讲误区）。</p>

  <table class="sym">
    <tr><th>状态 / 缺陷</th><th>物理机制</th><th>频域表现</th><th>时域表现</th></tr>
    <tr><td>正常运行</td><td>磁致伸缩 + 绕组电动力，\(\propto B^2\)</td><td>100 Hz 基频 + 偶次谐波，谱线稳定</td><td>近似周期、幅值平稳</td></tr>
    <tr><td>直流偏磁</td><td>铁芯半周饱和、正负不对称</td><td>新增 150 / 250 / 350 Hz（50 Hz 奇次倍频）</td><td>波形上下不对称</td></tr>
    <tr><td>铁芯 / 夹件松动</td><td>固有模态被电磁力激发、约束变松</td><td>谐波比例改变，出现新的窄带峰与宽带底噪</td><td>周期性变差，幅值调制</td></tr>
    <tr><td>绕组短路冲击</td><td>瞬态电动力冲击、结构位移</td><td>宽频能量突然抬升，随后衰减</td><td>短促强脉冲，非平稳</td></tr>
    <tr><td>局部放电（沿面/电晕/悬浮/间歇）</td><td>绝缘击穿产生压力脉冲</td><td>能量偏向高频（数 kHz 以上），基频区几乎不变</td><td>稀疏尖峰、重复率随类型变化</td></tr>
    <tr><td>重过载</td><td>电流增大、磁通与振动增强</td><td>100 Hz 幅值显著上升，谐波相对比例变化</td><td>整体幅值变大、波形仍周期</td></tr>
    <tr><td>油泵 / 风扇异响、冷却器</td><td>机械转动与叶片通过频率</td><td>固定低频线谱 + 与其谐波，常叠加宽带风噪</td><td>持续、准平稳</td></tr>
  </table>
  <div class="tip"><span class="t">和第 6 讲接上了</span>这张表解释了讲义反复强调的一句话：<b>设备声纹的判别信息集中在 100–500 Hz</b>。而 MFCC 的 Mel 滤波器组把这一段只分到 2–3 个通道，高频却分得很宽——所以照搬语音配置会丢掉主要信息。陆云才等（2023）也明确指出「梅尔频谱主要用于人声识别，和变压器这一场景并不完全相符，不利于提取变压器基频和高次倍频的信号特征」。</div>

  <h3>A.2　现场为什么必须先去噪</h3>
  <p>实验室里的合成信号干净，现场不是。陆云才等构建的声纹样本库共 <b>19 类</b>：4 类正常主变噪声（110 / 220 / 500 / ±800 kV，各 960 段）、5 种环境噪声（变电站噪声叠加雷声 / 鸟鸣 / 汽笛 / 人声 / 雨声，各 192 段）、10 类异常（短路冲击 160、沿面放电 150、电晕放电 150、间歇性放电 140、悬浮放电 150、重过载 300、直流偏磁 150、夹件松动 100、油泵异响 150、风扇异响 150 段）。采集条件是 <b>10 s、48 kHz</b>。</p>
  <p>为什么现场用 48 kHz、而本讲义用 8 kHz？局放脉冲的高频分量在数 kHz 以上，8 kHz 采样的奈奎斯特上限只有 4000 Hz（第 2 讲式 2-2），会把最关键的放电特征直接混叠掉；48 kHz 则留出充分余量。<b>采样率是任务定义的，不是随便选的</b>——这句话在第 2 讲说过，这里有了工程上的代价演示。</p>
  <p>朱柯佳（2021）把现场干扰分成三类，并实测出输入 SNR 常在 \([-5,\,5]\) dB：</p>
  <table class="sym">
    <tr><th>干扰类型</th><th>例子</th><th>特点</th><th>最合适的去噪法</th></tr>
    <tr><td>瞬时强干扰</td><td>雷声、汽笛、人声</td><td>短时、能量高、非平稳</td><td>小波阈值 / FastICA</td></tr>
    <tr><td>持续弱干扰</td><td>风机声、雨声</td><td>长时间、准平稳、与本体频段重叠</td><td>谱减法（但失真大）</td></tr>
    <tr><td>混合噪声</td><td>上述叠加</td><td>频谱结构复杂</td><td>小波阈值（对不同噪声最稳）</td></tr>
  </table>
  <p>论文结论值得原样记住：<b>小波阈值法对不同噪声类型的效果差别不大，但受输入 SNR 影响较大；FastICA 更适合瞬时干扰与混合噪声、处理持续弱干扰效果不佳；谱减法更适合持续弱干扰，但三种方法里它的信号失真度最高；三者中小波阈值法略优于 FastICA。</b>不存在「一种去噪打天下」。</p>

  <h3>A.3　去噪三法，逐个推到底</h3>
  <h4>A.3.1　小波阈值去噪</h4>
  <p>观测模型 \(y[n]=x[n]+d[n]\)。正交小波变换 \(W\) 是线性的，所以 \(Wy=Wx+Wd\)：有用信号的能量集中在少数大系数上，白噪声能量则摊平在所有系数上。于是去噪三步：<b>分解 → 对细节系数阈值量化 → 逆变换重构</b>。两种经典阈值函数：</p>
  <div class="mathbox">
    <div class="math">\[ \eta_{\mathrm{hard}}(w)=\begin{cases}w,&|w|\gt \lambda\\ 0,&|w|\le \lambda\end{cases}\qquad
    \eta_{\mathrm{soft}}(w)=\operatorname{sgn}(w)\big(|w|-\lambda\big)_+ \tag{A-2} \]</div>
    <div class="mathnote"><p>硬阈值在 \(w=\pm\lambda\) 处<strong>不连续</strong>，重构时容易产生振荡（吉布斯样伪影）；软阈值连续、重构平滑，但对所有保留系数都减去 \(\lambda\)，产生<strong>恒定偏差</strong>，幅值被系统性压低——论文原话是「会使得部分有效声音信号特征丢失」。</p></div>
  </div>
  <p>折中方案是<strong>半软阈值（firm shrinkage）</strong>：用两个阈值 \(\lambda_1\le\lambda_2\)，中间线性过渡，两端分别恒为 0 与恒等：</p>
  <div class="mathbox">
    <div class="math">\[ \eta_{\mathrm{firm}}(w)=\begin{cases}
    0,&|w|\le\lambda_1\\[3pt]
    \operatorname{sgn}(w)\,\dfrac{\lambda_2\big(|w|-\lambda_1\big)}{\lambda_2-\lambda_1},&\lambda_1\lt|w|\lt\lambda_2\\[9pt]
    w,&|w|\ge\lambda_2
    \end{cases} \tag{A-3} \]</div>
    <div class="mathnote"><p>取 \(\lambda_1=\lambda_2\) 退化为硬阈值，取 \(\lambda_2\to\infty\) 退化为软阈值。朱柯佳论文的「改进阈值函数」思路与此一致：调整 \(\pm\lambda\) 附近及区间内的函数形状，<b>既连续又不留恒定偏差</b>。这里给出的是该家族的标准形式，便于自己实现；论文中具体的分段系数以原图为准。</p></div>
  </div>
  <p><b>阈值怎么定：</b>Donoho–Johnstone 通用阈值（VisuShrink）用 \(\lambda=\sigma\sqrt{2\ln N}\)，其中噪声标准差由最细层细节系数的绝对中位差稳健估计 \(\hat\sigma=\mathrm{MAD}/0.6745\)。Stein 无偏风险估计（SURE / rigrsure）则在低 SNR 时更省；启发式阈值（heursure）按输入 SNR 在两者间选：</p>
  <div class="mathbox">
    <div class="math">\[ \lambda=\sigma\sqrt{2\ln N},\qquad
    \hat\sigma=\frac{\operatorname{median}\big(|cD_1|\big)}{0.6745},\qquad
    \lambda_j=\hat\sigma_j\sqrt{2\ln N_j}\ \ (j=1,\dots,J) \tag{A-4} \]</div>
    <div class="mathnote"><p>最后一式是<strong>分层阈值</strong>：不同分解层的噪声能量不同，每层用自己的 \(\hat\sigma_j\) 算一个 \(\lambda_j\)，传进去的是一个<strong>数组</strong>而不是单一数值。这正是朱柯佳论文的第二处改进；配合 A-3 的改进阈值函数，实测输出 SNR 提高约 <b>1 dB</b>，整体去噪性能提升 <b>8–9%</b>，RMSE 与 LSD 都更小、波动也更小。</p></div>
  </div>

  <h4>A.3.2　谱减法</h4>
  <p>假设噪声加性且短时平稳，先从前导静音段估出噪声谱 \(\hat N[k]\)，再从带噪谱里减掉：</p>
  <div class="mathbox">
    <div class="math">\[ |\hat X[k]|^2=|Y[k]|^2-\alpha\,\big|\hat N[k]\big|^2,\qquad
    |\hat X[k]|=\max\!\Big(|Y[k]|-\alpha\,|\hat N[k]|,\ \beta\,|Y[k]|\Big) \tag{A-5} \]</div>
    <div class="mathnote"><p>\(\alpha\ge 1\) 是<strong>过减因子</strong>（噪声估计偏低时补偿），\(\beta|Y[k]|\) 是<strong>谱下限</strong>（防止减出负值导致相位翻转般的失真）。减完仍用带噪信号的相位 \( \angle Y[k] \) 做逆变换，因为人耳/后续特征对相位不敏感（第 1 讲式 1-6）。</p></div>
  </div>
  <p><b>音乐噪声</b>是谱减法的固有副作用：随机频点上被减成孤立尖峰，逆变换后听感像断续的音调。缓解办法是过减 + 谱下限、对噪声谱做时间平滑、以及多帧最小值跟踪。论文里谱减法失真度始终偏高，正与此有关。</p>

  <h4>A.3.3　FastICA（盲源分离）</h4>
  <p>把多通道观测写成 \(\mathbf y=A\mathbf s\)，目标是在只知道 \(\mathbf y\) 的情况下找 \(W\approx A^{-1}\) 使 \(\mathbf u=W\mathbf y\) 的各分量尽量<strong>统计独立</strong>（非高斯性最大）。FastICA 用负熵近似做固定点迭代：</p>
  <div class="mathbox">
    <div class="math">\[ \mathbf w^{+}\;\propto\;\mathbb E\!\left[\mathbf z\,g(\mathbf w^{\mathsf T}\mathbf z)\right]-\mathbb E\!\left[g'(\mathbf w^{\mathsf T}\mathbf z)\right]\mathbf w,\qquad
    g(u)=\tanh(u)\ \text{or}\ u^3 \tag{A-6} \]</div>
    <div class="mathnote"><p>\(\mathbf z\) 是白化后的观测。每轮更新后做对称正交化 \(\;W\leftarrow (WW^{\mathsf T})^{-1/2}W\)，防止不同分量收敛到同一个源。它要求<strong>源之间相互独立且最多一个高斯源</strong>——持续弱干扰（风机、雨声）与本体振动在频带上长期重叠、统计上难以分离，这就是论文里 FastICA 对这类噪声效果不佳的原因。</p></div>
  </div>

  <h4>A.3.4　三个评价指标，别只看 SNR</h4>
  <div class="mathbox">
    <div class="math">\[ \begin{aligned}
    \mathrm{SNR}_{\mathrm{out}}&=10\log_{10}\frac{\sum_n x^2[n]}{\sum_n\big(\hat x[n]-x[n]\big)^2},\qquad
    \mathrm{RMSE}=\sqrt{\frac{1}{N}\sum_n\big(\hat x[n]-x[n]\big)^2}\\[4pt]
    \mathrm{LSD}&=\frac{1}{M}\sum_{m=1}^{M}\sqrt{\frac{1}{K}\sum_{k=1}^{K}\Big[20\log_{10}\big|X_m[k]\big|-20\log_{10}\big|\hat X_m[k]\big|\Big]^2}
    \end{aligned} \tag{A-7} \]</div>
    <div class="mathnote"><p>SNR / RMSE 看时域波形误差，<b>LSD（对数谱距离）看频谱畸变</b>——对声纹特征而言后者往往更关键：波形误差很小但某个谐波峰被削掉，特征照样崩。朱柯佳论文表 2-8 给出不同噪声类型下三法的 LSD 对比（如输入 SNR = −10 dB 的风机声：小波阈值 2.697、FastICA 2.695、谱减 2.803，数值越小越好），可以看到谱减法在各类噪声下都偏高。</p></div>
  </div>

  <h3>A.4　特征：为什么不是 MFCC，而是小波包能量 + TFCC</h3>
  <h4>A.4.1　小波包能量谱</h4>
  <p>第 7 讲的 DWT 每层只继续分解<strong>近似</strong>支路 \(cA\)，所以低频分辨率高、高频粗；<strong>小波包（wavelet packet）</strong>把近似<em>和</em>细节都继续分解，第 \(j\) 层得到 \(2^j\) 个<strong>等宽</strong>频带：</p>
  <div class="mathbox">
    <div class="math">\[ \Delta f_{\text{seg}}=\frac{F_s/2}{2^j},\qquad
    x[n]=\sum_{m=0}^{2^j-1}s_{j,m}[n],\qquad
    E_{j,m}=\sum_{n}\big|s_{j,m}[n]\big|^2 \tag{A-8} \]</div>
    <div class="mathnote"><p>三层分解 → 8 个频段；五层 → 32 个频段（朱柯佳论文采用五层，得到 32 维小波包能量谱）。以 \(F_s=8\,\mathrm{kHz}\)、\(j=5\) 为例，每段宽 \(4000/32=125\,\mathrm{Hz}\)——刚好能把 100 / 200 / 300 Hz 的谐波结构分开，又比逐根谱线稳健得多。论文的三步法：<b>① 小波包分解 → ② 各频段重构信号并求总能量 → ③ 排成特征向量</b> \(T=[E_{3,0},\dots,E_{3,7}]\)。</p></div>
  </div>
  <p>通常再做归一化与能量熵，避免整体音量变化主导特征：</p>
  <div class="mathbox">
    <div class="math">\[ p_{m}=\frac{E_{j,m}}{\sum_{m'}E_{j,m'}},\qquad
    H=-\sum_{m}p_m\log_2 p_m,\qquad 0\le H\le j \tag{A-9} \]</div>
    <div class="mathnote"><p>能量集中在少数频带（稳态嗡鸣）→ \(H\) 小；能量摊平（局放宽带、强噪声）→ \(H\) 大。<b>单这一个标量就能粗分「周期性故障」与「宽带放电」</b>，但它丢掉了「能量落在哪一段」的信息，所以还要保留完整的 \(p_m\) 向量。</p></div>
  </div>

  <h4>A.4.2　TFCC：把 Mel 滤波器组换成设备专用的</h4>
  <p>第 6 讲 MFCC 的流程是「功率谱 → Mel 三角滤波器组 → log → DCT」。TFCC（Transformer Sound Frequency Cepstrum Coefficients，变压器声音频率倒谱系数）保留这个骨架，只换掉<strong>频率轴的划分方式</strong>：既然判别信息在 100 Hz 基频及其低次谐波，就把滤波器中心对准谐波簇、在低频加密，而不是按人耳的 Mel 刻度。</p>
  <div class="mathbox">
    <div class="math">\[ E_m=\sum_{k}P[k]\,H^{\mathrm{TF}}_m[k],\qquad
    L_m=\ln(E_m+\varepsilon),\qquad
    c_i=\sqrt{\frac{2}{M}}\sum_{m=1}^{M}L_m\cos\!\left[\frac{\pi i}{M}\Big(m-\tfrac12\Big)\right] \tag{A-10} \]</div>
    <div class="mathnote"><p>与第 6 讲式 6-5、6-7 的唯一差别是 \(H_m\) 换成 \(H^{\mathrm{TF}}_m\)。朱柯佳论文用<strong>遍历法</strong>筛选关键系数，得到 <b>40 维</b> TFCC，单独用于故障诊断的准确率 98.85%。<b>关键洞察：Mel 刻度是给人耳设计的，不是给变压器设计的。</b>陆云才等从另一条路得出同样结论，改用「时域 + 频域双通道」把原始频谱直接喂给网络。</p></div>
  </div>

  <h4>A.4.3　特征选择：Laplacian 得分 + Fisher 得分</h4>
  <p>32 维小波包能量 + 40 维 TFCC = 72 维，其中大量冗余甚至噪声维度。两个互补的过滤式评分：</p>
  <div class="mathbox">
    <div class="math">\[ \begin{aligned}
    \text{Fisher:}\quad &S_r=\frac{\sum_{c}n_c(\mu_r^{c}-\mu_r)^2}{\sum_c n_c\big(\sigma_r^{c}\big)^2}\\[4pt]
    \text{Laplacian:}\quad &L_r=\frac{\sum_{i,j}\big(f_{r,i}-f_{r,j}\big)^2\,S_{ij}}{\sum_{i,j}\big(f_{r,i}-f_{r,j}\big)^2\,D_{ii}}
    \ \ \big(D_{ii}=\textstyle\sum_j S_{ij}\big)
    \end{aligned} \tag{A-11} \]</div>
    <div class="mathnote"><p>Fisher 看<strong>类间散度 / 类内散度</strong>，偏好「不同故障取值差得开、同一故障取值稳」的维度；Laplacian Score 用样本近邻图 \(S_{ij}\)（常用热核 \(e^{-\|x_i-x_j\|^2/t}\)）衡量该维度是否<strong>保持局部几何结构</strong>，方差小、得分低。两者一个看判别性、一个看结构保持，加权融合 \(\text{score}=\alpha\,\tilde S_r+(1-\alpha)\,\tilde L_r\)；论文实验取 \(\alpha=0.8\) 时故障诊断准确率最高。</p></div>
  </div>
  <p>融合选维后的<strong>小波包能量–TFCC 特征</strong>：维度比 72 低，准确率 <b>99.65%</b>（干净条件）与 <b>99.4%</b>（高噪声现场），且论文特别指出「变压器声音信号失真后对故障诊断准确率影响最小」——也就是<strong>抗噪鲁棒性</strong>比单纯的高准确率更有价值。</p>

  <h4>A.4.4　一个反直觉但很重要的实验结论</h4>
  <div class="warn"><span class="t">别把去噪当成免费午餐</span>朱柯佳论文第 4 章发现：三种去噪方法都能降低噪声，但<strong>去噪后的信号都存在一定失真度</strong>；用「未去噪的本体声音信号」训练故障模型、用「去噪后的信号」去测试，反而比反过来更好；高噪声现场下，改进小波阈值去噪后的最高诊断准确率是 <b>95.1%</b>，而换用抗噪特征（小波包能量–TFCC）能做到 <b>99.4%</b>。<b>结论：去噪主要服务于推理端，而「选对特征」带来的收益往往大于「把噪声削干净」。</b>这和讲义第 10 讲「别一上来就调网络，先按层排查」是同一个思路。</div>

  <h3>A.5　诊断模型：多通道 CNN + 注意力 + 集成学习</h3>
  <h4>A.5.1　输入怎么构造成 (8, 96000)</h4>
  <p>陆云才等没有用「一张梅尔频谱图当图片」的常见做法，理由有二：二维时频谱要很高分辨率、内存吃不消；而 Mel 频谱是为<strong>人声</strong>设计的，压缩频率轴后不利于保留变压器基频与高次倍频。他们改成<strong>时域 + 频域双通道</strong>，让网络同时看见稳态周期结构与暂态异常：</p>
  <table class="sym">
    <tr><th>步骤</th><th>操作</th><th>维度账（文献设定：10 s @ 48 kHz）</th></tr>
    <tr><td>①</td><td>对整段做 FFT 得频域信号；时域信号做均值方差归一化并抽稀到与频域等长</td><td>两路各 \(480000\) 点量级，抽稀后对齐</td></tr>
    <tr><td>②</td><td>两路并联成双通道数据</td><td>\(2\times L\)</td></tr>
    <tr><td>③</td><td>4 s 窗、2 s 滑动步长切段</td><td>10 s 上得到 4 段（窗口重叠 50%）</td></tr>
    <tr><td>④</td><td>4 段 × 2 通道重新并联</td><td><b>(8, 96000)</b>；\(96000=2\,\mathrm{s}\times48\,\mathrm{kHz}\)，即抽稀到原采样率一半的长度</td></tr>
  </table>
  <p>这里 \(96000\) 的具体换算属于按文献参数反推，实际以原论文的预处理实现为准；<b>要学的是这套构造逻辑</b>：用「通道」承载不同视图，用「时间窗 + 重叠」把长信号切成等长样本，既扩充样本量又保留局部暂态。</p>

  <h4>A.5.2　基学习器：一维 CNN + CBAM</h4>
  <p>4 个一维卷积层，每层后接最大池化与 ReLU，并紧跟一个 CBAM（卷积块注意力模块）；之后 2 个全连接层（含 Dropout 与 ReLU）。卷积核尺寸依次为 \(64\times11\times8\)、\(192\times5\times64\)、\(384\times3\times192\)、\(256\times3\times384\)（输出通道 × 核长 × 输入通道）。CBAM 的串联结构：</p>
  <div class="mathbox">
    <div class="math">\[ \begin{aligned}
    M_c(F)&=\sigma\Big(\mathrm{MLP}\big(\mathrm{AvgPool}(F)\big)+\mathrm{MLP}\big(\mathrm{MaxPool}(F)\big)\Big)\\
    M_s(F)&=\sigma\Big(\mathrm{conv}\big([\mathrm{AvgPool}_c(F);\,\mathrm{MaxPool}_c(F)]\big)\Big)\\
    F'&=M_s\big(F\odot M_c(F)\big)\odot\big(F\odot M_c(F)\big)
    \end{aligned} \tag{A-12} \]</div>
    <div class="mathnote"><p>通道注意力回答「哪个特征通道重要」，空间（这里是时间轴）注意力回答「哪个时间位置重要」。现场不同电压等级、不同工况与干扰会让某些通道/时段的响应失真，CBAM 让网络自适应地把权重压到真正有判别力的部分——可以看成第 9 讲「感受野」之后再加一层<strong>可学习的软掩码</strong>。</p></div>
  </div>

  <h4>A.5.3　Stacking 集成：只在容易错的地方做二次诊断</h4>
  <p>单纯 CNN 在正常 vs 异常二分类上，20 轮迭代后只有 <b>92.0%</b>；错误集中在「220 kV 主变噪声」与「重过载」互相混淆（两者都是大幅值、周期性、频谱形状接近）。论文的做法很务实：<strong>不把集成学习铺到所有样本上</strong>，而是——</p>
  <div class="defbox"><div class="dh">条件触发的二次诊断（stacking）</div>
  <ol>
    <li>CNN 预测标签<strong>不是</strong>易混淆类 → 直接映射为「正常 / 缺陷」并输出，省时间；</li>
    <li>预测标签<strong>是</strong>易混淆类 → CNN 不出结果，把它的<strong>预测向量</strong>与「特征分析法」的预测向量<strong>串联</strong>；</li>
    <li>送进由 2 隐层 MLP 构成的<strong>元学习器</strong>（交叉熵损失）做综合预测，输出最终标签。</li>
  </ol>
  <p>基学习器捕捉非线性模式，特征分析法提供可解释的描述性证据，元学习器学会「什么时候该信谁」。这属于集成学习三大类（堆叠 / 提升 / 装袋）里的<strong>堆叠</strong>。</p></div>

  <h4>A.5.4　结果阶梯：每一步改动的收益都看得见</h4>
  <table class="sym">
    <tr><th>场景</th><th>方法</th><th>结果</th><th>出处</th></tr>
    <tr><td>正常 vs 异常</td><td>单独 CNN，20 轮</td><td>92.0%</td><td>陆云才 2023，图 10</td></tr>
    <tr><td>19 类单一缺陷（训练集）</td><td>条件触发 stacking，15 轮</td><td>98.7%</td><td>同上，图 11</td></tr>
    <tr><td>6 大类单一缺陷（测试集）</td><td>集成模型</td><td><b>99.2%</b>，其中局放与短路冲击 100%，重过载较低</td><td>同上，图 12</td></tr>
    <tr><td>6 类任选 2 类融合 = 15 类混合缺陷</td><td>单独 CNN，20 轮</td><td>97.1%</td><td>同上，图 13</td></tr>
    <tr><td>混合缺陷</td><td>CNN + 4 个二分类集成模型</td><td><b>99.7%</b></td><td>同上，摘要</td></tr>
    <tr><td>高噪声现场（朱柯佳）</td><td>TFCC 单独</td><td>98.85%</td><td>朱柯佳 2021，第 5 章</td></tr>
    <tr><td>高噪声现场</td><td>小波包能量–TFCC（选维后）</td><td>99.65%（干净）/ <b>99.4%</b>（现场）</td><td>同上</td></tr>
    <tr><td>高噪声现场</td><td>改进小波阈值去噪后</td><td>最高 95.1%</td><td>同上</td></tr>
  </table>
  <p>为什么混合缺陷里「夹件松动 + 局部放电」最容易混？论文分析是<strong>两者频率及能量分布影响了识别</strong>：一个是结构松动带来的中低频调制，一个是宽带高频脉冲，混合后能量量级不同、原有特征被相互破坏。于是他们再建 4 个二分类集成模型专门处理含这两类的情况——<b>先定位错误集中在哪，再定点补模型</b>，这比盲目加深网络有效得多，也正是第 10 讲「看混淆矩阵而不是只看总准确率」的实战版。</p>

  <h3>A.6　代码：把 A.3 与 A.4 跑起来</h3>
  <pre><code>import numpy as np

# --- 式(A-2)(A-3)：三种阈值函数 ---
def shrink(w, lam, kind="soft", lam2=None):
    a = np.abs(w)
    if kind == "hard":
        return np.where(a > lam, w, 0.0)
    if kind == "soft":
        return np.sign(w) * np.maximum(a - lam, 0.0)
    l1, l2 = lam, (lam2 or 2 * lam)          # firm shrinkage
    return np.where(a <= l1, 0.0,
           np.where(a >= l2, w,
                    np.sign(w) * l2 * (a - l1) / (l2 - l1)))

# --- 式(A-4)：分层阈值 + 稳健噪声估计 ---
def denoise_levels(coeffs, rule="visu"):
    out = []
    for c in coeffs:
        sigma = np.median(np.abs(c)) / 0.6745 + 1e-12
        lam = sigma * np.sqrt(2 * np.log(len(c)))
        out.append(shrink(c, lam, "firm"))
    return out                                # 每层一个 lam，不是全局一个

# --- 式(A-5)：谱减法（含过减与谱下限）---
def spectral_subtract(y, noise, n_fft=1024, alpha=1.3, beta=0.02):
    Y = np.fft.rfft(y[:n_fft])
    N = np.abs(np.fft.rfft(noise[:n_fft]))
    mag = np.maximum(np.abs(Y) - alpha * N, beta * np.abs(Y))
    return np.fft.irfft(mag * np.exp(1j * np.angle(Y)), n=n_fft)

# --- 式(A-8)(A-9)：频段能量与能量熵 ---
E = np.array([np.sum(node**2) for node in nodes])   # nodes: 2^j 个重构频段
p = E / (E.sum() + 1e-12)
H = -(p * np.log2(p + 1e-12)).sum()

# --- 式(A-11)：Fisher 得分（过滤式特征选择）---
def fisher_score(F, y):
    mu = F.mean(axis=0)
    sb = sum((y == c).sum() * (F[y == c].mean(axis=0) - mu)**2
             for c in np.unique(y))
    sw = sum(F[y == c].var(axis=0) * (y == c).sum()
             for c in np.unique(y))
    return sb / (sw + 1e-12)</code></pre>
  <p>把 <code>nodes</code> 换成第 7 讲 <code>dwt()</code> 的多层细节/近似重构序列，就得到可运行的小波包近似版；<code>F</code> 是 \(T\times72\) 的特征矩阵，<code>y</code> 是故障标签。建议先在 <code>acoustic-lab/data/</code> 的 6 段合成声纹上跑通，再人为叠加不同 SNR 的高斯/风机噪声复现 A.2 的对照表。</p>

  <div class="derive">
    <div class="dtitle">推导详解 · 专题 A　两条最容易算错的账</div>
    <h4>1. 从 50 Hz 到 100 Hz，再到奇次谐波</h4>
    <p>把磁化曲线在工作点附近展开到二阶：\(B(t)=B_m\sin\omega t+\gamma B_m^2\sin^2\omega t+\cdots\)。磁致伸缩 \(\varepsilon\propto B^2\)，代入并保留到 \(\omega\) 的二阶：</p>
    <div class="math sub">\[ \varepsilon(t)\propto \frac{B_m^2}{2}-\frac{B_m^2}{2}\cos 2\omega t
    \;+\;\gamma B_m^3\sin\omega t\sin^2\omega t+\cdots \tag{A-13} \]</div>
    <p>直流项不辐射声音，\(\cos 2\omega t\) 给出 100 Hz 基频；用 \(\sin\theta\sin^2\theta=\frac14(\sin\theta-\sin3\theta)\) 展开高阶项，出现 \(\sin3\omega t\) 即 150 Hz，以及更高奇次倍频。直流偏磁相当于给 \(B(t)\) 加一个常量 \(B_0\)，于是 \((B_0+B_m\sin\omega t)^2\) 里出现 \(2B_0B_m\sin\omega t\)（50 Hz）与后续奇次项——<b>这就是「直流偏磁 → 50 Hz 奇次倍频」的数学来源</b>，也是本讲义合成数据里 150/250/350 Hz 峰的依据。</p>
    <h4>2. 频率分辨率：小波包、DFT、Mel 三者别混</h4>
    <div class="math sub">\[ \Delta f_{\mathrm{DFT}}=\frac{F_s}{N_{\mathrm{obs}}},\qquad
    \Delta f_{\mathrm{WP}}=\frac{F_s/2}{2^j},\qquad
    \Delta f_{\mathrm{Mel}}\ \text{increases with } f \tag{A-14} \]</div>
    <p>以 8 kHz、观测 0.2 s 为例：DFT 的真实分辨率是 \(1/0.2=5\,\mathrm{Hz}\)（第 4 讲式 4-6，由观测时长决定，补零不改变它）；五层小波包的每个频段是 \(4000/32=125\,\mathrm{Hz}\)（由<strong>分解层数</strong>决定，与观测时长无关，但每段内仍含足够多采样点）；Mel 滤波器在 100–500 Hz 一段只有带宽约 50–95 Hz 的少数几个三角形（第 6 讲表格）。<b>三者是不同意义上的「分辨率」，写论文或调参时混用会得出完全错误的结论。</b></p>
    <h4>3. 类别不平衡下准确率会骗人</h4>
    <p>陆云才样本库里正常主变噪声每类 960 段、夹件松动只有 100 段。若按样本数直接算微平均准确率，模型只要把小类全判成大类也能拿到很高的分数。正确做法是第 10 讲的宏平均 \(F_1\) 与混淆矩阵，或像论文那样<strong>专门针对易混淆类做二次诊断</strong>。看表 A.5-4 时请连同每类的样本数一起看。</p>
  </div>

  <h3>误区与注意事项</h3>
  <div class="warn"><span class="t">误区</span>① <b>把文献准确率当成自己系统的性能。</b>样本库、采样率、噪声条件全不同，不可比。② <b>认为去噪一定提升识别率。</b>去噪必然带来失真，朱柯佳的实测是「本体信号训练 + 去噪信号测试」更优。③ <b>直接用 8 kHz 数据做局放检测。</b>4000 Hz 奈奎斯特上限会砍掉高频放电特征。④ <b>照搬 Mel 频谱图。</b>它是为人声设计的，压缩后不利于基频与倍频。⑤ <b>只报总准确率。</b>样本数 960 : 100 的不平衡下必须同时给宏 \(F_1\) 和混淆矩阵。⑥ <b>把「改进阈值函数」当成万能。</b>它只解决小波阈值自身的两个缺陷；面对持续弱干扰，谱减法或换特征可能更有效。</div>

  <h3>自检</h3>
  <div class="checklist">
    <label><input type="checkbox" data-k="qA-1"> 我能从 \(\varepsilon\propto B^2\) 推出 100 Hz 基频，并解释直流偏磁为什么冒出 150/250/350 Hz。</label>
    <label><input type="checkbox" data-k="qA-2"> 我能说清硬阈值、软阈值、半软阈值各自的缺陷，以及分层阈值为什么要传数组。</label>
    <label><input type="checkbox" data-k="qA-3"> 我能解释为什么 TFCC / 小波包能量谱比照搬 MFCC 更适合设备声纹。</label>
    <label><input type="checkbox" data-k="qA-4"> 我能复述 (8, 96000) 多通道输入的构造，以及 stacking 为什么只在易混淆类上触发。</label>
    <label><input type="checkbox" data-k="qA-5"> 我知道「去噪后准确率 95.1%」与「换特征后 99.4%」的对比说明了什么。</label>
  </div>
</section>
"""
