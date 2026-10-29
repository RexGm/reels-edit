#!/usr/bin/env python3
"""Videoda bir bölgeyi (avuç, yüz, ekran köşesi, nesne) kare kare takip eder.

Kullanım:
  python3 track_point.py <video> --at 12.4 --box 0.62,0.48,0.10,0.08 [--end 15.0] [--step 1]
                         [--smooth 5] [--comp 1080x1920] [-o work/track_palm.json]

  --box   x,y,genişlik,yükseklik. 0-1 arası değerler kareye oranlıdır, büyükse piksel.
          Kutu, takip edilecek şeyin --at anındaki konumudur: önce o kareyi
          `ffmpeg -ss 12.4 -i video -frames:v 1 kare.png` ile çıkar, bak, kutuyu belirle.
  --comp  kompozisyon boyutu (video kareyi tam kaplıyorsa); çıktıya px koordinatları ekler.

Çıktı JSON: {fps, width, height, points:[{t, cx, cy, w, h, ok, px, py}]}
  t: saniye (videonun kendi zamanı), cx/cy: merkez (0-1), px/py: kompozisyon pikseli.
  GSAP'e aktarmak için: her nokta bir keyframe (`tl.to(el, {x, y, duration: dt, ease:"none"}, t)`).

Gerekli: pip install opencv-contrib-python-headless numpy
"""
import argparse
import json
import sys


def make_tracker(cv2):
    for name in ("TrackerCSRT_create", "TrackerKCF_create"):
        if hasattr(cv2, name):
            return getattr(cv2, name)()
        legacy = getattr(cv2, "legacy", None)
        if legacy is not None and hasattr(legacy, name):
            return getattr(legacy, name)()
    if hasattr(cv2, "TrackerMIL_create"):
        return cv2.TrackerMIL_create()
    sys.exit("OpenCV takipçisi yok: pip install opencv-contrib-python-headless")


def smooth(values, n):
    if n <= 1:
        return values
    out, half = [], n // 2
    for i in range(len(values)):
        win = values[max(0, i - half): i + half + 1]
        out.append(sum(win) / len(win))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--at", type=float, required=True)
    ap.add_argument("--box", required=True)
    ap.add_argument("--end", type=float)
    ap.add_argument("--step", type=int, default=1)
    ap.add_argument("--smooth", type=int, default=5)
    ap.add_argument("--comp", default="")
    ap.add_argument("--max-jump", type=float, default=0.12,
                    help="bir karede merkez bu orandan fazla sıçrarsa kesme say ve dur (0 = kapalı)")
    ap.add_argument("-o", "--output", default="track.json")
    a = ap.parse_args()

    try:
        import cv2
    except ImportError:
        sys.exit("pip install opencv-contrib-python-headless numpy")

    cap = cv2.VideoCapture(a.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.set(cv2.CAP_PROP_POS_MSEC, a.at * 1000)
    ok, frame = cap.read()
    if not ok:
        sys.exit("Başlangıç karesi okunamadı")
    x, y, w, h = [float(v) for v in a.box.split(",")]
    if max(x, y, w, h) <= 1.0:
        x, y, w, h = x * W, y * H, w * W, h * H
    tracker = make_tracker(cv2)
    tracker.init(frame, (int(x), int(y), int(w), int(h)))

    pts = [{"t": round(a.at, 4), "x": x, "y": y, "w": w, "h": h, "ok": True}]
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        idx += 1
        t = a.at + idx / fps
        if a.end and t > a.end:
            break
        found, box = tracker.update(frame)
        if idx % a.step:
            continue
        if found and a.max_jump:
            pcx, pcy = pts[-1]["x"] + pts[-1]["w"] / 2, pts[-1]["y"] + pts[-1]["h"] / 2
            ncx, ncy = box[0] + box[2] / 2, box[1] + box[3] / 2
            if abs(ncx - pcx) / W > a.max_jump or abs(ncy - pcy) / H > a.max_jump:
                print(f"{t:.2f}s: ani sıçrama (muhtemelen kesme), takip burada bitti")
                break
        if found:
            bx, by, bw, bh = box
            pts.append({"t": round(t, 4), "x": bx, "y": by, "w": bw, "h": bh, "ok": True})
        else:  # kaybolursa son konumu koru, işaretle
            last = dict(pts[-1])
            last.update(t=round(t, 4), ok=False)
            pts.append(last)

    cxs = smooth([(p["x"] + p["w"] / 2) / W for p in pts], a.smooth)
    cys = smooth([(p["y"] + p["h"] / 2) / H for p in pts], a.smooth)
    cw = ch = None
    if a.comp:
        cw, ch = [int(v) for v in a.comp.lower().split("x")]
        # video kompozisyonu "cover" ile dolduruyor varsayımı
        scale = max(cw / W, ch / H)
        offx, offy = (cw - W * scale) / 2, (ch - H * scale) / 2
    out = []
    for p, cx, cy in zip(pts, cxs, cys):
        row = {"t": p["t"], "cx": round(cx, 5), "cy": round(cy, 5),
               "w": round(p["w"] / W, 5), "h": round(p["h"] / H, 5), "ok": p["ok"]}
        if cw:
            row["px"] = round(cx * W * scale + offx, 1)
            row["py"] = round(cy * H * scale + offy, 1)
        out.append(row)
    lost = sum(1 for r in out if not r["ok"])
    with open(a.output, "w") as f:
        json.dump({"video": a.video, "fps": fps, "width": W, "height": H, "comp": a.comp or None,
                   "lost_frames": lost, "points": out}, f, indent=1)
    print(f"{a.output}: {len(out)} nokta, kayıp {lost}")
    if lost > len(out) * 0.1:
        print("Uyarı: takip %10'dan fazla kayboldu; kutuyu küçült/netleştir veya aralığı böl.")


if __name__ == "__main__":
    main()
