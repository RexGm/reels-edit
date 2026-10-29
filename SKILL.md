---
name: reels-edit
description: Dikey kısa video (Instagram Reels, TikTok, YouTube Shorts) editleme stüdyosu. Ham konuşma videosunu altyazı, kart, 3D öğe, geçiş ve ses efektiyle editler; beğenilen bir referans videoyu analiz edip birebir yeniden kurar; Blender ile 2D/3D görsel öğe üretip kütüphanede saklar ve tekrar kullanır. Kullanıcı bir videoyu editlemek, "şu videodaki gibi" yapmak, bir efekt (snap zoom, person pop out, orbit, kinetic captions, chat drop, checklist, dolly zoom vb.) istemek, referans reels incelemek, 3D yazı/ikon/mockup üretmek veya reels-studio klasöründe çalışmak istediğinde mutlaka kullan; HyperFrames, Remotion veya Blender adı geçmese bile.
---

# Reels Edit

Kullanıcının kısa video stüdyosu. Dört iş yapar:

1. **Edit** — ham çekimi stilli, altyazılı, efektli dikey videoya çevirir.
2. **Kopya** — referans videoyu analiz edip aynı yapı ve hisle kullanıcının çekimiyle yeniden kurar → `references/recreate.md`.
3. **Öğe** — 2D/3D görsel öğe üretir (Blender, HyperFrames, üretilmiş görsel), kütüphaneye kaydeder, sonra tekrar kullanır.
4. **Öğrenme** — yeni referansları analiz eder, yeni efektleri kataloğa ve kütüphaneye ekler.

Motor HyperFrames'tir (HTML → MP4, belirlenimci render). Bu skill onun üstünde bir katmandır: stil, efekt tarifleri, Blender boru hattı, kütüphane ve iş akışı. HyperFrames'in kendi kuralları (render sözleşmesi, `class="clip"`, `window.__timelines`, media-treatment) için `/hyperframes` skill'ini **her projede önce oku**; burada tekrar edilmez.

## Çalışma alanı

Kök: `$REELS_STUDIO`, yoksa `~/Movies/reels-studio`.

```
reels-studio/
  CLAUDE.md          proje kuralları (bu skill'e yönlendirir)
  BRAND.md           kendi tarzımız: renk, font, altyazı, ritim, varyasyon havuzu
  edit-log.md        her videoda kullanılan varyasyonlar (tekrarı önlemek için)
  inbox/             kullanıcının bıraktığı ham çekimler
  projects/<tarih>_<ad>/   her video: media/ work/ output/ hf/ project.json
  library/           tekrar kullanılabilir öğeler + index.json (scripts/library.py)
  references/videos/      beğenilen referans videolar
  references/analysis/    referans analizleri (analyze_reference.py çıktısı)
  output/            teslim edilen final videolar
```

Script'ler bu skill'in `scripts/` klasöründe; yolu `<skill>` diye anıyoruz (`~/.claude/skills/reels-edit`).

## Araç seçimi

