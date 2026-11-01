# Strumenti per i post SYB

Stile: fondo scuro #17191d o crema #f6f3ee, accento rame #c06e45 (#d99a74 su scuro), titoli Instrument Serif con parola chiave in corsivo, testo Inter.
Caroselli 1080x1350 (7 slide: copertina scura, 5 slide numerate chiare, chiusura scura con CTA). Reel 1080x1920 (6 schermate, ~30 s, sound brand/syb_sound.mp3).

1. Font: `git clone --depth 1 --filter=blob:none --sparse https://github.com/google/fonts gf && git -C gf sparse-checkout set ofl/instrumentserif && mkdir -p ~/.fonts && cp gf/ofl/instrumentserif/*.ttf ~/.fonts && fc-cache -f` (Inter è già installato).
2. Scrivi la spec JSON (esempi in tools/specs; `*parola*` = corsivo rame).
3. `python3 tools/render.py spec.json cartella_png`
4. Reel: `tools/make_reel.sh cartella_png reels/reel_AAAA-MM-GG_slug.mp4 4.5 5 6.5 6 6 5.5`
5. Caroselli: converti i PNG in JPG dentro AAAA-MM-GG_slug/, poi commit e push su main.
6. In Metricool usa gli URL https://raw.githubusercontent.com/micol2405-ai/syb-social/main/<percorso>.
