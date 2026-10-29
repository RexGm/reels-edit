# Referans videoyu birebir yeniden yapmak

Kullanıcı bir video gösterip "bunun aynısını yap", "bu tarzda yap" veya "şu efekti kopyala" dediğinde. Hedef: kullanıcının kendi çekimiyle, referansla aynı zamanlama, kompozisyon, tipografi, renk ve hareketi elde etmek.

Referanstaki **teknik ve stil** kopyalanır; başkasının görüntüsü, logosu, marka adı ve yüzü yayınlanacak videoya konmaz. Referans kendi kanalından değilse bunu kullanıcıya bir cümleyle hatırlat (yasak değil, sadece yayın öncesi bilgi). Bu kural sadece teknik kopyayı değil, "birebir" isteğini de kapsar: birebir = aynı yapı ve his, kullanıcının kendi içeriğiyle.

## 1. Referansı parçala

```bash
python3 <skill>/scripts/analyze_reference.py referans.mp4 references/analysis/<ad> --fps 4 --transcribe
```

- Kısa ve yoğun videolarda `--fps 4–6` (kinetik yazılar 0.25 sn'de değişiyor). Sakin videolarda 2 yeter.
- Aynı kadraj jump cut'ları kaçarsa `--scene 0.04`.
- `report.md`'yi oku, sonra `sheets/` ve `keyframes/` görsellerinin **hepsine** Read ile bak. Atlamadan bak: bir efekt çoğu zaman 3–6 karede olup biter.
- Kritik bir efekti çözmek için o aralığı kare kare çıkar:
  `ffmpeg -ss 6.0 -t 1.0 -i referans.mp4 -vf "fps=30,scale=360:-2,tile=6x5" work/efekt_6s.png`

## 2. Çözümleme tablosu

`work/breakdown.md` dosyasına her plan veya grafik olayı için bir satır yaz:

| zaman | plan/çekim | söylenen | grafik olay | efekt slug | katman sırası | font/renk | hareket (süre, ease) | ses |
|---|---|---|---|---|---|---|---|---|
| 0.00–0.50 | yakın, sol kadraj | "I'm gonna" | kelimeler gövdeyi sarar | text-on-path + mixed-type-words | video → yazı → fg | Poppins beyaz / Anton kırmızı | kelime başı 0.15 sn, expo.out | whoosh |

- Efekti `effects.md`'deki slug'larla adlandır. Katalogda yoksa yeni slug uydur ve `effects.md`'nin "Yeni efekt eklemek" adımlarını uygula.
- Fontları tanı: harf şekillerine bak (a, g, R, y kuyrukları), `styles.md`'deki ücretsiz karşılıklardan veya Google Fonts'tan en yakınını seç. Emin değilsen 2–3 adayı aynı kelimeyle render edip referans karesiyle yan yana göster.
- Renkleri karelerden örnekle (Pillow `getpixel`) veya `palette.json`'dan al.
- Süreleri kare sayarak ölç: 30 fps'te 1 kare = 0.033 sn.

## 3. Kullanıcının çekimini eşle

- Referansın çekim dili (açılar, mesafe, ışık) farklıysa en yakın karşılığı öner: tek kamerayla `digital-zoom` ile açı değişimi, B-roll eksikse `AI` veya kütüphaneden.
- Konuşma metni farklıysa yapı korunur: referanstaki her grafik anı, kullanıcının metnindeki eşdeğer kelimeye bağlanır. Eşleşmeyen anları kullanıcıya listele.

## 4. Kur ve kıyasla

1. Kompozisyonu çözümleme tablosuna göre kur (`SKILL.md` adımları).
2. Aynı anlardan kare al ve yan yana koy:
   ```bash
   python3 <skill>/scripts/compare.py referans.mp4 output/taslak.mp4 -o work/compare.png --every 0.5 --diff
   ```
   Zamanlar farklı uzunluktaysa (farklı metin) `--at` ile eşdeğer anları ver.
3. Farkları listele: konum, ölçek, font boyutu, renk tonu, giriş süresi, katman sırası. Her turda en büyük 3–5 farkı düzelt.
4. Renk için: `npx hyperframes grade-compare` ile birkaç grade adayını referans karesine en yakın olana göre seç.
5. Kullanıcı "tamam" diyene kadar 2–4 tur normaldir. Her turda compare.png'yi kullanıcıya da göster.

## 5. Kalıcı yap

Çözülen her yeni efekti şablon olarak kütüphaneye kaydet (`library.py add ... --kind template`), referansın analiz klasörünü `references/analysis/` altında bırak. Bir sonraki "o videodaki gibi" isteği sıfırdan başlamaz.
