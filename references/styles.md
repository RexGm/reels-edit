# Stil profilleri

Kullanıcının beğendiği dört referans videodan çıkarılmış üç stil. Ölçümler `scripts/analyze_reference.py` ile alındı (720x1280 kaynak, değerler 1080x1920'ye ölçeklendi). Renkler karelerden piksel örneklemesiyle alındı; fontlar, görünüşe en yakın **ücretsiz** Google Fonts karşılıklarıdır (orijinaller çoğunlukla ticari fontlar).

Bu profiller iki işe yarar:
1. **Birebir kopya** istendiğinde hedef değerler buradadır (`recreate.md` ile birlikte kullan).
2. **Kendi tarzımız** için yapı taşıdır. Projede `BRAND.md` varsa renk ve font orada yazandır; buradaki profillerden yalnızca hareket dili, ritim ve efekt seçimleri alınır.

İçindekiler: A. Editoryal Yeşil · B. Kinetik Kırmızı Sinematik · C. Cam Derinlik · Ortak dersler

---

## A. Editoryal Yeşil ("Claude edited this video" / "Masterclass Q&A")

**His:** Sakin, premium, dergi sayfası. Talking head + yoğun arayüz kartları. Kurgu hızlı ama grafikler yumuşak.

**Ölçümler**
- Kesme sıklığı: 10 sn'de 2.7–4.0 kesme; medyan plan 1.4–2.9 sn, en uzun plan 8–12 sn.
- Ses: -14.2 LUFS entegre, tepe -0.9 / -1.2 dBFS. Konuşma boşluksuz kesilmiş (sessizlik yok).
- Çekim: 3-4 farklı açı/mekân (masa geniş, yakın plan, ayakta geniş, koltukta), hepsi aynı oda paleti (koyu yeşil duvar, sıcak lamba).

**Renk**
| Rol | Hex |
|---|---|
| Ana yeşil (bölüm kartı zemini, altyazı kutusu) | `#1C382D` |
| Koyu yeşil (başlık zemini) | `#163227` |
| Krem (dev yazı, aktif kelime) | `#EDE6D8` |
| Pasif altyazı kelimesi | `#9FBFA5` (yeşile çalan açık ton) |
| Kart zemini (soru kartı, liste) | `#F7F5F0` beyaz-krem, metin `#1A1A1A` |
| Uyarı/çizik | gül kurusu `#C2505E` (üstü çizme kalemi) |

**Tipografi**
- Altyazı ve dev yazılar: yüksek kontrastlı, hafif dar serif → **Instrument Serif** (Regular + Italic). Büyük başlıklar BÜYÜK HARF ("CLAUDE EDITED"), bölüm kartında italik küçük kelime + dev rakam ("*Number* / 2").
- Arayüz kartları: **Inter** 500/600.

**Altyazı (imza öğesi)**
- Kutu: `#1C382D`, köşe yarıçapı ~4px, iç boşluk 14px yatay / 4px dikey, opaklık %100.
- Satırda 3–4 kelime; söylenen kelime krem, kalanı `#9FBFA5`. Kelime kelime ilerler (karaoke).
- Konum: yatay ortalı, dikeyde karenin %69–72'si. 1080x1920'de font ~58px.
- Bazı anahtar kelimeler altyazı yerine **ekranın üst üçte birinde italik serif tek kelime** olarak çıkar ("the model", "the effort level", "your computer") — yeşil, gölgesiz, yavaş fade.

**Grafik dili**
- Arayüz taklidi kartlar: model seçici açılır menü + imleç, effort kadranı (LOW–MAX), takvim haftası dolması, bildirim yığını, Instagram soru kutusu ("Question 1"), yorum yığını, bekleme listesi, gereksinim listesi + kırmızı kalemle üstü çizme, zarf/mühür, render ilerleme çubuğu, storyboard kart ızgarası, "Mini course" pencere kartı.
- Kartlar beyaz-krem, ince gri kenar, yumuşak gölge (0 8px 24px rgba(0,0,0,.18)), köşe 10–14px.
- Dev yazı kafanın arkasında (kişi maskesi): "CLAUDE EDITED", "1 2 3", "12".
- Bölüm kartı: tam ekran `#1C382D`, ortada italik "Number", altında ince çizgi + nokta, sonra dev rakam; yazılar hafif yukarı kayarak + fade.
- Siyah-beyaz flaş (bölüm başında 4–8 kare), daire maske zoom, bulanık geçiş.
- Başka reels'lerden kanıt: telefon çerçevesinde, hafif eğik kartlar.
- Kapanış: "Comment EDIT" yorum kutusu yazılıyor animasyonu.

**Hareket**
- Kart girişi: alttan 30–40px + fade, 0.35–0.45 sn, `power3.out`. Çıkış daha hızlı (0.2 sn).
- Liste maddeleri 0.12 sn arayla.
- Yaklaşma zoom'ları 1.0 → 1.08, kesmeyle anında (punch-in), ara sıra yavaş kayma.


**Ek referans `20-efekt`** ("20 effects. 20 seconds.", aynı üretici)
- Liste videosu kalıbı: 23 sn'de 20 efekt, her madde ~1.1 sn, söylenen ada kilitli. Kamera tek ve sabit (en uzun plan 10.7 sn); hareketi grafikler ve punch-in'ler veriyor. -14.1 LUFS.
- Omurga: sağda sabit `effect-index` paneli (`#163227`, aktif madde beyaz hap). Kişi kadrajın sol-ortasında oturuyor, sağ üçte bir panele ayrılmış.
- Yeni vurgu rengi: altın `#BCA562` (italik serif kelimeler: "*20 seconds.*", "*HOOK*", "*ring.*", finaldeki "+40" satırı). Kart yeşili `#1D392C`, kâğıt `#F1EBDF`, fosforlu kalem `#D6C49A`, kalem pembesi `#C2505E`–`#B86774`.
- Açılış: üstte başlık "20 effects. *20 seconds.*" (Instrument Serif krem + italik altın), altta `pill-caption` (beyaz satır kutuları, Inter 700, anahtar kelime koyu yeşil `#1B302D`).
- Efektler: `magazine-cover`, `knockout-captions`, `live-markup`, `film-look`, `jiggle-delete`, `screenplay-page`, `grid-collapse`, `prompt-bar`, `contact-sheet-hook`, keycaps (`apple-ui-key`), `comment-cta`, `picture-dive`, `nle-timeline`, `playing-grid`, `serif-stamp`, `icon-strike`, `grease-pencil-sheet`, `lens-ring`, `reel-cascade`, `video-card` — hepsinin bu videodaki varyantı `effects.md`'de `20-efekt` etiketiyle.
- Geçişler: panel dikey şeritlere bölünüp açılır, alt panel çizgiye çöker, contact sheet'ten kareye dalış, punch-in.

---

## B. Kinetik Kırmızı Sinematik ("Nobody cares about your logo")

**His:** Agresif, sinematik, reklam ajansı. Yazı her yerde ve hareket halinde; kişiyle iç içe geçiyor.

**Ölçümler**
- 29 sn, 13 plan: 10 sn'de 4.1 kesme, medyan plan 1.7 sn, en kısa 2 kare (flaş).
- Ses: -14.1 LUFS, tepe -2.5 dBFS. Yoğun SFX (whoosh, kâğıt, vurgu).
- Çekim: sinema kamerası, sığ alan derinliği, sıcak pratik ışıklar, desenli duvar kâğıdı. Bir plan dizüstü klavye B-roll'ü.

**Renk / görünüm**
- Sinematik grade: sıcak orta tonlar, turuncu-kırmızı pratikler, gölgeler yeşilimsi-gri, kontrast yüksek, hafif grain ve vinyet.
- Vurgu kırmızısı `#CC1F30`, beyaz `#F2F0EA`, siyah `#050505`.

**Tipografi (üç katmanlı karışım, imza öğesi)**
1. Gövde kelimeler: yuvarlak geometrik sans, beyaz, hafif glow → **Poppins** SemiBold veya **Montserrat** SemiBold (küçük harf).
2. Vurgu kelimeler: kırmızı, kalın, dar, çoğu zaman italik ve BÜYÜK HARF → **Anton** veya **Bebas Neue** (+ skew -8°). 3D ekstrüzyonlu versiyonları da var ("EVIDENCE", "PROOF", "TRUST").
3. Süs kelimeler: küçük el yazısı/script ("on", "you're", "actually") → **Yellowtail** veya **Caveat**, beyaz, gövde kelimenin üstüne bindirilmiş.

**Grafik dili**
- Kelimeler kişinin gövdesini **kavis boyunca sarar** (text on path), bazıları kafanın arkasından geçer (kişi maskesi).
- Kelime kelime belirme ama sabit satır yok; her kelime kendi konumuna "atılır" (scale 1.3→1 + blur 8→0, 0.15 sn).
- Tasarım yazılımı seçim kutusu (kırmızı tutamaçlar) bir kelimenin etrafında: "logo".
- Kâğıt yırtma: kırmızı kâğıt yırtılır, altından para görünür (paper cutout / tear reveal).
- Yüz parçası kolajı: göz, ağız gibi dikdörtgen kırpımlar kişinin üstüne dağılır (image collage).
- Uçan 3D broşür/kart, üzerinde damga ("PROOF").
- Çerçeve içinde çerçeve: plan yuvarlak köşeli karta küçülür, halftone dokusu, arkada dev bulanık marka yazısı.
- Yapay zekayla üretilmiş sahne: müze koridoru, güneş gözlüklü tablo, kamera ileri itilir (dolly) — sonra 3D kırmızı "PROOF".
- Siyah-beyaz flaşlar, ışık sızıntısı, hareket bulanıklığı geçişleri, dev dönen kırmızı harfler ("WE").
- Kapanış: siyah zemin, ışık topları uçuşup logoya dönüşür, altında iletişim bilgisi.

**Hareket**
- Çok hızlı girişler (0.12–0.2 sn), `expo.out`; bazı kelimeler 3D'de dönerek gelir (rotationX 90→0).
- Kamera sarsıntısı vurgu anlarında (2–4px, 6 kare).

---

## C. Cam Derinlik ("I'll be honest with you" — emlakçı)

**His:** Aydınlık, Apple reklamı gibi temiz, lüks. Kişi sakin konuşur; etrafında 3D cam arayüz uzayı.

**Ölçümler**
- 65 sn, 13 plan: 10 sn'de 1.8 kesme, medyan plan 4.2 sn. Kesmelerin çoğu aynı çekimde dijital zoom (geniş ↔ yakın) — tek kamera.
- Ses: -14.3 LUFS, tepe -0.7 dBFS.
- Çekim: 4K, aydınlık salon, sığ alan derinliği, kişi ortada koltukta.

**Renk / görünüm**
- Parlak, düşük kontrast, sıcak beyazlar, cilt tonu korunmuş. Siyah flaş yok; **beyaz bloom flaşı** geçiş olarak (aşırı pozlama 6–8 kare).
- Yazı: beyaz; vurgu kelimelerde degrade (kırmızı→beyaz "AGENTS", çok renkli "2014", teal "HOME"), metalik altın "$40 MILLION", krom "2 YEARS".

**Tipografi**
- Altyazı: **tek kelime**, küçük, beyaz, kalın sans (SF Pro benzeri) → **Inter** 600, 1080x1920'de ~44px, hafif gölge. Göğüs hizasında, kişinin üstünde.
- Başlık kelimeleri: üstte küçük satır ("that most") + altında dev BÜYÜK HARF kelime ("AGENTS") → **Inter** 800 / **Inter Tight** 800, kafanın arkasında (kişi maskesi), kelime harf harf maskelenerek açılır.

**Grafik dili**
- Kişinin etrafında 3D uzayda yüzen cam/ekran kartları: Instagram profil ekranı (perspektifli telefon), fotoğraf kartları kişinin önünde yay şeklinde dizilip döner (depth scatter / carousel), sosyal medya gönderi ızgarası, analitik paneli **avucunun üstünde durur** (el takipli nesne), logo kartı, belge kişinin ellerinde (el takibi), bulanık/pixelli belge.
- 3D beyaz cam dişli ikonları dönerek belirir; krom küreler halka yörüngede döner (orbit), ince çember çizgisi.
- Profil kartı kişinin **arkasında** durur (derinlik katmanı).
- B-roll: siyah zemin üstünde yuvarlak köşeli film karesi, hafif grain, kenarda vinyet; altyazı devam eder.
- Rakam değişimi: "2014" → "2026" yerinde morph.

**Hareket**
- Yavaş ve yumuşak: kart girişleri 0.5–0.7 sn, `power2.out`, 3D'de hafif rotationY (15°→0) + z-derinlik.
- Kartlar ekranda dururken hafif süzülür (y ±6px, 3 sn döngü yerine timeline'a bağlı sinüs).

**Uyarlama: açık duvar / düz konuşma çekimi**
- Krem/beyaz duvarda beyaz dev yazı ve beyaz cam kaybolur: dev kelimeler grafit `#1A1D24` → renk degrade (teal `#0E8C96`, mor `#6E4BD8`, altın `#C99A2E`, kırmızı `#D8432F`); kartlar koyu cam `rgba(15,16,22,.78)` + 22 px blur, içi beyaz yazı.
- Grade: `skin-soft` 0.55, pozlama +0.04, kontrast −0.04, ışıklar −0.1, gölgeler +0.1, sıcaklık +0.04, vinyet 0.08. Bloom flaşı `--hf-color-grading-exposure` 0.85 → 0 (0.26 sn), video ve maskede birlikte.
- Tek açılı, sıkıcı çekim: C'nin yavaş ritmi hızlandırılır. Her cümlede dijital zoom kesmesi (1.0 ↔ 1.12–1.22), aralarda yavaş itme, kart girişleri 0.3–0.4 sn.
- Tam boy yakın çekimde (kafa ~700 px) altyazı göğüste (y 1440, Inter 700 58 px). Kartlar sol sütunda ya da kafanın üstündeki duvarda (`face_layout.py` ile ölçülür).
- Çok terimli anlatım için kalıcı ilerleme şeridi: üstte 4 cam hap, aktif terim renkli, biten ✓.

---

## Ortak dersler (üçünde de)

- Konuşma boşluksuz; -14 LUFS civarı; ilk 2 saniyede güçlü bir görsel (dev yazı veya hareket).
- Kişi maskesiyle **yazıyı kişinin arkasına koymak** üç stilin de imzası. Bu yüzden her projede `npx hyperframes remove-background` çıktısını erken üret.
- Altyazı stili tüm video boyunca sabit; değişen şey vurgu kelimeler ve kartlar.
- Grafikler konuşulan kelimeyle **aynı karede** başlar (kelime zaman damgasına kilitli), ±2 kare.
- Kapanışta tek çağrı (yorum yaz / logo).

---

## Teknik referansı: Kolaj ("Social Post and TV Character Collage Promo")

Stil sorusunda ayrı seçenek değildir (konuşan kişi yok, şablon tanıtımı); herhangi bir stile **Karışım** olarak eklenir: "B + kolaj figürleri" gibi. Video `references/videos/social-post-tv-collage.mp4`, analiz `references/analysis/social-post-tv-collage/`. Tarifler: `effects.md` → `photo-collage`, `satin-bg`.

**Ölçüler**
- 12 sn, 8 plan, 10 sn'de 5.8 kesme; plan ort. 1.5 sn (0.8–3.5).
- Renk: kırık beyaz `#FCFCFC`, vurgu mavisi `#2171E7`, mürekkep `#191919`, gri saten `#A0A0A0`–`#DDDDDD`. Tek sıcak ayrıntı: saat akreplerinde sarı.
- Font: kalın grotesk (Inter Tight 700 karşılığı), sıkı aralık, 2 satır; ikinci satır büyük ("make / Better Posts", "Pick a / template").

**Teknikler**
- Siyah-beyaz kesik fotoğraf figürleri: dev saat taşıyan adam, kafası TV olan takım elbiseli adam, kafası kitap olan oturan adam, gravür işaret parmağı.
- Gri saten zemin yavaşça dalgalanır; figür arkasında soluk ızgara.
- Mavi daire rozet figürün arkasında; TV ekranında kullanıcının görüntüsü.
- Açılış: mavi ve mürekkep iki dikey panel, arasından gravür el yükselir; yazı harf harf belirir.
- Eğik süzülen Instagram gönderi kartları (`social-proof` kartı ile aynı aile).
- Düz renk sahneler (mavi / beyaz) arasında tek kelime ("Ready", "to share") kesmeleri.