| İhtiyaç | Araç |
|---|---|
| Kompozisyon, altyazı, kartlar, arayüz taklitleri, 2D animasyon | HyperFrames (`/hyperframes`, GSAP) |
| Adı olan bir efekt/geçiş/kart | Önce `effects.md` tarifi, sonra `npx hyperframes catalog <kelimeler>` (`/hyperframes-registry`) |
| Kişinin arkasına yazı/nesne, pop out, frame escape | `npx hyperframes remove-background media/<v> -o work/fg.webm` |
| Kart/dev kelime/altyazı yerleşimi için kafa üstü, yüz x aralığı, omuz ölçümü | `scripts/face_layout.py hf/assets/video/fg.webm -o work/layout.json --edl work/edl.json --zoom 1.18` |
| Grade, grain, blur, vinyet, film görünümü | `npx hyperframes media-treatment` (`/media-use`); footage'a CSS filtresi yok |
| Gerçek 3D (metal yazı, yörünge, telefon, tuş, ikon) | Blender → `references/blender.md` |
| Elde tutulan panel, yapışık yazı, köşe sabitleme | `scripts/track_point.py` |
| Üretilmiş görsel/video (sahne, B-roll, doku) | `/media-use` veya kullanıcının aracı; prompt'u kütüphaneye yaz |
| Görseli kesik kolaj/kâğıt parçasına çevirme, saten zemin | `scripts/paper_cutout.py`, `scripts/satin_bg.py` (`effects.md` → `photo-collage`, `satin-bg`) |
| Telifsiz müzik + efekt, storyboard anlarına kilitli (trap, lofi, ambient…; kâğıt, damga, kalem, daktilo…) | `~/.local/opt/mg-venv/bin/python scripts/mg_music.py` (`references/mg-styles.md`) |
| Hazır motion design stili (kolaj, variety yazıları, sticker explainer, HUD, synthwave, line boil…) | `references/mg-styles.md` (kaynak: `references/mg-styles-15`) |
| Remotion projesi gelirse | `/remotion-to-hyperframes` ile taşı; Remotion skill'leri sadece kullanıcı Remotion isterse |
| Türkçe transkript | `npx hyperframes transcribe <v> --engine whisper --model large-v3 --language tr` |

`.en` ile biten Whisper modelleri sadece İngilizce'dir. Intel Mac'te large-v3 yavaş olabilir; uzun videoda `--timeout` artır.

## Stil seçimi

Her edit, girdi toplanıp ölçüldükten sonra kullanıcıya stil sorarak ilerler (1.3). Seçenekler:

- **BRAND:** kendi tarzımız (`BRAND.md`). Renk, font ve altyazı sabit; geçiş ve efektler varyasyon havuzundan döner.
- **A Editoryal Yeşil / B Kinetik Kırmızı / C Cam Derinlik:** `references/styles.md` profili bu video için BRAND'in yerine geçer. Renk, font, altyazı, ritim, grafik yoğunluğu ve grafik dili o profilden gelir. Bu kare kare kopya değildir; belirli bir referansın birebir kopyası bölüm 2'deki kopya akışıdır.
- **Karışım:** kullanıcı tarif eder ("C'nin cam kartları + BRAND altyazı"). Storyboard'da her öğenin kaynağı yazılır.

Seçim `work/style.md`'ye yazılır; sonraki bütün adımlar ona göre yürür. BRAND'e özgü kurallar (varyasyon havuzu, %40–60 grafik yoğunluğu, dönüşüm kuralları) yalnız BRAND seçilince geçerlidir. A/B/C'de profilin ölçülmüş değerleri geçerlidir.

## 1. Edit akışı

Her adımın sonunda kullanıcıya kısa bilgi ver; **storyboard onayından önce render alma.**

### 1.1 Hazırlık
1. `npx hyperframes doctor` — eksik varsa söyle. Script'ler için `python3 -c "import PIL, numpy, cv2"`; eksikse kullanıcı onayıyla `pip3 install --user pillow numpy opencv-contrib-python-headless`.
2. `BRAND.md`, `edit-log.md` ve `references/styles.md`'yi oku.
3. Proje aç:
   `python3 <skill>/scripts/new_project.py <kisa-ad> --footage inbox/<dosyalar> --hf`
   Orijinal dosyalar değiştirilmez; her şey proje klasöründe.
4. Girdiyi topla ve ölç:
   `python3 <skill>/scripts/input_report.py <proje>/media -o <proje>/work/input --proxies <proje>/work/sdr`
   Klip başına süre, çözünürlük, HDR, ses seviyesi, zemin parlaklığı, kamera hareketi ve kafa üstü konumu ölçülür; kontak sayfaları ve stil uyum notları `work/input/report.md`'ye yazılır. HDR (iPhone HLG) kaynak VideoToolbox ile tonemap edilmiş SDR proxy'ye çevrilir; kurgu bu proxy'lerle yapılır. Kontak sayfalarının hepsine bak. 9:16 olmayan klipte dur, kendiliğinden kırpma.

