#!/usr/bin/env python3
"""Girdi raporu: ham çekimleri ölçer, stil seçimi (SKILL.md 1.3) için kanıt toplar.

Kullanım:
  python3 input_report.py <klip|klasör> [...] -o <proje>/work/input [--proxies <proje>/work/sdr] [--no-headroom]

Üretir (-o klasöründe):
  report.md / report.json  klip başına süre, çözünürlük (döndürme sonrası), fps, HDR, ses (LUFS),
                           üst bant parlaklığı, kamera hareketi, kafa üstü konumu; altta stil uyum notları
  sheet_NN.jpg             her klipten saniyede 2 kare, etiketli kontak sayfası (Pillow ile; drawtext gerekmez)
--proxies: her klip için 1080x1920 / 30 fps / SDR H.264 proxy. HDR (HLG/PQ) kaynak macOS'ta VideoToolbox ile
           doğru tonemap edilir (naif dönüşüm soluk ve gri çıkar). Varolan proxy tekrar üretilmez.
           Ölçümler proxy varsa ondan yapılır.
Kafa üstü: her klibin orta karesinde `npx hyperframes remove-background` ile kişi maskesi (klip başı birkaç sn).

Gerekli: ffmpeg/ffprobe, Pillow, numpy. Kafa ölçümü için HyperFrames CLI.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

VIDEO_EXT = {".mov", ".mp4", ".m4v", ".mkv", ".webm"}
FONT = next((p for p in ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
                         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"] if Path(p).exists()), None)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def probe(f):
    d = json.loads(run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(f)]).stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    rot = rot or int(v.get("tags", {}).get("rotate", 0) or 0)
    w, h = v["width"], v["height"]
    if abs(rot) % 180 == 90:
        w, h = h, w
    num, den = (v.get("avg_frame_rate") or v.get("r_frame_rate") or "30/1").split("/")
    return {"duration": round(float(d["format"]["duration"]), 3), "width": w, "height": h, "rotation": rot,
            "fps": round(float(num) / float(den or 1), 2), "codec": v.get("codec_name"),
            "transfer": v.get("color_transfer", ""), "hdr": v.get("color_transfer") in ("arib-std-b67", "smpte2084"),
            "audio": any(s["codec_type"] == "audio" for s in d["streams"])}


def make_proxy(f, info, out):
    if out.exists():
        return out, "var"
    if abs(info["width"] / info["height"] - 9 / 16) > 0.02:
        return None, "9:16 değil, proxy üretilmedi (kendiliğinden kırpılmaz)"
    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-g", "15", "-keyint_min", "15", "-sc_threshold", "0",
           "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart"]
    if info["hdr"] and sys.platform == "darwin":
        rot = info["rotation"]
        sw, sh = (1920, 1080) if abs(rot) % 180 == 90 else (1080, 1920)
        tr = {-90: ",transpose_vt=dir=clock", 270: ",transpose_vt=dir=clock", 90: ",transpose_vt=dir=cclock",
              -270: ",transpose_vt=dir=cclock"}.get(rot, "")
        flip = ",hflip,vflip" if abs(rot) == 180 else ""
        vf = (f"scale_vt=w={sw}:h={sh}:color_matrix=bt709:color_primaries=bt709:color_transfer=bt709{tr},"
              f"hwdownload,format=p010le{flip},fps=30,format=yuv420p")
        r = run(["ffmpeg", "-v", "error", "-y", "-noautorotate", "-hwaccel", "videotoolbox", "-hwaccel_output_format",
                 "videotoolbox_vld", "-i", str(f), "-vf", vf, *enc, str(out)])
        if r.returncode == 0:
            return out, "HDR→SDR (VideoToolbox tonemap)"
        note = "VideoToolbox başarısız, tonemap'siz dönüştürüldü (renkler soluk olabilir): " + r.stderr[-200:]
    else:
        note = "HDR ama macOS değil: tonemap'siz (zscale/libplacebo ile yeniden dene)" if info["hdr"] else "SDR"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-vf", "scale=1080:1920,fps=30", *enc, str(out)])
    return out, note


def frames(f, fps=4, w=108):
    info = probe(f)
    h = int(round(w * info["height"] / info["width"] / 2) * 2)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.uint8)
    n = len(a) // (w * h * 3)
    return a[: n * w * h * 3].reshape(n, h, w, 3).astype(np.float32)


def lufs(f):
    r = run(["ffmpeg", "-hide_banner", "-i", str(f), "-vn", "-af", "ebur128", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else None


def headroom(f, dur, tmp):
    """Kafanın üst kenarı (karenin %'si) ve kişinin kaplama oranı: %25/%50/%75 karelerinden, tek maske çağrısıyla.
    Kişinin az göründüğü kareler (B-roll, kamera dönüşü) hesaba katılmaz."""
    tiles = []
    for k, p in enumerate((0.25, 0.5, 0.75)):
        t = Path(tmp) / f"t{k}.png"
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{dur * p:.2f}", "-i", str(f), "-frames:v", "1", "-vf", "scale=360:-2", str(t)])
        if t.exists():
            tiles.append(Image.open(t).convert("RGB"))
    if not tiles:
        return None, None
    w, h = tiles[0].size
    strip, cut = Path(tmp) / "strip.png", Path(tmp) / "strip_cut.png"
    im = Image.new("RGB", (w * len(tiles), h))
    for k, t in enumerate(tiles):
        im.paste(t.resize((w, h)), (k * w, 0))
    im.save(strip)
    r = run(["npx", "hyperframes", "remove-background", str(strip), "-o", str(cut)])
    if r.returncode or not cut.exists():
        return None, None
    alpha = np.asarray(Image.open(cut).convert("RGBA"))[:, :, 3] > 128
    tops, covers = [], []
    for k in range(len(tiles)):
        a = alpha[:, k * w:(k + 1) * w]
        covers.append(a.mean())
        rows = np.where(a.sum(1) > w * 0.03)[0]
        if a.mean() >= 0.2 and len(rows):
            tops.append(rows[0] / h)
    cover = round(100 * float(np.median(covers)), 1)
    return (round(100 * float(np.median(tops)), 1) if tops else None), cover


def contact_sheets(clips, outdir):
    font = ImageFont.truetype(FONT, 14) if FONT else ImageFont.load_default()
    rows = []
    for c in clips:
        fr = frames(c["measured_from"], fps=2, w=180)
        for k in range(0, len(fr), 10):
            chunk = fr[k:k + 10]
            hh = chunk.shape[1]
            row = Image.new("RGB", (10 * 183, hh), (15, 15, 15))
            for i, im in enumerate(chunk):
                tile = Image.fromarray(im.astype(np.uint8))
                d = ImageDraw.Draw(tile)
                d.rectangle([0, 0, 180, 18], fill=(0, 0, 0))
                d.text((3, 2), f"{c['name']} {(k + i) * 0.5:.1f}s", fill=(255, 220, 0), font=font)
                row.paste(tile, (i * 183, 0))
            rows.append(row)
    paths, per = [], 6
    for s in range(0, len(rows), per):
        group = rows[s:s + per]
        sheet = Image.new("RGB", (max(r.width for r in group), sum(r.height + 4 for r in group)), (40, 40, 40))
        y = 0
        for r in group:
            sheet.paste(r, (0, y))
            y += r.height + 4
        p = outdir / f"sheet_{s // per + 1:02d}.jpg"
        sheet.save(p, quality=82)
        paths.append(p.name)
    return paths


def label(v, cuts, names):
    for c, n in zip(cuts, names):
        if v < c:
            return n
    return names[-1]


def style_fit(clips):
    """Kaba, şeffaf kurallar: son kararı transkriptin tonu ve edit-log ile Claude verir."""
    tot = sum(c["duration"] for c in clips) or 1
    wavg = lambda k: sum((c[k] or 0) * c["duration"] for c in clips if c[k] is not None) / tot
    hr = [c["head_top_pct"] for c in clips if c["head_top_pct"] is not None]
    head = float(np.median(hr)) if hr else None
    luma, motion = wavg("top_luma"), wavg("motion")
    loud = [c["lufs"] for c in clips if c["lufs"] is not None]
    is4k = min(c["width"] for c in clips) >= 2000
    stable, moving = motion < 7, motion >= 14
    dark, bright = luma < 95, luma > 150
    many = len(clips) >= 4
    fit = {}

    def add(style, ok, plus, minus):
        fit.setdefault(style, {"score": 0, "why": []})
        if ok:
            fit[style]["score"] += 1
            fit[style]["why"].append("+ " + plus)
        elif minus:
            fit[style]["why"].append("− " + minus)

    room = head is not None and head >= 28
    add("BRAND", room, f"kafa üstünde boşluk var (%{head}): dev yazı kafanın arkasında okunur",
        f"kafa üstü %{head}: dev yazı kafanın arkasında büyük ölçüde gizlenir, küçük ve yukarıda tutulmalı" if head is not None else "")
    add("BRAND", True, "BRAND paletinin koyu ve açık rengi her zeminde çalışır (dev yazı rengi zemine göre seçilir)", "")
    add("BRAND", not moving, "sakin kurgu bu kamera hareketine uyar", "kamera çok hareketli; sakin editoryal his zorlanır")
    add("A", room, "üstte boşluk: A'nın imzası olan krem dev yazı + kart dizisi oturur", f"kafa üstü %{head}: A'nın üst üçte bir yerleşimi için yer yok" if head is not None else "")
    add("A", dark, "koyu zemin: krem kart ve yazılar öne çıkar",
        "açık zemin: A'nın krem dev yazısı ve kartları zeminde kaybolur" if bright else
        "orta parlaklıkta zemin: A'nın krem yazıları için koyu duvar gerekir")
    add("A", stable, "sabit kadraj (A tripodla çekilmiş, çok açılı)", "elde/hareketli çekim; A sabit kadraj ister")
    add("B", moving or not stable, "hareketli çekim: kinetik yazı ve hızlı kesme sarsıntıyı örter", "")
    add("B", many, f"{len(clips)} ayrı plan/mekân: B'nin yoğun kesme ritmine malzeme", "tek plan: B'nin ritmi için B-roll gerekir")
    add("B", dark, "koyu/sıcak görünüm: B'nin sinematik grade'ine yakın",
        "aydınlık düz ışık: B'nin sinematik koyu görünümü grade ile sınırlı kurulur")
    add("C", stable, "sabit kadraj: 3D kartlar ve dijital zoom için şart", "hareketli çekim: C'nin 3D cam uzayı ve takip zorlaşır")
    add("C", bright, "aydınlık temiz zemin: C'nin cam kartları ve beyaz yazısı",
        "koyu zemin: C'nin aydınlık lüks hissi tutmaz" if dark else
        "orta parlaklık: C'nin aydınlık hissi için daha çok ışık gerekir")
    add("C", is4k and (head or 0) >= 22, "4K ve kişinin etrafında boşluk: dijital zoom ve derinlik kartları", "kişi kareyi dolduruyor ya da 4K değil: C'nin derinlik kartlarına yer az")
    notes = []
    if loud and float(np.median(loud)) < -28:
        notes.append(f"Ses kısık (medyan {np.median(loud):.1f} LUFS): yaka mikrofonu önerilir; kurguda -14 LUFS'e çekilir, gürültü belirginleşebilir.")
    if any(c["hdr"] for c in clips):
        notes.append("HDR (HLG/PQ) kaynak: HyperFrames SDR çalışır, proxy'ler tonemap edilmeli (--proxies).")
    if any(abs(c["width"] / c["height"] - 9 / 16) > 0.02 for c in clips):
        notes.append("9:16 olmayan klip var: kendiliğinden kırpılmaz, kullanıcıya sor.")
    summary = {"head_top_median_pct": head, "top_luma": round(luma, 1), "motion": round(motion, 1),
               "motion_label": label(motion, [7, 14], ["sabit", "hafif", "hareketli"]),
               "background": label(luma, [95, 150], ["koyu", "orta", "açık"]), "clips": len(clips),
               "total_duration": round(tot, 2), "is_4k": is4k}
    return summary, fit, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--proxies")
    ap.add_argument("--no-headroom", action="store_true")
    a = ap.parse_args()
    files = []
    for p in map(Path, a.inputs):
        files += sorted(x for x in p.iterdir() if x.suffix.lower() in VIDEO_EXT) if p.is_dir() else [p]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    clips = []
    with tempfile.TemporaryDirectory() as tmp:
        for f in files:
            info = probe(f)
            c = {"name": f.stem, "file": str(f), **info, "proxy": None, "proxy_note": ""}
            src = f
            if a.proxies:
                Path(a.proxies).mkdir(parents=True, exist_ok=True)
                px, note = make_proxy(f, info, Path(a.proxies) / f"{f.stem}.mp4")
                c["proxy"], c["proxy_note"] = (str(px) if px else None), note
                src = px or f
            c["measured_from"] = str(src)
            fr = frames(src)
            luma = fr[..., 0] * 0.299 + fr[..., 1] * 0.587 + fr[..., 2] * 0.114
            hh = luma.shape[1]
            c["top_luma"] = round(float(luma[:, int(hh * 0.11):int(hh * 0.30)].mean()), 1)
            c["motion"] = round(float(np.abs(np.diff(luma, axis=0)).mean()), 2) if len(luma) > 1 else 0.0
            c["lufs"] = lufs(src) if info["audio"] else None
            c["head_top_pct"], c["person_cover_pct"] = (None, None) if a.no_headroom else headroom(src, info["duration"], tmp)
            clips.append(c)
            print(f"{c['name']}: {c['duration']}s {c['width']}x{c['height']} hdr={c['hdr']} luma={c['top_luma']} "
                  f"hareket={c['motion']} kafa=%{c['head_top_pct']} {c['lufs']} LUFS {c['proxy_note']}", flush=True)
    sheets = contact_sheets(clips, out)
    summary, fit, notes = style_fit(clips)
    (out / "report.json").write_text(json.dumps({"clips": clips, "summary": summary, "style_fit": fit, "notes": notes,
                                                 "sheets": sheets}, indent=1, ensure_ascii=False))
    L = ["# Girdi raporu", "", "| klip | süre | boyut | fps | HDR | ses LUFS | üst bant parlaklığı | hareket | kafa üstü | kişi kaplama | proxy |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in clips:
        L.append(f"| {c['name']} | {c['duration']} | {c['width']}x{c['height']} | {c['fps']} | {'evet' if c['hdr'] else '—'} | "
                 f"{c['lufs']} | {c['top_luma']} | {c['motion']} | {'%' + str(c['head_top_pct']) if c['head_top_pct'] is not None else '?'} | "
                 f"{'%' + str(c['person_cover_pct']) if c['person_cover_pct'] is not None else '?'} | {c['proxy_note']} |")
    L += ["", f"**Özet:** {summary['clips']} klip, {summary['total_duration']} sn · zemin {summary['background']} "
               f"(üst bant {summary['top_luma']}/255) · kamera {summary['motion_label']} ({summary['motion']}) · "
               f"kafa üstü medyan %{summary['head_top_median_pct']} · {'4K' if summary['is_4k'] else '4K değil'}", "",
          "Ölçek: üst bant parlaklığı <95 koyu, >150 açık. Hareket <7 sabit, 7–14 hafif, >14 hareketli. "
          "Kafa üstü: kafanın üst kenarı karenin yüzde kaçında (üst güvenli alan %11.5; dev yazı için ≥%28 rahat).", "",
          "## Stil uyumu (kaba kurallar; tonu transkriptten sen ekle)", ""]
    for s in ("BRAND", "A", "B", "C"):
        f = fit.get(s, {"score": 0, "why": []})
        L.append(f"- **{s}** {f['score']}/3 — " + "; ".join(f["why"]))
    if notes:
        L += ["", "## Notlar", ""] + [f"- {n}" for n in notes]
    L += ["", "Kontak sayfaları: " + ", ".join(sheets)]
    (out / "report.md").write_text("\n".join(L))
    print(out / "report.md")


if __name__ == "__main__":
    main()
