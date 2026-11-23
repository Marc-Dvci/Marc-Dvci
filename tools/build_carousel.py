"""Build the results carousel: a ring of 3D cards in an animated SVG (CSS 3D inside foreignObject).

GitHub shows README images without scripts, but CSS 3D transforms and keyframes run
inside an SVG's foreignObject. The ring turns one card at a time and holds it in front.
Each card names its domain the way the project network does, in the domain's colour.
"""
import math, sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from projects import CLUSTERS

# result, participants (when known), project, competition, domain key (see projects.CLUSTERS)
RESULTS = [
    ("3rd place", "850+ teams", "FieldScreen AI", "Google MedGemma Impact Challenge", "health"),
    ("Winner, EdgeAgent track", "8k participants", "LUMEN", "Global AI Hackathon with Qwen Cloud", "health"),
    ("1st place", "216 projects", "Footlight", "Learn AR with SPECS · Snap × Devpost", "consumer"),
    ("3rd place", None, "Hodgkin's Razor", "AI4S Open Innovation · Pazhou Algorithm Competition", "science"),
    ("2nd place", "9k participants", "On the Line", "AWS Agents for Humans · Good Neighbor Agents", "agents"),
    ("2nd place", "10k participants", "Raccord", "Agentic Cinema · Grafana track", "agents"),
    ("4th place", "368 competitors", "Poker coordination detector", "Detect Suspicious Value Transfers in Poker", "ml"),
    ("Finalist, 1 of 5", None, "OrbitE", "TII OrbitSight Challenge", "ml"),
    ("Finalist, 1 of 6", None, "IP Value Framework", "European Patent Office CodeFest", "controls"),
    ("2nd place, Pro", None, "Python and C++", "Euro-Information Concours de Code", "systems"),
    ("Honorable mention", None, "Vitrify", "Tesseract Hackathon", "science"),
]
W, H = 880, 306
CARD_W, CARD_H = 300, 222
STEP_S = 3.2          # seconds per card (move + hold)
MOVE = 0.28           # share of each step spent turning
RADIUS = 470
SLOT_DEG = 36         # angle between neighbouring cards, whatever the number of results
BG = "#0b0f17"
FONT = "-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"


def keyframes(n):
    """One card's path round the ring: hold at each slot, then turn to the next.

    Neighbours always sit SLOT_DEG apart, so a new result never squeezes the cards together.
    Only the slots within 90 degrees of the front are visible; a card waiting further back
    jumps from the far left to the far right while invisible.
    """
    step = 100 / n
    slot = max(SLOT_DEG, 360 / n)                           # fewer than 10 cards: a plain ring
    frames = []
    for k in range(n + 1):
        r = (n // 2 - k) % n - n // 2                       # signed slot from the front, negative = left
        ang = slot * r
        a = math.radians(ang)
        front = (1 + math.cos(a)) / 2                       # 1 in front, 0 behind
        op = max(0.0, math.cos(a)) ** 1.5                   # back half of the ring is invisible
        bright = 0.35 + 0.65 * front
        t0 = k * step
        t1 = min(100, t0 + step * (1 - MOVE))
        style = f"transform:rotateY({ang:.2f}deg) translateZ({RADIUS}px);opacity:{op:.3f};filter:brightness({bright:.2f})"
        frames.append(f"{t0:.3f}%{{{style}}}")
        if k < n:
            frames.append(f"{t1:.3f}%{{{style}}}")
    return "@keyframes ring{" + "".join(frames) + "}"


def card(i, n, result, crowd, project, comp, domain):
    label, color = CLUSTERS[domain]
    delay = -((n - i) % n) * STEP_S      # the next card waits on the right
    return f"""<div class="card" style="--c:{color};--t:{color}1c;animation-delay:{delay:.2f}s">
<div class="dom"><span></span>{escape(label)}</div><div class="res">{escape(result)}</div>{f'<div class="crowd">{escape(crowd)}</div>' if crowd else ''}<div class="proj">{escape(project)}</div><div class="comp">{escape(comp)}</div></div>"""


def svg():
    n = len(RESULTS)
    total = n * STEP_S
    cards = "\n".join(card(i, n, *r) for i, r in enumerate(RESULTS))
    css = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
.stage{{width:{W}px;height:{H}px;overflow:hidden;position:relative;font-family:{FONT};background-color:{BG};
background-image:radial-gradient(ellipse 45% 60% at 50% 50%,#151c2b,transparent)}}
.world{{position:absolute;left:50%;top:50%;perspective:1300px;perspective-origin:50% 40%}}
.ring{{position:absolute;transform-style:preserve-3d;transform:translateZ(-{RADIUS}px)}}
.card{{position:absolute;left:-{CARD_W // 2}px;top:-{CARD_H // 2}px;width:{CARD_W}px;height:{CARD_H}px;border-radius:4px;padding:20px 24px;
background-color:#0d1117;background-image:radial-gradient(130% 100% at 0% 0%,var(--t),transparent 60%);
border:1px solid #30363d;box-shadow:0 16px 40px #000c;overflow:hidden;animation:ring {total:.1f}s cubic-bezier(.65,0,.35,1) infinite}}
.dom{{display:flex;align-items:center;gap:9px;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--c)}}
.dom span{{width:9px;height:9px;border-radius:1px;background-color:var(--c)}}
.res{{margin-top:16px;font-size:27px;font-weight:700;letter-spacing:-.01em;color:#f0f6fc;line-height:1.15}}
.crowd{{margin-top:6px;font-size:13px;font-weight:600;letter-spacing:.04em;color:#8b949e}}
.proj{{margin-top:12px;font-size:18px;font-weight:600;color:#e6edf3}}
.comp{{margin-top:6px;font-size:14px;line-height:1.4;color:#8b949e}}
{keyframes(n)}
@media (prefers-reduced-motion:reduce){{.card{{animation-play-state:paused}}}}
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Competition results: {escape('; '.join(r[0] + (f' ({r[1]})' if r[1] else '') + ', ' + r[2] for r in RESULTS))}">
<foreignObject width="{W}" height="{H}"><div xmlns="http://www.w3.org/1999/xhtml" class="stage"><style>{css}</style>
<div class="world"><div class="ring">
{cards}
</div></div></div></foreignObject></svg>
"""


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results.svg")
    out.write_text(svg(), encoding="utf-8")
    print(out, len(out.read_text(encoding="utf-8")) // 1000, "KB")
