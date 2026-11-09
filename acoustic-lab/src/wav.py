"""声纹信号模型 x(t) 与 WAV 读写（仅标准库 wave + numpy）。

信号模型对应综述第 3 节：变压器本体声以磁致伸缩 2*f0 = 100 Hz 为基频，
叠加 50 Hz 漏磁分量；不同故障以调制、谐波结构、瞬态脉冲、宽带噪声来表征。
    x(t) = sum_k A_k sin(2*pi*k*100*t + phi_k) + 0.06 sin(2*pi*50*t) + s_fault(t) + n(t)
    x[n] = x(n*Ts), Ts = 1/fs
"""
from __future__ import annotations
import os
import wave
import numpy as np

FS = 8000
DUR = 0.5
CLASSES = ["正常", "铁芯松动", "直流偏磁", "局部放电", "短路冲击", "风机老化"]
CLASS_COLORS = [(76, 155, 232), (45, 212, 167), (245, 165, 36),
                (242, 109, 109), (167, 139, 250), (136, 148, 164)]


def _harmonic_base(t, rng, jitter=0.0):
    f0 = 50.0 * (1.0 + jitter)
    amps = [1.0, 0.42, 0.20, 0.10, 0.05]
    phases = rng.uniform(0, 2 * np.pi, len(amps))
    x = np.zeros_like(t)
    for k, a in enumerate(amps, 1):
        x += a * np.sin(2 * np.pi * (2 * f0) * k * t + phases[k - 1])
    return 0.55 * x


def synth(label: int, seed: int, fs: int = FS, dur: float = DUR) -> np.ndarray:
    """生成一类工况的一段声纹；返回 [-1,1] 浮点波形。"""
    rng = np.random.default_rng(seed)
    n = int(fs * dur)
    t = np.arange(n, dtype=np.float64) / fs
    x = _harmonic_base(t, rng, rng.normal(0, 0.012))
    x += 0.06 * np.sin(2 * np.pi * 50 * t + rng.uniform(0, 2 * np.pi))

    if label == 1:  # 铁芯松动：50 Hz 幅值调制 + 周期性金属敲击
        x *= 1.0 + 0.45 * np.sin(2 * np.pi * 50 * t + rng.uniform(0, 2 * np.pi))
        period = 0.085 + rng.uniform(-0.008, 0.008)
        for k in range(int(dur / period)):
            c = (k + 0.35) * period + rng.uniform(-0.004, 0.004)
            env = np.exp(-np.maximum(t - c, 0) / 0.0018) * (t >= c)
            x += 0.42 * env * np.sin(2 * np.pi * 780 * (t - c))

    elif label == 2:  # 直流偏磁：奇次谐波抬升 + 波形不对称（削顶）
        for f, a in [(150, 0.32), (250, 0.22), (350, 0.14), (50, 0.20)]:
            x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))
        x = 1.25 * np.tanh(1.7 * x)

    elif label == 3:  # 局部放电：稀疏高频衰减振荡脉冲
        for _ in range(rng.integers(9, 17)):
            c = rng.uniform(0.02, dur - 0.02)
            env = np.exp(-np.maximum(t - c, 0) / 0.0012) * (t >= c)
            f_hi = rng.uniform(2200, 3400)
            x += rng.uniform(0.35, 0.7) * env * np.sin(2 * np.pi * f_hi * (t - c))

    elif label == 4:  # 短路冲击：瞬态宽带冲击 + 低频"沸腾"调制
        c = rng.uniform(0.13, 0.25)
        env = np.exp(-np.abs(t - c) / 0.022)
        x += 0.55 * env * rng.normal(0, 1, n)
        x += 0.35 * env * np.sin(2 * np.pi * 430 * (t - c))
        boil = 1.0 + 0.35 * np.sin(2 * np.pi * 17 * t) * rng.normal(0.8, 0.2)
        x *= boil

    elif label == 5:  # 风机老化：宽带气动噪声抬升 + 转频调制
        x *= 0.75
        mod = 1.0 + 0.55 * np.sin(2 * np.pi * 12 * t + rng.uniform(0, 2 * np.pi))
        x += 0.13 * mod * rng.normal(0, 1, n)
        x += 0.09 * np.sin(2 * np.pi * 24 * t)

    x += 0.035 * rng.normal(0, 1, n)          # 环境底噪
    x *= rng.uniform(0.85, 1.15)              # 通道增益抖动
    x = x / (np.max(np.abs(x)) + 1e-12) * 0.88
    return x


def write_wav(path: str, x: np.ndarray, fs: int = FS):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(fs)
        w.writeframes(pcm.tobytes())
    return path


def read_wav(path: str):
    with wave.open(path, "rb") as w:
        fs = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    return x, fs


def build_dataset(n_per_class: int = 40, seed: int = 2026, fs: int = FS, dur: float = DUR):
    """返回 (signals, labels)；signals 为 list[np.ndarray]。"""
    signals, labels = [], []
    for c in range(len(CLASSES)):
        for i in range(n_per_class):
            signals.append(synth(c, seed + c * 10007 + i * 131, fs, dur))
            labels.append(c)
    return signals, np.asarray(labels, int)


def save_examples(out_dir: str, fs: int = FS):
    paths = []
    for c, name in enumerate(CLASSES):
        p = os.path.join(out_dir, f"{c}_{name}.wav")
        write_wav(p, synth(c, 9000 + c), fs)
        paths.append(p)
    return paths
