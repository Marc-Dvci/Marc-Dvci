"""Build the results carousel: a ring of 3D cards in an animated SVG (CSS 3D inside foreignObject).

GitHub shows README images without scripts, but CSS 3D transforms and keyframes run
inside an SVG's foreignObject. The ring turns one card at a time and holds it in front.
"""
import sys
from pathlib import Path

# result, project, competition, domain colour
RESULTS = [
    ("3rd of 850+ teams", "FieldScreen AI", "Google MedGemma Impact Challenge", "#fb923c"),
    ("Winner, EdgeAgent track", "LUMEN", "Global AI Hackathon with Qwen Cloud", "#fb923c"),
    ("3rd place", "Hodgkin's Razor", "AI4S Open Innovation · Pazhou Algorithm Competition", "#f472b6"),
    ("2nd place", "On the Line", "AWS Agents for Humans · Good Neighbor Agents", "#a78bfa"),
    ("2nd place", "Raccord", "Agentic Cinema · Grafana track", "#a78bfa"),
    ("4th of 368", "Poker coordination detector", "Detect Suspicious Value Transfers in Poker", "#22d3ee"),
    ("Finalist, 1 of 5", "OrbitE", "TII OrbitSight Challenge", "#22d3ee"),
    ("Finalist, 1 of 6", "IP Value Framework", "European Patent Office CodeFest", "#60a5fa"),
    ("2nd place, Pro", "Python and C++", "Euro-Information Concours de Code", "#fbbf24"),
    ("Honorable mention", "Vitrify", "Tesseract Hackathon", "#f472b6"),
]
W, H = 880, 290
CARD_W, CARD_H = 300, 188
STEP_S = 3.2          # seconds per card (move + hold)
MOVE = 0.28           # share of each step spent turning
RADIUS = 470
FONT = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"


def keyframes(n):
    """One card's path round the ring: hold at each slot, then turn to the next."""
    import math
    step = 100 / n
    frames = []
    for k in range(n + 1):
        ang = -360 * k / n
        a = math.radians(ang % 360)
        front = (1 + math.cos(a)) / 2                       # 1 in front, 0 behind
        op = max(0.0, math.cos(a)) ** 1.5           # back half of the ring is invisible
        bright = 0.35 + 0.65 * front
        t0 = k * step
        t1 = min(100, t0 + step * (1 - MOVE))
        style = f"transform:rotateY({ang:.2f}deg) translateZ({RADIUS}px) rotateY({-ang * 0:.0f}deg);opacity:{op:.3f};filter:brightness({bright:.2f})"
        frames.append(f"{t0:.3f}%{{{style}}}")
        if k < n:
            frames.append(f"{t1:.3f}%{{{style}}}")
    return "@keyframes ring{" + "".join(frames) + "}"


def card(i, n, result, project, comp, color):
    delay = -((n - i) % n) * STEP_S      # the next card waits on the right
    return f"""<div class="card" style="--c:{color};animation-delay:{delay:.2f}s">
<div class="glow"></div><div class="res">{result}</div><div class="proj">{project}</div><div class="comp">{comp}</div></div>"""


def svg():
    n = len(RESULTS)
    total = n * STEP_S
    cards = "\n".join(card(i, n, *r) for i, r in enumerate(RESULTS))
    css = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
.stage{{width:{W}px;height:{H}px;overflow:hidden;position:relative;font-family:{FONT};background-color:#0b0f17;
background-image:linear-gradient(#ffffff0e 1px,transparent 1px),linear-gradient(90deg,#ffffff0e 1px,transparent 1px),linear-gradient(#ffffff06 1px,transparent 1px),linear-gradient(90deg,#ffffff06 1px,transparent 1px);
background-size:120px 120px,120px 120px,24px 24px,24px 24px;background-position:-1px -1px}}
.world{{position:absolute;left:50%;top:50%;perspective:1300px;perspective-origin:50% 40%}}
.ring{{position:absolute;transform-style:preserve-3d;transform:translateZ(-{RADIUS}px)}}
.card{{position:absolute;left:-{CARD_W // 2}px;top:-{CARD_H // 2}px;width:{CARD_W}px;height:{CARD_H}px;border-radius:4px;padding:26px 24px 20px;
background-color:#0d1117;border:1px solid #30363d;border-top:3px solid var(--c);box-shadow:0 16px 40px #000c;
overflow:hidden;animation:ring {total:.1f}s cubic-bezier(.65,0,.35,1) infinite}}
.glow{{display:none}}
.res{{font-size:27px;font-weight:700;letter-spacing:-.01em;color:#f0f6fc;line-height:1.15}}
.proj{{margin-top:12px;font-size:18px;font-weight:600;color:var(--c)}}
.comp{{margin-top:8px;font-size:14px;line-height:1.4;color:#8b949e}}
.floor{{display:none}}
{keyframes(n)}
@media (prefers-reduced-motion:reduce){{.card{{animation-play-state:paused}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Competition results: {'; '.join(r[0] + ', ' + r[1] for r in RESULTS)}">
<foreignObject width="{W}" height="{H}"><div xmlns="http://www.w3.org/1999/xhtml" class="stage"><style>{css}</style>
<div class="world"><div class="ring">
{cards}
</div></div><div class="floor"></div></div></foreignObject></svg>
"""


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results.svg")
    out.write_text(svg(), encoding="utf-8")
    print(out, len(out.read_text(encoding="utf-8")) // 1000, "KB")