### 1.2 Transkript ve temizlik
1. Türkçe transkript (yukarıdaki komut). Marka/ürün adlarını düzelt (Claude, Opus, ChatGPT, Gemini, HyperFrames…), anlam değiştiren şüpheleri sor.
   Whisper arkadaki bir konuşmayı ya da TV sesini de cümle diye yazabilir; kısa parçada hiç söylenmemiş bir cümle uydurabilir ("İzlediğiniz için teşekkür ederim"). Tek cümlelik kısa klipleri, düşük güvenli kelimeleri ve konuyla bağı zayıf cümleleri storyboard'dan önce "bu klipte X diyorsun, kullanayım mı?" diye teyit ettir.
2. Sessizlik, dolgu kelime ("ııı", "şey", tekrar başlangıçlar) tespit et; `npx hyperframes audio` sessizlikleri ölçer. Listeyi `work/cuts.md`'ye yaz ve göster. İçerik cümlesi onaysız kesilmez.
3. Kesimlerden sonra kelime zamanlarını yeni zaman çizelgesine taşı.

### 1.3 Stil seçimi — dur ve sor
Girdi raporu, kontak sayfaları, transkriptin tonu ve `edit-log.md` (son videolarda hangi stil kullanıldı) birlikte değerlendirilir.

1. **Öneriyi kur.** Raporun uyum puanlarından başla, transkriptin tonuyla düzelt: bilgilendirici/öğretici → A ya da BRAND; satış, iddialı, ajans dili → B; lüks, sakin, ürün/mekân → C; kendi kanalının rutin videosu → BRAND. Çekim önerilen stili taşımıyorsa açıkça söyle (ör. "A koyu duvar ve baş üstü boşluk ister; bu çekimde kafa üstü %17, krem dev yazı kafanın arkasında kaybolur").
2. **AskUserQuestion ile sor.** Soru: "Bu video hangi stilde olsun?". Dört seçenek BRAND, A, B, C; önerin ilk sırada ve etiketinde "(Önerilen)". Her açıklamada bu çekime özel tek cümle: neden uygun ya da zayıf, ve neyi değiştirir (palet, altyazı, yoğunluk). Karışım "Other" ile gelir. Bekleyen diğer kararları aynı çağrıda sor: klip sırası, onay gereken içerik kesimleri, görüntüdeki başka kişiler, müzik/trend ses (en fazla 4 soru).
3. **Cevabı `work/style.md`'ye yaz:** seçilen stil, geçerli değerler (renk kodları, fontlar, altyazı ölçüleri, yoğunluk aralığı, grafik dili) ve karışımsa hangi öğenin nereden geldiği.

### 1.4 Malzeme listesi
`references/materials.md`'ye göre `work/needs.md` yaz:
- **Benim hallettiklerim:** ücretsiz ve lisansı temiz her şeyi sormadan getir (OFL fontlar, CC0/CC BY efektler, Blender öğeleri, kendi çekiminden kareler). Önce kütüphaneye bak.
- **Senden gerekenler / isteğe bağlı:** yalnız kullanıcıda olan şeyler (logo, gerçek ekran kayıtları, gerçek yorum/istatistik, konuya özel B-roll, lisanslı müzik, izinler). Her madde için ne, hangi format, nereye (`inbox/ek/`), videonun hangi anı için ve gelmezse yedek plan yazılır.
- Seçilen stile uyum raporda ≤ 1/3 ise **"Sonraki çekim için"** 3–4 somut öneri ekle.

Listeyi tek mesajda göster; cevabı bekleyip akışı durdurma. Malzemeye bağlı anlar storyboard'da "(malzeme #n bekleniyor)" diye işaretlenir, gelmezse yedek plan uygulanır.

