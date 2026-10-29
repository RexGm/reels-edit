#!/usr/bin/env python3
"""Storyboard anlarına kilitli müzik + efekt üretir (mgaudio, references/mg-styles-15/lib/audio).

mgaudio'nun bağımlılıkları ayrı ortamda; bu script o ortamın Python'uyla çalışır:
    ~/.local/opt/mg-venv/bin/python mg_music.py --duration 34.4 --style B --drop 2.1 --outro 31.5 \\
        [--hits 2.1,9.0,15.2] [--cues work/sfx_cues.json] [--recipe trap] [--kw flavor=chill] -o work/mg

    --style    BRAND | A | B | C | kolaj | variety  -> tarif seçimi (aşağıdaki STYLE tablosu); --recipe ile ez
    --drop     müziğin oturduğu an (kanca ya da kahraman an); bar 0 tam burada başlar
    --outro    kapanış/CTA anı; müzik burada çözülür
    --hits     görsel vuruş anları; BPM bunlara en iyi oturan 8'lik ızgaraya göre seçilir
    --cues     efekt listesi JSON: [{"t": 2.1, "sfx": "paper", "args": ["flip"], "kw": {}, "gain": 0, "pan": 0}]
               sfx adları mgaudio.sfx fonksiyonları (paper, sticker_slap, stamp, pen, typing, whoosh, pop,
               ui, click, tick, impact, riser, shutter ...). t = görsel olayın anı (whoosh'ta geçiş tepesi,
               riser'da vuruş); öne kaydırma hesaplama.
    --kw       tarife ek parametre (keys=piano, flavor=boombap, vinyl=1 ...), birden çok verilebilir

Çıktı (-o klasörü):
    music.wav   yalnız müzik, ~-26 LUFS (konuşmanın altı için doğru seviye; HF'de ducking ile)
    sfx.wav     yalnız efektler, ~-28 LUFS
    mix.wav     müzik + efekt, -14 LUFS (kulak kontrolü ya da konuşmasız video için)
    spec.png    spektrogram (Read ile bak: boşluk, kırpılma)
    mg.json     form (bpm, drop, outro, akorlar) + ölçümler
Lisans: mgaudio MIT, örnekler CC0 (VCSL) -> çıktı bizim; atıf gerekmez.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(os.environ.get("MG_STYLES") or os.path.join(os.environ.get("REELS_STUDIO", "~/Movies/reels-studio"), "references/mg-styles-15")).expanduser()
sys.path.insert(0, str(REPO / "lib" / "audio"))
try:
    import mgaudio  # noqa: F401
    from mgaudio import recipes, sfx
except ImportError as e:
    sys.exit(f"mgaudio yüklenemedi ({e}). ~/.local/opt/mg-venv/bin/python ile çalıştır; depo: {REPO}")

# stil -> (tarif, parametreler); seçim gerekçesi references/mg-styles.md'de
STYLE = {
    "BRAND": ("lofi", {"keys": "rhodes", "flavor": "chill"}),
    "A": ("lofi", {"keys": "piano", "flavor": "chill"}),
    "B": ("trap", {}),
    "C": ("ambient", {"flavor": "glass"}),
    "kolaj": ("lofi", {"keys": "piano", "flavor": "boombap", "vinyl": True}),
    "variety": ("variety", {"flavor": "bouncy"}),
}


def parse_kw(items):
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        if v.lower() in ("1", "true", "yes"):
            v = True
        elif v.lower() in ("0", "false", "no"):
            v = False
        else:
            try:
                v = float(v) if "." in v else int(v)
            except ValueError:
                pass
        out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--style", default="BRAND", choices=list(STYLE))
    ap.add_argument("--recipe")
    ap.add_argument("--drop", type=float)
    ap.add_argument("--build", type=float)
    ap.add_argument("--outro", type=float)
    ap.add_argument("--hits", default="")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--key")
    ap.add_argument("--cues")
    ap.add_argument("--kw", action="append")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()

    name, kw = STYLE[a.style]
    if a.recipe:
        name, kw = a.recipe, {}
    kw = {**kw, **parse_kw(a.kw)}
    for k in ("drop", "build", "outro", "bpm", "key"):
        if getattr(a, k) is not None:
            kw[k] = getattr(a, k)
    if a.hits:
        kw["hits"] = tuple(float(x) for x in a.hits.split(","))
    m = getattr(recipes, name)(duration=a.duration, **kw)

    for c in json.load(open(a.cues)) if a.cues else []:
        s = getattr(sfx, c["sfx"])(*c.get("args", []), **c.get("kw", {}))
        m.sfx(s, at=c["t"], gain=c.get("gain", 0), pan=c.get("pan"))

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        res = m.export(str(out / "mix.wav"), spectrogram=str(out / "spec.png"), stems_dir=td)
        shutil.copy(Path(td) / "group.music.wav", out / "music.wav")
        if (Path(td) / "group.sfx.wav").exists():
            shutil.copy(Path(td) / "group.sfx.wav", out / "sfx.wav")
    f = m.form
    info = {"recipe": name, "params": {k: v for k, v in kw.items() if k != "hits"}, "bpm": f.bpm,
            "drop": f.drop, "outro": f.outro, "duration": res.get("duration"), "mix_lufs": res.get("lufs"),
            "mix_true_peak": res.get("true_peak"), "warnings": res.get("warnings")}
    (out / "mg.json").write_text(json.dumps(info, indent=2, ensure_ascii=False, default=str))
    print(json.dumps(info, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
