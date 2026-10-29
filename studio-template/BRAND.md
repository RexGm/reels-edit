# BRAND.md — Video Edit Kuralları

> **Bu bir şablon.** Kendi renklerini, fontlarını ve kurallarını yaz; Claude her videoda bu dosyayı okur. Renk adları rol adıdır (Zemin, Metin, Vurgu…), değerleri istediğin gibi değiştir.

Bu dosya her video editinde okunur. İki katmanı var:

- **SABİT KİMLİK (Bölüm 1-6):** Her videoda aynı. Videoyu "bizim" yapan şey bu. Asla değişmez.
- **VARYASYON HAVUZU (Bölüm 7-9):** Her videoda farklı. Efektler, geçişler, kart animasyonları bu havuzdan seçilir ve videodan videoya döner.

Amaç: İzleyici hiçbir iki videoyu aynı bulmasın, ama her videoyu ilk saniyede tanısın.

---

## 1. Genel his

- Sakin, premium, editoryal. Dergi sayfası gibi; YouTuber kaosu gibi değil.
- Az renk, çok boşluk, büyük serif yazılar.
- Hareketler yumuşak ve kararlı. Zıplayan, sallanan, gökkuşağı efektler yok.
- Her grafik konuşulan şeyi anlatır. Süs olsun diye grafik eklenmez.

## 2. Renk paleti (sabit)

| Rol | Ad | Hex | Kullanım |
|---|---|---|---|
| Zemin | Gece | `#14161B` | Bölüm kartları, altyazı kutusu, kart zeminleri |
| Metin | Kâğıt | `#F2F0EB` | Ana yazı, aktif altyazı kelimesi, açık kartlar |
| Vurgu | Turuncu | `#FF6A3D` | Tek bir anahtar kelime, rakamlar, onay işaretleri |
| İkincil | Sis | `#8B9099` | Pasif altyazı kelimeleri, küçük etiketler, ayraç çizgileri |
| Uyarı | Kırmızı | `#E0454A` | Sadece üstü çizme, "yanlış" ve "yapma" anları |

