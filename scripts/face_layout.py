#!/usr/bin/env python3
"""Kişi maskesinden (fg.webm, alfa) yerleşim ölçümü: kafa üstü, yüz x aralığı, omuz çizgisi.

Kartları, dev kelimeleri ve altyazıyı tahminle değil ölçümle yerleştirmek için.
Örnek: kafa üstü 600 diye varsayılan bir çekimde gerçek değer bölüme göre 550–715 çıktı,
yüz bazı bölümlerde x 500–960'a kaydı; sağ sütundaki kartlar yüze biniyordu.

Kullanım:
  python3 face_layout.py hf/assets/video/fg.webm -o work/layout.json \
      [--every 0.5] [--edl work/edl.json] [--zoom 1.18] [--origin-y 1000]

--edl verilirse her kurgu parçası için özet basılır (parçalar in/out kaynak süreleriyle art arda dizilir). --zoom ile kamera yakınlaşınca kafa üstü/çene nereye gider, onu da yazar
(dönüş noktası x = yüz merkezi, y = --origin-y).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    return s["width"], s["height"], float(d["format"]["duration"])


def alpha_frames(path, every, w, h, sw=270):
    """Alfa kanalını küçük ölçekte (sw genişlik) akıtır; VP9 alfa için libvpx-vp9 çözücü şart."""
    sh = round(h * sw / w)
    cmd = ["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", path, "-vf",
           f"fps=1/{every},alphaextract,scale={sw}:{sh}", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = sw * sh
    k = 0
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield k * every, np.frombuffer(buf, np.uint8).reshape(sh, sw), w / sw
        k += 1
    p.wait()


def measure(a, f):
    m = a > 127
    rows = np.where(m.sum(1) > 2)[0]
    if not len(rows):
        return None
    top = rows[0]

    def span(y):
        y = min(y, m.shape[0] - 1)
        c = np.where(m[y])[0]
        return (int(c[0] * f), int(c[-1] * f)) if len(c) else None

    head = span(top + round(120 / f)) or span(top + 5)
    face = span(top + round(250 / f)) or head
    hw = (head[1] - head[0]) if head else 0
    shoulder = None
    for y in range(top + round(150 / f), m.shape[0]):
        s = span(y)
        if s and hw and (s[1] - s[0]) > 1.7 * hw:
            shoulder = int(y * f)
            break
    return {"head_top": int(top * f), "head_x": head, "face_x": face, "shoulder": shoulder}


def segments(edl):
    d = json.loads(Path(edl).read_text())
    segs = d.get("segments", d) if isinstance(d, dict) else d
    out, t = [], 0.0
    for s in segs:
        # kaynak giriş/çıkışı (in/out ya da start/end) → çıkış zaman çizelgesinde art arda
        dur = s.get("dur") or (s["out"] - s["in"] if "in" in s else s["end"] - s["start"])
        out.append((s.get("id", "?"), t, t + dur))
        t += dur
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fg")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--edl")
    ap.add_argument("--zoom", type=float, default=1.0)
    ap.add_argument("--origin-y", type=float, default=1000)
    a = ap.parse_args()
    w, h, dur = probe(a.fg)
    samples = []
    for t, fr, f in alpha_frames(a.fg, a.every, w, h):
        r = measure(fr, f)
        if r:
            r["t"] = round(t, 2)
            samples.append(r)
    Path(a.out).write_text(json.dumps({"width": w, "height": h, "samples": samples}, indent=1))
    print(f"{a.out}: {len(samples)} örnek, {w}x{h}, {dur:.1f} sn")
    groups = segments(a.edl) if a.edl else [("tümü", 0, dur)]
    print(f"{'parça':8} {'zaman':>13}  kafa üstü     yüz x         omuz   | zoom {a.zoom}: kafa üstü")
    for sid, s0, s1 in groups:
        r = [x for x in samples if s0 <= x["t"] < s1]
        if not r:
            continue
        ht = [x["head_top"] for x in r]
        fl = [x["face_x"][0] for x in r if x["face_x"]]
        fr = [x["face_x"][1] for x in r if x["face_x"]]
        sh = [x["shoulder"] for x in r if x["shoulder"]]
        cx = (np.median(fl) + np.median(fr)) / 2 if fl else w / 2
        zt = a.origin_y - (a.origin_y - min(ht)) * a.zoom
        print(f"{sid:8} {s0:6.2f}–{s1:6.2f}  {min(ht):4}–{max(ht):4}   {min(fl) if fl else '-':>4}–{max(fr) if fr else '-':<4} "
              f"(orta {cx:4.0f})  {int(np.median(sh)) if sh else '-':>5}  | {zt:5.0f}")
    print("Kart bölgeleri: yüzün solu/sağı (yüz x dışı), kafa üstü ile güvenli üst bant (220) arası duvar;"
          " altyazı çenenin altında, alt 420 px'in üstünde. Yakınlaşmada dönüş noktasını yüz merkezine koy.")


if __name__ == "__main__":
    sys.exit(main())
