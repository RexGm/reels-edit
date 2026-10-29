# Blender ile 3D ve 2D öğeler

Blender, HyperFrames'in tarayıcıda yapamayacağı ya da zor yapacağı şeyler için: gerçek malzemeli 3D yazı (altın, krom, kırmızı plastik), yörüngede dönen küreler, dönen telefon, klavye tuşu, SVG'den 3D ikon, uçan kart, cam kırılması, karmaşık kamera hareketleri. Çıktı **alfa kanallı video** (VP9 webm veya ProRes 4444 mov) ve videonun üstüne bindirilir.

2D işlerin çoğu (kart, liste, yazı, grafik) HyperFrames'te daha hızlıdır; Blender'ı 3D derinlik, gerçek ışık/yansıma veya fizik gerektiğinde kullan.

## Kurulum ve bulma

```bash
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
[ -x "$BLENDER" ] || BLENDER="$(command -v blender)"
"$BLENDER" --version
```
Yoksa kullanıcıya sor ve onay alınca: `brew install --cask blender`. Blender 4.2+ ve 5.x desteklenir.

## Hazır tarif script'i

```bash
"$BLENDER" -b --factory-startup -P <skill>/scripts/blender_render.py -- work/tarif.json
```

Tarif alanları script'in başındaki açıklamada. Sahne türleri:

| scene | ne üretir | önemli alanlar | tipik efekt |
|---|---|---|---|
| `text3d` | 3D kalınlıklı yazı | text, font, material, extrude, bevel, italic_skew, animation | extruded-3d-word, headline-gradient-metal |
| `orbit` | halka yörüngede krom küreler | count, radius, turns, tilt_deg, split_depth | orbit |
| `card` | görsel dokulu kart/broşür | image, card_width, animation=fly | flying-card, freebie-doc |
| `phone` | telefon, ekranında görsel veya video | image / video, animation=turn | phone-mockup, reel-feed |
| `keycap` | klavye tuşu ve etiket | label, material, animation=press | apple-ui-key |
| `svg` | SVG'den 3D ikon | svg, extrude, material, animation=spin | icon-strike, dişli ikonları |

Malzemeler: `red`, `gold`, `chrome`, `silver`, `white`, `black`, `glass` veya `#RRGGBB`.
Animasyonlar: `rise`, `drop`, `spin`, `float`, `fly`, `turn`, `press`, `none`. Kamera: `static`, `push`, `orbit`.

**Örnek: stil C "$40 MILLION" altın başlık**
```json
{"scene": "text3d", "text": "$40 MİLYON", "font": "/Users/.../Inter-ExtraBold.ttf",
 "material": "gold", "extrude": 0.08, "bevel": 0.015, "animation": "rise",
 "camera": {"move": "push"}, "duration": 2.0, "engine": "eevee", "samples": 64,
 "output": "work/blender/kirk-milyon", "name": "kirk-milyon-altin", "format": "webm"}
```

**Örnek: kişinin arkasından geçen yörünge**
```json
{"scene": "orbit", "count": 7, "radius": 2.2, "turns": 0.5, "tilt_deg": 72,
 "material": "chrome", "split_depth": true, "duration": 4, "output": "work/blender/yorunge"}
```
`split_depth` iki video üretir: `_back` (kişinin arkası) ve `_front` (kişinin önü). Katman sırası: video → `_back` → fg.webm (kişi maskesi) → `_front`.

## Hız ve kalite

- **Önce taslak:** `"width": 540, "height": 960, "samples": 16, "duration"` gerçek değer → kareye bak → sonra tam kalite.
- `engine: "eevee"` hızlıdır ve Mac'te Metal ile çalışır; cam ve gerçekçi yansıma için `cycles` (script Metal GPU'yu kendisi açar). Intel Mac'te Cycles yavaştır: 1080x1920'de 3 sn'lik sahne için önce eevee dene.
- Render sonrası `poster.png` orta karedir. Şeffaf olduğu için Read'de zor görünür: Pillow ile gri bir zemine bindirip öyle bak (`Image.new("RGBA", size, (120,120,120,255)).alpha_composite(poster)`).
- Türkçe karakterler için font dosyası ver; varsayılan Blender fontu ğ, ş, İ'yi destekler ama marka fontu değildir.

## Hazır tariflerin yetmediği durumlar

Script'te olmayan bir sahne gerekiyorsa (cam kırılması, parçacık, karmaşık model):
1. `blender_render.py`'deki yapıyı kopyala (setup_scene, add_lights, add_camera, render ve paketleme aynı kalsın), yeni sahne fonksiyonunu `work/blender/<ad>.py` olarak yaz.
2. Belirlenimci tut: rastgelelik varsa sabit `seed`.
3. Çalışırsa ve tekrar kullanılabilirse skill'in `scripts/blender_render.py` dosyasına yeni `scene` türü olarak eklemeyi kullanıcıya öner.
4. `.blend` dosyasını da sakla: `bpy.ops.wm.save_as_mainfile(filepath=...)` → kütüphaneye `--kind blender-scene`.

## HyperFrames'e bağlamak

```html
<video id="proof3d" class="clip" src="assets/library/proof-red/proof-red.webm"
       data-start="4.2" data-duration="2" muted playsinline
       style="position:absolute; inset:0; width:100%; height:100%; object-fit:contain; z-index:5"></video>
```
- VP9 alfa webm Chrome'da şeffaf oynar; HyperFrames render'ı da Chrome kullanır.
- Kişinin arkasında kalacaksa z-index'i fg.webm'den küçük ver.
- Bitince kütüphaneye kaydet: `python3 <skill>/scripts/library.py add work/blender/<ad> --name <ad> --tags ... --desc "..." --skip-frames`.
