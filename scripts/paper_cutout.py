#!/usr/bin/env python3
"""Bir görseli kolaj parçasına çevirir: arka planı siler, baskı görünümü verir,
isteğe bağlı elle kesilmiş kâğıt kenarı, kâğıt dokusu, kırışık ve yumuşak gölge ekler.

Kullanım:
    python3 paper_cutout.py <görsel> -o <çıktı.png> [--look bw|color|halftone|retro]
                            [--border 0] [--rough 1.0] [--creases 0] [--cut tight|scissor]
                            [--mask ai|detail|both] [--white-bg] [--trim-dark] [--split]
                            [--no-shadow] [--max 1600]

    --look bw        siyah-beyaz fotoğraf baskısı (varsayılan; referans kolaj videoları)
    --look color     renk korunur, yalnız kontrast
    --look halftone  gazete baskısı nokta dokusu (s/b)
    --look retro     eski renkli baskı: soluk mürekkep, sararmış kâğıt, renk kayması, ince nokta, lif dokusu
    --border N       N px kâğıt kenarı (0 = temiz fotoğraf kesimi; 12-24 = kâğıttan kesilmiş)
    --rough          kâğıt kenarının makas düzensizliği (0 = düz, 1 = el kesimi, 2 = kaba)
    --creases N      kâğıtta N katlanma/kırışık izi (retro'da 1-3 iyi durur)
    --cut tight      kesim nesnenin kenarını izler (varsayılan; --border ile çıkartma/sticker görünümü)
    --cut scissor    dergiden makasla kesilmiş: köşeli, sadeleşmiş kesim çizgisi; içinde baskının zemini de kalır.
                     Maske kusurlu olduğunda da sağlam sonuç verir
    --mask ai        yapay zekâ kişi/nesne maskesi (varsayılan; fotoğraflar)
    --mask detail    doku maskesi: düz/gradyan zemin üstündeki ayrıntılı illüstrasyon (ateş, tüy, saç tutamları)
    --mask both      ikisinin birleşimi (maske delik bırakıyorsa)
    --white-bg       beyaz zeminli çizim/gravür: arka plan yapay zekâ yerine kenardan doldurmayla silinir
    --trim-dark      koyu zeminli görsel: kenardaki koyu parıltı/haleyi kırp (kişi fotoğrafında kullanma:
                     siyah saç ve kıyafet kenarını da yer)
    --split          "vs" görseli: iki figürü ayır -> <çıktı>_sol.png, <çıktı>_sag.png (iki ayrı parça yoksa
                     aradaki en karanlık dikey yoldan böler)
    --no-shadow      gölgeyi pişirme (HyperFrames'te CSS drop-shadow ile verilecekse)

Saydam PNG verilirse arka plan silme atlanır. Çıktı kırpılmış, saydam PNG'dir.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

PAPER = np.array([245, 242, 234], np.float32)  # saf beyaz değil: kâğıt
AGED = np.array([238, 228, 205], np.float32)   # retro: sararmış kâğıt
INK = np.array([36, 30, 34], np.float32)       # retro: soluk mürekkep siyahı
LUMA = np.array([0.299, 0.587, 0.114], np.float32)
SEED = 7


def load_rgba(path, white_bg, mask):
    im = Image.open(path)
    rgba = np.asarray(im.convert("RGBA")).astype(np.float32)
    a = rgba[..., 3]
    if (a < 250).mean() > 0.01:
        return rgba, False
    if white_bg:
        return key_white(rgba), False
    if mask == "detail":
        rgba[..., 3] = detail_mask(rgba[..., :3])
        return rgba, False
    ai = remove_bg(path)
    if mask == "both":
        rgba[..., 3] = np.maximum(ai[..., 3], detail_mask(rgba[..., :3]))
        return rgba, False
    return ai, True


def detail_mask(rgb):
    # ayrıntılı çizim/fotoğraf düz ya da yumuşak gradyanlı zeminde: yerel doku yüksek = nesne
    lum = rgb @ LUMA
    mu = cv2.blur(lum, (9, 9))
    sd = np.sqrt(np.maximum(cv2.blur(lum * lum, (9, 9)) - mu * mu, 0))
    sd = cv2.GaussianBlur(sd, (0, 0), max(2.0, min(lum.shape) / 170))
    return np.clip((sd - 6) / 6, 0, 1) * 255


def remove_bg(path):
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "cut.png"
        r = subprocess.run(["npx", "-y", "hyperframes", "remove-background", str(path), "-o", str(out)],
                           capture_output=True, text=True)
        if r.returncode or not out.exists():
            sys.exit("remove-background başarısız:\n" + r.stderr[-1500:])
        return np.asarray(Image.open(out).convert("RGBA")).astype(np.float32)


def key_white(rgba):
    # kenara bağlı açık bölge = zemin; çizginin içindeki beyazlar (ör. kâğıt göz bebeği) korunur
    lum = rgba[..., :3].mean(-1)
    bg = (lum > 235).astype(np.uint8)
    h, w = bg.shape
    ff = np.zeros((h + 2, w + 2), np.uint8)
    fill = bg.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1)]:
        if fill[y, x] == 1:
            cv2.floodFill(fill, ff, (x, y), 2)
    a = np.where(fill == 2, 0, 255).astype(np.float32)
    rgba[..., 3] = cv2.GaussianBlur(a, (0, 0), 0.8)
    return rgba


def trim_dark(rgba):
    # kenar bandındaki koyu pikseller zemindir (parıltı, hale); içerideki koyu alanlar (lacivert forma) korunur
    alpha = rgba[..., 3]
    m = (alpha > 128).astype(np.uint8)
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    lum = rgba[..., :3] @ LUMA
    keep = np.clip((lum - 22) / 40, 0, 1)
    band = np.clip(1 - dist / 30, 0, 1)
    rgba[..., 3] = alpha * (1 - band * (1 - keep))
    return rgba


def clean_alpha(alpha):
    # kâğıttan kesilen parçada kırıntı ve iğne deliği olmaz: küçük adaları at, küçük delikleri doldur
    m = (alpha > 128).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n > 1:
        areas = st[1:, cv2.CC_STAT_AREA]
        keep = np.r_[False, areas >= areas.max() * 0.02]
        m = keep[lab].astype(np.uint8)
    h, w = m.shape
    n, lab, st, _ = cv2.connectedComponentsWithStats(1 - m, connectivity=4)
    x, y, bw, bh, ar = (st[:, i] for i in range(5))
    inner = (x > 0) & (y > 0) & (x + bw < w) & (y + bh < h)
    fill = inner & (ar < m.sum() * 0.04)
    fill[0] = False
    solid = (m > 0) | fill[lab]
    # parça içi tam opak (yarı saydam leke kalmaz), kenar ince yumuşak: kâğıt kesiği keskindir
    return cv2.GaussianBlur(solid.astype(np.float32) * 255, (0, 0), 0.8)


def split_parts(rgba):
    # figürleri doku maskesinden bul (yapay zekâ maskesi ikisini alttan birleştirebilir),
    # sonra her pikseli en yakın figüre ata; iki ayrı figür yoksa dikiş yolu
    m = ((detail_mask(rgba[..., :3]) > 128) & (rgba[..., 3] > 128)).astype(np.uint8)
    m = cv2.erode(m, np.ones((9, 9), np.uint8))  # ince temasları kopar
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n > 2:
        order = np.argsort(st[1:, cv2.CC_STAT_AREA])[::-1][:2] + 1
        if st[order[1], cv2.CC_STAT_AREA] > st[order[0], cv2.CC_STAT_AREA] * 0.25:
            i, j = sorted(order, key=lambda k: cen[k][0])
            di = cv2.distanceTransform((lab != i).astype(np.uint8), cv2.DIST_L2, 5)
            dj = cv2.distanceTransform((lab != j).astype(np.uint8), cv2.DIST_L2, 5)
            parts = []
            for side in (di <= dj, di > dj):
                p = rgba.copy()
                p[..., 3] *= side
                parts.append(p)
            return parts
    return split_seam(rgba)


def split_seam(rgba):
    # orta %40'ta, maske ve parlaklığı en az kesen dikey yol (dinamik programlama)
    h, w = rgba.shape[:2]
    x0, x1 = int(w * 0.3), int(w * 0.7)
    # parlaklık ağırlıklı: maske alttan birleşse de iki figür arasındaki karanlık boşluğu izler
    e = (rgba[:, x0:x1, :3] @ LUMA) / 255 + rgba[:, x0:x1, 3] / 255 * 0.25
    e += 0.5 * ((np.arange(x1 - x0) - (x1 - x0) / 2) / ((x1 - x0) / 2)) ** 2  # ortadan uzaklaşma cezası
    cost = e.copy()
    for r in range(1, h):
        p = cost[r - 1]
        cost[r] += np.minimum(p, np.minimum(np.r_[np.inf, p[:-1]], np.r_[p[1:], np.inf]))
    seam = np.zeros(h, int)
    seam[-1] = int(cost[-1].argmin())
    for r in range(h - 2, -1, -1):
        c = seam[r + 1]
        lo, hi = max(0, c - 1), min(x1 - x0, c + 2)
        seam[r] = lo + int(cost[r, lo:hi].argmin())
    cols = np.arange(w)[None, :]
    left = cols < (seam + x0)[:, None]
    parts = []
    for side in (left, ~left):
        p = rgba.copy()
        p[..., 3] *= side
        parts.append(p)
    return parts


def crop(rgba, pad):
    ys, xs = np.where(rgba[..., 3] > 8)
    if not len(xs):
        sys.exit("görselde nesne bulunamadı")
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    out = np.zeros((y1 - y0 + 2 * pad, x1 - x0 + 2 * pad, 4), np.float32)
    out[pad:pad + y1 - y0, pad:pad + x1 - x0] = rgba[y0:y1, x0:x1]
    return out


def halftone(g, cell, angle=45):
    # g 0..1 (1 = kâğıt). Döndürülmüş ızgarada karanlığa göre büyüyen noktalar; 1 kâğıt, 0 mürekkep döner
    h, w = g.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    c, s = np.cos(np.radians(angle)), np.sin(np.radians(angle))
    u, v = (xx * c - yy * s) / cell, (xx * s + yy * c) / cell
    d = np.hypot(u - np.round(u), v - np.round(v))
    dark = 1 - cv2.GaussianBlur(g, (0, 0), cell * 0.5)
    return 1 - np.clip((np.sqrt(np.clip(dark, 0, 1)) * 0.72 - d) * cell, 0, 1)


def paper_texture(h, w, rng):
    # kâğıt: geniş lekeler + yatay lifler; çarpan olarak ~0.93-1.03
    low = cv2.resize(rng.normal(0, 1, (max(2, h // 90), max(2, w // 90))).astype(np.float32), (w, h),
                     interpolation=cv2.INTER_CUBIC)
    fib = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sigmaX=2.5, sigmaY=1.2)
    fine = rng.normal(0, 1, (h, w)).astype(np.float32)
    return 1 + low * 0.018 + fib / (fib.std() + 1e-6) * 0.006 + fine * 0.008


def creases(h, w, n, rng):
    # katlanma izi: çizginin bir yanı aydınlık, öbür yanı gölge
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = np.ones((h, w), np.float32)
    for _ in range(n):
        th = rng.uniform(0, np.pi)
        px, py = rng.uniform(0.25, 0.75) * w, rng.uniform(0.25, 0.75) * h
        d = (xx - px) * np.cos(th) + (yy - py) * np.sin(th)
        out *= 1 + 0.07 * np.exp(-((d - 2.5) / 2.2) ** 2) - 0.09 * np.exp(-((d + 2) / 2.8) ** 2) \
            - 0.02 * np.tanh(d / 60)
    return out


def look(rgb, alpha, mode, rng):
    m = alpha > 128
    if mode == "color":
        lo, hi = np.percentile(rgb[m], [1, 99]) if m.any() else (0, 255)
        return np.clip((rgb - lo) / max(hi - lo, 1) * 255, 0, 255)
    h, w = alpha.shape
    cell = max(4, round(min(h, w) / 180))
    if mode == "retro":
        x = rgb / 255
        g = x @ LUMA
        x = g[..., None] + (x - g[..., None]) * 0.78  # renkler biraz solar
        lo, hi = np.percentile(g[m], [1, 99.5]) if m.any() else (0, 1)
        x = np.clip((x - lo) / max(hi - lo, 1e-3), 0, 1)
        x = x * x * (3 - 2 * x) * 0.35 + x * 0.65
        x = x * (0.8 + 0.2 * halftone(x @ LUMA, max(3, cell - 1), 15))[..., None]  # ince baskı noktası
        out = INK + (AGED - INK) * x  # siyahlar mürekkep, beyazlar sararmış kâğıt
        k = max(1, round(min(h, w) / 450))  # baskı kayması: kırmızı ve mavi kalıp hafif kaymış
        out[..., 0] = np.roll(out[..., 0], (k, k), (0, 1))
        out[..., 2] = np.roll(out[..., 2], (-k, -k), (0, 1))
        out *= paper_texture(h, w, rng)[..., None]
        return np.clip(out + rng.normal(0, 4, out.shape), 0, 255)
    g = rgb @ LUMA
    lo, hi = np.percentile(g[m], [1.5, 99.5]) if m.any() else (0, 255)
    g = np.clip((g - lo) / max(hi - lo, 1), 0, 1)
    g = g * g * (3 - 2 * g) * 0.55 + g * 0.45  # yumuşak S eğrisi: baskı kontrastı
    if mode == "halftone":
        g = 1 - (1 - halftone(g, cell)) * 0.92
    g = g * 255 + rng.normal(0, 5, g.shape)  # film greni
    g = np.clip(g, 0, 255)
    return np.repeat(g[..., None], 3, -1)


def paper_mask(alpha, border, rough, rng):
    base = (alpha > 128).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * border + 1, 2 * border + 1))
    # makas ince girintilere giremez: önce kapat (boşlukları doldur), sonra genişlet
    big = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4 * border + 1, 4 * border + 1))
    closed = cv2.morphologyEx(base, cv2.MORPH_CLOSE, big)
    m = cv2.GaussianBlur(cv2.dilate(closed, k).astype(np.float32), (0, 0), border / 3)
    h, w = m.shape
    noise = np.zeros_like(m)
    for scale, amp in [(border * 3, 0.6), (border, 0.4)]:  # makas: uzun düz kesimler + küçük sapmalar
        sm = rng.normal(0, 1, (max(2, h // scale), max(2, w // scale))).astype(np.float32)
        noise += cv2.resize(sm, (w, h), interpolation=cv2.INTER_CUBIC) * amp
    m = m + noise * 0.12 * rough
    m = (m > 0.5).astype(np.float32)
    m = np.maximum(m, base.astype(np.float32))  # kâğıt nesnenin içine girmez
    return cv2.GaussianBlur(m * 255, (0, 0), 0.7)


def scissor_mask(alpha, margin):
    # makas: boşlukları kapat, payı bırak, kenarı kısa düz kesimlere indir (köşeli çokgen)
    base = (alpha > 128).astype(np.uint8)
    r = max(3, margin * 2)
    m = cv2.morphologyEx(base, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1,) * 2))
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * margin + 1,) * 2))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    up = 4  # kenar yumuşatma için 4 kat çizip küçült
    h, w = m.shape
    big = np.zeros((h * up, w * up), np.uint8)
    for c in cs:
        poly = cv2.approxPolyDP(c, 0.0035 * cv2.arcLength(c, True), True)
        cv2.fillPoly(big, [poly * up], 255)
    return cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32)


def render(rgba, ai_mask, a, rng):
    sh = 0 if a.no_shadow else 40
    rgba = crop(rgba, a.border * 2 + sh + 4)
    h, w = rgba.shape[:2]
    if max(h, w) > a.max:
        f = a.max / max(h, w)
        rgba = cv2.resize(rgba, (round(w * f), round(h * f)), interpolation=cv2.INTER_AREA)
        h, w = rgba.shape[:2]

    alpha = rgba[..., 3]
    if ai_mask:  # yapay zekâ maskesi kenarda zemin rengi bırakır; ince çizgili çizimde aşındırma çizgiyi siler
        alpha = cv2.GaussianBlur(cv2.erode(alpha, np.ones((3, 3), np.uint8), iterations=2), (0, 0), 0.6)
    if a.cut == "scissor":
        alpha = scissor_mask(alpha, max(a.border, 10))
    rgb = look(rgba[..., :3], alpha, a.look, rng)

    if a.border > 0 and a.cut == "tight":
        pm = paper_mask(alpha, a.border, a.rough, rng)
        tex = (AGED if a.look == "retro" else PAPER) * paper_texture(h, w, rng)[..., None]
        t = (alpha / 255)[..., None]
        rgb = rgb * t + tex * (1 - t)
        alpha = np.maximum(alpha, pm)
    if a.creases:
        rgb = rgb * creases(h, w, a.creases, rng)[..., None]

    out = np.dstack([rgb, alpha])
    if sh:
        # yumuşak gölge: aşağı kaymış, bulanık, %32
        sa = cv2.GaussianBlur(alpha, (0, 0), 14)
        sa = np.roll(sa, 18, axis=0) * 0.32
        top = alpha / 255
        a_out = alpha + sa * (1 - top)
        col = (rgb * alpha[..., None] + 25 * (sa * (1 - top))[..., None]) / np.maximum(a_out, 1e-3)[..., None]
        out = np.dstack([col, a_out])
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--look", choices=["bw", "color", "halftone", "retro"], default="bw")
    ap.add_argument("--border", type=int, default=0)
    ap.add_argument("--rough", type=float, default=1.0)
    ap.add_argument("--creases", type=int, default=0)
    ap.add_argument("--cut", choices=["tight", "scissor"], default="tight")
    ap.add_argument("--mask", choices=["ai", "detail", "both"], default="ai")
    ap.add_argument("--no-shadow", action="store_true")
    ap.add_argument("--white-bg", action="store_true")
    ap.add_argument("--trim-dark", action="store_true")
    ap.add_argument("--split", action="store_true")
    ap.add_argument("--max", type=int, default=1600, help="uzun kenar sınırı (px)")
    a = ap.parse_args()

    rng = np.random.default_rng(SEED)
    rgba, ai_mask = load_rgba(a.image, a.white_bg, a.mask)
    rgba[..., 3] = clean_alpha(rgba[..., 3])  # önce delikleri doldur: yoksa koyu kırpma deliklerin kenarını da yer
    if a.trim_dark:
        rgba = trim_dark(rgba)
        rgba[..., 3] = clean_alpha(rgba[..., 3])

    out = Path(a.output)
    if a.split:
        jobs = [(p, out.with_name(f"{out.stem}_{n}{out.suffix}")) for p, n in zip(split_parts(rgba), ("sol", "sag"))]
    else:
        jobs = [(rgba, out)]
    for part, path in jobs:
        part[..., 3] = clean_alpha(part[..., 3])
        img = render(part, ai_mask, a, rng)
        Image.fromarray(img, "RGBA").save(path)
        print(f"{path}  {img.shape[1]}x{img.shape[0]}")


if __name__ == "__main__":
    main()
