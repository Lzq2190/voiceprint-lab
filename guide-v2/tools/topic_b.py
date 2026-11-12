# -*- coding: utf-8 -*-
"""专题 B：经典语音算法补遗（完整 <section>）。

资料来源（按知识地图）：
  赵力《语音信号处理（第三版）》第 3/4/5/6/7/8/9 章（矢量量化、HMM、LPC/LSP、
    端点检测、基音/共振峰、语音增强、DTW、语音编码）
  韩纪庆《语音信号处理（第3版）》第 2/3/4 章（产生模型、同态解卷积、线性预测）
  柳若边《深度学习语音识别技术实践》第 1/6/7/8 章（WFST、DTW、端到端、N-gram 与平滑）
这三本里赵力与姜囡、宋知用的 PDF 为扫描版，本专题只用其目录作知识地图，
具体公式按标准教材形式自行推导，不转录原文。
"""

TOPIC_B = r"""
<section id="sB">
  <h2><span class="no">专题 B</span>经典算法补遗：LPC、VQ、HMM、DTW 与它们的位置</h2>

  <div class="goal">
    <div class="g">目标</div>
    <ul>
      <li>补齐第 1–14 讲之间被跳过的经典方法，并说清它们各自解决什么问题、后来为什么被谁替代。</li>
      <li>能手动推出 Yule–Walker 方程、前向算法、维纳滤波与 DTW 递推，而不是只会调库。</li>
      <li>把「模板匹配 → 概率模型 → 深度模型」这条演进线和讲义第 11–14 讲接起来。</li>
    </ul>
  </div>
  <div class="goal">
    <div class="g">产出</div>
    <ul><li>一张经典方法对照表；一段能跑的 Levinson–Durbin / Viterbi / DTW 代码；一次对「为什么 HMM 要取对数」的定量验证。</li></ul>
  </div>

  <div class="note"><span class="t">为什么单开一个专题</span>前面 17 讲走的是「信号 → 特征 → 神经网络 → 声纹识别」这条依赖链，为了不打断它，把<strong>线性预测、矢量量化、隐马尔可夫、动态时间规整、语音增强、语言模型</strong>这些经典分支压到了这里。它们不是过时废物：LPC 至今是语音编码与共振峰分析的基础，Viterbi 解码是 WFST 与 CTC 的前身，维纳滤波是 A.3 谱减法的理论升级版，N-gram 的平滑思想在今天的语言模型里仍在用。</div>

  <h3>B.1　语音产生模型与线性预测 LPC</h3>
  <p>第 1 讲把声音看成正弦叠加，那是<strong>信号视角</strong>；语音处理还有<strong>产生视角</strong>：声带（激励源）→ 声道（时变滤波器）→ 口唇辐射。把三者合起来，浊音可近似成一个全极点系统：</p>
  <div class="mathbox">
    <div class="math">\[ s[n]=\sum_{k=1}^{p}a_k\,s[n-k]+G\,e[n],\qquad
    H(z)=\frac{S(z)}{E(z)}=\frac{G}{A(z)}=\frac{G}{1-\sum_{k=1}^{p}a_k z^{-k}} \tag{B-1} \]</div>
    <div class="mathnote"><p>\(e[n]\) 是声门激励（浊音为周期脉冲串、清音为白噪声），\(G\) 是增益，\(p\) 是预测阶数（8 kHz 常取 \(p=10\sim12\)：每对共轭极点对应一个共振峰，再加若干补偿）。<b>线性预测的假设就是「当前样本可由前 \(p\) 个样本线性加权得到」</b>——声道是一个共鸣腔，自然带记忆。</p></div>
  </div>
  <p>定义预测误差 \(e[n]=s[n]-\sum_k a_k s[n-k]\)，在一帧内最小化 \(\mathcal E=\sum_n e^2[n]\)。对 \(a_i\) 求偏导并令为 0：</p>
  <div class="mathbox">
    <div class="math">\[ \frac{\partial\mathcal E}{\partial a_i}=0
    \ \Longrightarrow\
    \sum_{k=1}^{p}a_k\,R[|i-k|]=R[i],\qquad i=1,\dots,p,\qquad
    R[i]=\sum_{n}s[n]\,s[n-i] \tag{B-2} \]</div>
    <div class="mathnote"><p>写成矩阵就是 <strong>Yule–Walker 方程</strong> \(R_p\mathbf a=\mathbf r\)，其中 \(R_p\) 是 Toeplitz 矩阵（元素只依赖于 \(|i-k|\)）。这个结构让一般 \(O(p^3)\) 的求解降到 \(O(p^2)\)——Levinson–Durbin 递推：</p></div>
  </div>
  <div class="mathbox">
    <div class="math">\[ \begin{aligned}
    E_0&=R[0],\qquad
    k_m=\frac{R[m]-\sum_{j=1}^{m-1}a_j^{(m-1)}R[m-j]}{E_{m-1}}\\[4pt]
    a_m^{(m)}&=k_m,\qquad
    a_j^{(m)}=a_j^{(m-1)}-k_m\,a_{m-j}^{(m-1)}\ \ (j=1,\dots,m-1)\\[4pt]
    E_m&=\big(1-k_m^2\big)E_{m-1}
    \end{aligned} \tag{B-3} \]</div>
    <div class="mathnote"><p>\(k_m\) 叫<strong>反射系数 / PARCOR 系数</strong>。只要 \(|k_m|\lt 1\)，就有 \(E_m\gt 0\) 且 \(A(z)\) 的全部根落在单位圆内 → <strong>合成滤波器必定稳定</strong>。这是 LPC 被广泛用于编码的关键性质：直接量化 \(a_k\) 可能让滤波器炸掉，量化 \(k_m\) 则只要卡住 \(|k_m|\lt 1\) 就安全。</p></div>
  </div>
  <p><b>手算一遍（\(p=2\)）：</b>设 \(R[0]=1,\ R[1]=0.5,\ R[2]=0.2\)。</p>
  <div class="mathbox">
    <div class="math">\[ \begin{aligned}
    m=1&:\ k_1=\frac{R[1]}{R[0]}=0.5,\quad a_1^{(1)}=0.5,\quad E_1=(1-0.25)\cdot1=0.75\\
    m=2&:\ k_2=\frac{R[2]-a_1^{(1)}R[1]}{E_1}=\frac{0.2-0.25}{0.75}=-0.0667\\
        &\quad a_2^{(2)}=-0.0667,\quad a_1^{(2)}=0.5-(-0.0667)(0.5)=0.5333\\
        &\quad E_2=(1-0.00444)\cdot0.75=0.7467
    \end{aligned} \tag{B-4} \]</div>
    <div class="mathnote"><p>回代验证 \(a_1R[0]+a_2R[1]=0.5333-0.0333=0.5=R[1]\) ✓，\(a_1R[1]+a_2R[0]=0.2667-0.0667=0.2=R[2]\) ✓。预测误差能量从 1.0 降到 0.7467，说明用一个二阶模型就能解释约 25% 的样本方差。</p></div>
  </div>

  <h4>B.1.1　LPC 倒谱、共振峰与线谱对</h4>
  <p>第 6 讲的倒谱来自「\(\log\) 功率谱 + 反变换」；用全极点模型时，可以直接从 \(a_k\) 递推出倒谱系数，不必再跑一次 FFT：</p>
  <div class="mathbox">
    <div class="math">\[ c_1=a_1,\qquad
    c_n=a_n+\frac{1}{n}\sum_{k=1}^{n-1}k\,c_k\,a_{n-k}\ \ (2\le n\le p),\qquad
    c_n=\frac{1}{n}\sum_{k=1}^{p}(n-k)\,c_{n-k}\,a_k\ \ (n\gt p) \tag{B-5} \]</div>
    <div class="mathnote"><p>由 \(\ln H(z)=\ln G-\ln A(z)\) 两边对 \(z^{-1}\) 求导、比较系数即得（推导见本专题末尾）。LPCC 与 MFCC 目的一样——描述<strong>谱包络</strong>；区别是 MFCC 靠听觉滤波器组，LPCC 靠全极点拟合，后者对共振峰更锐利、对噪声更敏感。</p></div>
  </div>
  <p>把 \(A(z)=1-\sum_k a_k z^{-k}\) 求根，共轭根 \(z_i=r_i e^{j\theta_i}\) 直接给出<strong>共振峰</strong>的位置与带宽：</p>
  <div class="mathbox">
    <div class="math">\[ F_i=\frac{\theta_i}{2\pi}F_s,\qquad
    B_i=-\frac{\ln r_i}{\pi}F_s \tag{B-6} \]</div>
    <div class="mathnote"><p>例：\(F_s=8000\)、\(r=0.90,\ \theta=2\pi(500/8000)\) → \(F_1=500\,\mathrm{Hz}\)，\(B_1=-\ln(0.9)\cdot8000/\pi\approx268\,\mathrm{Hz}\)。\(r\) 越接近 1，峰越尖锐（带宽越窄）——这正是「共振」的直观含义。若改用<strong>线谱对 LSP</strong>，构造</p>
      <p>\(P(z)=A(z)+z^{-(p+1)}A(z^{-1})\)、\(Q(z)=A(z)-z^{-(p+1)}A(z^{-1})\)，可以证明二者的根都在<strong>单位圆上且彼此交错</strong>。把 \(p\) 个实数量化成 \(p\) 个角度，插值时系统仍稳定、误差只影响附近的谱峰——所以 LPC-10、G.729 一类编码器传的是 LSP 而不是 \(a_k\)。</p></div>
  </div>

  <h3>B.2　矢量量化 VQ 与 LBG</h3>
  <p>把一帧特征向量 \(\mathbf x\in\mathbb R^d\) 用码本 \(\mathcal C=\{\mathbf c_1,\dots,\mathbf c_K\}\) 中最近的一个码字代替：</p>
  <div class="mathbox">
    <div class="math">\[ Q(\mathbf x)=\mathop{\arg\min}_{1\le k\le K}d(\mathbf x,\mathbf c_k),\qquad
    D=\frac{1}{T}\sum_{t=1}^{T}\min_k d(\mathbf x_t,\mathbf c_k),\qquad
    d(\mathbf x,\mathbf c)=\|\mathbf x-\mathbf c\|^2 \tag{B-7} \]</div>
    <div class="mathnote"><p>码本大小 \(K=2^b\)，每帧只传 \(b\) bit；这是第 9 讲「参数量」之外的另一种压缩思路——<strong>压缩的是数据本身，不是模型</strong>。失真测度不一定是欧氏距离：用 LPC 系数时常用 <strong>Itakura–Saito 失真</strong>，它按预测残差能量归一化，对增益变化不敏感；说话人识别里还可用「识别失真测度」，直接在度量里加入类间判别信息。</p></div>
  </div>
  <p><strong>LBG 算法</strong>（Linde–Buzo–Gray，也叫广义 Lloyd）是 k-means 的码本版，靠<em>逐步分裂</em>避开局部最优：</p>
  <div class="defbox"><div class="dh">LBG 流程</div>
  <ol>
    <li>用全部训练向量求质心，作为 \(K=1\) 的唯一码字；</li>
    <li><strong>分裂</strong>：每个码字 \(\mathbf c\to \mathbf c(1\pm\epsilon)\)（\(\epsilon\) 取 0.01 量级），码本大小翻倍；</li>
    <li><strong>最近邻划分</strong>：把所有训练向量归到最近的码字；<strong>更新质心</strong>为各类均值；</li>
    <li>重复 3 直到平均失真 \(D\) 的相对下降小于阈值（如 1%）；</li>
    <li>若 \(K\) 未达目标，回到 2 再分裂。</li>
  </ol>
  <p>每次划分与质心更新都保证 \(D\) 不增，所以收敛有保证。<b>用 VQ 做说话人确认</b>：给每个注册人训一个专属码本 \(\mathcal C_c\)，测试时算总失真 \(D_c\)，取最小的那个——这是第 12 讲「打分」的一种最朴素实现，也解释了为什么后来需要 z-norm：不同人码本的失真尺度天生不同。</p></div>

  <h3>B.3　隐马尔可夫模型 HMM：三个问题、三个算法</h3>
  <p>离散 HMM 由 \(\lambda=(A,B,\pi)\) 定义：状态转移 \(a_{ij}=P(q_t=j\mid q_{t-1}=i)\)、观测发射 \(b_j(k)=P(o_t=v_k\mid q_t=j)\)、初始分布 \(\pi_i\)。语音是时序信号，GMM（第 13 讲）只建模「这一帧像谁」而<strong>丢掉了帧间顺序</strong>，HMM 补上这一维。三个基本问题：</p>
  <table class="sym">
    <tr><th>问题</th><th>要算什么</th><th>算法</th><th>复杂度</th></tr>
    <tr><td>评估</td><td>\(P(O\mid\lambda)\)</td><td>前向–后向（或只用前向）</td><td>\(O(TN^2)\)</td></tr>
    <tr><td>解码</td><td>最可能的状态序列 \(Q^*\)</td><td>Viterbi</td><td>\(O(TN^2)\)</td></tr>
    <tr><td>学习</td><td>估计 \(\lambda\) 使 \(P(O\mid\lambda)\) 最大</td><td>Baum–Welch（EM 的特例）</td><td>每轮 \(O(TN^2)\)</td></tr>
  </table>
  <div class="mathbox">
    <div class="math">\[ \begin{aligned}
    \alpha_t(j)&=\Big[\sum_{i=1}^{N}\alpha_{t-1}(i)\,a_{ij}\Big]b_j(o_t),\qquad
    P(O\mid\lambda)=\sum_{i=1}^{N}\alpha_T(i)\\[4pt]
    \beta_t(i)&=\sum_{j=1}^{N}a_{ij}\,b_j(o_{t+1})\,\beta_{t+1}(j),\qquad
    \delta_t(j)=\max_i\Big[\delta_{t-1}(i)a_{ij}\Big]b_j(o_t)
    \end{aligned} \tag{B-8} \]</div>
    <div class="mathnote"><p>前向 \(\alpha\) 与 Viterbi \(\delta\) 只差「求和 vs 取最大」——这是同一个动态规划骨架换掉一个算子（概率和 → 最大概率路径），也叫 <strong>Viterbi 是对数域/极大域里的前向算法</strong>。\(T\) 帧、\(N\) 状态的朴素枚举是 \(N^T\)，动态规划降到 \(O(TN^2)\)。</p></div>
  </div>
  <div class="mathbox">
    <div class="math">\[ \gamma_t(i)=\frac{\alpha_t(i)\beta_t(i)}{P(O\mid\lambda)},\qquad
    \xi_t(i,j)=\frac{\alpha_t(i)\,a_{ij}\,b_j(o_{t+1})\,\beta_{t+1}(j)}{P(O\mid\lambda)},\qquad
    \hat a_{ij}=\frac{\sum_{t=1}^{T-1}\xi_t(i,j)}{\sum_{t=1}^{T-1}\gamma_t(i)} \tag{B-9} \]</div>
    <div class="mathnote"><p>\(\gamma_t(i)\) 是「第 \(t\) 帧处于状态 \(i\)」的后验，\(\xi_t(i,j)\) 是「\(t\to t+1\) 从 \(i\) 转到 \(j\)」的后验——与第 13 讲 GMM 的责任度 \(\gamma_{tc}\) 完全对应：<strong>Baum–Welch 就是带时序约束的 EM</strong>。E 步算 \(\gamma,\xi\)，M 步用它们重估 \(A,B,\pi\)，每轮保证似然不降。</p></div>
  </div>
  <div class="warn inline"><span class="t">必须取对数</span>\(\alpha_t(j)\) 是 \(2t\) 个小于 1 的数连乘，\(T=100\) 帧时双精度早已下溢为 0（\(0.5^{200}\approx10^{-60}\)，虽仍在双精度范围内，但真实发射概率常小到 \(10^{-10}\) 量级，\(T\) 稍大就归零）。工程实现要么每帧归一化并重标尺度，要么全程在对数域做 \(\ln\alpha\) 并用 log-sum-exp。<b>这与第 13 讲 GMM 的 log-sum-exp、第 8 讲 softmax 减 max 是同一类数值技巧。</b></div>
  <p><b>和讲义主线怎么接：</b>单状态 HMM 的输出密度用 GMM，就退化成第 13 讲的 UBM；把状态数设为 1、去掉转移矩阵，就是「忽略时序」的 i-vector / x-vector 路线。<strong>深度学习声纹不是推翻了 HMM，而是用统计池化（第 14 讲式 14-1）换掉了显式状态对齐</strong>；而 ASR 侧的 HMM 则被 CTC / attention 的端到端对齐替代（见 B.6）。</p>

  <h3>B.4　DTW：不用概率模型的模板匹配</h3>
  <p>同一个词，说得快和说得慢，特征序列长度不同。DTW 用动态规划找一条<strong>非线性时间对齐路径</strong> \(W=\{(i_l,j_l)\}\)，使累计距离最小：</p>
  <div class="mathbox">
    <div class="math">\[ D(i,j)=d(\mathbf q_i,\mathbf c_j)+\min\Big\{D(i-1,j),\ D(i,j-1),\ D(i-1,j-1)\Big\},\qquad
    D_{\min}=\frac{D(N,M)}{L_W} \tag{B-10} \]</div>
    <div class="mathnote"><p>约束：单调（\(i,j\) 不减）、连续（每步最多跳 1）、边界（从 \((1,1)\) 到 \((N,M)\)），再加 <strong>Sakoe–Chiba 带</strong> \(|i-j|\le R\) 防止病态对齐并省一半计算。除以路径长度 \(L_W\) 是为了让不同长度模板可比，否则长模板天然吃亏。</p></div>
  </div>
  <table class="sym">
    <tr><th></th><th>DTW</th><th>HMM</th><th>本讲义的深度模型</th></tr>
    <tr><td>建模对象</td><td>一条（或几条）模板</td><td>概率分布 + 状态转移</td><td>可学的 embedding / 分类器</td></tr>
    <tr><td>训练</td><td>几乎不需要</td><td>Baum–Welch 迭代</td><td>SGD + 大量数据</td></tr>
    <tr><td>时间对齐</td><td>显式 DP 路径</td><td>隐式状态序列</td><td>注意力 / 统计池化</td></tr>
    <tr><td>适合</td><td>孤立词、小样本、与文本相关</td><td>连续语音、中等数据</td><td>开集、变长、大数据</td></tr>
  </table>
  <p>赵力《语音信号处理（第三版）》第 7、8 章分别把 DTW 用于孤立字识别与说话人确认；柳若边书第 6.5 节也把 DTW 放进「语音信号处理」入门链条里。<b>它的价值不在于性能，而在于让你亲手看见「时间对齐」这件事本身</b>——理解了 DTW 的路径，再看 CTC 的 blank 折叠、注意力权重图就不会觉得抽象。</p>

  <h3>B.5　增强、端点检测与基音估计的补遗</h3>
  <h4>B.5.1　维纳滤波：谱减法的理论升级</h4>
  <p>A.3 的谱减法是「减掉噪声功率谱」；维纳滤波从<strong>最小均方误差</strong>出发，直接导出最优增益。设 \(Y=X+N\) 且信号与噪声不相关，令 \(\hat X=H Y\)，最小化 \(\mathbb E|X-HY|^2\)，对 \(H\) 求导置零得：</p>
  <div class="mathbox">
    <div class="math">\[ H(k)=\frac{P_X(k)}{P_X(k)+P_N(k)}=\frac{\xi(k)}{1+\xi(k)},\qquad
    \xi(k)=\frac{P_X(k)}{P_N(k)}\ \text{(a priori SNR)} \tag{B-11} \]</div>
    <div class="mathnote"><p>谱减法相当于给 \(H\) 一个硬阈值式的近似，维纳增益则在 \(0\sim1\) 之间平滑过渡：\(\xi\gg1\) 时 \(H\approx1\)（几乎不处理），\(\xi\to0\) 时 \(H\to0\)（几乎全抑制）。先验 SNR 未知，工程上用<strong>决策导向</strong>估计</p>
      <p>\(\hat\xi_t(k)=\alpha\,\dfrac{|\hat X_{t-1}(k)|^2}{P_N(k)}+(1-\alpha)\max\!\Big(\dfrac{|Y_t(k)|^2}{P_N(k)}-1,\,0\Big)\)，\(\alpha\approx0.98\)。</p>
      <p>它同样会产生音乐噪声，但比谱减法温和。<b>把它和 A.3 的表连起来看：小波阈值、谱减、维纳、FastICA 是四条不同假设下的去噪路线，没有哪条在所有场景都赢。</b></p></div>
  </div>

  <h4>B.5.2　端点检测、基音与共振峰的其他判据</h4>
  <p>第 3 讲用了能量 + 过零率双门限，赵力书第 5 章还列了自相关法、<strong>谱熵法</strong>、比例法、对数频谱距离法。谱熵法最直观：把每帧归一化谱当成概率分布 \(p_k=|X[k]|^2/\sum_j|X[j]|^2\)，</p>
  <div class="mathbox">
    <div class="math">\[ H=-\sum_{k}p_k\log_2 p_k\in[0,\log_2 K] \tag{B-12} \]</div>
    <div class="mathnote"><p><b>噪声段谱平坦 → \(H\) 大；语音段有共振峰结构 → \(H\) 小。</b> 谱熵对<strong>幅值不敏感</strong>（归一化消掉了增益），所以在稳态噪声下比能量门限稳；代价是对谱估计的方差敏感，需配合多帧平滑。</p></div>
  </div>
  <p>基音检测除第 3 讲的自相关外，还有 <strong>AMDF（平均幅度差函数）</strong>与<strong>倒谱法</strong>：</p>
  <div class="mathbox">
    <div class="math">\[ D_{\mathrm{AMDF}}(k)=\sum_{n=0}^{N-1-k}\big|s[n]-s[n-k]\big|,\qquad
    k_0=\mathop{\arg\min}_{k\in[k_{\min},k_{\max}]}D_{\mathrm{AMDF}}(k),\quad f_0=\frac{F_s}{k_0} \tag{B-13} \]</div>
    <div class="mathnote"><p>与自相关 \(R(k)\) 互补：<strong>周期处 \(R(k)\) 取峰、\(D_{\mathrm{AMDF}}(k)\) 取谷</strong>。AMDF 只需加减法和绝对值，没有乘法，早年在定点 DSP 上很吃香；缺点是谷底较宽、易受幅值调制影响，所以常与自相关或倒谱法联合、并做中值平滑后处理（赵力书第 5.3.5「基音检测的后处理」）。<b>倒谱法</b>则利用「激励的周期性在倒谱域表现为 \(k_0\) 处的尖峰」，把卷积变相加后再找峰，正是第 6 讲同态解卷积的另一个用途。</p></div>
  </div>

  <h3>B.6　解码那一侧：N-gram、WFST 与端到端</h3>
  <p>第 11 讲说过「语音识别要知道说了什么、声纹识别要知道谁说的，方向正交」。补上 ASR 这一侧的最小知识，才能理解为什么讲义的声纹打分不依赖文本内容。</p>
  <div class="mathbox">
    <div class="math">\[ P(W)\approx\prod_{i=1}^{n}P\big(w_i\mid w_{i-2},w_{i-1}\big),\qquad
    \hat P_{\mathrm{MLE}}(w_3\mid w_1w_2)=\frac{C(w_1w_2w_3)}{C(w_1w_2)} \tag{B-14} \]</div>
    <div class="mathnote"><p>三元模型的最大似然估计就是数数。问题在于没见过的三元组概率为 0，会让整句概率归零 → 必须<strong>平滑</strong>。加一平滑 \(\hat P=(C+1)/(C_{\text{context}}+V)\) 最粗糙；Good–Turing 把「出现 1 次的计数」重分配给未见事件；Kneser–Ney 更进一步，用「该词能接在多少种不同上下文之后」而不是原始计数来算回退权重。柳若边书第 8.1 节把这些做成了一条从一元到 N 元的完整链条。</p></div>
  </div>
  <div class="mathbox">
    <div class="math">\[ \mathrm{PPL}(W)=2^{-\frac{1}{N}\sum_{i=1}^{N}\log_2 P(w_i\mid h_i)},\qquad
    W^*=\mathop{\arg\max}_{W}\;P(X\mid W)\,P(W)\ \xrightarrow{\ \mathrm{WFST}\ }\ H\circ C\circ L\circ G \tag{B-15} \]</div>
    <div class="mathnote"><p>困惑度 PPL 可理解为「每个词的等效分支数」，越小越好。传统 Kaldi 把 HMM 状态（H）、上下文（C）、词典（L）、语言模型（G）都做成加权有限状态转换器，先组合再求最短路——<strong>柳若边书第 1.9 节的 FSA/FST/WFST 就是为这里做铺垫</strong>，第 7 章的 nnet3 则把声学模型换成 DNN。</p></div>
  </div>
  <p><strong>端到端</strong>把这条流水线压成一个网络。CTC 引入 blank 符号与折叠映射 \(\mathcal B\)（把连续重复字符合并、去掉 blank），对<strong>所有能折叠成标签的对齐路径</strong>求和：</p>
  <div class="mathbox">
    <div class="math">\[ L_{\mathrm{CTC}}=-\ln\sum_{\pi\in\mathcal B^{-1}(\mathbf y)}\prod_{t=1}^{T}p(\pi_t\mid \mathbf x),\qquad
    \mathcal B(a\!-\!\text{-}\!b\!-\!b)=\mathcal B(a\!-\!b\!-\!-\!b)=\text{ab} \tag{B-16} \]</div>
    <div class="mathnote"><p>这个求和用前向–后向（式 B-8 的骨架）在 \(O(T\cdot|\mathbf y|)\) 内算完，<b>不需要帧级标注</b>——这正是 CTC 取代 HMM 对齐的关键。注意力式 encoder–decoder 则让解码器每步自己「看」编码器的不同时间位置，权重图其实就是一条<strong>学出来的 DTW 对齐路径</strong>（呼应 B.4）。第 14 讲的统计池化与注意力池化，用的也是同一套思想，只是目的从「输出文字」变成「输出说话人 embedding」。</p></div>
  </div>

  <h3>B.7　代码：四个算法的最小实现</h3>
  <pre><code>import numpy as np

# --- 式(B-3) Levinson-Durbin：R[0..p] -> LPC 系数、反射系数、误差能量 ---
def levinson(R, p):
    a = np.zeros(p + 1); a[0] = 1.0
    E = R[0]; ks = []
    for m in range(1, p + 1):
        k = (R[m] - np.dot(a[1:m], R[m-1:0:-1])) / E
        old = a.copy()
        a[m] = k
        for j in range(1, m):
            a[j] = old[j] - k * old[m-j]
        E *= (1 - k*k); ks.append(k)
    return -a[1:], np.array(ks), E     # 注意 A(z)=1-sum(a_k z^-k) 的符号

# --- 式(B-5) LPC 倒谱 ---
def lpc_cepstrum(a, n_ceps):
    p = len(a); c = np.zeros(n_ceps)
    c[0] = a[0]
    for n in range(1, n_ceps):
        if n <= p:
            c[n] = a[n] + sum(k*c[k]*a[n-k] for k in range(1, n)) / n
        else:
            c[n] = sum((n-k)*c[n-k]*a[k] for k in range(1, p+1)) / n
    return c

# --- 式(B-8) 前向 + Viterbi（对数域）---
def forward_log(A, B, pi, obs):
    T, N = len(obs), A.shape[0]
    la = np.log(pi + 1e-300) + np.log(B[:, obs[0]] + 1e-300)
    for t in range(1, T):
        # log-sum-exp 取代 sum，避免下溢
        m = la.max()
        la = np.log(np.exp(la - m) @ A + 1e-300) + m + np.log(B[:, obs[t]] + 1e-300)
    m = la.max()
    return m + np.log(np.exp(la - m).sum())

def viterbi_log(A, B, pi, obs):
    T, N = len(obs), A.shape[0]
    d = np.log(pi + 1e-300) + np.log(B[:, obs[0]] + 1e-300); psi = []
    for t in range(1, T):
        s = d[:, None] + np.log(A + 1e-300)
        psi.append(s.argmax(axis=0)); d = s.max(axis=0) + np.log(B[:, obs[t]] + 1e-300)
    path = [int(d.argmax())]
    for p in reversed(psi): path.append(int(p[path[-1]]))
    return path[::-1]

# --- 式(B-10) DTW（带 Sakoe-Chiba 带）---
def dtw(Q, C, R=None):
    N, M = len(Q), len(C); R = R or max(N, M)
    D = np.full((N+1, M+1), np.inf); D[0, 0] = 0.0
    for i in range(1, N+1):
        for j in range(max(1, int(i*M/N)-R), min(M, int(i*M/N)+R)+1):
            d = np.linalg.norm(Q[i-1] - C[j-1])
            D[i, j] = d + min(D[i-1, j], D[i, j-1], D[i-1, j-1])
    return D[N, M]

# --- 式(B-7) LBG 的一次「划分 + 更新」---
def lbg_step(X, C):
    lab = np.argmin(((X[:, None, :] - C[None, :, :])**2).sum(-1), axis=1)
    return np.array([X[lab == k].mean(axis=0) if (lab == k).any() else C[k]
                     for k in range(len(C))])

# --- 式(B-11)(B-13) 维纳增益 / AMDF ---
def wiener(Y, PN, alpha=0.98):
    post = np.abs(Y)**2 / (PN + 1e-12)
    H = np.empty_like(Y); prev = np.zeros_like(PN)
    for t in range(len(Y)):
        xi = alpha*prev/(PN+1e-12) + (1-alpha)*np.maximum(post[t]-1, 0)
        H[t] = xi/(1+xi); prev = (H[t]**2)*np.abs(Y[t])**2
    return H * Y

def amdf(x, fmin=80, fmax=400, fs=8000):
    lo, hi = int(fs/fmax), int(fs/fmin)
    D = np.array([np.abs(x[k:] - x[:-k]).mean() for k in range(lo, hi+1)])
    return fs/(lo + D.argmin()), lo + D.argmin()</code></pre>

  <div class="derive">
    <div class="dtitle">推导详解 · 专题 B　四个「为什么」</div>
    <h4>1. Yule–Walker 方程怎么来的</h4>
    <p>令 \(e[n]=s[n]-\sum_{k=1}^p a_k s[n-k]\)，\(\mathcal E=\sum_n e^2[n]\)。对 \(a_i\) 求偏导：</p>
    <div class="math sub">\[ \frac{\partial\mathcal E}{\partial a_i}
    =-2\sum_n e[n]\,s[n-i]=0
    \ \Longrightarrow\
    \sum_n s[n]s[n-i]=\sum_{k=1}^{p}a_k\sum_n s[n-k]s[n-i] \tag{B-17} \]</div>
    <p>右边内层求和正是 \(R[|i-k|]\)（自相关法用加窗帧、零填充外的值），于是得到式 (B-2)。<b>注意这是「自相关法」的解</b>；若不对帧外补零、改用协方差法，矩阵不再 Toeplitz，就不能用 Levinson–Durbin，要直接解一般线性方程——赵力书第 4.6.2 节、韩纪庆书第 4.2 节对这两种解法有专门比较。</p>
    <h4>2. 反射系数为什么保证稳定</h4>
    <p>由式 (B-3)，\(E_m=(1-k_m^2)E_{m-1}\)。误差能量必为正，故 \(|k_m|\lt 1\)；反过来，若所有 \(|k_m|\lt 1\)，递推出的 \(A(z)\) 所有根都在单位圆内（这是 Schur–Cohn 稳定判据的等价形式）。因此<strong>只要约束反射系数，合成滤波器就不会发散</strong>——这就是编码器宁可传 \(k_m\) / LSP 也不直接量化 \(a_k\) 的原因。</p>
    <h4>3. LPC 倒谱递推怎么推</h4>
    <p>对 \(\ln H(z)=\ln G-\ln A(z)\) 两边取 \(z^{-1}\) 的导数，并利用 \(\ln H(z)=\sum_{n\ge1}c_n z^{-n}\)（忽略直流项）：</p>
    <div class="math sub">\[ \frac{\mathrm d}{\mathrm d z^{-1}}\ln H(z)
    =-\frac{A'(z^{-1})}{A(z^{-1})}
    \ \Longrightarrow\
    \sum_{n\ge1}n c_n z^{-n-1}
    =\frac{\sum_{k=1}^{p}k a_k z^{-k-1}}{1-\sum_{k=1}^{p}a_k z^{-k}} \tag{B-18} \]</div>
    <p>两边乘 \(A(z^{-1})\) 并比较 \(z^{-n-1}\) 的系数，即得 \(n c_n=n a_n+\sum_{k=1}^{n-1}k a_k c_{n-k}\)，整理就是式 (B-5)。<b>这说明 LPCC 与 MFCC 是同一件事的两种算法路径</b>：一个从全极点模型的系数直接递推，一个从谱的 DCT 得到，目标都是「谱包络的低维表示」。</p>
    <h4>4. 维纳增益为什么是 MMSE 最优</h4>
    <p>令 \(\hat X=HY\)，\(J(H)=\mathbb E|X-HY|^2=\mathbb E|X|^2-2H\,\mathrm{Re}\,\mathbb E[XY^*]+H^2\mathbb E|Y|^2\)。对 \(H\) 求导置零：</p>
    <div class="math sub">\[ H^*=\frac{\mathbb E[XY^*]}{\mathbb E|Y|^2}
    =\frac{P_X}{P_X+P_N}=\frac{\xi}{1+\xi},\qquad
    J_{\min}=\frac{P_XP_N}{P_X+P_N} \tag{B-19} \]</div>
    <p>用了信号与噪声不相关（\(\mathbb E[XN^*]=0\)）。可见维纳滤波是<strong>线性 MMSE 估计</strong>，而谱减法只是它的一种粗略近似，这解释了 A.3 里谱减法失真度最高的现象。</p>
  </div>

  <h3>误区与注意事项</h3>
  <div class="warn"><span class="t">误区</span>① <b>把 LPC 阶数当越大越好。</b>\(p\) 过大拟合噪声、谱峰虚假分裂；8 kHz 一般 10–12 阶。② <b>直接量化 \(a_k\) 做编码。</b>可能让 \(A(z)\) 根跑到单位圆外，合成时发散；应量化反射系数或 LSP。③ <b>HMM 不取对数。</b>几十帧连乘必然下溢，且症状隐蔽（概率全 0 但不报错）。④ <b>DTW 忘记按路径长度归一化。</b>长模板系统性吃亏。⑤ <b>把 CTC 的 blank 当成「静音」。</b>它是允许重复字符与无对齐输出的占位符，与声学静音无关。⑥ <b>以为经典方法都过时了。</b>Viterbi、log-sum-exp、反射系数、维纳增益这些结构今天仍在深度模型内部。</div>

  <h3>自检</h3>
  <div class="checklist">
    <label><input type="checkbox" data-k="qB-1"> 我能从最小化预测误差推出 Yule–Walker 方程，并用 B-4 的数字验算一遍 Levinson–Durbin。</label>
    <label><input type="checkbox" data-k="qB-2"> 我能说明为什么 \(|k_m|\lt 1\) 保证滤波器稳定，以及 LSP 为什么更适合量化。</label>
    <label><input type="checkbox" data-k="qB-3"> 我能写出前向算法与 Viterbi 的递推，并说出它们只差一个算子。</label>
    <label><input type="checkbox" data-k="qB-4"> 我能解释 DTW 的路径约束、谱熵 VAD 为什么抗增益变化、AMDF 与自相关为何互补。</label>
    <label><input type="checkbox" data-k="qB-5"> 我能把 CTC 的 blank 折叠、注意力权重、统计池化三者串成一条「时间对齐」的演进线。</label>
  </div>
</section>
"""
