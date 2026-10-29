# MG stilleri ve kodla ses (mg-styles-15)

Kaynak: github.com/Vincentwei1021/mg-styles-15 (MIT). Claude Opus 5.5'in koddan ürettiği 15 motion design stili: her birinin 10 sn filmi, tam prompt'u ve kaynak kodu; HTML→MP4 render aracı; kodla müzik/efekt sentezleyen **mgaudio** (103 CC0 enstrüman örneği).

Kurulum (isteğe bağlı; repodaki `bash kur.sh --muzik` hepsini yapar):
- Depo: `$REELS_STUDIO/references/mg-styles-15` — `git pull` ile güncellenir. Bitmiş filmler `videos/`, prompt'lar `prompts/`, kaynak `demos/<ad>/`.
- Python ortamı: `~/.local/opt/mg-venv/bin/python` (numpy, scipy, soundfile, numba, pedalboard, pyloudnorm, librosa, matplotlib). Depodaki sabit sürümler kurulmazsa (ör. Intel Mac) sürümsüz kurulum da çalışır; sesler bit düzeyinde biraz farklı olabilir. Yol `MG_STYLES` ortam değişkeniyle değiştirilebilir.
- Demo filmleri yeniden render etmek için depoda `npm install` ve Chrome gerekir; yalnız müzik/efekt için gerekmez.
- Türkçe işlerde depodaki Çince fontlar gerekmez.
- Hız: ilk mgaudio çalıştırması numba derlemesiyle ~1 dk sürer, sonra 30–40 sn'lik müzik ~20 sn.

## 1. Müzik ve efekt: `scripts/mg_music.py` (en çok kullanılacak kısım)

Storyboard anlarına kilitli, telifsiz müzik + efekt. Kütüphanedeki müzikler sakin-umutlu; sert/sinematik/trap ya da kâğıt-damga-kalem gibi efektler gerekiyorsa buradan üret.

```bash
~/.local/opt/mg-venv/bin/python <skill>/scripts/mg_music.py --duration 34.4 --style B \
    --drop 2.1 --outro 31.5 --hits 2.1,9.0,15.2 --cues work/sfx_cues.json -o work/mg
```
- `--drop` kanca/kahraman an, `--outro` CTA anı, `--hits` görsel vuruşlar (BPM bunlara oturur).
- Çıktı: `music.wav` (~-26 LUFS) ve `sfx.wav` (~-28 LUFS) ayrı → HF'de iki `<audio>`; müzik konuşma altında `data-automation` ducking. `mix.wav` (-14 LUFS) kulak kontrolü ya da konuşmasız video için. `spec.png`'ye bak, `mg.json`'da bpm/akorlar.
- Beğenilen müzik `library.py add work/mg/music.wav --kind music --name muzik_mg_<tarif>_<bpm> --license own --source "mg_music.py <parametreler>"`.

| Stil | Tarif (`--style`) | Alternatif (`--recipe`) |
|---|---|---|
| BRAND | `lofi` rhodes chill | `ambient --kw flavor=piano` |
| A Editoryal Yeşil | `lofi` piano chill | `ambient --kw flavor=piano` |
| B Kinetik Kırmızı | `trap` | `glitch_hop`, `darksynth` |
| C Cam Derinlik | `ambient` glass | `explainer` (marimba tech) |
| Kolaj (`photo-collage`) | `lofi` boombap + vinyl | — |
| Eğlenceli/variety | `variety` bouncy | `variety --kw flavor=cute` |
| Retro/VHS, piksel | `synthwave`, `chiptune` | `vaporwave` |

**Efekt listesi** (`work/sfx_cues.json`, `t` = görsel olayın anı):
```json
[{"t": 2.1, "sfx": "sticker_slap", "gain": 2}, {"t": 5.0, "sfx": "pen", "args": ["marker", 0.5]},
 {"t": 8.3, "sfx": "stamp", "args": ["rubber"]}, {"t": 14.5, "sfx": "whoosh", "kw": {"kind": "swoosh"}}]
```

| Efekt (`effects.md`) | mgaudio sesi |
|---|---|
| `shoulder-peek`, `photo-collage` girişi | `sticker_slap`, `paper('slide')` |
| `paper-cutout` tokat, sayfa çevirme | `paper('flip')`, `sticker_peel`, `scissors` |
| `live-markup`, `grease-pencil-sheet` | `pen('marker', dur)` |
| `serif-stamp`, onay mührü | `stamp('rubber'\|'seal')` |
| `prompt-bar`, `screenplay-page` | `typing(n)`, `typewriter` |
| keycaps (`apple-ui-key`) | `click('hard')` |
| `comment-cta`, bildirim | `ui('notify')`, `pop('bubble')`, `ding` |
| `lens-ring`, sayaç | `tick('clock')` |
| `magazine-cover` donma | `shutter('film')` |
| geçiş, `grid-collapse`, `whip-pan` | `whoosh(kind=...)`, `transition('whoosh_hit')` |
| `giant-captions`, `kinetic-hook` | `text_hit('slam'\|'pop')` |
| kanca vuruşu | `impact('cinematic')`, `riser` (t = vuruş) |
| `film-look`, VHS | `vinyl`, `vhs_noise`, `head_switch` |

