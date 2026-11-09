"""手写信号处理算法（只依赖 numpy）。

包含：DFT / FFT(Cooley-Tukey, 向量化蝶形) / STFT / 功率谱 / Mel 滤波器组 /
MFCC / Gamma 校正 / Gammatone 听觉滤波器组 / Haar 与 db4 DWT / Morlet CWT /
EMD(自写自然三次样条包络)。末尾 verify() 给出全部数值验证。
"""
from __future__ import annotations
import numpy as np

# ---------------------------------------------------------------- FFT 族

def _bitrev(n: int) -> np.ndarray:
    bits = int(round(np.log2(n)))
    i = np.arange(n, dtype=np.int64)
    r = np.zeros(n, dtype=np.int64)
    for b in range(bits):
        r = (r << 1) | ((i >> b) & 1)
    return r


def fft_rows(a: np.ndarray, n: int | None = None) -> np.ndarray:
    """对矩阵每一行做 radix-2 FFT（向量化蝶形，比 Python 循环快百倍）。"""
    a = np.asarray(a, np.complex128)
    m = a.shape[0]
    if n is None:
        n = 1 << (a.shape[1] - 1).bit_length() if a.shape[1] > 1 else 1
    if a.shape[1] < n:
        a = np.pad(a, ((0, 0), (0, n - a.shape[1])))
    elif a.shape[1] > n:
        a = a[:, :n]
    br = _bitrev(n)
    out = a[:, br].copy()
    length = 2
    while length <= n:
        half = length // 2
        w = np.exp(-2j * np.pi * np.arange(half) / length)
        v = out.reshape(m, -1, length)
        u = v[:, :, :half].copy()
        t = v[:, :, half:] * w
        v[:, :, :half] = u + t
        v[:, :, half:] = u - t
        out = v.reshape(m, n)
        length *= 2
    return out


def fft(x, n: int | None = None) -> np.ndarray:
    return fft_rows(np.asarray(x, np.complex128)[None, :], n)[0]


def ifft(X) -> np.ndarray:
    X = np.asarray(X, np.complex128)
    return np.conj(fft(np.conj(X))) / X.shape[-1]


def dft(x) -> np.ndarray:
    """教学版 O(N^2) DFT：X[k] = sum_n x[n] * exp(-2j*pi*k*n/N)。"""
    x = np.asarray(x, np.complex128)
    n = len(x)
    k = np.arange(n)
    return np.exp(-2j * np.pi * np.outer(k, k) / n) @ x


def frames(x: np.ndarray, frame: int, hop: int) -> np.ndarray:
    """分帧，尾部反射填充到完整帧。"""
    n = len(x)
    if n < frame:
        x = np.pad(x, (0, frame - n))
    n = len(x)
    count = 1 + (n - frame) // hop
    idx = np.arange(frame)[None, :] + hop * np.arange(count)[:, None]
    return x[idx]


