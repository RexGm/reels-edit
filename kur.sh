#!/usr/bin/env bash
# reels-edit kurulumu (macOS / Linux).
#
#   bash kur.sh            skill + stüdyo klasörü + Python paketleri + HyperFrames skill'leri + gürültü modeli
#   bash kur.sh --muzik    yukarıdakiler + kodla müzik/efekt üreten mgaudio (isteğe bağlı, ~1 GB)
#
# Tekrar çalıştırmak güvenlidir: var olan skill yedeklenip güncellenir, var olan stüdyodaki dosyalara dokunulmaz
# (yalnız eksik olanlar eklenir).
#
# Ortam değişkenleri: REELS_STUDIO (stüdyo yeri, varsayılan ~/Movies/reels-studio)
# Test için: SKIP_PIP=1 SKIP_HF=1 SKIP_NET=1
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STUDIO="${REELS_STUDIO:-$HOME/Movies/reels-studio}"
SKILL_DIR="$HOME/.claude/skills/reels-edit"
MUZIK=0
for a in "$@"; do
  case "$a" in
    --muzik|--müzik) MUZIK=1 ;;
    -h|--help) sed -n 2,12p "$0"; exit 0 ;;
    *) echo "Bilinmeyen seçenek: $a"; exit 1 ;;
  esac
done

b() { printf "\n\033[1m%s\033[0m\n" "$*"; }
ok() { printf "  \033[32m✓\033[0m %s\n" "$*"; }
uy() { printf "  \033[33m!\033[0m %s\n" "$*"; }
hata() { printf "  \033[31m✗\033[0m %s\n" "$*"; }

b "1/7 Gerekli programlar"
EKSIK=()
for c in node npx ffmpeg ffprobe python3 git; do
  if command -v "$c" >/dev/null 2>&1; then ok "$c"; else hata "$c bulunamadı"; EKSIK+=("$c"); fi
