from __future__ import annotations
import html

def cube_html(label: str, height: int = 220) -> str:
    safe = html.escape(str(label))
    return f"""<!doctype html>
<html><head><meta charset='utf-8' />
<style>
body {{ margin:0; background: transparent; }}
.wrap {{ height:{height}px; display:flex; align-items:center; justify-content:center; }}
.scene {{ width:120px; height:120px; perspective:600px; }}
.cube {{ width:120px; height:120px; position:relative; transform-style:preserve-3d; animation: spin 1.2s ease-in-out; }}
.face {{
  position:absolute; width:120px; height:120px; display:flex; align-items:center; justify-content:center;
  font-family: ui-sans-serif, system-ui; font-size: 44px; font-weight: 700;
  border: 2px solid rgba(255,255,255,0.25);
  background: rgba(20,20,25,0.92); color: rgba(245,245,245,0.95);
  border-radius: 18px; box-shadow: 0 10px 25px rgba(0,0,0,0.35);
}}
.front  {{ transform: rotateY(0deg) translateZ(60px); }}
.back   {{ transform: rotateY(180deg) translateZ(60px); }}
.right  {{ transform: rotateY(90deg) translateZ(60px); }}
.left   {{ transform: rotateY(-90deg) translateZ(60px); }}
.top    {{ transform: rotateX(90deg) translateZ(60px); }}
.bottom {{ transform: rotateX(-90deg) translateZ(60px); }}
@keyframes spin {{
  0% {{ transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg); }}
  70% {{ transform: rotateX(520deg) rotateY(610deg) rotateZ(260deg); }}
  100% {{ transform: rotateX(20deg) rotateY(25deg) rotateZ(0deg); }}
}}
</style></head>
<body>
<div class="wrap"><div class="scene"><div class="cube">
  <div class="face front">{safe}</div>
  <div class="face back">★</div>
  <div class="face right">⚔️</div>
  <div class="face left">🛡️</div>
  <div class="face top">🎲</div>
  <div class="face bottom">⚡</div>
</div></div></div>
</body></html>"""
