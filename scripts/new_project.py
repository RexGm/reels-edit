#!/usr/bin/env python3
"""Yeni bir video projesi klasörü açar.

Kullanım:
  python3 new_project.py <kisa-ad> [--studio ~/Movies/reels-studio] [--footage dosya1.mp4 dosya2.mov ...]
                         [--style A|B|C|brand] [--hf]

Oluşturur:  <studio>/projects/<YYYY-MM-DD>_<kisa-ad>/
              media/    ham çekimler (kopyalanır, orijinaller değişmez)
              work/     transkript, kesim listesi, storyboard, maske, takip, karşılaştırma
              output/   renderlar
              project.json
            --hf verilirse: hf/ altında HyperFrames projesi (dikey 1080x1920, transkripsiyonsuz)
Son satırda proje yolunu basar.
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


def slug(s):
    tr = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return re.sub(r"[^a-zA-Z0-9]+", "-", s.translate(tr)).strip("-").lower() or "video"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--studio", default=os.environ.get("REELS_STUDIO", "~/Movies/reels-studio"))
    ap.add_argument("--footage", nargs="*", default=[])
    ap.add_argument("--style", default="brand")
    ap.add_argument("--hf", action="store_true")
    a = ap.parse_args()

    studio = Path(a.studio).expanduser().resolve()
    proj = studio / "projects" / f"{dt.date.today().isoformat()}_{slug(a.name)}"
    for sub in ("media", "work", "output"):
        (proj / sub).mkdir(parents=True, exist_ok=True)
    copied = []
    for f in a.footage:
        src = Path(f).expanduser().resolve()
        dst = proj / "media" / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
        copied.append(f"media/{src.name}")
    meta = {"name": a.name, "created": dt.datetime.now().isoformat(timespec="seconds"),
            "style": a.style, "footage": copied, "status": "yeni"}
    (proj / "project.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    if a.hf:
        # --video verilmez: init HDR kaynağı tonemap etmeden dönüştürür; kurgu input_report.py proxy'leriyle yapılır
        cmd = ["npx", "-y", "hyperframes@latest", "init", "hf", "--non-interactive",
               "--resolution", "portrait", "--skip-transcribe"]
        env = dict(os.environ, HYPERFRAMES_SKIP_SKILLS="1")
        r = subprocess.run(cmd, cwd=proj, env=env)
        if r.returncode:
            print("Uyarı: hyperframes init başarısız; elle çalıştır:", " ".join(cmd))
    print(proj)


if __name__ == "__main__":
    main()
