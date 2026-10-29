# Malzeme listesi

Stil seçildikten sonra (SKILL.md 1.4) videonun neye ihtiyacı olduğunu çıkarmak için. İlke: **ücretsiz ve lisansı temiz olan her şeyi Claude kendisi getirir; kullanıcıdan yalnızca onda olanı ister.** Önce `library.py list` ile kütüphaneye bak; olanı tekrar isteme.

## Claude'un kendisinin halledeceği (kullanıcıya sorulmaz)

| Ne | Nereden | Not |
|---|---|---|
| Fontlar | google/fonts GitHub (OFL / Apache) → `library/fonts` | Türkçe glif testi (ğ ü ş ı ö ç İ Ğ Ü Ş Ö Ç) yapılmadan kullanılmaz |
| Müzik + efekt, storyboard anlarına kilitli | `scripts/mg_music.py` (mgaudio; `references/mg-styles.md`) | Stile göre tarif (B: trap, A/BRAND: lofi, C: ambient glass); telifsiz, atıf yok |
| Eksik efekt kategorisi (`kagit_`, `cizik_` …) | önce `mg_music.py` efekt listesi; gerçek kayıt gerekiyorsa `npx hyperframes media-use resolve --type sfx` (Openverse, CC0/CC BY) | BRAND önekiyle kütüphaneye, CC BY ise `library/audio/CREDITS.md` |
| Kâğıt dokusu, washi bant, gren, toz | önce kütüphane; yoksa ambientCG / Openverse (CC0) ya da `mg-styles-15/assets` (MIT), `library.py add` ile kaydet | önerilen adlar: `kagit_doku`, `washi_bant`, `gren_film35`, `toz_overlay` |
| 3D yazı, ikon, yörünge, telefon, tuş | Blender (`references/blender.md`) | Blender kuruluysa; değilse HyperFrames 2D/CSS 3D |
| Kişi maskesi, takip, transkript | `remove-background`, `track_point.py`, whisper | Yerel |
| Küçük resim, dondurulmuş kare, kanıt kesiti | Kullanıcının kendi çekiminden | |

## Stil başına