def stft(x, frame: int = 200, hop: int = 80, n_fft: int = 512,
         hamming: bool = True) -> np.ndarray:
    """短时傅里叶变换，返回复数谱 (帧数, n_fft//2+1)。"""
    fr = frames(np.asarray(x, float), frame, hop)
    if hamming:
        fr = fr * np.hamming(frame)[None, :]
    S = fft_rows(fr, n_fft)
    return S[:, : n_fft // 2 + 1]


def spectrum(x, fs: int, n_fft: int = 4096):
    S = np.abs(fft(x, n_fft))[: n_fft // 2 + 1]
    f = np.arange(n_fft // 2 + 1) * fs / n_fft
    return f, S


# ---------------------------------------------------------------- 听觉特征

def hz2mel(f):
    return 2595.0 * np.log10(1.0 + np.asarray(f, float) / 700.0)


def mel2hz(m):
    return 700.0 * (10.0 ** (np.asarray(m, float) / 2595.0) - 1.0)


def mel_filterbank(fs: int, n_fft: int = 512, n_mels: int = 26,
                   fmin: float = 80.0, fmax: float | None = None) -> np.ndarray:
    fmax = fs / 2 if fmax is None else fmax
    n_freqs = n_fft // 2 + 1
    pts = mel2hz(np.linspace(hz2mel(fmin), hz2mel(fmax), n_mels + 2))
    bins = np.floor(pts * n_fft / fs).astype(int)
    bins = np.clip(bins, 0, n_freqs - 1)
    fb = np.zeros((n_mels, n_freqs))
    for m in range(1, n_mels + 1):
        l, c, r = bins[m - 1], bins[m], bins[m + 1]
        if c > l:
            fb[m - 1, l:c] = (np.arange(l, c) - l) / (c - l)
        if r > c:
            fb[m - 1, c:r] = (r - np.arange(c, r)) / (r - c)
    fb = np.where(fb.sum(axis=1, keepdims=True) > 0, fb / np.maximum(fb.sum(axis=1, keepdims=True), 1e-12), fb)
    return fb


def dct_matrix(n_in: int, n_out: int) -> np.ndarray:
    k = np.arange(n_out)[:, None]
    n = np.arange(n_in)[None, :]
    D = np.cos(np.pi * k * (2 * n + 1) / (2 * n_in)) * np.sqrt(2.0 / n_in)
    D[0] *= 1.0 / np.sqrt(2.0)
    return D


def mfcc(x, fs: int, n_mels: int = 26, n_mfcc: int = 13, frame: int = 200,
         hop: int = 80, n_fft: int = 512, preemph: float = 0.97,
         return_logmel: bool = False):
    """手写 MFCC：预加重 → 分帧加窗 → FFT → Mel 三角滤波 → log → DCT-II。"""
    x = np.asarray(x, float)
    xp = np.concatenate([x[:1], x[1:] - preemph * x[:-1]])
    fr = frames(xp, frame, hop) * np.hamming(frame)[None, :]
    S = np.abs(fft_rows(fr, n_fft)[:, : n_fft // 2 + 1]) ** 2
    fb = mel_filterbank(fs, n_fft, n_mels)
    logmel = np.log(S @ fb.T + 1e-10)
    D = dct_matrix(n_mels, n_mfcc)
    cc = logmel @ D.T
    if return_logmel:
        return cc, logmel.T
    return cc


def delta(f: np.ndarray, width: int = 2) -> np.ndarray:
    """一阶差分（Δ），用于 39 维 MFCC 中的动态特征。"""
    f = np.asarray(f, float)
    pad = np.pad(f, ((width, width), (0, 0)), mode="edge")
    num = np.zeros_like(f)
    den = 2 * sum(i * i for i in range(1, width + 1))
    for i in range(1, width + 1):
        num += i * (pad[width + i: width + i + len(f)] - pad[width - i: width - i + len(f)])
    return num / den


def gamma_correct(S, gamma: float = 0.4, eps: float = 1e-10) -> np.ndarray:
    """谱图 Gamma 校正：先归一化到 [0,1]，再做 s^gamma 的非线性压缩。

    gamma<1 抬升弱能量分量（抑制强谐波掩蔽）；gamma>1 增强对比度。
    """
    S = np.asarray(S, float)
    lo, hi = S.min(), S.max()
    Sn = (S - lo) / (hi - lo + eps)
    return Sn ** gamma


def gammatone_filters(fs: int, n_fft: int = 512, n_ch: int = 26,
                      fmin: float = 80.0, fmax: float = 3800.0,
                      order: int = 4, dur: float = 0.04):
    """Gammatone 听觉滤波器组：h(t)=t^(n-1) exp(-2*pi*b*t) cos(2*pi*fc*t)。

    注意：这是「伽马变换」的另一种含义（听觉滤波器），与上面的幂律 Gamma
    校正不是同一件事。b 由 ERB(fc)=24.7*(4.37*fc/1000+1) 给出。
    """
    # ERB 数域上等距取中心频率
    def erb(f):
        return 21.4 * np.log10(1 + 0.00437 * np.asarray(f, float))
    e0, e1 = erb(fmin), erb(fmax)
    edges = np.linspace(e0, e1, n_ch + 1)
    # 反解 ERB
    inv = lambda e: (10 ** (e / 21.4) - 1) / 0.00437
    cfs = inv((edges[:-1] + edges[1:]) / 2)
    t = np.arange(int(dur * fs)) / fs
    H = []
    for fc in cfs:
        b = 24.7 * (4.37 * fc / 1000.0 + 1.0)
        h = t ** (order - 1) * np.exp(-2 * np.pi * b * t) * np.cos(2 * np.pi * fc * t)
        h /= np.sum(np.abs(h)) + 1e-12
        H.append(np.abs(np.fft.rfft(h, n_fft)))
    return np.asarray(H), cfs


def gammatonegram(x, fs: int, frame: int = 200, hop: int = 80,
                  n_fft: int = 512, n_ch: int = 26):
    H, cfs = gammatone_filters(fs, n_fft, n_ch)
    fr = frames(x, frame, hop) * np.hamming(frame)[None, :]
    S = np.abs(fft_rows(fr, n_fft)[:, : n_fft // 2 + 1]) ** 2
    return np.log(S @ H.T + 1e-10).T, cfs


# ---------------------------------------------------------------- 小波

def haar_dwt(x, levels: int = 4):
    """Haar 离散小波分解，返回 [(cA, cD), ...]，能量正交。"""
    a = np.asarray(x, float).copy()
    out = []
    for _ in range(levels):
        if len(a) % 2:
            a = a[:-1]
        cA = (a[0::2] + a[1::2]) / np.sqrt(2.0)
        cD = (a[0::2] - a[1::2]) / np.sqrt(2.0)
        out.append((cA, cD))
        a = cA
    return out


def haar_idwt(coeffs) -> np.ndarray:
    a = coeffs[-1][0]
    for cA, cD in reversed(coeffs):
        up = np.empty(2 * len(cD))
        up[0::2] = (cA + cD) / np.sqrt(2.0)
        up[1::2] = (cA - cD) / np.sqrt(2.0)
        a = up
    return a


# Daubechies db4 (D8) 分解低通；h1 为它的正交镜像高通
DB4_H = np.array([-0.010597401784997, 0.032883011666885, 0.030841381835987,
                  -0.187034811718881, -0.027983769416983, 0.630880767929590,
                  0.714846570552542, 0.230377813308855])


def _down_periodic(x, f):
    """周期相关 + 抽取：c[k] = sum_p f[p] * x[(2k-p) mod n]，即分析算子 A 的行。"""
    x = np.asarray(x, float)
    n, L = len(x), len(f)
    k = np.arange(n // 2)
    c = np.zeros(n // 2)
    for p in range(L):
        c += f[p] * x[(2 * k - p) % n]
    return c


def _up_periodic(c, f, n):
    """A 的转置 A^T：x[n] = sum_k c[k] * f[2k-n]，与 _down_periodic 严格互逆。"""
    c = np.asarray(c, float)
    L = len(f)
    k = np.arange(len(c))
    x = np.zeros(n)
    for p in range(L):
        np.add.at(x, (2 * k - p) % n, c * f[p])
    return x


def db4_dwt(x, levels: int = 3):
    h0 = DB4_H
    h1 = (-1.0) ** np.arange(len(h0)) * h0[::-1]
    a = np.asarray(x, float).copy()
    out = []
    for _ in range(levels):
        if len(a) % 2 or len(a) < 16:
            break
        cA, cD = _down_periodic(a, h0), _down_periodic(a, h1)
        out.append((cA, cD))
        a = cA
    return out


def db4_idwt(coeffs) -> np.ndarray:
    h0 = DB4_H
    h1 = (-1.0) ** np.arange(len(h0)) * h0[::-1]
    a = coeffs[-1][0]
    for cA, cD in reversed(coeffs):
        n = 2 * len(cA)
        a = _up_periodic(cA, h0, n) + _up_periodic(cD, h1, n)
    return a


def cwt_morlet(x, fs: int, freqs=None, w0: float = 6.0):
    """连续小波变换（复 Morlet），返回幅度尺度图与频率轴。"""
    x = np.asarray(x, float)
    n = len(x)
    if freqs is None:
        freqs = np.geomspace(50, 3500, 56)
    scales = w0 / (2 * np.pi * np.asarray(freqs, float))  # 尺度（秒）
    f = np.fft.fftfreq(n, 1.0 / fs)
    X = np.fft.fft(x)
    W = np.empty((len(scales), n), float)
    for i, a in enumerate(scales):
        psi = np.pi ** -0.25 * np.exp(-0.5 * (2 * np.pi * a * f - w0) ** 2)
        W[i] = np.abs(np.fft.ifft(X * np.sqrt(a) * psi))
    return W, np.asarray(freqs, float)


# ---------------------------------------------------------------- EMD

def _thomas(lower, diag, upper, rhs):
    """解三对角方程（Thomas 算法，O(m)）。"""
    m = len(diag)
    cp, dp = np.zeros(m), np.zeros(m)
    cp[0] = upper[0] / diag[0]
    dp[0] = rhs[0] / diag[0]
    for i in range(1, m):
        den = diag[i] - lower[i] * cp[i - 1]
        cp[i] = upper[i] / den if i < m - 1 else 0.0
        dp[i] = (rhs[i] - lower[i] * dp[i - 1]) / den
    out = np.zeros(m)
    out[-1] = dp[-1]
    for i in range(m - 2, -1, -1):
        out[i] = dp[i] - cp[i] * out[i + 1]
    return out


def natural_spline(xk, yk, xq):
    """自然三次样条插值（端点二阶导为 0），用于 EMD 上下包络。"""
    xk = np.asarray(xk, float)
    yk = np.asarray(yk, float)
    xq = np.asarray(xq, float)
    m = len(xk)
    if m < 3:
        return np.interp(xq, xk, yk)
    h = np.diff(xk)
    diag = np.zeros(m)
    lower = np.zeros(m)
    upper = np.zeros(m)
    rhs = np.zeros(m)
    diag[0] = diag[-1] = 1.0
    for i in range(1, m - 1):
        lower[i] = h[i - 1]
        diag[i] = 2 * (h[i - 1] + h[i])
        upper[i] = h[i]
        rhs[i] = 6 * ((yk[i + 1] - yk[i]) / h[i] - (yk[i] - yk[i - 1]) / h[i - 1])
    M = _thomas(lower, diag, upper, rhs)
    j = np.clip(np.searchsorted(xk, xq, side="right") - 1, 0, m - 2)
    hi = h[j]
    a = (xk[j + 1] - xq) / hi
    b = (xq - xk[j]) / hi
    return (a * yk[j] + b * yk[j + 1]
            + ((a ** 3 - a) * M[j] + (b ** 3 - b) * M[j + 1]) * hi ** 2 / 6.0)


def _extrema(x):
    d = np.diff(x)
    imax = np.where((d[:-1] > 0) & (d[1:] <= 0))[0] + 1
    imin = np.where((d[:-1] < 0) & (d[1:] >= 0))[0] + 1
    n = len(x)
    mx = np.concatenate(([0], imax, [n - 1]))
    mn = np.concatenate(([0], imin, [n - 1]))
    return mx, mn


def emd(x, max_imf: int = 5, max_sift: int = 20, sd_stop: float = 0.05):
    """经验模态分解：筛分出 IMF，返回 (imfs, residual)。

    停止准则为连续两次筛分的标准差 SD = sum((h-m)^2)/sum(h^2)。
    """
    r = np.asarray(x, float).copy()
    idx = np.arange(len(r), dtype=float)
    imfs = []
    for _ in range(max_imf):
        h = r.copy()
        mx, mn = _extrema(h)
        if len(mx) < 3 or len(mn) < 3:
            break
        for _ in range(max_sift):
            mx, mn = _extrema(h)
            if len(mx) < 3 or len(mn) < 3:
                break
            upper = natural_spline(mx, h[mx], idx)
            lower = natural_spline(mn, h[mn], idx)
            m = 0.5 * (upper + lower)
            d = h - m
            sd = np.sum(m * m) / (np.sum(h * h) + 1e-12)
            h = d
            if sd < sd_stop:
                break
        imfs.append(h)
        r = r - h
        mx, mn = _extrema(r)
        if len(mx) < 3 or np.sum(r * r) < 1e-8:
            break
    return np.asarray(imfs), r


# ---------------------------------------------------------------- 验证

def verify(fs: int = 8000, x: np.ndarray | None = None) -> dict:
    """全部算法的数值验证表；返回 dict，供讲义/表格使用。"""
    rng = np.random.default_rng(7)
    if x is None:
        x = rng.normal(0, 1, 4000)
    x = np.asarray(x, float)
    xx = x[:1024] if len(x) >= 1024 else np.pad(x, (0, 1024 - len(x)))

    e_dft = np.max(np.abs(dft(xx[:256]) - np.fft.fft(xx[:256])))
    e_fft = np.max(np.abs(fft(xx) - np.fft.fft(xx)))

    fr = frames(xx[:1000], 200, 80)
    S_manual = fft_rows(fr * np.hamming(200)[None, :], 512)[:, :257]
    S_ref = np.fft.rfft(fr * np.hamming(200)[None, :], n=512, axis=1)
    e_stft = np.max(np.abs(S_manual - S_ref))

    sig = rng.normal(0, 1, 4000)
    rec_h = haar_idwt(haar_dwt(sig, 4))
    e_haar = np.sqrt(np.mean((rec_h - sig) ** 2))
    rec_d = db4_idwt(db4_dwt(sig, 3))
    e_db4 = np.sqrt(np.mean((rec_d[:len(sig)] - sig) ** 2))

    # EMD 用一段真实合成声纹的降采样版本，控制耗时
    src = x[:2000] if len(x) >= 2000 else np.pad(x, (0, 2000 - len(x)))
    imfs, res = emd(src, max_imf=5, max_sift=20)
    rec_e = np.sum(imfs, axis=0) + res
    e_emd = np.sqrt(np.mean((rec_e - src) ** 2))
    orth = 0.0
    for i in range(len(imfs)):
        for j in range(i + 1, len(imfs)):
            orth += abs(np.dot(imfs[i], imfs[j])) / (np.sum(src ** 2) + 1e-12)

    # FFT 复杂度实测（次幂长度）
    import time
    t0 = time.perf_counter()
    for _ in range(20):
        fft(rng.normal(0, 1, 2048))
    t_fft = (time.perf_counter() - t0) / 20 * 1000
    t0 = time.perf_counter()
    dft(rng.normal(0, 1, 256))
    t_dft256 = (time.perf_counter() - t0) * 1000

    return {
        "dft_vs_numpy": e_dft,
        "fft_vs_numpy": e_fft,
        "stft_vs_numpy": e_stft,
        "haar_recon_rmse": e_haar,
        "db4_recon_rmse": e_db4,
        "emd_recon_rmse": e_emd,
        "emd_orthogonality": orth,
        "emd_imf_count": len(imfs),
        "fft_2048_ms": t_fft,
        "dft_256_ms": t_dft256,
    }