### 1.5 Erken hazırlanacaklar
- Kişi maskesi (`fg.webm`): stil ne olursa olsun neredeyse her videoda gerekiyor; arka planda erken başlat.
- Kütüphaneyi tara: `python3 <skill>/scripts/library.py search <konu kelimeleri>` — daha önce yapılmış logo, 3D yazı, şablon varsa tekrar üretme.

### 1.6 Varyasyon seçimi
- **BRAND:** `edit-log.md`'ye bak, `BRAND.md`'deki dönüşüm kurallarına uy (son videolarda kullanılan geçiş, bölüm kartı, dev yazı stili ve müzik tekrar edilmez). İçeriğin tonuna göre seç.
- **A/B/C:** efektleri profilin "grafik dili"nden ve `effects.md`'den seç. Aynı stilin son videosundaki imza anlarını birebir tekrarlama.
- `library/audio/sfx` ve `library/audio/music` içeriğini önek kategorilerine göre listele; eksik kategori varsa 1.4'teki gibi kendin getir.

### 1.7 Storyboard — dur ve onay al
`work/storyboard.md` (ilk satır: `Stil: <seçim>`):

```
00:00.0–00:02.1 | "Claude bu videoyu editledi" | giant-captions + text-behind-subject "CLAUDE EDİTLEDİ" | snap-zoom | vurgu_bass_01
00:02.1–00:05.4 | "Üç ana kural var" | number-morph 1→2→3 | — | tik_mouse_02
00:05.4–00:09.0 | "Opus 5.5 seç" | model-picker + cursor-tracker | digital-zoom | tik_mouse_01
...
Varyasyon: G1,G3 | B2 | K1,K4 | Y3 | müzik: muzik_sakin_01
Üretilecek öğeler: 3D "1-2-3" (Blender text3d, chrome) — kütüphanede yok
```