| | Çekim koşulu (rapordaki ölçüler) | Fontlar | Kullanıcıdan (zorunlu) | Kullanıcıdan (isteğe bağlı) |
|---|---|---|---|---|
| **BRAND** | kafa üstü ≥ %28 rahat; zemin her ton (dev yazı rengi zemine göre BRAND'in koyu ya da açık rengi); hafif hareket olur | Instrument Serif, Inter (Google Fonts, OFL) | — | logo + kullanıcı adı (kapanış), konuşmada geçen yazılımın ekran kaydı |
| **A Editoryal Yeşil** | koyu/dokulu duvar (üst bant < 95), sıcak lamba, tripod (hareket < 7), kafa üstü ≥ %30, mümkünse 2–3 açı | Instrument Serif, Inter (Google Fonts, OFL) | konuşmada geçen arayüzlerin gerçek ekran görüntüsü/kaydı (UI kartları) | gerçek yorum/DM görüntüleri (comment stack), önceki reels'ler (telefon çerçevesinde kanıt), logo |
| **B Kinetik Kırmızı** | sıcak pratik ışık, koyu sinematik ortam; elde/hareketli çekim olur; çok plan iyi | Poppins / Montserrat SemiBold, Anton / Bebas Neue, Yellowtail / Caveat (Google Fonts, OFL) | konuya özel B-roll: 4–6 adet, 2–4 sn (eller, klavye, ürün, ekran) | yapay zekâ sahne görselleri (yerel üretici yoksa kendi aracında üret, prompt'u Claude yazar), logo (logo-outro) |
| **C Cam Derinlik** | aydınlık düzenli oda (üst bant > 150), tripod, 4K, kişinin etrafında boşluk (kaplama ≤ %45) | Inter, Inter Tight (Google Fonts, OFL) | cam kartlara konacak gerçek ekranlar (profil, istatistik, ürün) ve fotoğraflar | belge/broşür (PDF/PNG), logo |

Çekim stili taşımıyorsa (raporda seçilen stil ≤ 1/3) `needs.md`'ye "Sonraki çekim için" bölümü ekle: o stilin çekim koşulundan 3–4 somut madde (tripod, baş üstü boşluk, zemin, ışık, yaka mikrofonu).

## Her videoda kontrol edilen genel liste

1. **Logo + kullanıcı adı** (SVG ya da şeffaf PNG ≥ 1000 px): bir kez alınır, `library/logos`'a kaydedilir, sonra sorulmaz.
2. **Konuşmada adı geçen yazılım/site/ürün:** gerçek ekran kaydı (macOS: Cmd+Shift+5, ≥ 1080p, 5–15 sn). Yoksa sade arayüz taklidi kart; marka taklidi değil.
3. **Sosyal kanıt:** yalnız gerçek ekran görüntüleri. Uydurma yorum/istatistik yok.
4. **Kolaj görselleri** (storyboard'da `photo-collage` varsa): figür başına bir görsel, PNG/JPG ≥ 1024 px, mümkünse beyaz zeminde. Kullanıcı kendi aracında üretir (ChatGPT, Gemini, Midjourney); Claude her figür için `effects.md` → `photo-collage` şablonundan prompt'u hazır yazar. Kendi fotoğrafı ya da kamu malı arşiv (Wikimedia Commons PD, Openverse CC0) da olur; internetten rastgele görsel olmaz. Gelmezse: yalnız tipografi + saten zemin. Codex (`media-use resolve --type image --provider codex`) yalnız hesabı Codex'te model açıyorsa çalışır; 2026-10'da bu hesapta açmıyordu.
5. **Müzik:** platformun trend sesi (müziksiz render) / `mg_music.py` ile ritme kilitli üretim (sert, trap, lofi, ambient — Claude yapar) / kütüphane / kullanıcının lisanslı parçası. Kullanıcı belirli bir şarkı ya da tür isterse Pixabay Music gibi atıfsız kaynaktan indirmesi istenir (`library/audio/music/`, `muzik_` önekiyle).
6. **Görüntüde başka kişi:** yayın izni teyidi.
7. **Ses kısıksa** (rapor < -28 LUFS): sonraki çekim için yaka mikrofonu önerisi.

## Format ve teslim yeri

- Kullanıcı ek malzemeyi `inbox/ek/` klasörüne bırakır (dosya adı serbest, listedeki numarayı söylemesi yeter).
- Görsel PNG/JPG ≥ 1080 px · video MP4/MOV ≥ 1080p · logo SVG ya da şeffaf PNG · müzik MP3/WAV.

## `work/needs.md` şablonu

```
# Malzeme listesi — <video> (stil: B)

## Benim hallettiklerim
- [x] Anton + Yellowtail fontları (OFL), Türkçe glif testi geçti
- [x] kagit_yirtma_01 efekti (Openverse CC0)
- [x] Müzik: trap 150 bpm, drop 00:02.1, kapanış 00:31.5 (mg_music.py, telifsiz)

## Senden gerekenler
1. [ ] Klavye B-roll'ü, 3 sn, MP4 → inbox/ek/ — "edit kısmı" anı (00:10). Gelmezse: chips kartı
2. [ ] Logo, SVG → inbox/ek/ — kapanış kartı (00:31). Gelmezse: yalnız yazı

## İsteğe bağlı
3. [ ] Önceki reels'lerinin ekran kaydı (telefon çerçevesinde kanıt) → inbox/ek/. Gelmezse: o an yalnız altyazı

## Sonraki çekim için (B'ye uyum 1/3)
- ...
```

Listeyi tek mesajda göster, cevabı bekleyip akışı durdurma: malzemeye bağlı anlar storyboard'da "(malzeme #n bekleniyor)" diye işaretlenir; gelmezse yedek plan uygulanır.
