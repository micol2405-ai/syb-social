"""Render SYB social slides (carousel 1080x1350, reel frames 1080x1920) from a JSON spec."""
import json, sys, html
from pathlib import Path
from playwright.sync_api import sync_playwright


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:%(w)dpx;height:%(h)dpx;font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased}
.s{position:relative;width:100%%;height:100%%;padding:%(pad)dpx 96px;display:flex;flex-direction:column}
.dark{background:#17191d;color:#f3efe8}
.light{background:#f6f3ee;color:#1c1d20}
.top{display:flex;justify-content:space-between;align-items:center}
.logo{font-family:'Instrument Serif';font-size:40px;letter-spacing:.5px}
.tag{font-size:19px;letter-spacing:4px;text-transform:uppercase;opacity:.7}
.bars{position:absolute;top:70px;left:96px;right:96px;display:flex;gap:10px}
.bars i{flex:1;height:4px;background:rgba(127,127,127,.25);border-radius:2px}
.bars i.on{background:#c06e45}
.body{flex:1;display:flex;flex-direction:column;justify-content:center}
.dot{width:12px;height:12px;border-radius:6px;background:#c06e45;margin-bottom:44px}
.label{font-size:22px;letter-spacing:4px;text-transform:uppercase;color:#c06e45;font-weight:600;margin-bottom:32px}
.dark .label{color:#d99a74}
h1{font-family:'Instrument Serif';font-weight:400;font-size:%(h1)dpx;line-height:1.02;letter-spacing:-.5px}
h2{font-family:'Instrument Serif';font-weight:400;font-size:%(h2)dpx;line-height:1.05}
em{font-style:italic;color:#c06e45}
.dark em{color:#d99a74}
.num{font-family:'Instrument Serif';font-size:230px;line-height:.9;color:#c06e45;margin-bottom:34px}
.rule{width:96px;height:2px;background:#c06e45;margin:48px 0}
p{font-size:%(p)dpx;line-height:1.55;opacity:.88;max-width:860px}
.cta{color:#d99a74;font-size:%(p)dpx;margin-top:40px;opacity:1}
ul{list-style:none}
li{font-size:%(p)dpx;line-height:1.5;margin:20px 0;display:flex;gap:26px}
li:before{content:'';flex:0 0 30px;height:2px;background:#c06e45;margin-top:24px}
.box{margin-top:52px;background:#ebe5dc;border-left:4px solid #c06e45;padding:34px 40px;border-radius:4px}
.box b{display:block;font-size:19px;letter-spacing:4px;text-transform:uppercase;color:#c06e45;margin-bottom:14px}
.box span{font-size:%(bx)dpx;line-height:1.5}
.foot{display:flex;justify-content:space-between;font-size:19px;letter-spacing:4px;text-transform:uppercase;opacity:.6}
"""

def esc(t):
    # *testo* -> <em>testo</em>, rest escaped
    out, parts = "", html.escape(t).split("*")
    for i, p in enumerate(parts):
        out += f"<em>{p}</em>" if i % 2 else p
    return out.replace("\n", "<br>")

def slide_html(sl, i, n, kind, tag, footer_right):
    reel = kind == "reel"
    theme = sl.get("theme", "light")
    inner = ""
    if sl.get("dot"): inner += '<div class="dot"></div>'
    if sl.get("label"): inner += f'<div class="label">{esc(sl["label"])}</div>'
    if sl.get("num"): inner += f'<div class="num">{sl["num"]}</div>'
    if sl.get("h1"): inner += f'<h1>{esc(sl["h1"])}</h1>'
    if sl.get("h2"): inner += f'<h2>{esc(sl["h2"])}</h2>'
    inner += '<div class="rule"></div>'
    if sl.get("p"): inner += f'<p>{esc(sl["p"])}</p>'
    if sl.get("list"): inner += "<ul>" + "".join(f"<li><span>{esc(x)}</span></li>" for x in sl["list"]) + "</ul>"
    if sl.get("box"): inner += f'<div class="box"><b>{esc(sl["box"][0])}</b><span>{esc(sl["box"][1])}</span></div>'
    if sl.get("cta"): inner += f'<p class="cta">{esc(sl["cta"])}</p>'
    bars = ""
    if reel:
        bars = '<div class="bars">' + "".join(f'<i class="{"on" if k <= i else ""}"></i>' for k in range(n)) + "</div>"
    foot = "" if reel else f'<div class="foot"><span>{i+1:02d} / {n:02d}</span><span>{footer_right if i == n-1 else "Scorri →"}</span></div>'
    top_pad = '<div style="height:40px"></div>' if reel else ""
    return f'<div class="s {theme}">{bars}{top_pad}<div class="top"><span class="logo">SYB</span><span class="tag">{esc(tag)}</span></div><div class="body">{inner}</div>{foot}</div>'

def main(spec_path, out_dir):
    spec = json.loads(Path(spec_path).read_text())
    kind = spec["kind"]
    w, h = (1080, 1920) if kind == "reel" else (1080, 1350)
    dims = dict(w=w, h=h, pad=150 if kind == "reel" else 80,
                h1=132 if kind == "reel" else 126, h2=104 if kind == "reel" else 94,
                p=36 if kind == "reel" else 33, bx=32 if kind == "reel" else 29)
    css = CSS % dims
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    n = len(spec["slides"])
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h})
        for i, sl in enumerate(spec["slides"]):
            doc = f"<html><head><style>{css}</style></head><body>{slide_html(sl, i, n, kind, spec['tag'], spec.get('footer_right','sybstrategies.com'))}</body></html>"
            pg.set_content(doc); pg.wait_for_timeout(250)
            pg.screenshot(path=str(out / f"slide{i+1:02d}.png"))
        b.close()
    print("rendered", n)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
