# Efekt kataloğu

Her efektin bir **slug**'ı var (storyboard'da bu adla anılır), ne olduğu, nasıl yapılacağı ve hangi aracı kullandığı. Kullanıcı bir efekti İngilizce adıyla da isteyebilir; ad parantez içinde.

**Araç etiketleri**
- `HF` — HyperFrames kompozisyonu (HTML/CSS + GSAP). Varsayılan.
- `REG: a, b` — işe yarayabilecek hazır registry blokları. Registry değişir: kullanmadan önce `npx hyperframes catalog <kelimeler>` ile doğrula, bloğu kurup (`npx hyperframes add <ad>`) projenin renk ve fontlarına uyarla. Uygun blok yoksa elle yaz.
- `MASK` — kişi maskesi: `npx hyperframes remove-background <video> -o work/fg.webm` (ön plan) ve gerekirse `-b work/bg-hole.webm`. Katman sırası: orijinal video → grafik → fg.webm.
- `TRACK` — nesne/nokta takibi: `scripts/track_point.py` → kare kare konum JSON'u → GSAP keyframe'leri.
- `BL` — Blender: `scripts/blender_render.py` ile alfa kanallı render (bkz. `blender.md`).
- `MT` — `npx hyperframes media-treatment` (grade, grain, blur, vinyet; footage'a CSS filtresi yasak).
- `FF` — ffmpeg ön işleme.
- `AI` — üretilmiş görsel/video (`/media-use` skill'i veya kullanıcının kendi aracı). Prompt'u kütüphanede sakla.
- `LIB` — bitince `scripts/library.py add` ile kütüphaneye kaydet; tekrar kullanılabilir.

Genel kurallar: grafik konuşulan kelimenin zaman damgasında başlar (±2 kare); her efektin bir ses karşılığı düşünülür (whoosh, tık, pop…) ama hepsi seslendirilmez; efekt bitince ekran nefes alır.

## İçindekiler
1. Kamera ve geçişler
2. Kişi, derinlik ve maskeler
3. Yazı ve altyazı
4. Arayüz ve ekran
5. Veri ve grafikler
6. Kâğıt, el çizimi ve doku
7. Görünüm ve renk
8. 3D ve mekân
9. Sosyal, CTA ve kapanış

---

## 1. Kamera ve geçişler

### `digital-zoom` (Digital zoom)
Aynı çekimde kadrajı değiştirmek: geniş ↔ yakın arası kesme veya plan boyunca yavaş itme. Tek kamerayla çok açılı his verir (stil C).
- HF: video sarmalayıcısına `scale` + `transformOrigin` yüze. Kesme: anında 1.0 → 1.6 (4K kaynakta kalite kaybı yok, 1080p'de en fazla 1.3). Yavaş itme: 1.0 → 1.06, plan süresince `none` ease.
- Yüz merkezini `TRACK` ile bulup origin'i oraya koy.

### `snap-zoom` (Snap zoom)
Vurgu kelimede 3–4 karede ani yaklaşma (1.0 → 1.2), 2 karelik hareket bulanıklığı, tok bir vurgu sesi. Bir sonraki kesmede normale döner.
- HF: `scale` 0.1 sn `expo.out`. Bulanıklık için iki ara karede `MT` blur veya `REG: transitions-scale, cinematic-zoom`.

### `zoom-through-cut` (Zoom through cut)
A planının merkezine hızla dalınır, zirvede kesme, B planı aynı hızla geriden açılır. Hareket bulanıklığı ve whoosh ile tek hareket gibi görünür.
- REG: `transitions-scale, cinematic-zoom, parallax-zoom`. Zirve 6–8 kare; A 1.0→2.5, B 2.5→1.0.

### `over-shoulder-zoom` (Over the shoulder zoom)
Konuşanın omzunun arkasından ekrana bakan plan; ekran içeriğine dalınır.
- Gerçek omuz çekimi varsa: ekranı köşelerinden sabitle (corner pin: 4 nokta → CSS `matrix3d`, noktalar `TRACK` ile), içine ekran kaydını koy, sonra ekrana `digital-zoom`.
- Çekim yoksa: konuşanın `MASK` ön planını büyütüp kenara kaydır, önüne ekran kartı koy; sahte omuz plan.

### `zoom-portal` (Zoom portal)
Bir nesnenin içine (telefon ekranı, harf, kapı, tablo) dalınır ve o nesne sonraki sahne olur.
- REG: `vfx-portal, gallery-tunnel, wireframe-portal-title`. Sonraki sahne nesnenin şekliyle maskelenip büyüyerek tam ekrana açılır.

### `match-cut` (Match cut)
İki plan aynı şekil, konum veya hareket üzerinden birbirine bağlanır (el savurma → sonraki sahne, yuvarlak saat → yuvarlak tabak).
- Storyboard aşamasında planlanır. Sonraki planı ölçek/konumla hizala (`snapshot` ile iki kareyi üst üste kontrol et). Yazı versiyonu: `REG: text-match-cut`.

### `iris` (Iris effect)
Eski film iris'i: daire maske kapanıp açılır; bir öğeye odaklanır veya sahne değiştirir.
- REG: `iris-reveal`. `clip-path: circle()` yarıçapı animasyonu; merkez yüzde veya hedef öğede.

### `whip-pan` (referans ek)
Yatay hızlı kaydırma, 8 kare, yönlü hareket bulanıklığı. REG: `whip-pan-cut`.

### `blur-dissolve` (referans ek)
6 karelik bulanık çapraz geçiş. REG: `transitions-blur`.

### `bw-flash` (referans ek — stil A/B)
Bölüm başında veya vurgu anında 4–8 kare siyah-beyaz, sonra renge dönüş. `MT` ile siyah-beyaz kopya üret, kısa klip olarak üstüne koy.

### `white-bloom-flash` (referans ek — stil C)
Aşırı pozlanmış beyaz parlama ile geçiş, 6–8 kare: beyaz katman opaklık 0→0.9→0 + `MT` bloom.

### `camera-shake` (referans ek)
Vurgu anında 2–4px, 6 karelik sarsıntı; seeded gürültüyle. REG: `camera-shake`.

### `dolly-zoom` (Dolly Zoom) ve `vertigo` (Vertigo)
Kişi aynı boyutta kalırken arka plan genişler/daralır. Vertigo, aynı efektin daha uzun ve abartılı hali.
- Gerçek çekimde: kamera geri giderken zoom ileri (çekimde yapılır).
- Sonradan: `MASK` ile kişi ve arka planı ayır; arka planı ölçekle (1.0→1.4), kişiyi sabit tut. Boşluk için `-b` arka plan plakasının deliğini `AI` ile doldur veya bulanıklaştır. REG: `camera-dolly-zoom`.

### `pull-back-reveal` (Pull-back reveal)
Detaydan başlayıp geri çekilerek bütün sahneyi göstermek (yakın yüz → kolaj, tek kart → kart duvarı).
- REG: `pull-back-reveal, parallax-unzoom`. Başlangıç ölçeği 2.5–4, 1.2–1.8 sn `power3.inOut`.

### `studio-reveal` (Studio Reveal)
Yakın plandan geri çekilip stüdyo setini (ışıklar, kamera, mikrofon) göstermek; "perde arkası" anı.
- Geniş 4K çekim gerekir: 2.0x dijital zoom'la başla, 1.0'a aç. Ek olarak ışıkların yanına küçük etiketler (`U` kartları).

### `picture-dive` (referans ek — stil A, `20-efekt`)
Duvardaki tablo pencereye dönüşür: içinde aynı video oynar (iç içe yansıma), kamera çerçeveye dalar ve içerideki görüntü yeni plan olur.
- Çerçeve: sahnedeki gerçek tablonun üstüne beyaz paspartulu kart; kamera oynuyorsa 4 köşe `TRACK`. İçinde aynı video çerçeve boyutuna ölçekli; içindeki çerçeve de öyle (2–3 kat derinlik yeter).
- Dalış: tüm kompozisyona çerçeve merkezine doğru `scale` + `x/y` (0.5 sn `power2.in`); çerçeve ekranı doldurduğu karede ana videoya kes. Görüntü aynı olduğu için dikiş görünmez.
- Ses: `whoosh_kisa`.

### `lens-ring` (referans ek — stil A, `20-efekt`)
Objektif odak halkası arayüzü (85 · 70 · 50 · 35 · 24) yatay kayar, görüntü aynı anda yakından genişe açılır (ya da tersi).
- Üstte yeşil `#1D392C` şerit: ince çentikli cetvel + rakamlar, ortada sabit ibre, aktif rakam altın `#BCA562`. Rakam dizisi `x` ile kayar.
- Görüntü: `digital-zoom` 1.35→1.0, rakamlarla aynı süre ve ease. 4K çekimde kalite kaybı olmaz.
- Altta başlık kartı: kalın sans kelime harf harf zıplayarak + italik altın serif kelime ("lens *ring.*"), üstünde ince kaydırıcı çizgisi.
- Ses: her rakamda hafif `tik_`.

---

## 2. Kişi, derinlik ve maskeler

### `text-behind-subject` (referans ek — üç stilin imzası)
Dev yazı kişinin arkasında: kafa yazının önünden geçer.
- `MASK` zorunlu. Sıra: video → yazı → fg.webm. Yazı kafa hizasında, üst üçte birde.

### `person-pop-out` (Person pop out)
Kişi arka plandan kopup öne çıkar: arkası kararır/bulanıklaşır veya grafik zemine geçer, kişiye beyaz kontur + gölge, hafif ölçek artışı (1.0→1.05).
- `MASK` + arka planı `MT` ile karart/bulanıklaştır. Kontur için önce `/media-use` treatments'ta outline/sticker var mı bak.

### `frame-escape` (Frame Escape)
Kişi bir çerçevenin (kart, telefon, tablo) içindedir; elini veya kafasını çerçevenin dışına çıkarır.
- Çerçeve kartı içinde video (kırpılmış), üstünde `MASK` ön plan **kırpılmadan**: çerçeve dışına taşan kısım görünür. Çerçeve kenarı ön plandan önce, ön plan en üstte.

### `frame-break` (Frame Break)
Çerçeve çatlar/parçalanır ve sahne serbest kalır.
- REG: `glass-shard-title`. Parçalar seeded rastgele yönlere `rotation` + `y` ile dağılır; `BL` ile gerçek cam kırılması da render edilebilir.

### `depth-scatter` (Depth scatter)
Görseller kişinin etrafında farklı derinliklere dağılmış; bazıları önde bazıları arkada, kamera hareketiyle paralaks.
- HF 3D CSS (`perspective`, `translateZ`). Arkadakiler video ile fg.webm arasına, öndekiler fg.webm üstüne. Kamera paralaksı: kapsayıcıya yavaş `rotationY` 6°→-6°.

### `orbit` (Orbit)
Nesneler (küreler, ikonlar, kartlar) kişinin etrafında yörüngede döner; arkaya geçtiğinde kişinin arkasında kalır.
- `BL` `orbit` sahnesi (krom küreler + halka) veya REG: `carousel-orbit-1..5, orbit-card`. Arkaya geçiş: iki katman render et (ön yarı / arka yarı) ya da z sırasını açıya göre değiştir.

### `held-object` (referans ek — stil C)
Panel, kart veya belge kişinin avucunun üstünde ya da elinde durur ve elle hareket eder.
- `TRACK` ile avuç/el noktası → kartın `x/y` keyframe'leri. Belge eldeyse `MASK` ile parmakları kartın önüne al.

### `sticky-text` (Sticky text)
Yazı sahnedeki hareketli bir nesneye/kişiye yapışık gider.
- `TRACK` → yazı konteynerine keyframe'ler. Takip titrekse veriyi `--smooth` ile yumuşat.

### `green-screen` (Green screen)
Yeşil fon çekimini başka sahneye koymak.
- Yeşil fon: `FF` `chromakey=0x00ff00:0.12:0.08` → alfa webm. Fon yoksa: `MASK`. Yeni arka plan: B-roll, `AI` sahne veya HF grafik.

### `image-collage` (Image collage)
Fotoğraflar dağınık kolaja dizilir. Varyant **yüz parçası kolajı** (stil B): konuşanın göz, ağız gibi dikdörtgen kırpımları kişinin üstüne dağılır.
- REG: `carousel-*` (dizilim için). Yüz parçası: aynı videodan `clip-path` ile kırpılmış kopyalar, her biri farklı ölçekte, 0.08 sn arayla pop.

### `b-roll-overlay` (B-roll Overlay)
Konuşma sürerken B-roll görüntüsü: tam ekran, yuvarlak köşeli kart veya **siyah zemin üstünde film karesi** (stil C, grain + vinyet).
- HF; ses konuşmadan devam (J/L cut). Film karesi için `MT` grain.

### `shoulder-peek` (Omuz arkasından çıkan kesik parça)
Kesik kâğıt parça (`photo-collage`) konuşanın omzunun arkasından eğilerek yükselir, bekler, aynı yoldan geri çekilip kaybolur. "vs" kalıbında iki parça iki omuzdan da çıkabilir.
- `MASK` zorunlu; sıra: video → parça → `fg.webm`. Parça kişinin arkasında kaldığı için kaybolma maskeyle doğal olur, fade gerekmez.
- Omuz noktası: o karedeki `fg.webm` alfasından (baş altındaki en dış kişi pikseli) ya da kişi hareket ediyorsa `TRACK` ile omuz takibi; parça omuza bağlı gider.
- Parça: `paper_cutout.py … --no-shadow` (gölge CSS'te).
- Giriş (0.5 sn): `transform-origin` parçanın alt ortası, omuz hizasının 40–80 px altında başlar (tamamen kişinin arkasında). `y` +420→0, `rotation` ±18°→±4° (omuzdan dışa açılır). Kâğıt hissi için `steps(6)` (12 fps), yumuşak istenirse `back.out(1.4)`. `kagit_` efekti.
- Bekleme: 12 fps kaynama (seeded ±0.6°, ±2 px).
- Çıkış (0.35 sn): ters yol, `power2.in`.
- İki parça: sol omuz / sağ omuz, birbirine bakar; çarpışma anında 2 px `camera-shake`.
- Kural: parça yüzü kapatmaz; kafa üstü boşluk azsa (`input_report` kafa üstü %) parça küçük kalır, yanlardan çıkar.
- Plan tipine göre: **orta plan** (kişi kareyi %35–45 kaplıyor) tam karede çalışır; parçalar ~0.6 ölçek, alt kenarları omuz çizgisinin arkasında. **Yakın plan** (kafa kareyi dolduruyor, yanlarda <200 px) için **kart modu**: kamera ve maske birlikte 0.72 ölçek + ±2° eğim, videonun arkasına kâğıt kenar (`#F3EDE0`), arkaya zemin (kâğıt dokulu zemin ya da `satin-bg`); parçalar kart kenarından taşar.
- Konum = hedef nokta: gaga/ağız gibi "yüz noktasını" görselde ölç, kafanın yanındaki hedefe göre sol-üst hesapla. Çalışan sürümü `library.py add ... --kind template` ile şablon olarak kaydet.

---

## 3. Yazı ve altyazı

### `karaoke-caption` (referans ek — stil A)
Kutulu, kelime kelime renk değiştiren altyazı. Ölçüler `styles.md` A'da. Kelime zamanları transkriptten.

### `single-word-caption` (referans ek — stil C)
Göğüs hizasında tek kelime, beyaz, küçük kalın sans. Her kelime kendi süresince.

### `giant-captions` (Giant captions)
Bir-iki kelime ekran genişliğini doldurur; çoğu zaman kişinin arkasında (`text-behind-subject`).
- REG: `caption-kinetic-slam, caption-editorial-emphasis`. Font boyutu genişliğe sığacak şekilde hesaplanır (`fitText`).

### `kinetic-hook` (Kinetic hook)
İlk 2 saniyede kelimeler sert vurgularla ekrana çarpar, her kelimeye bir ses.
- REG: `headline-slam, caption-kinetic-slam`. Kelime başına 0.12–0.2 sn, scale 1.4→1 + blur, kamera sarsıntısı.

### `gravity-drop` (Gravity drop)
Harfler/kelimeler yukarıdan düşer, zıplar ve yığılır.
- Fizik bir kez seeded olarak hesaplanır (yükleme sırasında diziye), timeline zamanına göre okunur (HyperFrames 3D/determinizm kuralı). REG: `char-slam-explode`.

### `text-on-path` (referans ek — stil B)
Kelimeler kişinin gövdesini kavis boyunca sarar; bazı kelimeler kafanın arkasından geçer.
- SVG `<textPath>` + `startOffset` animasyonu; arka geçiş için `MASK`. Kavis kişinin silüetine göre elle çizilir (snapshot üstünde).

### `mixed-type-words` (referans ek — stil B)
Gövde kelime yuvarlak sans, vurgu kırmızı dar italik, süs kelime script; üst üste bindirilmiş. Fontlar `styles.md` B'de.

### `headline-gradient-metal` (referans ek — stil C)
Dev başlık kelimesi degrade (kırmızı→beyaz), çok renkli, metalik altın veya krom.
- Degrade/çok renk: CSS `background-clip:text`. Gerçek metal görünüm: `BL` `text3d` (material `gold`/`chrome`) alfa render.

### `number-morph` (referans ek — stil C)
Rakam yerinde değişir (2014 → 2026), sayaç gibi akar. REG: `apple-money-count`.

### `chapter-card` (referans ek — stil A) ve `title-card` (Title card)
Tam ekran bölüm kartı: italik küçük kelime + çizgi + dev rakam (stil A) ya da başlık kartı.
- REG: `hw-title, glass-hero, canopy-part-title` (başlık ilhamı). Stil A'yı `styles.md`'den birebir kur.

### `selection-box` (referans ek — stil B)
Bir kelimenin etrafında tasarım yazılımı seçim kutusu (kırmızı köşe tutamaçları), kutu kelimeyi "seçer" ve hafifçe büyütür.
- HF: 8 kare içinde kutunun köşelerden açılması. REG: `cursor-marquee-select`.

### `knockout-captions` (referans ek — stil A, `20-efekt`)
Dev harfler krem bir panelden oyulmuş: harflerin içinden video görünür ("KNOCK / OUT"), üstte italik küçük kelime ("captions.").
- HF: krem panel `#F1EBDF`, harfler SVG `<mask>` ile delik (panel beyaz, metin siyah maske). Video panelin arkasında oynamaya devam eder.
- Öncesi: yüzün yanında yeşil etiket kutusunda serif kelime(ler) ("knockout" → "knockout captions."). Panel ekranın ~%65'i, sol yarıda.
- Çıkış: panel 2–3 dikey şeride bölünüp iki yana açılır (0.25 sn `power2.in`).
- Font Instrument Serif büyük harf, satır yüksekliği 0.85.

### `serif-stamp` (referans ek — stil A, `20-efekt`)
Dev krem serif kelime kafanın arkasına harf harf damga gibi basılır ("STAMP"); sol üstünde küçük italik altın kelime ("serif").
- `MASK`; sıra video → kelime → fg. Önce italik kelime (0.2 sn). Her harf `scale` 1.35→1 + `opacity` 0→1, 0.12 sn, harfler arası 0.07 sn; son harfte 2 px `camera-shake`.
- Instrument Serif Regular büyük harf, 1080 genişlikte ~300 px; italik kelime `#BCA562`.

### `pill-caption` (referans ek — stil A, `20-efekt`)
Açılış altyazısı: her satır ayrı beyaz kutu (`#F8F8F8`, köşe 6 px), kalın koyu sans (Inter 700), anahtar kelime koyu yeşil `#1B302D`. Video boyunca değil, kanca cümlesi ve CTA için ("Every effect in this video / was made by Claude", "Comment EDIT").
- Kutular satır satır 0.08 sn arayla `y` +12→0 + fade. Konum: dikeyde %63–70.

### `variety-caption` (referans: `mg-styles-15` 18 — Variety Captions, 9:16)
TV programı tarzı tepki yazısı: kalın yuvarlak harfler, çok katmanlı kenar, yaylanarak gelir; duyguya göre süs (soru işaretleri, ter damlası, patlama çerçevesi, ışıltı, mühür).
- Yazı üç katman: dolgu (degrade olabilir) + kalın beyaz kenar + renkli dış kenar/gölge. CSS: `-webkit-text-stroke` + çok katmanlı `text-shadow`, ya da SVG `paint-order: stroke`. Font: Fredoka / Luckiest Guy / Poppins Black (Türkçe testli).
- Giriş: `scale` 0→1.15→1, ~8 kare; ya da harf harf 2 kare arayla zıplama. Olaydan 2–3 kare sonra belirir (daha doğal). Dururken hafif wiggle (±1.5°, timeline'a bağlı).
- Duygu eşlemesi: şaşkınlık → patlama çerçevesi + hız çizgileri + beyaz flaş (2 kare); utanma → ter damlası; laf sokma → eğik el yazısı; onay → mühür (`serif-stamp` ile değil, yuvarlak lastik mühür).
- Renk: doygun pembe/sarı/camgöbeği + beyaz kenar. Seçilen stilin paletine uyarla (BRAND'de vurgu rengi + açık renk kenar).
- Ses: `pop`, `boing`, `ding`, `record_scratch` (mgaudio). Kaynak: `references/mg-styles-15/demos/18-hanazi`.

---

## 4. Arayüz ve ekran

Ortak kural: gerçek ürün ekranı varsa onun ekran görüntüsü/kaydı kullanılır; arayüz taklitleri sade, markayı taklit etmeyen ama tanıdık bileşenlerle yapılır.

### `prompt-bar` (Prompt bar)
Yapay zeka giriş çubuğu: metin harf harf yazılır, imleç yanıp söner, gönder butonu basılır.
- REG: `ai-chat-reveal, claude-exchange, chatgpt-exchange, typing-indicator`. Yazma hızı ~35 karakter/sn, kelime aralarında küçük duraklama.
- Varyant (referans ek — stil A, `20-efekt`): krem çubuk, üstte küçük mono etiket "PROMPT"; gönderilince metin italik serife döner, etiket "GÖNDERİLDİ", koyu yeşil yuvarlak buton onay işaretine.

### `chat-drop` (Chat Drop)
Sohbet balonları tek tek düşer (konuşanın yanında).
- REG: `chat-thread, message-thread-reveal, chat-message`. Balon girişinde küçük yay (`back.out(1.6)`), pop sesi.

### `chat-takeover` (Chat takeover)
Sohbet arayüzü tüm ekranı kaplar, konuşma oynar, sonra küçülüp konuşana döner.
- REG: `ai-chat-reveal`. Giriş: kart konuşanın yanından tam ekrana büyür (`flip` hissi).

### `comment-bubble` (Comment Bubble)
Tek bir sosyal medya yorumu konuşanın yanında belirir ("@kullanıcı'ya cevap").
- REG: `yt-comment-card`.

### `notification-stack` (referans ek — stil A)
Bildirimler üst üste yığılarak gelir. REG: `notification-cascade, macos-notification, liquid-glass-notification`.

### `qa-card` (referans ek — stil A)
Instagram soru kutusu: "Question 1" etiketi + soru, video boyunca üstte sabit; her soruda değişir.

### `model-picker` / `effort-dial` / `calendar-fill` / `render-progress` / `waitlist` / `envelope-reveal` (referans ek — stil A)
Konuşulan kavramı taklit eden küçük arayüz anları: açılır menüden seçim + imleç; LOW–MAX kadranı dönen ibre; haftalık takvimin dolup boşalması; render ilerleme çubuğu; bekleme listesine "you" yazılması; zarfın açılıp kartın çıkması. Hepsi HF, krem kartlar, `styles.md` A.

### `cursor-tracker` (Cursor tracker)
Büyük imleç ekrandaki öğeleri gösterir, tıklamada dalga; kamera imleci takip ederek yaklaşır.
- REG: `oversized-cursor, cursor-zoom-follow, press-ripple, agent-cursor`.

### `apple-ui-key` (Apple ui key)
Apple tarzı büyük klavye tuşu (⌘, Enter, Space) basılır; tuş aşağı iner, yazı belirir.
- `BL` `keycap` sahnesi (alfa) veya HF 3D CSS. Basış: 0.08 sn aşağı, 0.15 sn geri, tok tık sesi.
- `keycaps` yağmuru (referans ek — stil A, `20-efekt`): krem tuşlar (⌘K, ⌘Z, ⌘B, space, J/K/L, ⇧; birkaçı yeşil ⌥ ⌘), altlarında küçük etiket ("geri al"), üstten düşüp kafanın üstünde yığılır (`gravity-drop`, ±12° dönüş), 0.06 sn arayla. Konuşulan kısayollarla eşleştir.

### `jiggle-delete` (Jiggle delete)
iOS ana ekran düzenleme: ikonlar titrer, X'e basılır, ikon küçülüp kaybolur, diğerleri kayar.
- HF: titreme `rotation` ±2.5°, her ikon için faz farkı, timeline zamanına bağlı sinüs (setInterval yok).
- Varyant (referans ek — stil A, `20-efekt`): krem panel, mono başlık ("DÜZENLEME MODU · 4 uygulama"), ikonlarda eksi rozeti, sırayla silinir, panel boş kalır. Gerçek uygulama ikonu marka öğesidir: sade harf karosu kullan ya da kullanıcının kendi ekran görüntüsünden al.

### `icon-strike` (Icon strike)
Araç/uygulama ikonları sıralanır; kırmızı çizgiyle üstleri çizilir veya X ile vurulur, sarsılır, solar.
- REG: `icon-swap, headline-slam`. Çizik: SVG `stroke-dashoffset`.
- Varyant (referans ek — stil A, `20-efekt`): ikonlar sol üstte, pembe kalem çizgisi ikisinin üstünden geçer, ikonlar dönerek aşağı düşer, yerine italik serif tek kelime ("strike.") belirir.

### `file-drop` (File drop)
Dosya ikonu sürüklenip bir pencereye bırakılır; bırakma alanı parlar, yükleme çubuğu dolar.
- REG: `cursor-drag-drop`.

### `nle-timeline` (NLE timeline)
Video editör zaman çizelgesi: renkli klipler, oynatma kafası ilerler, klipler kesilir/kayar.
- REG: `beat-timeline, keyframe-scrub-stack`. Klipler gerçek kurgudaki planlardan üretilebilir (`scenes.json`).
- Varyant (referans ek — stil A, `20-efekt`): alt üçte birde koyu yeşil panel ("Timeline 00:00:00:00"), V1'de küçük etiketli klipler soldan dolar, A1 dalga formu, başlık izi altın, oynatma kafası kırmızı; çıkışta panel yatay çizgiye çöker (`scaleY`→0.02, 0.2 sn).

### `storyboard-deck` (Storyboard deck)
Storyboard kareleri kart destesi gibi dağıtılır, ızgaraya dizilir, biri seçilip büyür (stil A'daki "shot board").
- HF; kare görselleri `snapshot` veya `keyframes/` çıktılarından.

### `grade-slider` (Grade slider)
Kaydırıcı sürüklendikçe görüntünün renk düzenlemesi değişir; çizginin solu ham, sağı düzenlenmiş.
- İki versiyon üret (`MT` ile graded/ham), kaydırıcı konumuyla `clip-path: inset()` maske. REG: `grade-split-reveal`.

### `eyedropper-grade` (Eyedropper grade)
Damlalık imleci kareden renk seçer, renk örneği çıkar, ardından o renge göre grade uygulanır.
- HF imleç + renk dairesi; geçiş iki `MT` versiyonu arasında yumuşak fade.

### `product-demo` (Product Demo)
Ekran kaydı cihaz çerçevesinde; imleç tıklamaları, önemli yerlere zoom, etiketler.
- REG: `device-frame-stage, browser-device-stage, cursor-zoom-follow, ui-focus-zoom`.

### `sticker-explainer` (referans: `mg-styles-15` 19 — Sticker Explainer)
Açıklama videosu dili: fotoğraflar kalın beyaz kenarlı çıkartmaya döner, düz ikonlar ve kesin grafiklerle dev bir tuvale dizilir; tek kesintisiz kamera hareketi bilgi noktalarını dolaşır.
- Çıkartma: `paper_cutout.py <foto> --look color --border 10 --rough 0` (8–12 px düzgün beyaz kenar, yumuşak gölge).
- Tuval: kompozisyondan büyük kapsayıcı (ör. 4000×7000), kamera = kapsayıcının `x/y/scale` keyframe'leri, uzun ease (`power3.inOut`, 0.8–1.2 sn). Her cümle yeni bir öğe getirir.
- Grafikler gerçek veriyle: çubuk büyür + sayaç (`tick`), harita yolu çizilir, etiketli parça patlatma (leader line).
- Sakin zemin (`#E9EEF2` + arduvaz), 2–3 renk + tek vurgu; eşit kalınlıkta sans.
- Kaynak: `references/mg-styles-15/demos/19-paperclip`.

### `phone-mockup` (Phone Mockup)
Video veya ekran görüntüsü telefon içinde; düz, perspektifli veya 3D dönen.
- REG: `vfx-iphone-device, device-frame-stage, multi-device-splay, app-showcase`. Gerçek 3D: `BL` `phone` sahnesi (ekrana görsel/video dokusu).

### `pixelated-closeup` (Pixelated screen close up)
Ekrana makro yakınlaşma: RGB alt pikseller görünür hale gelir.
- HF canvas: görüntüyü düşük çözünürlükte `image-rendering: pixelated` ile büyüt + RGB şerit maskesi üstte; uzaktan yakına 1.0→12 zoom, sonra keskin kesme.

### `ui-world` (Ui world)
Kamera sonsuz bir arayüz paneli uzayında süzülür (paneller farklı derinliklerde).
- REG: `parallax-device-dive, ui-focus-zoom`. Büyük ölçekte `BL` (`card` sahnesi çoğaltılarak).

### `liquid-glass` (Liquid Glass)
iOS 26 tarzı kırılmalı cam paneller.
- REG: `ios26-liquid-glass, liquid-glass-notification, liquid-glass-widgets, vfx-liquid-glass, macos-tahoe-liquid-glass`.

### `freebie-doc` (Freebie doc)
"Ücretsiz rehber" belgesi: kapak sayfası uçarak gelir, sayfalar yelpaze açılır, "yorum yaz, gönderelim".
- HF; belge kapağını bir kez tasarlayıp `LIB`'e kaydet; varyant `held-object` ile kişinin elinde.

### `headline-storm` (Headline storm)
Çok sayıda haber başlığı hızla, kaotik ve katman katman ekrana yağar (gerginlik/kanıt).
- HF: 20–40 başlık kartı, seeded rastgele konum/dönüş, 0.05 sn arayla; kamera hafif sarsıntı. Başlıklar gerçek haberlerden ise kaynak göster.

### `headline-wall` (Headline wall)
Başlıklar bir duvar ızgarası oluşturur; kamera geri çekilip duvarın büyüklüğünü gösterir.
- `headline-storm` kartları + `pull-back-reveal`.

### `magazine-cover` (Magazine Cover)
Kare dondurulur ve dergi kapağına dönüşür: dergi adı kafanın arkasında (`MASK`), kapak yazıları, barkod.
- REG: `freeze-frame-dressing`.
- Varyant (referans ek — stil A, `20-efekt`): üstte mono sayı bandı ("EKİM 2026 · EFEKT SAYISI"), sol üstte küçük "KAPAKTA" + kalın başlık, dev serif dergi adı kafanın arkasında, sol altta barkod, ince altın çerçeve; 0.6 sn'de altın yuvarlak etiket ("tek *çekim*") `scale` 0→1.1→1 ile gelir.

### `effect-index` (referans ek — stil A, `20-efekt`)
"Bu videoda" dizini: sağda sabit yeşil panel, numaralı liste; konuşulan madde beyaz hapla işaretlenir, sayaç "07 / 20" ilerler, bitince alt satır altın olur. Liste videolarının (5 ipucu, 3 araç, 20 efekt) omurgası.
- Panel `#163227`, köşe 10 px, sağdan 14 px içeride; genişlik ekranın ~%29'u, yükseklik ~%47'si, üst %6'dan başlar.
- Başlık mono, harf aralıklı ("BU VİDEODA · 01 / 20"). Maddeler Inter 500 + sönük numara; geçmiş maddeler krem %90, gelecek %45, aktif madde beyaz hap `#F6F6F4` içinde koyu metin. Alt satır kalın ("+40 efekt daha"), finalde altın zemin `#BCA562`.
- Hap, madde söylendiği kelimede bir alt satıra kayar (0.2 sn `power2.out`).
- Sağ güvenli alanı (140 px) bilerek kaplar: kişi kadrajın sol-ortasında durmalı (çekim notu), kartlar panelin solunda kalır.
- Uyarlama (yüz kadrajda klipten klibe 400–860 px kayıyorsa): sabit panel yerine her maddede ~1.2 sn görünen dizin kartı, `face_layout.py` ölçümüne göre yüzün boş tarafında (genişlik ~244, y 640–1220); sol üstte kalıcı küçük etiket ("03/08 · Quiz"). Maddenin arayüz kartı aynı sütundaysa dizin kartı çekilince girer.
- Üst başlık: "20 efekt. *20 saniye.*" — Instrument Serif krem + italik altın. Açılış altyazısı `pill-caption`.

### `screenplay-page` (referans ek — stil A, `20-efekt`)
Ekran senaryo sayfasına döner: daktilo yazısıyla sahne başlığı ("İÇ. YEŞİL ODA – GÜNDÜZ"), karakter adı, "(kameraya)", konuşulan cümle; söylenen kelime fosforlu kalemle işaretlenir, geçmiş kelimeler soluk; altta "KESME:".
- Kâğıt `#F1EBDF` tam ekran, üstten hafif eğik kayarak gelir (`rotation` -2°→0, `y` -100%→0, 0.35 sn).
- Font Courier Prime (Google Fonts, OFL; Türkçe tam). Senaryo düzeni: karakter adı ortada, diyalog dar sütun.
- Vurgu kelime zamanına kilitli: `#D6C49A` dikdörtgen soldan sağa büyür (0.12 sn). Geçmiş kelime `#8C877D`.

---

## 5. Veri ve grafikler

### `growth-curve` (Growth Curve)
Üstel eğri çizilir, ucunda parlayan nokta, eksende sayılar akar.
- REG: `mk-line-graph, data-chart`. Çizgi: SVG `stroke-dashoffset`; uç noktası çizgiyle birlikte.

### `velocity-line-graph` (Velocity line graph)
Çizgi grafiği hızla çizilir; eğim arttıkça çizgi kalınlaşır/parlar, hız hissi (whoosh).
- `growth-curve` + çizim hızı eğriye bağlı (`power4.in`), iz bulanıklığı.

### `dynamic-checklist` (Dynamic Checklist), `checklist-pop` (Checklist pop), `checklist` (Checklist)
- `checklist`: madde listesi ve onay işaretleri.
- `dynamic-checklist`: maddeler konuşmayla senkron belirir ve konuşuldukça işaretlenir; üstü çizilenler (kırmızı kalem) de olabilir.
- `checklist-pop`: her onay işareti yaylanarak (scale 0→1.3→1) ve tık sesiyle gelir.
- REG: `marker-checklist-card, mk-specs-list`.

### `before-after` (Before + after)
Kaydırmalı karşılaştırma veya yan yana.
- REG: `before-after-wipe, comparison-split, split-tilt-cards`.

---

## 6. Kâğıt, el çizimi ve doku

### `paper-cutout` (Paper cutout)
Kişi veya nesne kâğıttan kesilmiş gibi: beyaz kalın kontur, gölge, 12 fps adımlı (stop-motion) hareket, kâğıt dokusu.
- Durağan görsel ya da donmuş kare: `scripts/paper_cutout.py <görsel> -o <png> --border 16` (ayrıntı `photo-collage`'da). Video kişi: `MASK` + kontur. Adımlı hareket: GSAP `steps()` ease. Varyant **kâğıt yırtma** (stil B): üst katman (renkli kâğıt) yırtık kenar maskesiyle ikiye ayrılır, altındaki görüntü açılır; yırtık kenar dokusunu bir kez üret ve `LIB`'e kaydet.

### `photo-collage` (Photo collage cutout — referans: `social-post-tv-collage`)
Siyah-beyaz kesilmiş fotoğraf figürleri (takım elbiseli adam, dev obje, gravür el, TV kafa) saten ya da düz zeminde, arkada soluk ızgara, kalın sans başlık. Figür cümlenin metaforunu taşır: "zaman yetmiyor" → dev saat taşıyan adam, "kendi tarzın" → TV kafalı adam, "tek bir kural" → işaret parmağı gravürü.
- **Görsel:** kullanıcı getirir (`materials.md` → kolaj görselleri); Claude prompt'u yazar (aşağıda). Lisans: kendi ürettiği (`--license ai`, prompt `--source`'ta), kendi fotoğrafı ya da kamu malı arşiv. İnternetten rastgele bulunmuş görsel ve tanınmış kişi yok.
- **Çevirme:** `python3 <skill>/scripts/paper_cutout.py <görsel> -o hf/assets/img/<ad>.png`
  - `--look bw` referans görünümü (gri ton + baskı kontrastı + gren), `halftone` gazete noktası, `color` renk korunur, `retro` eski renkli baskı (soluk mürekkep, sararmış kâğıt, kalıp kayması, ince nokta, lif). `--creases 1-3` katlanma izi (retro ile).
  - `--border 14-20` kâğıttan kesilmiş kenar (kırık beyaz `#F5F2EA`, retro'da sararmış), `--rough 0-2` makas düzensizliği. Referans kenarsızdır (`--border 0`); kenarlı hâl el yapımı/çıkartma hissi verir.
  - `--cut scissor`: dergiden makasla kesilmiş, köşeli sade kesim çizgisi; içinde görselin kendi zemini kalır. Maske kusurlu olduğunda en sağlam seçenek.
  - Maske: fotoğrafta varsayılan (`ai`). Düz/gradyan zeminde ayrıntılı illüstrasyon (ateş, tüy, alev) → `--mask both` (yapay zekâ + doku; yapay zekâ koyu formaları delik bırakabiliyor). Koyu zeminli görselde kenardaki parıltı için `--trim-dark` (kişi fotoğrafında kullanma: siyah saç ve kıyafeti yer).
  - "vs" görseli (iki figür karşı karşıya): `--split` → `<ad>_sol.png`, `<ad>_sag.png`; her figür ayrı hareket eder.
  - Beyaz zeminli gravür/çizim: `--white-bg` (yapay zekâ maskesi ince çizgileri yer; kenardan doldurma korur).
  - Örnek (iki figürlü "vs" görseli): `--mask both --look retro --border 18 --creases 2 --trim-dark --split`.
  - Gölge pişmiş gelir; HF'de gölge de animasyonlu olacaksa `--no-shadow` + CSS `filter: drop-shadow(0 18px 22px rgba(0,0,0,.3))` (görsele CSS filtresi serbest, footage'a değil).
- **Zemin:** `satin-bg` ya da düz vurgu rengi. Figürün arkasında %6–8 opak ızgara (`repeating-linear-gradient`, 48–56 px), `mask-image: radial-gradient` ile kenarlara doğru söner.
- **Giriş:** alttan 120 px kayarak + 1.06→1 ölçek, 0.35 sn `power3.out`; ya da **kâğıt tokat**: `steps(3)` ile -8°→-2° dönüş ve 1.12→1 ölçek + `kagit_` efekti. Durduğu sürede 12 fps kaynama: her 0.083 sn'de seeded ±0.6° dönüş ve ±2 px kayma (timeline'a bağlı, `Math.random` yok).
- **Başlık:** Inter Tight 700, `letter-spacing: -0.03em`, 2 satır, ikinci satır daha büyük; kelime kelime belirir. Figürün kafası yazının önüne geçebilir (figür katmanı yazının üstünde).
- **Varyantlar:**
  - *Nesne kafa:* kafanın yerinde TV, kitap ya da monitör (görseli öyle ürettir). TV ekranına kullanıcının videosu `clip-path` ile yerleşir.
  - *Daire rozet:* figürün arkasında vurgu renginde daire, 0→1 `back.out(1.6)`.
  - *Seçici renk:* tek ayrıntı renkli (saat akrebi sarı). Görseli bir kez `bw`, bir kez `color` kes; renkli parçayı `clip-path` ile üst katmana koy.
  - *Perde açılış:* iki dikey panel (vurgu rengi + mürekkep) yana kayarak açılır, arkasından gravür el yükselir.
- **Prompt şablonu** (beyaz zemin her zaman istenir, kesim temiz çıkar):
  - Fotoğraf: `Vintage black and white photograph of <figür + eylem>, full body, isolated on plain pure white background, studio lighting, high contrast, sharp detail, surreal photo collage style, no text`
  - Gravür: `Vintage copperplate engraving illustration of <nesne>, fine stipple and crosshatch shading, black ink on pure white background, isolated, no text`
  - Nesne kafa: `... businessman in a black suit whose head is a <1970s CRT television / old book / ...>, ...`
- **Ses:** giriş `kagit_cevirme` ya da `whoosh_kisa`, tokatta `kagit_` + hafif `tik_`.
- **Kişinin arkasında:** parça omzun arkasından çıkıp geri girecekse `shoulder-peek`.
- **mg-styles-15 Collage'dan teknikler:** kukla animasyonu (pivotlar omuz/dirsek/çene; parça parça döndür), ağız ayrı kesik ve 2–3 karelik değişimle konuşmaya eşlik eder, kafa kapak gibi açılıp içinden nesneler dökülür (Gilliam). Hareket 12 fps, bekleyişte 6 fps; ±2 px el titremesi. Katmanlar: kâğıt dokusu (`kagit_doku_paper001`) → büyük renk blokları → kesik fotoğraflar → bant (`washi_bant`) ve karalama → gren. Geçiş: el öğeyi sayfaya tokatlar ya da sayfa çevrilir. Kaynak: `references/mg-styles-15/demos/06-collage`.

### `satin-bg` (Satin background)
Dalgalanan parlak saten kumaş zemin (kolaj stilinin arka planı). Paralel, hafif eğik geniş kıvrımlar; açık alan geniş.
- `python3 <skill>/scripts/satin_bg.py -o hf/assets/video/satin.mp4 --seconds <sahne süresi>` → tam ekran `<video muted>` clip. Döngü dikişsizdir ama HF'de `loop`'a güvenme: uzun sahnede aynı dosyayı art arda iki clip olarak koy.
- `--dark/--light` renkler (gri varsayılan; mavi `#0F3A9E`/`#4A8DF7`), `--speed 1-3` hareket, `--seed` farklı kıvrım dizilimi; `.png` çıktısı hareketsiz zemin. Hazırları: `library.py search saten`.

### `doodle-boil` (Doodle boil)
El çizimi oklar, daireler, yıldızlar; çizgiler "kaynar" (her 2–3 karede hafif farklı çizim).
- REG: `hw-boil, hw-callout-circle, hw-underline, hw-scribble-transition`. Kaynama: 3 varyant, 8–12 fps döngü, timeline'a bağlı.
- mg-styles-15 Line Boil'dan: değişken kalınlıklı fırça (merkez çizgi + basınç → kontur), 3–4 titreşim varyantı her 2 karede bir; hızlı harekette tek karelik smear (nesne %150–300 uzar); kâğıt dokusu multiply %10–15. Kaynak: `references/mg-styles-15/demos/05-cel-boil`.

### `halftone-frame` (referans ek — stil B)
Plan yuvarlak köşeli karta küçülür, üstünde halftone nokta dokusu, arkada dev bulanık yazı. REG: `halftone-field`.

### `live-markup` (referans ek — stil A, `20-efekt`)
Görüntü siyah-beyaza döner, pembe kalemle yüzün etrafına el çizimi daire çizilir, el yazısı kelime yazılır ve oktan daireye bağlanır.
- S/b: `MT` ile, 0.15 sn geçiş (footage'a CSS filtresi yok).
- Daire: hafif düzensiz SVG path, uçları üst üste biner, `stroke-dashoffset` 0.35 sn. Yazı: Yellowtail ya da Caveat (Google Fonts), `clip-path` ile soldan sağa açılır. Ok: path çizimi 0.2 sn.
- Kalem gül kurusu pembe (`#C2505E`–`#B86774`), 5–6 px, hafif `doodle-boil` (3 varyant, 12 fps). Daire yüzü izler: kişi oynuyorsa `TRACK`.
- Çıkış: çizimler 0.2 sn fade, renk geri gelir.

### `grease-pencil-sheet` (referans ek — stil A, `20-efekt`)
Krem kontak kâğıdında 35 mm film şeritleri (videonun kareleri, perforasyonlu; altta mono künye "<tarih> · HAM ÇEKİM · 0:41"); yağlı kalemle iyi kare daire içine alınır, kötüler çarpılır, kenara el yazısı not düşülür ("ölü an", "kes").
- Kâğıt `#F1EBDF`, 3 şerit × 3–4 kare. Kareler gerçek kurgudaki kesilen anlardan (`cuts.md`): çarpılan kareler gerçekten kesilen sessizlikler olsun.
- Kalem `live-markup` ile aynı; işaretler 0.15 sn arayla.
- Giriş: kart sol üstten kayarak (0.3 sn); çıkış: `snap-zoom` ile videoya punch-in.

### `contact-sheet-hook` (referans ek — stil A, `20-efekt`)
Tam ekran yeşil zeminde "CONTACT SHEET" başlığı ve 5×4 boş numaralı ızgara; kareler videonun kendi anlarıyla tek tek dolar, dolan kare altın çerçeveyle işaretlenir; sonra italik altın "HOOK" belirir ve kamera seçilen kareye dalıp videoya döner.
- Kareler: `FF` ile videodan 20 eşit aralıklı kare. Dolma 0.04 sn/kare; boş hücrede sönük mono numara (01–20).
- Zemin `#163227`, hücre kenarı ince `#2A4A3C`. Başlık Instrument Serif büyük harf krem; "HOOK" italik altın `#BCA562`, ~2× büyük.
- Çıkış: seçilen kareye `zoom-through-cut`. Anlatı: "kancayı seçtim", "en iyi anı buldum".

---

## 7. Görünüm ve renk

### `cinematic-grade` (Cinematic Grade)
Sinematik renk: sıcak orta tonlar, serin gölgeler (teal-orange) veya stil B'nin sıcak kırmızı görünümü.
- `MT` ile grade; seçenekleri `npx hyperframes grade-compare` ile tek karede yan yana karşılaştır, kullanıcıya seçtir.

### `film-look` (Film look)
16/35mm hissi: grain, halation (parlak kenarlarda kırmızı hare), hafif gate weave, vinyet; istenirse 2.39 letterbox.
- `MT` (grain, vinyet) + REG: `grain-overlay, light-leak`.
- Varyant (referans ek — stil A, `20-efekt`): grade + gren + kare kayması: 2–3 kez görüntü 6–10 px aşağı kayar ve üstte ince beyaz kare çizgisi görünür (projektör kaçırması), her biri 2 kare.

### `light-leak` (referans ek — stil B)
Kenardan sızan sıcak ışık geçişi. REG: `light-leak, light-sweep-pass`.

---

## 8. 3D ve mekân

### `extruded-3d-word` (referans ek — stil B/C)
3D kalınlıklı kelime ("PROOF", "EVIDENCE", "$40 MILLION"): kırmızı plastik, altın veya krom.
- `BL` `text3d` sahnesi, alfa webm; ya da REG: `extruded-logo`. `LIB`'e kelime + malzeme etiketiyle kaydet.

### `ai-scene-push` (referans ek — stil B)
Yapay zekayla üretilmiş bir sahne (müze koridoru, tablo) ve içine doğru kamera itmesi; üstüne 3D yazı.
- `AI` görsel (dikey 9:16, yüksek çözünürlük) → HF `scale` 1.0→1.25 + hafif `rotation`; derinlik için görseli 2–3 katmana ayırıp paralaks.

### `flying-card` (referans ek — stil B)
Broşür/kart 3D'de dönerek uçar ve damga basılır.
- `BL` `card` sahnesi (görsel dokulu) veya HF 3D CSS.

### `logo-outro` (referans ek — stil B)
Siyah zemin, ışık topları uçuşup birleşir, logo ve iletişim bilgisi belirir.
- REG: `logo-outro`. Işık topları seeded yollar + bloom. Logo `LIB`'den.

---

## 9. Sosyal, CTA ve kapanış

### `comment-cta` (Comment CTA)
Yorum kutusunda anahtar kelime yazılır ("EDIT"), gönder butonuna basılır.
- REG: `yt-comment-card, instagram-follow, tiktok-follow`.
- Varyant (referans ek — stil A, `20-efekt`, `comment-drop` ile birleşik): dev kalın "EDIT" harf harf yazılır, harfler yorum kutusuna düşer ("Yorum ekle… Paylaş"), cümle yazılır, Paylaş'a basılır, kart yorum olarak yerleşir; kalp kırmızıya döner ve sayaç artar, altına ikinci yorum ("sen · EDIT") düşer. Altta `pill-caption` "Comment EDIT".

### `comment-drop` (Comment drop)
Yorumlar yukarıdan düşüp yığılır (sosyal kanıt).
- REG: `thread-message-stack, notification-cascade`. Gerçek yorumlar kullanılır; uydurma yorum yazılmaz.

### `reel-feed` (Reel feed)
Telefonda dikey reels akışı kaydırılır (kanıt veya örnek videolar).
- `phone-mockup` + içerde videoların dikey kaydırması (`y` keyframe, her video 0.6 sn bekleme).

### `video-card` (Video card)
Konuşanın yanında yuvarlak köşeli kartta oynayan video, başlık ve ilerleme çubuğu.
- HF; kartın içinde `<video>` muted, sarmalayıcı zamanlanır.
- Varyant (referans ek — stil A, `20-efekt`): yatay video kartı sol üstte (oynat düğmesi, ilerleme çubuğunda bölüm çentikleri), altında yeşil başlık kartı: serif "Video card" + mono "WALKTHROUGH · 2 bölüm"; video ilerledikçe alt satır "01 Ham çekim" → "02 Bitmiş reels" olur.

### `playing-grid` (Playing grid)
Birden çok video karesi ızgarada aynı anda oynar; biri büyüyüp öne çıkar.
- REG: `dynamic-grid, transitions-grid`. Çok sayıda video render'ı yavaşlatır: önce `FF` ile küçük proxy'ler üret.
- Varyant (referans ek — stil A, `20-efekt`): eğik kartlar üstten savrularak gelir, kafanın üstünde 3×2 ızgaraya oturur, hepsi oynar.

### `grid-collapse` (referans ek — stil A, `20-efekt`)
Ekran yeşil zeminde onlarca video küçük resmiyle (önceki reels'ler, kanıt) dolar; sonra ızgara çöker: kartlar kenarlara savrulup küçülür ve arkadan konuşan kişi geri gelir.
- Izgara: düzensiz 3 sütun (masonry), köşe 6 px; giriş 0.04 sn arayla `scale` 0.9→1 + fade.
- Çöküş (0.4 sn): her kart merkezden dışa vektörde `x/y` + `scale`→0.4 + `rotation` ±8°, `power2.in`; yeşil zemin aynı anda solar.
- Görseller kullanıcının kendi videoları (`materials.md` → sosyal kanıt); başkasının içeriği değil.

### `reel-cascade` (referans ek — stil A, `20-efekt`)
Dikey reels kartları önce boş cam çerçeveler olarak eğik savrularak gelir, kafanın üstünde 4×2 ızgaraya oturur, içleri dolup oynamaya başlar.
- Cam: `liquid-glass` kart (beyaz %12, ince kenar), `rotation` ±10°→0, 0.05 sn arayla; oturunca içerik `opacity` 0→1 (0.2 sn), videolar muted.
- Konum üst %40; `effect-index` varsa onun solunda. `playing-grid` ailesi; fark cam iskeletten dolma.

---

## Yeni efekt eklemek

Kullanıcı yeni bir efekt adı verirse veya bir referansta katalogda olmayan bir şey görürsen:
1. Ne olduğunu iki cümleyle tanımla ve kullanıcıya teyit ettir (adlar kişiden kişiye değişir).
2. Registry'de ara, yoksa HF / MASK / TRACK / BL kombinasyonuyla tarif çıkar.
3. Çalışan versiyonu `LIB`'e şablon olarak kaydet ve bu dosyaya aynı formatta yeni bir bölüm ekle.
