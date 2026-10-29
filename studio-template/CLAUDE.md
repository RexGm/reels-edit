# reels-studio

Kısa dikey video (Instagram Reels / TikTok / YouTube Shorts) stüdyosu.

- Her video işinde `reels-edit` skill'ini kullan (`~/.claude/skills/reels-edit/`). HyperFrames kuralları için `/hyperframes` skill'ini de oku.
- Kendi videolarımızın görünümü `BRAND.md`'de; varyasyon geçmişi `edit-log.md`'de.
- Ham çekimler `inbox/`, her video `projects/<tarih>_<ad>/`, finaller `output/`.
- Tekrar kullanılabilir öğeler `library/` (yönetimi: `python3 ~/.claude/skills/reels-edit/scripts/library.py`).
- Beğenilen referanslar `references/videos/`, analizleri `references/analysis/`.
- Orijinal dosyalar (`inbox/`, `projects/*/media/`, `references/videos/`) değiştirilmez.
- Türkçe transkript: `npx hyperframes transcribe <video> --engine whisper --model large-v3 --language tr`.
- Storyboard onayı olmadan final render alınmaz.