Kurallar:
- Bir karede en fazla 3 renk.
- Vurgu rengi bir karede tek yerde kullanılır. Her şeyi vurgulamak hiçbir şeyi vurgulamamaktır.
- Açık kart üstünde vurgu rengini yazı rengi olarak değil, dolgu (hap, daire) olarak kullan; açık zeminde turuncu/sarı yazı okunmaz.
- Saf beyaz (#FFFFFF) ve saf siyah (#000000) kullanılmaz.

## 3. Tipografi (sabit)

| Rol | Font | Ağırlık | Not |
|---|---|---|---|
| Başlık, dev yazı, bölüm kartı | Instrument Serif | Regular, İtalik | Büyük ve sıkı satır aralığı |
| Altyazı | Instrument Serif | Regular | |
| Arayüz kartları, etiketler | Inter | 500 / 600 | Küçük ve net |

- **Türkçe karakter testi zorunlu:** İlk renderda `ğ ü ş ı ö ç İ Ğ Ü Ş Ö Ç` doğru görünüyor mu kontrol et. Sorun varsa başlık ve altyazı için Fraunces kullan.
- Dev yazılar tamamen BÜYÜK HARF veya tamamen İtalik olur; ikisi aynı kelimede birleşmez.
- Türkçe büyük harf dönüşümünde `i → İ`, `ı → I` kuralına uy (`toLocaleUpperCase('tr-TR')`).

## 4. Altyazı (sabit — imza öğesi)

- Kelime kelime gösterim, Whisper kelime zamanlarına göre.
- Aynı anda 2-4 kelime görünür, satır en fazla 1.
- Kutu: Zemin rengi, %92 opaklık, köşe yarıçapı 6px, iç boşluk 10px yatay / 4px dikey.
- Söylenen kelime Metin rengi, henüz söylenmemiş kelimeler İkincil renk.
- Videonun ana fikrini taşıyan 1-2 kelime Vurgu renginde olabilir.
- Konum: dikeyde ekranın %62-68'i arası, yatayda ortalı. Yüzü ve ağzı asla kapatmaz.
- Boyut (1080x1920 için): 58-64px.
- Dolgu kelimeler ("ııı", "şey", "yani" tekrarları) altyazıdan çıkarılır, kurgudan da kesilir.
- Altyazı stili hiçbir videoda değişmez. Varyasyon havuzuna dahil değildir.

## 5. Güvenli alanlar (sabit)

1080x1920 karede Instagram, TikTok ve Shorts arayüzü şu alanları kapatır:
- Üst 220px: hiçbir yazı yok.
- Alt 420px: hiçbir yazı veya kart yok (açıklama ve butonlar burada).
- Sağ 140px: önemli öğe yok (beğeni ve yorum ikonları).
- Kartlar ve dev yazılar bu alanların içinde kalır.

## 6. Ritim ve kurgu (sabit)

- İlk 2 saniyede bir görsel olay olur: dev yazı, kart veya güçlü bir zoom. Boş açılış yok.
- Sessizlikler ve nefes araları kesilir. Cümle arası en fazla 0.15 sn.
- Aynı plan en fazla 4 saniye kesintisiz kalır; sonra kesme, zoom veya kart gelir.
- Videonun %40-60'ında ekranda bir grafik öğesi (kart, dev yazı, bölüm kartı) bulunur. Kalan anlarda sadece konuşan kişi ve altyazı vardır; yüz de nefes almalı.
- Bölümlü videolarda (sorular, ipuçları, maddeler) her bölüm bir bölüm kartıyla başlar.
- Son 3 saniye: tek bir çağrı (yorum yaz / kaydet / takip et). Hepsi birden değil.
- Video süresi hedefi: 35-60 sn.

### Ses (sabit kurallar)

- Konuşma: -14 LUFS entegre, tepe -1 dBTP.
- Müzik konuşmanın altında ~-22 LUFS (-27 LUFS telefonda neredeyse duyulmuyor). `duck_music.py` bunu kendisi ayarlar. Konuşma başlayınca 150 ms içinde kısılır, sustuğunda 400 ms içinde geri gelir (ducking).
- Efektler konuşmanın en az 6 dB altında. Hiçbir efekt bir kelimeyi bastırmaz.
- Müzik videonun başında 0.5 sn'de açılır, sonunda 1.5 sn'de kapanır.

---

## 7. Varyasyon havuzu — geçişler ve kamera hareketleri

Her video için bu havuzdan **3-5 öğe** seç. Seçim kuralları Bölüm 10'da. Havuz, reels-edit skill'inin efekt kataloğundaki (`references/effects.md`) herhangi bir efektle genişletilebilir; storyboard'da katalog slug'ını yaz.

**Kesme ve geçişler**
- `G1` Sert kesme + 1.08x yaklaşma (punch-in)
- `G2` Sert kesme + 1.08x'ten 1.0x'e geri çekilme
- `G3` 6 karelik bulanık geçiş (blur dissolve)
- `G4` Siyah-beyaz flaş: 4-8 kare siyah-beyaz, sonra renge dönüş
- `G5` Daire maske: yüzün etrafında daire açılıp kapanarak plan değişimi
- `G6` Hızlı yatay kaydırma (whip pan), 8 kare, hareket bulanıklığıyla
- `G7` Zemin rengi bir perdenin soldan sağa silerek geçmesi (wipe)
- `G8` Hafif dijital zoom kayması: 3 saniye boyunca 1.0x → 1.05x

**Bölüm kartı stilleri** (videoda yalnız biri kullanılır)
- `B1` "Number / 2" klasik: küçük italik kelime, ayraç çizgisi, dev rakam
- `B2` Rakam ekranın kenarından kayarak girer, kelime harf harf yazılır
- `B3` Rakam kişinin kafasının arkasında belirir (kişi maskesi gerekir)
- `B4` Rakam yerine tek kelimelik başlık (örn. "MODEL", "STİL", "STORYBOARD")
- `B5` Kâğıt kart: krem bir kart yukarıdan düşer, üzerinde rakam ve başlık

## 8. Varyasyon havuzu — kart ve yazı animasyonları

**Kart giriş animasyonları** (her videoda 2-3 tanesi)
- `K1` Aşağıdan 40px kayarak + saydamlıktan gelme
- `K2` 0.92x'ten 1.0x'e büyüyerek gelme
- `K3` Kenardan kayma (kartın konumuna göre soldan veya sağdan)
- `K4` Kartlar üst üste yığılarak gelir (bildirim yığını gibi)
- `K5` Kart yazılıyormuş gibi açılır: önce çerçeve, sonra satırlar tek tek
- `K6` Kâğıt gibi hafif dönerek düşme (en fazla 4° dönüş)

**Kart türleri** (içeriğe göre seç, havuz değil kütüphane)
- Arayüz taklidi: model seçici, açılır menü, ayar kadranı, imleç tıklaması
- Liste kartı: madde madde, üstü çizme (Uyarı) veya onay işareti (Vurgu)
- Soru kartı: Instagram soru kutusu tarzı
- Bildirim / yorum yığını
- Takvim, saat, ilerleme çubuğu, render çubuğu
- Ekran kaydı penceresi (yuvarlak köşeli, hafif gölgeli)
- Kâğıt öğeler: not kartı, zarf, damga, isim etiketi
- Önce / sonra bölünmüş kart
- Başka içeriklerden kanıt ekranı (telefon çerçevesi içinde)

**Dev yazı stilleri** (her videoda 1-2 tanesi)
- `Y1` Tam ekran üst bölüme oturan BÜYÜK HARF başlık
- `Y2` Kelime kişinin kafasının arkasında (kişi maskesi gerekir)
- `Y3` Harf harf yazılan italik kelime
- `Y4` Rakamların tek tek sayarak gelmesi (1 → 2 → 3)
- `Y5` Kelime üstüste iki katman, biri hafif kaymış (yankı efekti)
- `Y6` Ekranın üst köşesinde küçük etiket + altında dev kelime

## 9. Varyasyon havuzu — ses efektleri

Ses dosyaları `library/audio/sfx/` (efektler) ve `library/audio/music/` (müzik) klasörlerinde, kategori önekiyle adlandırılır:

| Önek | Ne zaman | Örnek dosyalar |
|---|---|---|
| `whoosh_` | Kart girişi, kaydırma, whip pan | `whoosh_kisa_01.wav`, `whoosh_yumusak_02.wav` |
| `tik_` | İmleç tıklaması, onay, seçim | `tik_mouse_01.wav`, `tik_klavye_02.wav` |
| `pop_` | Bildirim, küçük öğe belirmesi | `pop_bildirim_01.wav` |
| `swoosh_` | Bölüm kartı | `swoosh_derin_01.wav` |
| `kagit_` | Kâğıt kart, zarf, not | `kagit_cevirme_01.wav` |
| `daktilo_` | Harf harf yazı | `daktilo_01.wav` |
| `vurgu_` | Dev yazı, rakam düşüşü | `vurgu_bass_01.wav` |
| `cizik_` | Üstü çizme | `cizik_kalem_01.wav` |
| `glitch_` | Dijital kesme, bozulma geçişi | `glitch_01.mp3` |
| `uyari_` | Yanlış/hata anı | `uyari_hata_01.mp3` |
| `muzik_` | Arka plan | `muzik_sakin_01.wav`, `muzik_enerjik_01.wav` |

Kütüphane ilk başta boştur. Claude eksik kategoriyi kendisi üretir (`mg_music.py`) ya da lisansı temiz kaynaktan (Openverse CC0/CC BY) bulup kütüphaneye ekler. Lisanslar `library/audio/CREDITS.md`'de; CC BY müzik kullanılan gönderilerde atıf zorunlu.

Kurallar:
- Aynı kategoride birden fazla dosya varsa videodan videoya dönüşümlü kullan.
- Bir video içinde aynı efekt dosyası art arda iki olayda kullanılmaz.
- Her grafik olayına efekt koyma. Grafik olaylarının yaklaşık %60-70'i efektli olsun; gerisi sessiz kalsın ki efektler yorucu olmasın.
- Claude sesleri duyamaz; efektleri dosya adına ve zamanlamaya göre yerleştirir. Seviye ve uygunluk preview'da insan tarafından kontrol edilir.

## 10. Seçim kuralları (varyasyonun nasıl döneceği)

Her video başında:

1. `edit-log.md` dosyasını oku.
2. Son 2 videoda kullanılan bölüm kartı stilini (`B`) tekrar seçme.
3. Son videoda kullanılan geçişlerin (`G`) en fazla 1 tanesini tekrar kullan.
4. Son videoda kullanılan dev yazı stilini (`Y`) tekrar seçme.
5. Müzik dosyası son 3 videoda kullanılmadıysa seçilebilir.
6. Seçimi içeriğe göre yap: sakin ve bilgilendirici videoda `G3`, `G8`, `K1`, `K5`; enerjik veya haber videosunda `G1`, `G4`, `G6`, `K4`.
7. Bir video içinde aynı geçiş en fazla 3 kez kullanılır.
8. Kişi maskesi gerektiren öğeler (`B3`, `Y2`) her videoda değil, en fazla iki videoda bir kullanılır.

Video bitince `edit-log.md`'ye şu satırı ekle:

```
- <tarih> | <video adı> | stil: BRAND | G: G1,G3,G5 | B: B2 | K: K1,K4 | Y: Y3 | müzik: muzik_sakin_01
```

---

## 11. Çalışma sırası

İş akışının tamamı `reels-edit` skill'inde (proje açma, Türkçe transkript, kesimler, storyboard onayı, kurulum, ses, kontrol, render, kayıt). Bu dosya sadece görünümü tanımlar.

## 12. Asla

- Altyazı stilini, renk paletini veya fontları değiştirmek.
- Emoji, parlayan neon, gökkuşağı, 3D dönen yazı, zıplayan çıkartma.
- Aynı anda ekranda ikiden fazla kart.
- Yüzü veya ağzı kapatan grafik.
- Telifli müzik veya efekt.
- Render'ı storyboard onayı almadan başlatmak.
