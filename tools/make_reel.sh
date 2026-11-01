#!/usr/bin/env bash
# Uso: tools/make_reel.sh <cartella_png> <output.mp4> <durate separate da spazio, una per slide>
# Esempio: tools/make_reel.sh /tmp/reel out.mp4 4.5 5 6.5 6 6 5.5
set -euo pipefail
DIR=$1; OUT=$2; shift 2; D=("$@"); N=${#D[@]}; F=0.4
SOUND="$(dirname "$0")/../brand/syb_sound.mp3"
in=""; for ((i=0;i<N;i++)); do in="$in -loop 1 -t ${D[$i]} -framerate 30 -i $DIR/slide$(printf %02d $((i+1))).png"; done
fc=""; prev="[0:v]"; off=0
for ((i=1;i<N;i++)); do off=$(python3 -c "print(round($off+${D[$((i-1))]}-$F,2))"); fc="$fc${prev}[$i:v]xfade=transition=fade:duration=$F:offset=$off[v$i];"; prev="[v$i]"; done
total=$(python3 -c "import sys; d=[float(x) for x in sys.argv[1:]]; print(round(sum(d)-(len(d)-1)*$F,2))" "${D[@]}")
ffmpeg -v error -y $in -i "$SOUND" -filter_complex "${fc}${prev}format=yuv420p[v];[$N:a]atrim=0:$total,afade=t=in:d=0.6,afade=t=out:st=$(python3 -c "print($total-1.5)"):d=1.5,volume=0.8[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -crf 20 -r 30 -c:a aac -b:a 160k -movflags +faststart -shortest "$OUT"