done
if command -v claude >/dev/null 2>&1; then ok "claude (Claude Code)"; else uy "claude bulunamadı: Claude Code'u kurmayı unutma (README → Adım 1)"; fi
if [ ${#EKSIK[@]} -gt 0 ]; then
  echo
  if [ "$(uname)" = "Darwin" ]; then
    echo "  Eksikleri kurmak için:  brew install node ffmpeg python git"
    echo "  (Homebrew yoksa önce README'deki Adım 2'ye bak.)"
  else
    echo "  Eksikleri paket yöneticinle kur, örnek:  sudo apt install nodejs npm ffmpeg python3 python3-pip git"
  fi
  exit 1
fi

b "2/7 Python paketleri (görüntü ölçümü, kolaj, takip)"
PKGS=(pillow numpy opencv-contrib-python-headless fonttools)
if [ "${SKIP_PIP:-0}" = "1" ]; then
  uy "atlandı (SKIP_PIP=1)"
elif python3 -c "import PIL, numpy, cv2, fontTools" >/dev/null 2>&1; then
  ok "zaten kurulu"
else
  # Homebrew Python'u "externally-managed": --user reddedilirse yalnız kullanıcı klasörüne zorla kurulur
  if python3 -m pip install --user --quiet "${PKGS[@]}" 2>/dev/null \
     || python3 -m pip install --user --quiet --break-system-packages "${PKGS[@]}"; then
    ok "kuruldu: ${PKGS[*]}"
  else
    hata "pip kurulumu başarısız. Elle dene:  python3 -m pip install --user ${PKGS[*]}"
    exit 1
  fi
fi

b "3/7 Skill → $SKILL_DIR"
mkdir -p "$HOME/.claude/skills"
if [ -d "$SKILL_DIR" ]; then
  YEDEK="$SKILL_DIR.yedek-$(date +%Y%m%d-%H%M%S)"
  mv "$SKILL_DIR" "$YEDEK"
  uy "eski sürüm yedeklendi: $YEDEK"
fi
mkdir -p "$SKILL_DIR"
cp "$HERE/SKILL.md" "$SKILL_DIR/"
cp -R "$HERE/references" "$HERE/scripts" "$SKILL_DIR/"
ok "kopyalandı (SKILL.md, references/, scripts/)"

b "4/7 Stüdyo klasörü → $STUDIO"
if [ -d "$STUDIO" ]; then
  # var olan dosyaların üstüne yazmadan yalnız eksikleri ekle
  (cd "$HERE/studio-template" && find . -type d) | while read -r d; do mkdir -p "$STUDIO/$d"; done
  (cd "$HERE/studio-template" && find . -type f) | while read -r f; do
    [ -e "$STUDIO/$f" ] || cp "$HERE/studio-template/$f" "$STUDIO/$f"
  done
  ok "zaten vardı; eksik dosya ve klasörler eklendi"
else
  mkdir -p "$(dirname "$STUDIO")"
  cp -R "$HERE/studio-template" "$STUDIO"
  ok "oluşturuldu (inbox/, projects/, output/, library/, BRAND.md, CLAUDE.md)"
fi
python3 "$SKILL_DIR/scripts/library.py" --root "$STUDIO/library" init >/dev/null && ok "kütüphane hazır"

b "5/7 HyperFrames skill'leri (video motoru)"
if [ "${SKIP_HF:-0}" = "1" ]; then
  uy "atlandı (SKIP_HF=1)"
elif npx --yes hyperframes skills </dev/null; then
  ok "kuruldu"
else
  uy "kurulamadı; sonra elle dene:  npx hyperframes skills"
fi

b "6/7 Gürültü temizleme modeli (RNNoise)"
RNN_DIR="$HOME/.local/share/rnnoise-models"
if [ -f "$RNN_DIR/sh.rnnn" ]; then
  ok "zaten var"
elif [ "${SKIP_NET:-0}" = "1" ]; then
  uy "atlandı (SKIP_NET=1)"
else
  mkdir -p "$RNN_DIR"
  if curl -fsSL -o "$RNN_DIR/sh.rnnn" "https://raw.githubusercontent.com/GregorR/rnnoise-models/master/somnolent-hogwash-2018-09-01/sh.rnnn"; then
    ok "indirildi: $RNN_DIR/sh.rnnn"
  else
    uy "indirilemedi; gürültü temizliği olmadan da çalışır"
  fi
fi

b "7/7 Müzik ve efekt üretici (mgaudio)"
if [ "$MUZIK" = "1" ]; then
  MG="$STUDIO/references/mg-styles-15"
  if [ -d "$MG/.git" ]; then
    ok "depo zaten var: $MG"
  else
    git clone --depth 1 https://github.com/Vincentwei1021/mg-styles-15 "$MG" && ok "depo indirildi"
  fi
  VENV="$HOME/.local/opt/mg-venv"
  if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV" && ok "Python ortamı: $VENV"
  fi
  "$VENV/bin/python" -m pip install --quiet --upgrade pip
  "$VENV/bin/python" -m pip install --quiet numpy scipy soundfile numba pedalboard pyloudnorm librosa matplotlib && ok "ses paketleri kuruldu"
  # klonda bazı enstrüman örnekleri eksik gelebilir: dizini diskte olanlarla süz (asıl liste index.full.json)
  "$VENV/bin/python" - "$MG/lib/audio/samples" <<'PY'
import json, os, sys
d = sys.argv[1]
full = os.path.join(d, "index.full.json")
idx = os.path.join(d, "index.json")
if not os.path.exists(full):
    os.replace(idx, full)
data = json.load(open(full))
kept = {k: [s for s in v if os.path.exists(os.path.join(d, s["file"]))] for k, v in data.items()}
json.dump(kept, open(idx, "w"), ensure_ascii=False, indent=1)
print(f"  ✓ örnekler: {sum(map(len, kept.values()))}/{sum(map(len, data.values()))} dosya diskte")
PY
else
  uy "atlandı. Kodla müzik/efekt istersen:  bash kur.sh --muzik"
fi

b "Kontrol"
if [ "${SKIP_HF:-0}" != "1" ]; then npx --yes hyperframes doctor </dev/null || true; fi

b "Bitti 🎬"
cat <<EOF

  Şimdi:
    1) Çekimlerini şu klasöre koy:   $STUDIO/inbox/ilk-video/
    2) Terminalde:                   cd "$STUDIO" && claude
    3) Claude'a yaz:                 inbox/ilk-video klasöründeki çekimleri editle

  Görünümünü kendine göre ayarlamak için:  $STUDIO/BRAND.md
EOF
