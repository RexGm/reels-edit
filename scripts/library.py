#!/usr/bin/env python3
"""Görsel öğe kütüphanesi: üretilen her şeyi sakla, bul, tekrar kullan.

Kütüphane kökü: --root, yoksa $REELS_LIBRARY, yoksa çalışılan klasörden yukarı doğru
aranan ilk `library/index.json` (reels-studio/library).

Komutlar:
  init                                 kütüphane klasörlerini ve index.json'u oluştur
  add <dosya|klasör> --kind K --tags a,b --desc "..." [--name ad] [--source "prompt/tarif/url"]
                     [--license own|ai|licensed:<kaynak>|unknown] [--move]
                                       öğeyi kopyalar (veya taşır), önizleme üretir, kaydeder
                                       Blender çıktı klasörü verilirse meta.json'dan bilgileri alır
  search [kelimeler...] [--kind K] [--tag t]    ad/etiket/açıklamada arar
  list [--kind K]                      hepsini listeler
  show <id>                            tüm kaydı JSON olarak basar
  use <id> <proje_klasörü>             öğeyi projenin assets/library/ klasörüne kopyalar, kullanımı kaydeder
  remove <id>                          kaydı ve dosyaları siler (önce kullanıcıya sor)

Türler (--kind): image, video, alpha-video, 3d-render, blender-scene, svg, lottie,
                 sfx, music, font, template, texture, logo, ai-image, ai-video, other
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

KINDS = ["image", "video", "alpha-video", "3d-render", "blender-scene", "svg", "lottie", "sfx", "music",
         "font", "template", "texture", "logo", "ai-image", "ai-video", "other"]
FOLDER = {"image": "images", "ai-image": "images", "logo": "logos", "texture": "textures", "svg": "svg",
          "video": "video", "ai-video": "video", "alpha-video": "video-alpha", "3d-render": "3d",
          "blender-scene": "blender", "lottie": "lottie", "sfx": "audio/sfx", "music": "audio/music",
          "font": "fonts", "template": "templates", "other": "other"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}


def find_root(arg):
    if arg:
        return Path(arg).expanduser().resolve()
    if os.environ.get("REELS_LIBRARY"):
        return Path(os.environ["REELS_LIBRARY"]).expanduser().resolve()
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "library" / "index.json").exists():
            return d / "library"
        if (d / "index.json").exists() and d.name == "library":
            return d
    sys.exit("Kütüphane bulunamadı. --root ver, REELS_LIBRARY ayarla veya `init` çalıştır.")


def load(root):
    f = root / "index.json"
    return json.loads(f.read_text()) if f.exists() else {"version": 1, "items": []}


def save(root, data):
    tmp = root / "index.json.tmp"
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(root / "index.json")


def slug(s):
    tr = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    s = re.sub(r"[^a-zA-Z0-9_]+", "-", s.translate(tr)).strip("-_").lower()
    return s or "item"


def probe(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
                             capture_output=True, text=True, check=True).stdout
        d = json.loads(out)
        v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
        info = {"duration": round(float(d["format"].get("duration", 0) or 0), 3)}
        if v:
            info.update(width=v.get("width"), height=v.get("height"))
            alpha = v.get("pix_fmt", "").startswith(("yuva", "rgba", "argb", "bgra")) or \
                v.get("tags", {}).get("alpha_mode") == "1" or v.get("tags", {}).get("ALPHA_MODE") == "1"
            info["alpha"] = bool(alpha)
        return info
    except Exception:
        return {}


def make_thumb(src, dst, is_video):
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        if is_video:
            dur = probe(src).get("duration", 0) or 0
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{dur/2:.2f}", "-i", str(src), "-frames:v", "1",
                   "-vf", "scale=320:-2", str(dst)]
        else:
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-frames:v", "1", "-vf", "scale=320:-2", str(dst)]
        subprocess.run(cmd, check=True, capture_output=True)
        return dst
    except Exception:
        return None


def cmd_init(root, _a):
    root.mkdir(parents=True, exist_ok=True)
    for sub in sorted(set(FOLDER.values())) + ["_thumbs"]:
        (root / sub).mkdir(parents=True, exist_ok=True)
    if not (root / "index.json").exists():
        save(root, {"version": 1, "items": []})
    print(f"Kütüphane hazır: {root}")


def cmd_add(root, a):
    src = Path(a.path).expanduser().resolve()
    if not src.exists():
        sys.exit(f"Bulunamadı: {src}")
    data = load(root)
    meta = {}
    if src.is_dir() and (src / "meta.json").exists():  # blender_render.py çıktısı
        meta = json.loads((src / "meta.json").read_text())
    kind = a.kind or ("3d-render" if meta else None)
    if not kind:
        ext = src.suffix.lower()
        kind = "video" if ext in VIDEO_EXT else "image" if ext in IMAGE_EXT else "sfx" if ext in AUDIO_EXT else "other"
        if ext == ".svg":
            kind = "svg"
    if kind not in KINDS:
        sys.exit(f"Geçersiz tür: {kind}. Seçenekler: {', '.join(KINDS)}")
    name = a.name or meta.get("name") or src.stem
    base = slug(name)
    ids = {i["id"] for i in data["items"]}
    item_id, n = base, 2
    while item_id in ids:
        item_id, n = f"{base}-{n}", n + 1

    dest = root / FOLDER[kind] / (item_id if src.is_dir() else f"{item_id}{src.suffix.lower()}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if a.move:
        shutil.move(str(src), dest)
    elif src.is_dir():
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns("frames*") if a.skip_frames else None)
    else:
        shutil.copy2(src, dest)

    # ana dosya: klasörde video > poster > ilk görsel
    main = dest
    if dest.is_dir():
        cands = sorted([p for p in dest.iterdir() if p.suffix.lower() in VIDEO_EXT]) or \
            [p for p in [dest / "poster.png"] if p.exists()] or \
            sorted([p for p in dest.rglob("*") if p.suffix.lower() in IMAGE_EXT])
        main = cands[0] if cands else dest
    is_video = main.suffix.lower() in VIDEO_EXT
    info = probe(main) if (is_video or main.suffix.lower() in IMAGE_EXT | AUDIO_EXT) else {}
    if kind in ("sfx", "music") or main.suffix.lower() in AUDIO_EXT:
        info = {"duration": info.get("duration")}  # mp3 kapak resmi video sanılmasın
    thumb = None
    if main.suffix.lower() in VIDEO_EXT | (IMAGE_EXT - {".svg"}):
        poster = dest / "poster.png" if dest.is_dir() and (dest / "poster.png").exists() else main
        thumb = make_thumb(poster, root / "_thumbs" / f"{item_id}.jpg", poster.suffix.lower() in VIDEO_EXT)

    rel = lambda p: str(Path(p).relative_to(root)) if p else None
    item = {
        "id": item_id, "name": name, "kind": kind,
        "tags": sorted({t.strip().lower() for t in (a.tags or "").split(",") if t.strip()} |
                       ({meta.get("scene")} if meta.get("scene") else set())),
        "description": a.desc or "",
        "path": rel(dest), "main": rel(main), "thumb": rel(thumb),
        "info": {**info, **({"alpha": True} if meta.get("alpha") else {})},
        "source": a.source or (json.dumps(meta.get("spec"), ensure_ascii=False) if meta else ""),
        "license": a.license,
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "used_in": [],
    }
    data["items"].append(item)
    save(root, data)
    print(json.dumps(item, indent=2, ensure_ascii=False))


def match(item, words, kind, tag):
    if kind and item["kind"] != kind:
        return False
    if tag and tag.lower() not in item["tags"]:
        return False
    hay = " ".join([item["id"], item["name"], item["description"], " ".join(item["tags"]), item["kind"]]).lower()
    return all(w.lower() in hay for w in words)


def show_rows(items):
    if not items:
        print("(sonuç yok)")
        return
    for i in items:
        dims = i.get("info", {})
        size = f"{dims.get('width')}x{dims.get('height')}" if dims.get("width") else ""
        dur = f"{dims.get('duration')}s" if dims.get("duration") else ""
        alpha = "alfa" if dims.get("alpha") else ""
        print(f"{i['id']:<32} {i['kind']:<12} {size:<10} {dur:<8} {alpha:<5} [{', '.join(i['tags'])}] {i['description'][:60]}")


def cmd_search(root, a):
    data = load(root)
    show_rows([i for i in data["items"] if match(i, a.words, a.kind, a.tag)])


def cmd_list(root, a):
    data = load(root)
    show_rows([i for i in data["items"] if not a.kind or i["kind"] == a.kind])


def get(data, item_id):
    for i in data["items"]:
        if i["id"] == item_id:
            return i
    sys.exit(f"Bulunamadı: {item_id}")


def cmd_show(root, a):
    print(json.dumps(get(load(root), a.id), indent=2, ensure_ascii=False))


def cmd_use(root, a):
    data = load(root)
    item = get(data, a.id)
    proj = Path(a.project).expanduser().resolve()
    target_dir = proj / "assets" / "library"
    target_dir.mkdir(parents=True, exist_ok=True)
    src = root / item["path"]
    dst = target_dir / Path(item["path"]).name
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("frames*"))
        main = dst / Path(item["main"]).name if item.get("main") else dst
    else:
        shutil.copy2(src, dst)
        main = dst
    if str(proj) not in item["used_in"]:
        item["used_in"].append(str(proj))
    save(root, data)
    print(str(main.relative_to(proj)))  # kompozisyonda kullanılacak root-relative yol


def cmd_remove(root, a):
    data = load(root)
    item = get(data, a.id)
    p = root / item["path"]
    if p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
    elif p.exists():
        p.unlink()
    if item.get("thumb") and (root / item["thumb"]).exists():
        (root / item["thumb"]).unlink()
    data["items"] = [i for i in data["items"] if i["id"] != a.id]
    save(root, data)
    print(f"Silindi: {a.id}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p = sub.add_parser("add")
    p.add_argument("path")
    p.add_argument("--kind", choices=KINDS)
    p.add_argument("--tags", default="")
    p.add_argument("--desc", default="")
    p.add_argument("--name")
    p.add_argument("--source")
    p.add_argument("--license", default="own")
    p.add_argument("--move", action="store_true")
    p.add_argument("--skip-frames", action="store_true", help="Blender PNG karelerini kopyalama (sadece video + poster)")
    p = sub.add_parser("search")
    p.add_argument("words", nargs="*")
    p.add_argument("--kind")
    p.add_argument("--tag")
    p = sub.add_parser("list")
    p.add_argument("--kind")
    p = sub.add_parser("show")
    p.add_argument("id")
    p = sub.add_parser("use")
    p.add_argument("id")
    p.add_argument("project")
    p = sub.add_parser("remove")
    p.add_argument("id")
    a = ap.parse_args()

    if a.cmd == "init":
        root = Path(a.root).expanduser().resolve() if a.root else Path.cwd() / "library"
        return cmd_init(root, a)
    root = find_root(a.root)
    {"add": cmd_add, "search": cmd_search, "list": cmd_list, "show": cmd_show,
     "use": cmd_use, "remove": cmd_remove}[a.cmd](root, a)


if __name__ == "__main__":
    main()
