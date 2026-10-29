#!/usr/bin/env python3
"""Dalgalanan saten kumaş zemini üretir (kolaj stili arka planı). Döngü dikişsizdir.

Kullanım:
    python3 satin_bg.py -o <çıktı.mp4|.png> [--size 1080x1920] [--seconds 10] [--fps 30]
                        [--dark "#8E9196"] [--light "#F4F4F2"] [--speed 1] [--seed 3]

    .png  tek kare (önizleme ya da hareketsiz zemin)
    .mp4  --seconds uzunluğunda döngü; HyperFrames'te <video loop muted> olarak kullan
    --dark/--light  kıvrım dibi ve parlak sırt renkleri (gri saten varsayılan; mavi: #0F3A9E / #4A8DF7)

Kumaş yumuşak olduğu için yarım çözünürlükte hesaplanıp büyütülür.
"""
import argparse
import subprocess
import sys

import numpy as np
from PIL import Image


def hex_rgb(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def field(xx, yy, t, waves, warp):
    # t 0..1 döngü fazı; her terimin döngü sayısı tam sayı -> dikişsiz
    tau = 2 * np.pi
    wx = xx + warp[0] * np.sin(tau * (0.6 * yy + 0.25 * xx) + warp[2] + tau * t)
    wy = yy + warp[1] * np.sin(tau * (0.45 * xx - 0.3 * yy) + warp[3] - tau * t)
    f = np.zeros_like(xx)
    for amp, k, th, ph, n in waves:
        f += amp * np.sin(tau * k * (wx * np.cos(th) + wy * np.sin(th)) + ph + tau * n * t)
    # toplam genliğe bölmek değerleri ortada toplar (gri, mat); std'ye bölünce uçlar (beyaz sırt, gri dip) oluşur
    return np.tanh(f / (1.1 * np.sqrt(sum(w[0] ** 2 for w in waves) / 2)))  # yumuşak sınır: sert kırık yok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--seconds", type=float, default=10)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--dark", default="#8E9094")
    ap.add_argument("--light", default="#FDFDFC")
    ap.add_argument("--speed", type=int, default=1, help="döngü başına dalga turu (1 sakin, 2-3 hareketli)")
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()

    W, H = (int(v) for v in a.size.split("x"))
    w, h = W // 2, H // 2
    rng = np.random.default_rng(a.seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx, yy = xx / w, yy / w  # en boyu koru
    # paralel, hafif eğik yatay kıvrımlar (ekranda 3-4 bant); açılar birbirine yakın, yoksa adacık oluşur
    tilt = rng.uniform(80, 86)
    waves = [(1.0, 1.6, np.radians(tilt), rng.uniform(0, 6.28), a.speed),
             (0.55, 2.4, np.radians(tilt + rng.uniform(-4, 4)), rng.uniform(0, 6.28), -a.speed),
             (0.3, 1.0, np.radians(tilt + rng.uniform(-6, 6)), rng.uniform(0, 6.28), a.speed)]
    warp = (0.03, 0.025, rng.uniform(0, 6.28), rng.uniform(0, 6.28))
    dark, light = hex_rgb(a.dark), hex_rgb(a.light)

    def frame(t):
        f = field(xx, yy, t, waves, warp)
        # saten: yumuşak geçiş, açık alan geniş (gama < 1), sırtlarda hafif parlama
        s = np.clip(0.5 + 0.5 * f, 0, 1)
        lum = 0.92 * s ** 0.5 + 0.08 * np.exp(-((s - 0.9) / 0.08) ** 2)
        lum = np.clip(lum + rng.normal(0, 0.004, lum.shape), 0, 1)  # bantlaşmaya karşı titreme
        return (dark + (light - dark) * lum[..., None]).clip(0, 255).astype(np.uint8)

    if a.output.lower().endswith(".png"):
        Image.fromarray(frame(0.0)).resize((W, H), Image.BICUBIC).save(a.output)
        print(a.output)
        return

    n = round(a.seconds * a.fps)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                           "-r", str(a.fps), "-i", "-", "-vf", f"scale={W}:{H}:flags=bicubic",
                           "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", a.output], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(frame(i / n).tobytes())
    ff.stdin.close()
    if ff.wait():
        sys.exit("ffmpeg başarısız")
    print(a.output)


if __name__ == "__main__":
    main()
