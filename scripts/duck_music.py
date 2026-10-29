#!/usr/bin/env python3
"""Müzik yatağını konuşmanın altına oturtur: konuşma zarfından ducking, hedef seviye, başlangıç kırpma.

ffmpeg sidechaincompress oranı sidechain seviyesine bağlı olduğu için konuşma altında müziği 30+ dB
bastırabiliyor (müzik -49 LUFS'a kadar düşebiliyor). Bu betik sabit ve öngörülebilir bir kısma uygular.
Varsayılan: önce hafif sıkıştırma (lofi/trap davullarında tepe-ortalama farkı yüksek; tepe sınırı seviyeyi
kısıtlıyor), sonra konuşma altında ~-22 LUFS. -27 LUFS telefonda neredeyse duyulmuyor.

Kullanım:
  python3 duck_music.py work/mg/music.wav hf/assets/audio/voice.wav -o hf/assets/music/music.wav \
      [--start 8.0] [--duck 5] [--bed -18] [--no-compress] [--fade-in 0.12] [--fade-out 0.8]

  --start   müziğin videoda başladığı an (sn); hem müzik hem konuşma bu andan itibaren hizalanır,
            çıktı bu andan başlar (HF'de <audio data-start="START">)
  --duck    konuşma varken kısma (dB)
  --bed     müziğin ducking öncesi entegre seviyesi (LUFS); -18 + 5 dB kısma ≈ konuşma altında -22
  --no-compress  ön sıkıştırmayı kapat (acompressor 3:1 + alimiter)
Konuşma algılama: 20 ms RMS, eşik = gürültü tabanı (%30) + 6 dB; atak 60 ms, bırakma 400 ms.
"""
import argparse
import re
import subprocess

import numpy as np

SR = 48000


def load(path, ch):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def lufs_of(x):
    r = subprocess.run(["ffmpeg", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", str(x.shape[1]), "-i", "-",
                        "-af", "ebur128", "-f", "null", "-"], input=x.astype(np.float32).tobytes(), capture_output=True).stderr.decode()
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("music")
    ap.add_argument("voice")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duck", type=float, default=5.0)
    ap.add_argument("--bed", type=float, default=-18.0)
    ap.add_argument("--no-compress", action="store_true")
    ap.add_argument("--fade-in", type=float, default=0.12)
    ap.add_argument("--fade-out", type=float, default=0.8)
    a = ap.parse_args()

    src = a.music
    if not a.no_compress:
        import tempfile
        src = tempfile.mktemp(suffix=".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.music, "-af",
                        "acompressor=threshold=-24dB:ratio=3:attack=8:release=140:makeup=3,alimiter=limit=0.89:attack=4:release=60",
                        src], check=True)
    m = load(src, 2)
    v = load(a.voice, 1)[:, 0]
    n = len(m)
    v = np.pad(v, (0, max(0, n - len(v))))[:n]
    g = 10 ** ((a.bed - lufs_of(m)) / 20)
    hop = int(SR * 0.02)
    rms = np.sqrt(np.add.reduceat(v ** 2, np.arange(0, n, hop)) / hop)
    db = 20 * np.log10(rms + 1e-9)
    act = (db > np.percentile(db[db > -90], 30) + 6).astype(float)
    env, k_att, k_rel = np.zeros_like(act), 1 - np.exp(-0.02 / 0.06), 1 - np.exp(-0.02 / 0.4)
    for i in range(len(act)):
        prev = env[i - 1] if i else 0.0
        env[i] = prev + (k_att if act[i] > prev else k_rel) * (act[i] - prev)
    m *= g * (10 ** (-a.duck * np.repeat(env, hop)[:n] / 20))[:, None]
    out = m[int(a.start * SR):]
    fi, fo = int(a.fade_in * SR), int(a.fade_out * SR)
    if fi:
        out[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo:
        out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    peak = np.abs(out).max()
    if peak > 0.89:
        out *= 0.89 / peak
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s16le", a.out],
                   input=out.astype(np.float32).tobytes(), check=True)
    print(f"{a.out}: {len(out) / SR:.2f} sn, entegre {lufs_of(out):.1f} LUFS, tepe {20 * np.log10(np.abs(out).max() + 1e-9):.1f} dBFS")


if __name__ == "__main__":
    main()