Tüm liste ve parametreler: `references/mg-styles-15/lib/audio/README.md` (§3 SFX, §2 tarifler).

## 2. Görsel stiller

Her stil için `prompts/<ad>.md` → "Signature features and key techniques" bölümü tarifin özüdür; `demos/<ad>/index.html` çalışan kaynak. Filmler `window.renderAt(t)` ile belirlenimci (HyperFrames gibi).

| Film | Reels'te kullanım | Bizdeki karşılık |
|---|---|---|
| 06 Collage / Cut-out | kesik kâğıt kolaj, kukla animasyonu, sayfa çevirme | `photo-collage`, `paper-cutout` (teknikler oraya işlendi) |
| 18 Variety Captions (9:16) | eğlenceli tepki yazıları, ter damlası/patlama çerçevesi | `variety-caption` |
| 19 Sticker Explainer | açıklama videosu: çıkartma fotoğraflar + dev tuvalde kamera + grafikler | `sticker-explainer` |
| 05 Frame-by-Frame / Line Boil | el çizimi oklar/daireler, smear karesi | `doodle-boil` |
| 12 Aurora & Glass | cam kartlar, aurora zemin | stil C, `liquid-glass` |
| 22 HUD / FUI | teknoloji/yapay zekâ anlatımında tarama, kilitlenme | yeni segment |
| 10 Synthwave / VHS | retro geçiş, VHS bozulması | `film-look` varyantı |
| 08 Shape Morph | rakam/logo dönüşümü | `number-morph` |
| 09 Bauhaus | ritme kilitli geometrik açılış | kanca segmenti |
| 01 Flat Vector, 02 Line Art, 03 Isometric, 07 Liquid, 20 Pixel | açıklama araları, intro/outro | B-roll yerine grafik segment |
| 04 3D Render | yumuşak 3D ürün/ikon | Blender (`blender.md`) |

Kullanım yolları:
1. **Teknik ödünç al (varsayılan):** imza tekniğini HF kompozisyonunda GSAP ile kur; renk/font seçilen stilden.
2. **Segment olarak render:** demo'yu kopyala (`demos/<ad>` → `<proje>/work/mg/<ad>`), metni Türkçe'ye, `DEMO` boyutunu 1080×1920'ye çevir, `node harness/render.mjs <klasör>` (depo kökünden; yollar köke göre). Çıktı MP4 (alfa yok) → HF'de tam ekran clip. Kişinin üstüne bindirme gerekiyorsa yol 3.
3. **HF'ye taşı:** `/remotion-to-hyperframes` skill'i Canvas/Three.js/düz HTML'i kare kare doğrulayarak taşır.
4. **Prompt'tan yeni film:** `prompts/<ad>.md` bloğunu kullan; `Creative seed`'i kendi konumuzla değiştir, `Output`'u 1080×1920 yap, `Signature features`'a dokunma. İnceleme için `rubric.md`.

Kurallar: kaynak kod MIT (kopyala, uyarla); fotoğraflar CC0/PD; Çince yedek fontlu render'ı yayına koyma; demo'lardaki uydurma markaları kendi markamızla değiştir.

## 3. Paylaşılan dokular

Kâğıt dokusu (CC0), washi bant, film greni ve toz katmanları depodaki `assets/` altında (MIT); kullandıklarını `library.py add` ile kütüphaneye kaydet. Depoda `assets/hdri` (CC0) Blender için.


## Örnek kütüphanesi
Klonda VCSL enstrüman örneklerinin hepsi gelmeyebilir. `kur.sh --muzik`, `lib/audio/samples/index.json`'u diskte olan dosyalarla süzer (asıl liste `index.full.json` olarak saklanır); eksik notalar en yakın örnekten perde kaydırılarak çalınır. "Error opening ... .flac" hatası görürsen dizin asıl listeye dönmüştür: `kur.sh --muzik`'i tekrar çalıştır. Tam kütüphane ~0.45 GB (CC0): `tools/vcsl_list.tsv` + `tools/download_vcsl.sh` + `tools/build_samples.py`.
