# -*- coding: utf-8 -*-
"""专题 E：信号与系统（下册）——离散时间系统、z 域、DFT 与数字滤波器（完整 <section>）。

资料来源：郑君里、应启珩、杨为理《信号与系统》第三版 下册（第 7–12 章）。
扫描版无文本层，仅 72 条书签；本专题按目录框架重写标准结论与推导，未照抄原文。
保留书中记法：DFS 变换对式 (9-18)(9-19)、DTFT 式 (8-82)、z=e^{sT} 映射。
"""

TOPIC_E = r"""
<section id="sE">
  <h2><span class="no">专题 E</span>信号与系统（下）：z 域、DFT 与数字滤波器</h2>

  <div class="goal">
    <div class="g">目标</div>
    <ul>
      <li>能说清「数字信号」在 z 平面上的全部含义：单位圆、收敛域、极点位置各自对应什么物理事实。</li>
      <li>能自己从 DFS 推出 DFT，理解为什么 DFT 是「有损的」、圆周卷积在什么条件下等于线性卷积。</li>
      <li>会判断一个差分方程（滤波器）稳不稳定，知道 FIR 与 IIR 的本质差别在哪一个极点。</li>
      <li>能把声纹流程里的四个滤波器（抗混叠、预加重、Mel 组、工频陷波）对应到设计方法与公式。</li>
      <li>看得懂反馈系统与状态变量这套语言，知道它和训练发散、RNN、Kalman 是同一套数学。</li>
    </ul>
  </div>
  <div class="goal">
    <div class="g">产出</div>
    <ul><li>一张 z 平面到频率响应的读图法、一份 DFS→DFT→FFT 的完整链条推导、一张 12 章 → 17 讲的全映射表。</li></ul>
  </div>

  <div class="note"><span class="t">承接专题 D</span>专题 D 讲连续时间：卷积、傅里叶、拉普拉斯、抽样。本专题讲离散时间，两者是<strong>平行结构</strong>：卷积 \(\leftrightarrow\) 卷积和、拉普拉斯 \(\leftrightarrow\) z 变换、傅里叶 \(\leftrightarrow\) DTFT、微分方程 \(\leftrightarrow\) 差分方程。教材下册第 7–12 章依次是：时域分析、z 域分析、DFT 与离散正交变换、模拟与数字滤波器、反馈系统、状态变量。读完会发现，讲义第 4 讲的 <code>fft()</code> 落在第 9 章，第 6 讲的滤波器组落在第 10 章，第 10 讲的「训练发散」其实和第 11 章的稳定性判据是同构的。</div>

  <h3>E.1　序列、差分方程与卷积和</h3>
  <h4>1. 从微分方程到差分方程</h4>
  <p>连续系统的输入输出由微分方程描述，离散系统由差分方程描述。一般 N 阶线性常系数形式（§7.3）：</p>
  <div class="mathbox">
    <div class="math">\[ \sum_{k=0}^{N}a_k\,y[n-k]=\sum_{m=0}^{M}b_m\,x[n-m],\qquad a_0=1 \tag{E-1} \]</div>
    <div class="mathnote"><p>把 \(a_0\) 归一化为 1 后可以<strong>递推</strong>求解：\(y[n]=-\sum_{k=1}^{N}a_k y[n-k]+\sum_{m=0}^{M}b_m x[n-m]\)。这个式子就是「IIR 滤波器的直接 I 型实现」：当前输出由<strong>过去的输出</strong>（\(a_k\) 项）和<strong>当前与过去的输入</strong>（\(b_m\) 项）共同决定。<b>有 \(a_k\ (k\geq1)\) 非零 = 有反馈 = 有非零极点 = IIR</b>；若全部 \(a_k=0\)，就退化成 FIR 卷积。</p></div>
  </div>
  <h4>2. 单位样值响应与卷积和（§7.5–§7.6）</h4>
  <div class="mathbox">
    <div class="math">\[ h[n]=\mathcal{T}\{\delta[n]\},\qquad y[n]=\sum_{k=-\infty}^{\infty}x[k]\,h[n-k]=x[n]\ast h[n] \tag{E-2} \]</div>
    <div class="mathnote"><p>推导与 (D-2) 完全同构：\(\delta[n]\) 的筛选性质 \(x[n]=\sum_k x[k]\delta[n-k]\)，再用线性 + 时不变。因果性 \(h[n]=0\ (n\lt0)\)，稳定性 \(\sum_n|h[n]|\lt\infty\)。</p></div>
  </div>
  <h4>3. 解卷积（§7.7）：为什么频域除法会炸</h4>
  <div class="mathbox">
    <div class="math">\[ y[n]=x[n]\ast h[n]\ \Longrightarrow\ x[n]=y[n]\ast h^{-1}[n],\qquad H^{-1}(z)=\frac{1}{H(z)} \tag{E-3} \]</div>
    <div class="mathnote"><p>时域可以递推反求：\(x[n]=(y[n]-\sum_{k\geq1}h[k]x[n-k])/h[0]\)。频域更直观：\(X=Y/H\)。<b>问题在于</b>：若 \(H(e^{j\omega})\) 在某个频点接近 0（比如预加重的低频端，\(|H(0)|=0.03\)），除法会把该频段的噪声放大 \(1/0.03\approx33\) 倍。这就是「反卷积必须正则化」的根源，也是第 6 讲同态解卷积为什么不直接除、而要取 \(\log\) 再低通——把除法变成减法，再把「慢变的部分」平滑掉。</p></div>
  </div>

  <h3>E.2　z 变换：收敛域才是本体</h3>
  <div class="mathbox">
    <div class="math">\[ X(z)=\sum_{n=-\infty}^{\infty}x[n]\,z^{-n},\qquad z=re^{j\omega} \tag{E-4} \]</div>
  <div class="mathnote"><p>把 \(z=re^{j\omega}\) 代入：\(X(re^{j\omega})=\sum_n x[n]r^{-n}e^{-j\omega n}\)，即<strong>先给序列乘一个指数权 \(r^{-n}\)，再做 DTFT</strong>。所以 z 变换是「带衰减因子的傅里叶变换」，\(r\) 选得合适就能让原本不收敛的序列收敛。这就是 ROC（收敛域）的由来。</p></div>
  </div>
  <table class="sym">
    <tr><th>序列</th><th>\(X(z)\)</th><th>ROC</th><th>说明</th></tr>
    <tr><td>\(\delta[n]\)</td><td>1</td><td>全 z 平面</td><td>只有 \(n=0\) 一项</td></tr>
    <tr><td>\(u[n]\)</td><td>\(\dfrac{1}{1-z^{-1}}\)</td><td>\(|z|\gt1\)</td><td>单位圆上不收敛（临界）</td></tr>
    <tr><td>\(a^n u[n]\)</td><td>\(\dfrac{1}{1-az^{-1}}\)</td><td>\(|z|\gt|a|\)</td><td>右边序列，极点 \(z=a\)</td></tr>
    <tr><td>\(-a^n u[-n-1]\)</td><td>\(\dfrac{1}{1-az^{-1}}\)</td><td>\(|z|\lt|a|\)</td><td><b>同一代数式，左边序列</b></td></tr>
    <tr><td>\(n\,a^n u[n]\)</td><td>\(\dfrac{az^{-1}}{(1-az^{-1})^2}\)</td><td>\(|z|\gt|a|\)</td><td>重极点，对应 \(n\) 的多项式因子</td></tr>
    <tr><td>有限长序列</td><td>\(\sum_{n=N_1}^{N_2}x[n]z^{-n}\)</td><td>除 \(z=0,\infty\) 外全平面</td><td>DFT 的原型</td></tr>
  </table>
  <div class="defbox"><div class="dh">四种 ROC 形态（§8.3）</div>
  <ol>
    <li><b>右边序列</b>（因果）：ROC 是最外层极点以外的区域 \(|z|\gt r_{\max}\)。</li>
    <li><b>左边序列</b>（反因果）：ROC 是最内层极点以内的区域 \(|z|\lt r_{\min}\)。</li>
    <li><b>双边序列</b>：ROC 是环 \(r_1\lt|z|\lt r_2\)；若无极点夹在中间，可能整个平面。</li>
    <li><b>有限长序列</b>：ROC 是整个平面（可能除去 0 或 \(\infty\)）。</li>
  </ol>
  <p><b>为什么必须记 ROC：</b>\(1/(1-az^{-1})\) 对应两个完全不同的时域序列（因果 vs 反因果），只看代数式无法区分。这与连续域 (D-18) 是同一个道理，只是离散域的边界从「竖直直线」变成了「圆」。<b>实用推论：</b>判断一个 IIR 滤波器能否实时运行，看它的 ROC 是否包含单位圆且是右边序列——两者同时满足才叫「因果稳定」。</p></div>

  <h3>E.3　z 与 s 的映射、DTFT 与频率响应</h3>
  <h4>1. \(z=e^{sT}\)：一条指数映射</h4>
  <div class="mathbox">
    <div class="math">\[ z=e^{sT}=e^{\sigma T}e^{j\omega T},\qquad |z|=e^{\sigma T},\ \ \angle z=\omega T \tag{E-5} \]</div>
  </div>
  <table class="sym">
    <tr><th>s 平面</th><th>z 平面</th><th>物理含义</th></tr>
    <tr><td>左半平面 \(\sigma\lt0\)</td><td>单位圆内 \(|z|\lt1\)</td><td>衰减模态（稳定）</td></tr>
    <tr><td>虚轴 \(\sigma=0\)</td><td>单位圆 \(|z|=1\)</td><td>等幅振荡（临界）</td></tr>
    <tr><td>右半平面 \(\sigma\gt0\)</td><td>单位圆外 \(|z|\gt1\)</td><td>增长模态（不稳定）</td></tr>
    <tr><td>\(\sigma\) 为常数的竖线</td><td>半径为 \(e^{\sigma T}\) 的圆</td><td>同一衰减率</td></tr>
    <tr><td>\(\omega\) 为常数的横线</td><td>角度为 \(\omega T\) 的射线</td><td>同一频率</td></tr>
  </table>
  <div class="mathnote"><p><b>关键后果：</b>s 平面的虚轴（无穷长）被压到单位圆（有限长）上，且 \(\omega\) 以 \(2\pi/T\) 为周期重复映射到同一个角度——<strong>这就是离散频谱必然以 \(2\pi\) 为周期、必然发生混叠的几何原因</strong>。教材图 8-13 画的就是这条映射。</p></div>
  <h4>2. DTFT：单位圆上的 z 变换（教材式 8-82）</h4>
  <div class="mathbox">
    <div class="math">\[ X(e^{j\omega})=X(z)\big|_{z=e^{j\omega}}=\sum_{n=-\infty}^{\infty}x[n]e^{-j\omega n},\qquad X(e^{j(\omega+2\pi)})=X(e^{j\omega}) \tag{E-6} \]</div>
    <div class="mathnote"><p>这就是第 4 讲 <code>fft()</code> 计算的连续谱（DFT 只是它的 \(N\) 点采样，见 E.5）。<b>三个必须记住的性质：</b>① 以 \(2\pi\) 为周期；② 实序列满足共轭对称 \(X(e^{-j\omega})=X^*(e^{j\omega})\)，所以只看 \([0,\pi]\) 就够（第 4 讲单边谱）；③ 若 ROC 不含单位圆，DTFT 不存在，此时频率响应无从谈起——系统已经不稳定。</p></div>
  </div>
  <h4>3. 频率响应：把 \(z=e^{j\omega}\) 代进 \(H(z)\)</h4>
  <div class="mathbox">
    <div class="math">\[ H(e^{j\omega})=\frac{\sum_m b_m e^{-j\omega m}}{\sum_k a_k e^{-j\omega k}}=|H(e^{j\omega})|\,e^{j\varphi(\omega)} \tag{E-7} \]</div>
    <div class="mathnote"><p>它与 (D-20) 的零极点几何法完全一致，只是把 \(j\omega\) 换成单位圆上的点 \(e^{j\omega}\)：<b>极点越靠近单位圆，峰越尖</b>；极点落在单位圆上，增益无穷大（自激）；零点落在单位圆上，该频率被完全抑制（陷波）。这就是 E.7 要用的设计语言。</p></div>
  </div>

  <h3>E.4　系统函数、稳定性与 FIR / IIR 的分水岭</h3>
  <div class="mathbox">
    <div class="math">\[ H(z)=\frac{Y(z)}{X(z)}=\frac{\sum_{m=0}^{M}b_m z^{-m}}{\sum_{k=0}^{N}a_k z^{-k}}=K\,z^{N-M}\,\frac{\prod(z-z_i)}{\prod(z-p_k)} \tag{E-8} \]</div>
  <div class="mathnote"><p>由 (E-1) 两边取 z 变换、用移位性质 \(\mathcal{Z}\{y[n-k]\}=z^{-k}Y(z)\) 直接得到。<b>注意 \(z^{N-M}\) 这个因子</b>：它意味着原点处还有 \(|N-M|\) 个极点或零点，常被漏掉。</p></div>
  </div>
  <table class="sym">
    <tr><th>判据</th><th>条件</th><th>怎么查</th></tr>
    <tr><td>因果</td><td>\(h[n]=0,\ n\lt0\)</td><td>ROC 是某圆外，且 \(H(z)\) 在 \(\infty\) 处有限</td></tr>
    <tr><td>稳定</td><td>\(\sum_n|h[n]|\lt\infty\)</td><td>ROC 包含单位圆</td></tr>
    <tr><td>因果且稳定</td><td>两者同时成立</td><td><b>全部极点在单位圆内</b> \(|p_k|\lt1\)</td></tr>
  </table>
  <h4>FIR 与 IIR：差别只在一个极点</h4>
  <table class="sym">
    <tr><th></th><th>FIR</th><th>IIR</th></tr>
    <tr><td>差分方程</td><td>\(y[n]=\sum_{m=0}^{M}b_m x[n-m]\)</td><td>含 \(a_k\ (k\geq1)\) 反馈项</td></tr>
    <tr><td>\(H(z)\)</td><td>只有分子，极点全在 \(z=0\)</td><td>有非零极点</td></tr>
    <tr><td>稳定性</td><td><b>恒稳定</b>（极点都在原点）</td><td>需检查 \(|p_k|\lt1\)</td></tr>
    <tr><td>相位</td><td>可取严格线性相位（\(h[n]=\pm h[M-n]\)）</td><td>一般非线性相位</td></tr>
    <tr><td>同样指标所需阶数</td><td>高（要很多抽头）</td><td>低（几个极点就够陡）</td></tr>
    <tr><td>声纹里的例子</td><td>预加重、滑动平均、FIR 抗混叠</td><td>共振峰合成、工频陷波、LPC 合成滤波器</td></tr>
  </table>
  <div class="defbox"><div class="dh">最小相位与全通（离散版）</div>
  <p><b>最小相位</b>：全部零点与极点都在单位圆内。性质：逆系统 \(1/H(z)\) 也因果稳定；在相同幅频响应下，相位滞后最小、能量最集中在时间前端。<b>全通</b>：\(H_{ap}(z)=\prod_k\frac{z^{-1}-a_k^*}{1-a_kz^{-1}}\)，零点与极点关于单位圆镜像（\(z_i=1/p_k^*\)），幅频恒为 1，只改相位。声纹里的用途：全通做相位/时长扰动做数据增强；最小相位是倒谱分析（第 6 讲）与 LPC（专题 B）能用「取 \(\log\) 再低通」分离声道与激励的前提。</p></div>

  <h3>E.5　从 DFS 到 DFT：为什么 DFT 是「有损」的</h3>
  <h4>1. 周期序列不能做双边 z 变换（§9.3 的出发点）</h4>
  <p>教材下册书页 124 说得很直接：周期序列 \(x_p(n)=x_p(n+rN)\) 在 \(n\to\pm\infty\) 时永不衰减，<strong>找不到任何 \(z\) 使 \(x_p(n)z^{-n}\) 绝对可和</strong>，因此 z 变换不存在。这与连续域「周期信号不存在双边拉普拉斯变换、只能用傅里叶级数」完全对应。所以周期序列用 DFS 表示。教材式 (9-18)(9-19)：</p>
  <div class="mathbox">
    <div class="math">\[ \begin{cases} X_p(k)=\sum_{n=0}^{N-1}x_p(n)\,e^{-j\frac{2\pi}{N}nk}\\[4pt] x_p(n)=\dfrac{1}{N}\sum_{k=0}^{N-1}X_p(k)\,e^{j\frac{2\pi}{N}nk}\end{cases} \tag{E-9} \]</div>
    <div class="mathnote"><p>两式都是 \(N\) 项求和，且 \(X_p(k)\) 以 \(N\) 为周期。<b>结构上和 (D-10) 的 FS 一模一样</b>，只是积分换成求和、\(T\) 换成 \(N\)。教材指出：这里取时域间隔 \(T_s\) 与频域间隔 \(f_1\) 都等于 1，表达式才这么简洁；一般情形会出现 \(T_s f_1=1/N\) 的因子。</p></div>
  </div>
  <h4>2. DFT 就是 DFS 取一个主值区间</h4>
  <div class="mathbox">
    <div class="math">\[ X[k]=\sum_{n=0}^{N-1}x[n]\,e^{-j\frac{2\pi}{N}kn},\qquad x[n]=\frac{1}{N}\sum_{k=0}^{N-1}X[k]\,e^{j\frac{2\pi}{N}kn},\qquad 0\leq k,n\leq N-1 \tag{E-10} \]</div>
    <div class="mathnote"><p><b>关键理解：</b>DFT 把有限长序列 \(x[0..N-1]\) <em>当成</em>一个周期为 \(N\) 的周期序列的一个周期。这个「当成」是全部混淆的来源：</p>
    <ul>
      <li>频域被采样成 \(N\) 个点，\(X[k]=X(e^{j2\pi k/N})=X(z)|_{z=e^{j2\pi k/N}}\)，<b>丢掉了点与点之间的连续谱</b>；</li>
      <li>时域被当成周期延拓，<b>相邻周期的「尾巴」会卷回来叠加</b>，即圆周卷积；</li>
      <li>所以补零只能让 \(X[k]\) 采样更密（看到更多点），<b>不能真正提高分辨率</b>——分辨率由观测时长 \(T=NT_s\) 决定，\(\Delta f=1/T=F_s/N\)。第 4 讲「补零只改显示密度」的严格出处就在这里。</li>
    </ul></div>
  </div>
  <h4>3. 圆周卷积与线性卷积的等价条件</h4>
  <div class="mathbox">
    <div class="math">\[ \mathrm{DFT}\{x\circledast h\}=X[k]H[k],\qquad x\circledast h\text{ 等于 }x\ast h\ \Longleftrightarrow\ N\geq L_x+L_h-1 \tag{E-11} \]</div>
    <div class="mathnote"><p><b>算到账：</b>\(L_x=3\)、\(L_h=2\) 的 D.3 例子，线性卷积长度是 4；若取 \(N=4\) 做圆周卷积恰好相等；若取 \(N=3\)，第 4 个点会卷回第 0 个点，结果变成 \([1+(-3),1,1]=[-2,1,1]\)。<b>所以 FFT 加速卷积时必须补零到 \(N\geq L_x+L_h-1\)</b>；长信号分段处理则用重叠相加法（overlap-add）或重叠保留法（overlap-save），这是实时滤波与离线批处理的标准做法。</p></div>
  </div>
  <h4>4. DFT 的性质与「四性」</h4>
  <table class="sym">
    <tr><th>性质</th><th>表达式</th><th>讲义里的用处</th></tr>
    <tr><td>线性</td><td>\(\mathrm{DFT}\{ax+bg\}=aX+bG\)</td><td>多通道信号叠加</td></tr>
    <tr><td>圆周移位</td><td>\(x[(n-m)\bmod N]\leftrightarrow W_N^{km}X[k]\)</td><td>时延估计、相位差</td></tr>
    <tr><td>共轭对称</td><td>实序列 \(X[N-k]=X^*[k]\)</td><td>单边谱只取 \(N/2+1\) 点</td></tr>
    <tr><td>帕塞瓦尔</td><td>\(\sum_{n}|x[n]|^2=\frac{1}{N}\sum_k|X[k]|^2\)</td><td>D.9 已手算验证</td></tr>
    <tr><td>圆周卷积</td><td>(E-11)</td><td>频域滤波、卷积定理的离散版</td></tr>
  </table>

  <h3>E.6　FFT、DCT 与沃尔什变换</h3>
  <h4>1. FFT 只是算法，不是新变换</h4>
  <div class="mathbox">
    <div class="math">\[ \text{直接 DFT：}O(N^2)\ \longrightarrow\ \text{基-2 FFT：}O(N\log_2 N),\qquad N=512:\ 262144\to4608 \tag{E-12} \]</div>
    <div class="mathnote"><p><b>算到账：</b>\(512^2=262144\)，而 \((512/2)\log_2 512=256\times9=2304\) 次蝶形，每蝶形约 2 次复数乘法 ⇒ 约 4608，加速约 57 倍。第 4 讲已推过 Cooley–Tukey 的奇偶分解，这里只强调：<b>FFT 不改变 DFT 的数值结果，只改变算它的代价</b>；所有「精度问题、泄漏问题、分辨率问题」都来自 DFT 的定义 (E-10)，与 FFT 无关。</p></div>
  </div>
  <h4>2. DCT：把信号偶延拓后再 DFT（第 6 讲第 6 步的理论出处）</h4>
  <div class="mathbox">
    <div class="math">\[ X_c[k]=\alpha_k\sum_{n=0}^{N-1}x[n]\cos\!\Big[\frac{\pi}{N}\Big(n+\frac12\Big)k\Big],\qquad \alpha_0=\sqrt{\frac1N},\ \alpha_k=\sqrt{\frac2N} \tag{E-13} \]</div>
    <div class="mathnote"><p>教材 §9.10 用「偶对称延拓」解释 DCT：把 \(x[n]\) 沿 \(n=-1/2\) 偶延拓成 \(2N\) 长序列再 DFT，虚部自动抵消，只剩余弦项。<b>两个工程优势</b>：① 实数运算、无冗余；② 能量更集中（去相关能力强），所以 MFCC 用它压缩 26 维 Mel 能量到 13 维。<b>正交性</b>：\(\sum_n \alpha_k\cos[\cdot]\cdot\alpha_l\cos[\cdot]=\delta_{kl}\)，第 6 讲已验证 \(DD^{\mathsf T}=I\)。</p></div>
  </div>
  <h4>3. 沃尔什变换：只有加减的正交基</h4>
  <div class="mathnote"><p>教材 §6.5 与 §9.9 讲沃尔什（Walsh）函数：取值只有 \(\pm1\) 的完备正交函数集，变换只需加减法，适合硬件实现。今天它更多出现在图像/通信的快速变换里；对声纹而言，它的意义是<strong>再次印证「换一组正交基」的思路</strong>——DFT、DCT、Walsh、小波、Gammatone 都是不同基，选哪个取决于你要稀疏表示什么结构。</p></div>

  <h3>E.7　数字滤波器：从模拟原型到声纹的四个滤波器</h3>
  <h4>1. 模拟原型（§10.2）</h4>
  <div class="mathbox">
    <div class="math">\[ |H_{B}(j\Omega)|^2=\frac{1}{1+(\Omega/\Omega_c)^{2N}},\qquad |H_{C}(j\Omega)|^2=\frac{1}{1+\varepsilon^2T_N^2(\Omega/\Omega_c)} \tag{E-14} \]</div>
    <div class="mathnote"><p>巴特沃斯（Butterworth）在通带内最平坦、单调下降，\(N\) 阶在 \(\Omega_c\) 处衰减 3 dB，阻带以 \(-20N\) dB/dec 滚降；切比雪夫（Chebyshev）用纹波换更陡的过渡带。教材 §10.2 的「逼近」就是选 \(N\) 与 \(\Omega_c\) 去满足给定的通带/阻带指标——<b>这正是 D.8 佩利–维纳准则说的「必须有过渡带」的具体实现</b>。</p></div>
  </div>
  <h4>2. 双线性变换：把 s 左半平面压进单位圆</h4>
  <div class="mathbox">
    <div class="math">\[ s=\frac{2}{T}\cdot\frac{1-z^{-1}}{1+z^{-1}},\qquad \Omega=\frac{2}{T}\tan\frac{\omega}{2} \tag{E-15} \]</div>
    <div class="mathnote"><p>它把整个 \(j\Omega\) 轴一一映射到单位圆上，<strong>无混叠</strong>（这是它相对「脉冲响应不变法」的最大优势），代价是频率<strong>畸变</strong>：高频被压缩。所以设计时要先「预畸变」：把想要的数字频率 \(\omega_c\) 用 (E-15) 换成模拟 \(\Omega_c\) 再设计原型。教材 §10.6 讲 IIR 设计，核心就是这条链。</p></div>
  </div>
  <h4>3. FIR 窗函数法（§10.7）</h4>
  <div class="mathbox">
    <div class="math">\[ h[n]=h_d[n]\cdot w[n],\qquad h_d[n]=\frac{\sin[\omega_c(n-\tau)]}{\pi(n-\tau)},\ \ \tau=\frac{M}{2} \tag{E-16} \]</div>
    <div class="mathnote"><p>理想低通的 \(h_d\) 是 sinc、无限长且非因果（(D-23) 的离散版）。工程做法：<b>截断 + 加窗 + 右移 \(\tau\)</b>。加窗就是 D.4 的时域相乘，所以频域是「理想矩形响应与窗谱的卷积」——主瓣决定过渡带宽度（\(\approx\) 窗主瓣宽），旁瓣决定阻带衰减。矩形窗阻带仅 −21 dB，汉明 −53 dB，凯塞（Kaiser）窗可用参数 \(\beta\) 连续调节。<b>线性相位条件</b>：\(h[n]=\pm h[M-n]\) 时有严格线性相位，群延时恒为 \(M/2\) 个样点——这是 FIR 相对 IIR 的最大卖点。</p></div>
  </div>
  <h4>4. 声纹流程里的四个滤波器，分别是什么类型</h4>
  <table class="sym">
    <tr><th>滤波器</th><th>作用位置</th><th>类型 / 设计</th><th>关键指标</th></tr>
    <tr><td>抗混叠低通</td><td>ADC 之前（模拟）</td><td>模拟低通，巴特沃斯/椭圆</td><td>\(F_s/2=4\) kHz 处足够衰减，过渡带 3.4–4 kHz</td></tr>
    <tr><td>预加重</td><td>第 6 讲第 1 步</td><td>一阶 FIR 高通，\(h=[1,-0.97]\)</td><td>零点 \(z=0.97\)，低频 −30 dB、高频 +6 dB（D.2 表）</td></tr>
    <tr><td>Mel / Gammatone 组</td><td>第 6 讲第 4 步、第 7 讲</td><td>并联带通组（三角/伽马通）</td><td>中心频率按 Mel/Bark 分布，带宽随频率变宽</td></tr>
    <tr><td>工频陷波</td><td>专题 A 现场采集</td><td>IIR 陷波（二阶），零点在 \(e^{\pm j\omega_0}\)</td><td>50 Hz 与 100 Hz，\(Q\) 决定陷波宽度</td></tr>
  </table>
  <div class="mathbox">
    <div class="math">\[ H_{\text{notch}}(z)=\frac{1-2\cos\omega_0\,z^{-1}+z^{-2}}{1-2r\cos\omega_0\,z^{-1}+r^2z^{-2}},\qquad 0\lt r\lt1 \tag{E-17} \]</div>
    <div class="mathnote"><p>零点在单位圆上的 \(e^{\pm j\omega_0}\)（该频率增益严格为 0），极点在同角度的 \(r e^{\pm j\omega_0}\)（\(r\) 略小于 1，把陷波做窄、减少对邻近频段的伤害）。<b>\(r\to1\) 陷波越窄越尖锐，但极点贴近单位圆、瞬态拖长</b>——稳定性与选择性的一对矛盾，正是 E.4 判据的现场应用。变压器声纹的 100 Hz 基频与谐波若被 50 Hz 工频干扰污染，就靠它分离。</p></div>
  </div>

  <h3>E.8　反馈、稳定性与「训练为什么会炸」</h3>
  <p>§11 讲反馈系统：负反馈换带宽/降失真，正反馈产生自激。判定闭环稳定性的工具是奈奎斯特判据与根轨迹：</p>
  <div class="mathbox">
    <div class="math">\[ 1+G(s)H(s)=0,\qquad Z=P-N \tag{E-18} \]</div>
    <div class="mathnote"><p>\(Z\) 为右半平面闭环极点数，\(P\) 为开环右半平面极点数，\(N\) 为 \(1+GH\) 曲线顺时针包围原点的圈数。稳定要求 \(Z=0\)。§11.4 的根轨迹则描述「某个参数（通常是增益 \(K\)）从 0 变到 \(\infty\) 时闭环极点怎么走」——<b>参数过大导致极点越过虚轴 ⇒ 自激/发散</b>。</p></div>
  </div>
  <div class="defbox"><div class="dh">这个判据和第 10 讲的「训练发散」是同一件事</div>
  <p>把梯度下降看成闭环系统：参数更新 \(w_{t+1}=w_t-\eta\nabla L(w_t)\)。在极小点附近线性化，\(\nabla L\approx H(w-w^*)\)（\(H\) 为 Hessian），于是</p>
  <p style="text-align:center">\(w_{t+1}-w^*=(I-\eta H)(w_t-w^*)\)。</p>
  <p>收敛要求「闭环极点」\((1-\eta\lambda_i)\) 全部落在单位圆内，即 \(0\lt\eta\lambda_i\lt2\)，\(\lambda_i\) 是 \(H\) 的特征值。所以<b>学习率上限是 \(2/\lambda_{\max}\)</b>：曲率最大的方向决定你能用多大步长，超过就振荡发散——这就是「学习率太大 loss 变 NaN」的严格解释，与 (E-18) 中「增益过大极点出界」完全同构。第 10 讲的梯度裁剪、学习率衰减、Adam 的自适应步长，本质上都在给这个闭环加阻尼。</p></div>

  <h3>E.9　状态变量：从电路方程到 RNN</h3>
  <div class="mathbox">
    <div class="math">\[ \dot{\mathbf{x}}=A\mathbf{x}+B\mathbf{u},\quad \mathbf{y}=C\mathbf{x}+D\mathbf{u}\qquad\Longleftrightarrow\qquad \mathbf{x}[n+1]=A\mathbf{x}[n]+B\mathbf{u}[n],\quad \mathbf{y}[n]=C\mathbf{x}[n]+D\mathbf{u}[n] \tag{E-19} \]</div>
    <div class="mathnote"><p>§12 把高阶微分/差分方程降为一阶向量方程，状态 \(\mathbf{x}\) 是「记住过去所需的最小信息集」。连续解含矩阵指数 \(e^{At}\)，离散解含 \(A^n\)——<b>稳定性判据变成 \(A\) 的特征值模长小于 1</b>，与 E.4 的极点判据一致（极点就是 \(A\) 的特征值）。</p></div>
  </div>
  <table class="sym">
    <tr><th>概念</th><th>判据</th><th>在深度学习里的对应</th></tr>
    <tr><td>可控性</td><td>\([B\ \ AB\ \ \cdots\ \ A^{n-1}B]\) 满秩</td><td>输入能否影响全部隐状态</td></tr>
    <tr><td>可观性</td><td>\([C;\ CA;\ \cdots;\ CA^{n-1}]\) 满秩</td><td>隐状态能否由输出反推</td></tr>
    <tr><td>状态转移</td><td>\(\mathbf{x}[n]=A^n\mathbf{x}[0]+\sum AkB u\)</td><td>RNN 的隐状态递推、长程依赖衰减</td></tr>
  </table>
  <div class="mathnote"><p><b>这条线一直通到今天的模型：</b>RNN 就是 (E-19) 加上非线性激活；LSTM 的门控是在给 \(A\) 加「可学习的遗忘因子」；卡尔曼滤波是线性高斯下的最优状态估计；近年的状态空间模型（S4、Mamba）直接把 \(A\) 参数化成结构化矩阵，用 (E-19) 的卷积形式做长序列建模。<b>声纹里的 x-vector 统计池化，本质上也是在从变长序列里估计一个「状态摘要」。</b>第 14 讲说的「帧级特征 → 句级嵌入」，用状态变量的语言就是「用 \(C\) 观测、用池化汇总」。</p></div>

  <h3>E.10　全映射：郑君里 12 章 → 讲义 17 讲</h3>
  <table class="sym">
    <tr><th>教材章节</th><th>核心内容</th><th>对应讲义</th><th>读了能解决什么</th></tr>
    <tr><td>上册 §1</td><td>信号分类、δ、LTI 定义</td><td>第 1 讲</td><td>为什么正弦/复指数是「基本单元」</td></tr>
    <tr><td>上册 §2</td><td>微分方程、卷积、冲激响应</td><td>第 1、6 讲；专题 D.2–D.3</td><td>预加重、滤波器到底是什麼</td></tr>
    <tr><td>上册 §3</td><td>FS、FT、卷积定理、抽样</td><td>第 2、4 讲；专题 D.4–D.6</td><td>泄漏、分辨率、混叠的严格解释</td></tr>
    <tr><td>上册 §4</td><td>拉普拉斯、H(s)、零极点、稳定性</td><td>第 6 讲；专题 D.7</td><td>共振峰、最小相位、逆滤波</td></tr>
    <tr><td>上册 §5</td><td>无失真传输、理想滤波器、调制、PCM</td><td>第 2 讲；专题 D.8</td><td>为什么抗混叠必须有过渡带</td></tr>
    <tr><td>上册 §6</td><td>矢量空间、帕塞瓦尔、相关、匹配滤波、测不准</td><td>第 3、5、12 讲；专题 D.9</td><td>自相关、STFT 下界、模板匹配</td></tr>
    <tr><td>下册 §7</td><td>差分方程、卷积和、解卷积</td><td>第 3、6 讲；专题 E.1</td><td>IIR/FIR 的实现与反卷积</td></tr>
    <tr><td>下册 §8</td><td>z 变换、ROC、DTFT、频率响应</td><td>第 4、6 讲；专题 E.2–E.3</td><td>单位圆、共轭对称、滤波器频响</td></tr>
    <tr><td>下册 §9</td><td>DFS、DFT、FFT、DCT、沃尔什</td><td>第 4、6 讲；专题 E.5–E.6</td><td>DFT 为什么有损、补零为何不提分辨率</td></tr>
    <tr><td>下册 §10</td><td>模拟逼近、IIR、FIR、开关电容</td><td>第 6 讲；专题 E.7</td><td>Mel 组、陷波、线性相位</td></tr>
    <tr><td>下册 §11</td><td>反馈、自激、根轨迹、奈奎斯特</td><td>第 10 讲；专题 E.8</td><td>学习率上限、训练发散</td></tr>
    <tr><td>下册 §12</td><td>状态方程、可控可观</td><td>第 14 讲；专题 E.9</td><td>RNN、Kalman、状态空间模型</td></tr>
  </table>

  <h3>E.11　公式 ↔ 代码、边界与自检</h3>
  <table class="sym">
    <tr><th>结论</th><th>公式</th><th>代码</th><th>验证方式</th></tr>
    <tr><td>差分方程 / FIR</td><td>(E-1), (E-16)</td><td><code>mfcc()</code> 预加重</td><td>与 <code>np.convolve</code> 对拍</td></tr>
    <tr><td>DTFT / 频响</td><td>(E-6), (E-7)</td><td><code>fft()</code>、<code>stft()</code></td><td>纯音峰值落在预期 bin</td></tr>
    <tr><td>DFT 采样性</td><td>(E-10)</td><td><code>dft()</code> 与 <code>fft()</code></td><td>两者结果差 &lt; 1e-12</td></tr>
    <tr><td>圆周卷积条件</td><td>(E-11)</td><td>—</td><td>N=3 与 N=4 手算对比</td></tr>
    <tr><td>DCT 正交</td><td>(E-13)</td><td><code>dct_matrix()</code></td><td>\(DD^{\mathsf T}=I\)</td></tr>
    <tr><td>稳定性</td><td>(E-8)</td><td>递归滤波实验</td><td>极点 \(|p|\gt1\) 时输出发散</td></tr>
  </table>
  <div class="defbox"><div class="dh">五个常见错误</div>
  <ol>
    <li><b>看到 \(H(z)\) 就算频响</b>：先确认 ROC 含单位圆，否则系统不稳定、频响无意义。</li>
    <li><b>补零当升分辨率</b>：分辨率由观测时长决定，补零只是插值显示（E.5）。</li>
    <li><b>FFT 加速卷积忘了补零</b>：\(N\lt L_x+L_h-1\) 时结果是圆周卷积，尾部卷回头部（E.11 手算）。</li>
    <li><b>以为 FIR 一定线性相位</b>：只有满足 \(h[n]=\pm h[M-n]\) 的四种类型才是；任意抽头不保证。</li>
    <li><b>把陷波 \(Q\) 调得过高</b>：极点贴近单位圆，瞬态振铃长达几十毫秒，反而污染短帧特征。</li>
  </ol></div>

  <h3>自检</h3>
  <div class="checklist">
    <label><input type="checkbox" data-k="qE-1"> 我能说出同一个 \(1/(1-az^{-1})\) 在两种 ROC 下分别对应什么序列，并解释为什么 ROC 是变换的一部分。</label>
    <label><input type="checkbox" data-k="qE-2"> 我能画出 \(z=e^{sT}\) 的映射表，并说明「频谱以 \(2\pi\) 为周期」的几何原因。</label>
    <label><input type="checkbox" data-k="qE-3"> 我能从 DFS 写出 DFT，说清 DFT 丢了什么、补零为什么不能提高分辨率。</label>
    <label><input type="checkbox" data-k="qE-4"> 我能判断一个差分方程是否稳定，并解释 FIR 为什么恒稳定、IIR 为什么不一定。</label>
    <label><input type="checkbox" data-k="qE-5"> 我能写出二阶陷波器的 \(H(z)\)，说明零点、极点各在哪、\(r\) 调节什么。</label>
    <label><input type="checkbox" data-k="qE-6"> 我能把「学习率过大导致发散」解释成闭环极点出单位圆，并说出学习率上限与 Hessian 特征值的关系。</label>
  </div>
</section>
"""