Grafik adlarını `effects.md` slug'larıyla yaz. Kontrol: ilk 2 sn'de görsel olay var mı, grafik yoğunluğu seçilen stilin aralığında mı (BRAND %40–60; A/B/C için `styles.md`'deki ölçüler), ekranda en fazla iki kart mı, bazı olaylar bilerek sessiz mi. Göster, düzeltmeleri işle, onay bekle.

### 1.8 Kurulum
1. Her efekt için `effects.md`'deki tarifi oku; registry'de uygun blok varsa kur ve seçilen stilin renk/fontlarına uyarla, yoksa yaz.
2. Gereken 3D/2D öğeleri üret (bölüm 3), `library.py use <id> <proje>/hf` ile projeye al.
3. Katman sırası: video → arka grafikler → `fg.webm` → ön grafikler → altyazı. Kişinin arkasındaki her şey fg'nin altında.
4. Grafikler kelime zaman damgasına kilitli (±2 kare). Türkçe büyük harf: `toLocaleUpperCase('tr-TR')`.
5. Fontlar `hf/assets/fonts/` içinde `@font-face` ile (HyperFrames yalnızca paketli fontları adla tanır). Türkçe karakter testi: ğ ü ş ı ö ç İ Ğ Ü Ş Ö Ç. Arayüzde kullanılan simgeler de fontta olmalı: `fontTools` ile cmap'e bak (Inter'de ✎ ⌕ ＋ yok; JetBrains Mono'da ✓ ✗ yok). Eksik simge SVG ikon olur; tarayıcının yedek fontuna bırakılmaz.
6. **Yerleşim ölçümle yapılır, varsayımla değil.** `fg.webm` bitince `face_layout.py` parça başına kafa üstünü, yüz x aralığını ve omuz çizgisini verir. Kurallar:
   - Kartlar yüzün x aralığının dışında (çoğu zaman sol sütun) ya da kafa üstü ile üst güvenli bant (220) arasındaki duvarda durur. Yüz parçadan parçaya kayabilir (bir videoda x 300–740'tan 500–960'a kaydı); sağ sütun her parçada ayrıca kontrol edilir.
   - Kamera yakınlaşmasının dönüş noktası parça başına yüz merkezi x, y ≈ 1000 (`transformOrigin: "<x>px 1000px"`, kesme anında değiştirilir). Böylece yakın planda yüz yerinde kalır, çene altyazıya inmez.
   - Altyazı, çenenin en yakın plandaki konumunun altında ve alt 420 px'in üstünde durur (tam boy yakın çekimde göğüs: y ≈ 1440).
   - Kafanın arkasındaki dev kelimenin alt ~%35'i kafa üstünün arkasında kalacak şekilde `top`, o anki ölçekteki kafa üstünden hesaplanır.
7. Bilinen render tuzakları:
   - Alt kompozisyondaki `<video>`, üstüne altyazı/katman bindiğinde ya da hareket bulanıklığında **siyah** render edilebilir. Kısa cihaz ekranında (telefon, kart) videonun bir karesini `<img>` olarak koy ya da videoyu kök seviyede tut; snapshot'ta o bölgenin parlaklığını ölçerek doğrula.
   - `<template>`'siz registry blokları (ör. `editorial-flash-overlay`) id'leri sayfa genelinde seçer: iki kez kullanılacaksa id'leri değiştirilmiş kopyalar aç (`flash1.html`, `flash2.html`).
   - Yuva şablonları (`torn-paper-rip` için `<template data-slot>`) kök div'den sonra yazılır; önce gelirse `check` kökü bulamaz.
   - `media-treatment --apply` index.html'yi yeniden yazar (`data-hf-id` ekler, öznitelik sırası değişir): sonraki betik düzenlemelerinde tam metin yerine öznitelik sırasından bağımsız regex kullan.
   - Grade'li videoda flaş/pozlama için `--hf-color-grading-exposure` canlandırılır; kişi maskesi (`fg`) görünürse aynı tween ona da uygulanır, yoksa kişi flaşsız kalır.
   - SVG içindeki şekli döndürürken `svgOrigin: "12 12"` (viewBox koordinatı) kullan. Flex kart içindeki `<svg>` ya da sarmalayıcı div'e `rotation` + `transformOrigin: "50% 50%"` verilince şekil dönerken kartın içinde kaydı.
   - Çizilen çizgi (`stroke-dasharray`/`dashoffset`) yol uzunluğundan büyük olmalı; kısa kalırsa desenin ikinci tiresi çizim başlamadan görünür.
   - Harf harf açılan dev kelimede açılış, kelimenin çıkışından önce bitmeli (açılış ≤ çıkış zamanının %75'i). 0.7 sn'lik kelimede 0.42 sn + 0.045 sn kademe, son harfler açılmadan kelimeyi söndürdü.
   - Girişte `filter: blur()` tween'i alan büyük yazıda filtre öğede kalırsa Chrome içeriği öğenin kutusuna kırpar: Anton'da Ö Ğ İ Â'nın üst işaretleri kesilir. Girişten sonra `tl.set(el, { filter: "none" })`, büyük harfli Anton'da `line-height` ≥ 1.15.
   - Koyu kıyafet (lacivert, siyah) üstünde kırmızı vurgu yazısı okunmuyor (kontrast 1.5:1). Vurgu kelimesini kırmızı blok üstünde beyaz yaz (B'de altyazı vurguları ve bölüm başlıkları).
   - Kelime kelime altyazıda kelimeler `<span>` ise aradaki boşluk karakteri kapsayıcının yazı tipinde çizilir: kapsayıcıya da aynı font ve punto ver, yoksa 16 px'lik boşlukla kelimeler yapışır ("Velev kiöğretmenim").
   - GSAP 3'te `className` ayarlanamaz; karaoke vurgusu `tl.set(el, { color })` ile.
   - Kök `index.html`'nin CSS'i alt kompozisyonların içine de uygulanır (alt kompozisyonunki kendi kapsamında kalır). Kökte `#wc` gibi kısa bir kimlik varsa aynı adlı sahne öğesini bozar (kart ekranın altına kadar uzar). Kökteki kimliklere önek ver; şüphede `grep -o 'id="[^"]*"'` ile çakışma ara.
   - Sıfır ölçekten açılan öğe (üstü çizme çizgisi, vurgu bandı, kapatma bandı) CSS'te `transform: scaleX(0)` + `fromTo(..., { immediateRender: false })` ile yazılırsa motor geri sardığında tam boy görünür (vurgu, gelmesi gereken andan saniyeler önce görünür). CSS'e transform yazma; `fromTo` varsayılan `immediateRender` ile başlangıcı kendisi yazsın. SVG çizgi yüzdesi (`pathLength="1"`) `strokeDashoffset` yerine `attr: { "stroke-dashoffset": … }` ile canlandırılır.
   - Render her `<video>`un tüm karelerini geçici önbelleğe çıkarır (alfa video kare başına ~2.2 MB PNG; 64 sn'lik kişi maskesi ~4.3 GB). Maske, mono kopya gibi kısa anlarda kullanılan videoları yalnız o anların klibine kes (`trim=start_frame=..:end_frame=..`); tam boy maske diski doldurup render'ı düşürebilir. Render öncesi `df -h` ile yer kontrol et; başarısız render'ın yarım önbelleği `$TMPDIR/hyperframes-extract-cache-*/*.partial-*`. Yakalama aşaması da çok çalışanla her kareyi diske yazar (~1.8 GB / 65 sn); yer azsa `render --workers 1` kareleri doğrudan kodlayıcıya akıtır (daha yavaş, disk istemez).
   - Aynı videoyu iki öğede kullanmak lint uyarısı verir: kısa klip kes ya da sabit bağlantı aç (`ln`, ek disk yok).
   - Büyük medyada `check` bazen tarayıcı zaman aşımıyla düşer (`ERR_NETWORK_IO_SUSPENDED`, `check_runtime_failure`). Bu kompozisyon hatası değildir; tekrar çalıştır.

### 1.9 Ses
- Konuşma -14 LUFS, tepe -1 dBTP. Müzik konuşma altında -24/-28 LUFS, ducking. Efektler konuşmanın en az 6 dB altında.
- HyperFrames içinde: `<audio id=...>`, `data-volume`, `data-automation` ducking (`/media-use` → mixing). `npx hyperframes normalize-audio`, `npx hyperframes audio` ölçüm için.
- Efektleri dosya adına ve kategoriye göre seç; Claude sesleri duyamaz. Kulak kontrolünü kullanıcıdan iste.
- Müzik ve eksik efektler için önce `scripts/mg_music.py` (mgaudio): seçilen stile göre tarif, `--drop` kanca/kahraman anı, `--build` yükselmenin başı, `--outro` CTA, `--hits` görsel vuruşlar, efektler `work/sfx_cues.json`'dan. `music.wav` (~-26 LUFS) ve `sfx.wav` ayrı izler olarak HF'ye girer; telifsiz, atıf gerekmez. Tarif ve efekt eşlemesi `references/mg-styles.md`.
- Müziği konuşmanın altına `scripts/duck_music.py music.wav voice.wav -o hf/assets/music/music.wav --start <sn>` oturtur: önce hafif sıkıştırma, konuşma varken sabit 5 dB kısma, konuşma altında ~-22 LUFS. -27 LUFS telefonda neredeyse duyulmuyor. ffmpeg `sidechaincompress` kullanma; kısma miktarı konuşma seviyesine bağlı olduğundan müziği 30+ dB gömüyor. Başka sesli bir hook (çizgi film, alıntı) varsa müziği hook'un üstüne koyma; `--start` ile hook'un son ~1.5 sn'sinde yükselmeyle başlat, drop'u kırılma anına koy.
- Arka plan gürültüsü (uğultu, TV, konuşma): `build_aroll` ses zincirinde `highpass=f=90,arnndn=m=~/.local/share/rnnoise-models/sh.rnnn:mix=0.9,afftdn=nr=8:nf=-50` (RNNoise "somnolent-hogwash" = kayıt gürültüsü / konuşma; GregorR/rnnoise-models). Tipik sonuç: taban 13–15 dB düşer, konuşma seviyesi aynı kalır; kulak kontrolü kullanıcıda. Model dosyası `kur.sh` ile iner.
- Kütüphanede eksik kategori varsa: `npx hyperframes media-use resolve --type sfx --intent "<kağıt hışırtısı / kalem çizik…>" --project <proje>/hf` (Openverse, CC0/CC BY, hesap gerekmez). Seçilen sesi BRAND önekiyle `library.py add ... --kind sfx --license "<lisans>" --source "<url>"` ile kütüphaneye kaydet; CC BY ise `library/audio/CREDITS.md`'ye atıf ekle.
- CC BY müzik (ör. Tanner Helland) kullanıldıysa teslimde kullanıcıya gönderi açıklamasına yazılacak atıf satırını ver.
- Kullanıcı platformun trend sesini yükleme sırasında ekleyecekse (Instagram/TikTok uygulama içi müzik) müziksiz render al: sadece konuşma + efektler. Trend ses erişim için genelde daha iyidir; bunu bir kez öner.

### 1.10 Kontrol ve teslim
1. `npx hyperframes check --json` → her hatayı düzelt.
2. `npx hyperframes snapshot --at <her grafik anı>` ve kendin bak: güvenli alanlar (üst 220px, alt 420px, sağ 140px boş), Türkçe karakterler, yüzü kapatan grafik, kenarı titreyen maske, aynı anda üçten fazla renk.
3. `npx hyperframes preview --background` ile kullanıcıya göster; onay gelince
   `npx hyperframes render --output ../output/<tarih>_<ad>.mp4`, sonra kopyasını `reels-studio/output/`'a koy. `ffprobe` ile 1080x1920, 30 fps, H.264, AAC doğrula. Ses seviyesini `ebur128` ile ölç: render karışımı hedefin altında çıkabilir (örneğin -16 LUFS). Öyleyse görüntüye dokunmadan iki geçişli `loudnorm=I=-14:TP=-1` ile yalnız sesi düzelt (`-c:v copy`), ardından `-t <video süresi> -c copy` ile AAC'nin uzattığı kuyruğu kırp.
4. `edit-log.md`'ye satır ekle (`stil:` alanıyla; A/B/C videolarında kullanılan imza efektlerini de yaz). Bu videoda üretilen tekrar kullanılabilir öğeleri kütüphaneye kaydet.

Revizyon: geri bildirim önce storyboard'a, sonra kompozisyona. Küçük düzeltmede sadece ilgili kısım. Kalıcı bir kural değişikliği ("bundan sonra hep…") gelirse BRAND.md güncellemesini öner.

## 2. Kopya akışı

`references/recreate.md`'yi uygula: analiz → çözümleme tablosu → eşleme → kur → `compare.py` ile yan yana kıyas → farkları kapat. Referans videoyu `references/videos/`'a, analizini `references/analysis/<ad>/`'a koy.

## 3. Öğe üretme ve kütüphane

1. **Önce ara:** `library.py search ...`. Uygun öğe varsa `use`.
2. **Aracı seç:** düz 2D animasyon → HyperFrames (gerekirse ayrı kompozisyon olarak alfa webm render et); gerçek 3D → Blender; fotoğraf gerçekliğinde sahne/doku → üretilmiş görsel.
3. **Taslak:** düşük çözünürlük, az örnek; kareye bak, kullanıcıya göster.
4. **Final:** tam kalite, alfa kanallı.
5. **Kaydet:**
   ```bash
   python3 <skill>/scripts/library.py add <dosya-veya-klasör> --name <ad> --kind <tür> \
     --tags "stil-c,altin,baslik" --desc "kısa açıklama" --source "<prompt/tarif/url>" --license own
   ```
   Etiketler: stil (stil-a/b/c/brand), renk, malzeme, efekt slug'ı, konu. Blender klasörlerinde `--skip-frames` (sadece video + poster saklanır). Üretilmiş görsellerde `--license ai` ve prompt `--source`'ta.
6. Kullanıcı açıkça bir öğenin "her zaman" kullanılmasını isterse (logo, intro, imza geçiş) BRAND.md'ye ekle.

Kütüphaneden silme sadece kullanıcı isterse.

## 4. Yeni referans ve efekt öğrenme

- Kullanıcı yeni bir beğendiği video atarsa: `references/videos/`'a kopyala, `analyze_reference.py` ile analiz et, karelerin hepsine bak, kullanılan teknikleri `effects.md` slug'larıyla listele. Yeni bir stil ailesiyse `styles.md`'ye profil olarak eklemeyi öner.
- Katalogda olmayan efekt: tanımla, kullanıcıya teyit ettir, tarifini çıkar, çalışan versiyonu `--kind template` olarak kütüphaneye kaydet ve `effects.md`'ye ekle (skill dosyaları yazılabilir değilse, eklenecek metni kullanıcıya ver).

## Referans dosyalar

- `references/effects.md` — 95+ efektin tarifi (kamera, maske, yazı, arayüz, veri, kâğıt, görünüm, 3D, CTA). Storyboard yazmadan önce ilgili bölümleri oku.
- `references/styles.md` — üç referans stilin ölçülmüş değerleri (renk kodları, fontlar, altyazı ölçüleri, ritim).
- `references/materials.md` — stil başına çekim koşulu ve malzeme; Claude'un kendisinin getirdikleri ile kullanıcıdan istenenler.
- `scripts/input_report.py` — girdi raporu (HDR→SDR proxy, ölçümler, kontak sayfası, stil uyumu).
- `scripts/face_layout.py` — kişi maskesinden parça başına kafa üstü, yüz x aralığı, omuz; yakınlaşmada kafa üstü (yerleşim için).
- `scripts/paper_cutout.py` — görsel → kesik kolaj parçası (arka plan silme, s/b, halftone, retro, çıkartma/makas kesimi, kâğıt kenarı, kırışık, vs bölme, gölge).
- `scripts/satin_bg.py` — dikişsiz döngülü saten kumaş zemin (mp4/png, renk ayarlı).
- `references/mg-styles.md` — mg-styles-15: 15 MG stilinin reels'te kullanımı, render yolu, paylaşılan dokular.
- `scripts/mg_music.py` — storyboard anlarına kilitli müzik + efekt (mgaudio; `~/.local/opt/mg-venv/bin/python` ile).
- `scripts/duck_music.py` — müziği konuşma zarfıyla kısar, hedef seviyeye getirir, başlangıçtan kırpar.
- `references/recreate.md` — birebir kopya süreci.
- `references/blender.md` — Blender kurulumu, tarif script'i, sahne türleri, HyperFrames'e bağlama.

## Asla

- `media/`, `inbox/` veya `references/videos/` içindeki orijinalleri değiştirmek.
- Storyboard onayı olmadan final render almak.
- Stili kendi kararınla seçmek: stil 1.3'te kullanıcının seçimidir; seçilen stilin dışındaki renk/font/altyazıyı kullanmak (kopya modu hariç).
- Kullanıcıdan, kendinin ücretsiz ve temiz lisansla getirebileceği bir şeyi istemek (font, CC0 efekt vb.).
- Uydurma yorum, sahte sosyal kanıt veya telifi belirsiz müzik/efekt eklemek.
- Başkasının görüntüsünü, logosunu veya yüzünü kullanıcının yayınlayacağı videoya koymak.
