"""Build the project network as a Mermaid block for the profile README.

Clusters are hubs carrying the domain name; a branch runs from each hub to each of
its projects, and a few cross-links join related projects across domains. Positions are
computed here and applied with CSS, the plane is tilted in perspective, and the camera
sways slowly. Every project is a Mermaid `click` link, so it opens its repo.

Rules learnt on github.com:
- a single quote anywhere in the init JSON makes GitHub drop the whole directive;
- every rule is scoped under #diagram, so the root <svg> itself cannot be styled;
- clickable nodes sit in an <a> that carries Mermaid's own position: cancel it;
- the viewBox is measured after this CSS applies, so it wraps the network.
"""
import math, sys, json, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from projects import CLUSTERS, PROJECTS

GH = "https://github.com/Marc-Dvci/"
TILT = 42
COS = math.cos(math.radians(TILT))
SQUASH = 1 / COS
FONT = 26
ZOOM = 1.6                      # how far a hovered cluster spreads around its hub
ZONE = 360
EASE = "cubic-bezier(.16,1,.3,1)"   # ease-out-expo: fast start, soft landing
FONTS = "Segoe UI Variable Display,Segoe UI,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"
COLORS = {"health": "#ff7a45", "audit": "#5b9dff", "agents": "#b07cff", "money": "#25d0a6",
          "edge": "#ffc23d", "science": "#ff5fa8", "consumer": "#8fe04a"}
SHORT = {"health": "Health", "audit": "Audit", "agents": "Agents", "money": "Crypto",
         "edge": "Robotics", "science": "Science", "consumer": "Consumer"}
HUB_POS = {  # plane coordinates, chosen by hand for an organic spread
    "health": (-80, -560), "audit": (620, -330), "agents": (640, 330), "money": (90, 610),
    "edge": (-560, 470), "science": (-760, -20), "consumer": (-640, -500)}
CROSS = [("FieldScreen_AI", "LUMEN"), ("LUMEN", "LUMEN-Mobile"), ("LUMEN", "Kangaroo"), ("Titra", "Guardian-172"),
         ("Titra", "fastpath64"), ("night-audit", "four-hours"), ("four-hours", "arms-length"), ("pedigree", "slowest-link"),
         ("pedigree", "Undeclared"), ("On-the-Line", "Callibrate"), ("Callibrate", "awesome-phone-call-agents"),
         ("Silah", "RxLint"), ("Keystone", "Second-Key"), ("covered", "Criee"), ("Hodgkin-s-Razor", "Vitrify"),
         ("Mizan", "orbite-orbitsight"), ("RallyForge", "right-hand-rule-g1"), ("Breathing-Room", "SASH"),
         ("Footlight", "Understudy"), ("proof-of-loss", "Attestable"), ("Raccord", "Lore"), ("Mantel", "Encore"),
         ("Threshold", "Recall-Me-Maybe"), ("BACKSTOP", "Attestable")]


DESC_FILE = Path(__file__).parent / "descriptions.json"
DESC_EXTRA = {"Gitlab-2026-project": "Erases one customer's data across records, invoices, files and logs, one approved store at a time."}


def descriptions():
    """First sentence of each repo description (gh repo list --json name,description)."""
    raw = {r["name"]: (r["description"] or "") for r in json.loads(DESC_FILE.read_text(encoding="utf-8"))}
    raw.update(DESC_EXTRA)
    out = {}
    for repo, text in raw.items():
        text = text.replace(" — ", ": ").strip()
        cut = text.find(". ")
        first = text[:cut + 1] if cut > 0 else text
        out[repo] = first.replace('"', "").replace("#", "").replace(";", ",")
    return out


def label_w(name, win):
    return len(name) * FONT * (0.6 if win else 0.55) + 26


def layout(seed=7):
    rnd = random.Random(seed)
    pos, meta = {}, {}
    for k, (hx, hy) in HUB_POS.items():
        members = [p for p in PROJECTS if p[2] == k]
        n = len(members)
        base = rnd.uniform(0, 2 * math.pi)
        for j, p in enumerate(members):
            a = base + 2 * math.pi * j / n + rnd.uniform(-0.12, 0.12)
            r = 120 + 60 * (j % 3) + rnd.uniform(-15, 15)
            pos[p[0]] = [hx + r * math.cos(a), hy + r * math.sin(a)]
            meta[p[0]] = dict(name=p[1], k=k, win=p[3] is not None)
    # push labels apart in screen space (y foreshortened by the tilt)
    keys = list(pos)
    for _ in range(400):
        moved = False
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                (ax, ay), (bx, by) = pos[a], pos[b]
                wa, wb = label_w(meta[a]["name"], meta[a]["win"]), label_w(meta[b]["name"], meta[b]["win"])
                # label sits right of the dot when the project is right of its hub, else left
                ca = ax + (wa / 2 if ax >= HUB_POS[meta[a]["k"]][0] else -wa / 2)
                cb = bx + (wb / 2 if bx >= HUB_POS[meta[b]["k"]][0] else -wb / 2)
                ox = (wa + wb) / 2 + 12 - abs(ca - cb)
                oy = (FONT * 1.5 + 6) - abs(ay - by) * COS
                if ox > 0 and oy > 0:
                    moved = True
                    if oy / COS < ox:
                        s = (oy / COS) / 2 + 1
                        d = 1 if ay >= by else -1
                        pos[a][1] += d * s; pos[b][1] -= d * s
                    else:
                        s = ox / 2 + 1
                        d = 1 if ca >= cb else -1
                        pos[a][0] += d * s; pos[b][0] -= d * s
        # keep each project tied to its hub label (outside the hub text, within reach)
        for a in keys:
            hx, hy = HUB_POS[meta[a]["k"]]
            dx, dy = pos[a][0] - hx, pos[a][1] - hy
            d = math.hypot(dx, dy) or 1
            dd = min(max(d, 95), 270)
            pos[a] = [hx + dx * dd / d, hy + dy * dd / d]
        if not moved:
            break
    return pos, meta


def line_css(sel, x, y, tx, ty, flip=False):
    """A branch from (x, y) to (tx, ty): an arc drawn by a rounded top border, rotated into place."""
    L = math.hypot(tx - x, ty - y)
    ang = math.degrees(math.atan2(ty - y, tx - x))
    mirror = " scaleY(-1)" if flip else ""
    return f"{sel} foreignObject div::after{{width:{L:.0f}px;transform:rotate({ang:.1f}deg){mirror}}}"


def mermaid():
    pos, meta = layout()
    desc = descriptions()
    repos = list(pos)
    idx = {r: n for n, r in enumerate(repos)}
    keys = list(CLUSTERS)
    lines = ["flowchart LR", '  sky[" "]:::sky'] + [f'  c{q}[" "]:::corner' for q in range(4)]
    css = []
    # hub-to-hub backbone and cross-links, drawn from invisible nodes so they paint underneath
    for i in range(len(keys)):
        lines.append(f'  z{i}[" "]:::zone')
    for e, (a, b) in enumerate(CROSS):
        lines.append(f'  x{e}[" "]:::link')
    for i in range(len(keys)):
        lines.append(f'  b{i}[" "]:::bone')
    for n, r in enumerate(repos):
        m = meta[r]
        side = "R" if pos[r][0] >= HUB_POS[m["k"]][0] else "L"
        label = ("★ " if m["win"] else "") + m["name"] + f"<i>{desc.get(r, '')}</i>"
        lines.append(f'  p{n}["{label}"]:::{"win" if m["win"] else "proj"}{side}')
    for i, k in enumerate(keys):
        lines.append(f'  h{i}["{SHORT[k]}"]:::hub')
    ids = ["sky"] + [f"c{q}" for q in range(4)] + [f"z{i}" for i in range(len(keys))] + [f"x{e}" for e in range(len(CROSS))] + [f"b{i}" for i in range(len(keys))] + \
          [f"p{n}" for n in range(len(repos))] + [f"h{i}" for i in range(len(keys))]
    for a in range(0, len(ids), 5):
        lines.append("  " + " ~~~ ".join(ids[a:a + 5]))
    for n, r in enumerate(repos):
        lines.append(f'  click p{n} "{GH}{r}"')
    for i, k in enumerate(keys):     # a cluster class on every member keeps the CSS short
        lines.append(f"  class {','.join(f'p{idx[r]}' for r in repos if meta[r]['k'] == k)} k{i}")

    # invisible corners so the measured viewBox includes every label, not only the dots
    xs, ys = [], []
    for r in repos:
        x, y = pos[r]
        w = label_w(meta[r]["name"], meta[r]["win"])
        xs += [x - w - 20, x + w + 20]; ys += [y]
    for k in keys:
        xs.append(HUB_POS[k][0]); ys.append(HUB_POS[k][1] - 90)
    corners = [(min(xs), min(ys) - 40), (max(xs), min(ys) - 40), (min(xs), max(ys) + 40), (max(xs), max(ys) + 40)]
    for q, (cx_, cy_) in enumerate(corners):
        css.append(f"[id*=t-c{q}-]{{transform:translate({cx_:.0f}px,{cy_:.0f}px)}}")
    for i, k in enumerate(keys):
        hx, hy = HUB_POS[k]
        nx, ny = HUB_POS[keys[(i + 1) % len(keys)]]
        css.append(f"[id*=t-h{i}-]{{transform:translate({hx}px,{hy}px);--c:{COLORS[k]}}}")
        css.append(f"[id*=t-b{i}-]{{transform:translate({hx}px,{hy}px)}}")
        css.append(f"[id*=t-z{i}-]{{transform:translate({hx}px,{hy}px);--c:{COLORS[k]};--p:{-i * 1.7:.1f}s}}")
        css.append(line_css(f"[id*=t-b{i}-]", hx, hy, nx, ny, True))
    def zoomed(r):
        """Spread position when the cluster is forward, clamped so the label stays in the frame."""
        x, y = pos[r]
        hx, hy = HUB_POS[meta[r]["k"]]
        zx, zy = hx + ZOOM * (x - hx), hy + ZOOM * (y - hy)
        w = label_w(meta[r]["name"], meta[r]["win"])
        lo_x = min(xs) + 30 + (w if x < hx else 0)
        hi_x = max(xs) - 30 - (w if x >= hx else 0)
        return min(max(zx, lo_x), hi_x), min(max(zy, min(ys)), max(ys) + 10)

    for n, r in enumerate(repos):
        x, y = pos[r]
        hx, hy = HUB_POS[meta[r]["k"]]
        zx, zy = zoomed(r)
        za = math.degrees(math.atan2(hy - zy, hx - zx))
        mirror = " scaleY(-1)" if n % 2 == 1 else ""
        css.append(f"[id*=t-p{n}-]{{transform:translate({x:.0f}px,{y:.0f}px);--c:{COLORS[meta[r]['k']]};--d:{(n * 0.37) % 3:.1f}s;"
                   f"--zx:{zx:.0f}px;--zy:{zy:.0f}px;--zl:{math.hypot(hx - zx, hy - zy):.0f}px;--zt:rotate({za:.0f}deg){mirror}}}")
        css.append(line_css(f"[id*=t-p{n}-]", x, y, hx, hy, n % 2 == 1))
    # captions open toward the inside of the view when a zoomed project sits near an edge
    min_x, max_x, max_y = min(xs), max(xs), max(ys)
    flips = {"cr": [], "cl": [], "cu": []}
    cap_w, cap_h = 590, 230
    for n, r in enumerate(repos):
        x, y = pos[r]
        hx, hy = HUB_POS[meta[r]["k"]]
        zx, zy = zoomed(r)
        right_side = x >= hx
        if right_side and zx + 14 + cap_w > max_x:
            flips["cr"].append(f"p{n}")
        if not right_side and zx - 14 - cap_w < min_x:
            flips["cl"].append(f"p{n}")
        if zy + cap_h > max_y:
            flips["cu"].append(f"p{n}")
    for cls, members in flips.items():
        if members:
            lines.append(f"  class {','.join(members)} {cls}")
    for e, (a, b) in enumerate(CROSS):
        (ax, ay), (bx, by) = pos[a], pos[b]
        css.append(f"[id*=t-x{e}-]{{transform:translate({ax:.0f}px,{ay:.0f}px)}}")
        css.append(line_css(f"[id*=t-x{e}-]", ax, ay, bx, by, e % 2 == 0))
    # hovering a cluster spreads it around its hub, grows its labels and dims the rest
    for i, k in enumerate(keys):
        on = f".nodes:has(:is([id*=t-z{i}-],[id*=t-h{i}-],.k{i}):hover)"
        css.append(f"{on} .node:not(.sky,.corner,[id*=t-z{i}-],[id*=t-h{i}-],.k{i}){{opacity:.07}}")
        css.append(f"{on} .k{i}{{transform:translate(var(--zx),var(--zy))}}")
        css.append(f"{on} .k{i} foreignObject div::after{{width:var(--zl);transform:var(--zt);opacity:1;animation:flow 3.6s linear infinite;animation-delay:var(--d)}}")
        css.append(f"{on} .k{i} .nodeLabel{{font-size:{FONT + 8}px}}")
        css.append(f"{on} [id*=t-z{i}-] foreignObject div::before{{transform:scale({ZOOM + 0.15})}}")
        css.append(f"{on} [id*=t-h{i}-] .nodeLabel{{font-size:42px}}")
        css.append(f".nodes:has(.k{i}:hover) .k{i}:not(:hover){{opacity:.3}}")

    base = f"""
.edgePaths,.edgeLabels{{display:none}}
.nodes a{{transform:none!important}}
.nodes{{transform-box:fill-box;transform-origin:50% 50%;transform:perspective(2400px) rotateX({TILT}deg);animation:intro 2.2s {EASE} both}}
@keyframes intro{{from{{opacity:0;filter:blur(14px)}}to{{opacity:1;filter:blur(0)}}}}
.node{{transition:opacity .5s,transform 1.1s {EASE}}}
.node .nodeLabel{{transition:font-size 1.1s {EASE},color .3s,text-shadow .3s}}
.node foreignObject div::after{{transition:width 1.1s {EASE},transform 1.1s {EASE}}}
.node foreignObject{{overflow:visible}}
.node foreignObject div{{position:relative;overflow:visible!important}}
.node rect,.node polygon,.node circle{{fill:none!important;stroke:none!important}}
.node .nodeLabel{{position:absolute;left:50%;top:50%;display:block;transform:translate(-50%,-50%) scaleY({SQUASH:.3f});font:600 {FONT}px/1.2 {FONTS};letter-spacing:.005em;white-space:nowrap;color:#dbe4ff!important;text-shadow:0 0 8px #000,0 0 2px #000}}
.node .nodeLabel p{{margin:0;color:inherit!important}}
.sky,.link,.bone,.corner{{pointer-events:none}}
.zone foreignObject div::after{{display:none}}
.zone foreignObject div::before{{width:{2 * ZONE}px;height:{2 * ZONE}px;margin:-{ZONE}px;border-radius:50%;background-image:radial-gradient(circle,var(--c) 0,transparent 66%);opacity:.11;transition:transform 1.1s {EASE},opacity .6s;animation:nebula 11s ease-in-out infinite alternate;animation-delay:var(--p)}}
@keyframes nebula{{from{{scale:.86}}to{{scale:1.14}}}}
.nodes:has(.zone:hover) .zone foreignObject div::before{{opacity:.16}}
.corner foreignObject div::before,.corner foreignObject div::after{{display:none}}
.node foreignObject div::before,.node foreignObject div::after{{content:counter(x);color:transparent;font-size:0;position:absolute;left:50%;top:50%}}
.sky foreignObject div::after{{display:none}}
.sky foreignObject div::before{{width:5600px;height:5000px;margin:-2500px -2800px;
background:radial-gradient(1.4px 1.4px at 37px 61px,#ffffffaa 50%,transparent 51%),radial-gradient(1.2px 1.2px at 113px 19px,#cfe0ff88 50%,transparent 51%),radial-gradient(1.6px 1.6px at 171px 143px,#ffffff55 50%,transparent 51%),radial-gradient(ellipse at 50% 50%,#16203b 0,#0a1020 45%,#05070d 75%);
background-size:210px 170px,260px 230px,330px 290px,100% 100%}}
.link foreignObject div::before,.bone foreignObject div::before{{display:none}}
.node foreignObject div::after{{top:auto;bottom:50%;height:auto;aspect-ratio:6/1;transform-origin:0 100%;z-index:-1;border-top:2px solid transparent;border-radius:50%/100% 100% 0 0}}
.link foreignObject div::after{{aspect-ratio:9/1;border-top:1.5px dashed #a9bcff40}}
.bone foreignObject div::after{{aspect-ratio:4/1;border-top:2px solid #ffffff1c}}
.projL foreignObject div::after,.projR foreignObject div::after,.winL foreignObject div::after,.winR foreignObject div::after{{
border-top-color:var(--c);opacity:.75;
-webkit-mask-image:linear-gradient(90deg,#0006 0,#0006 44%,#000 50%,#0006 56%,#0006 100%);mask-image:linear-gradient(90deg,#0006 0,#0006 44%,#000 50%,#0006 56%,#0006 100%);
-webkit-mask-size:300% 100%;mask-size:300% 100%}}
@keyframes flow{{from{{-webkit-mask-position:100% 0;mask-position:100% 0}}to{{-webkit-mask-position:0 0;mask-position:0 0}}}}
.projL foreignObject div::before,.projR foreignObject div::before,.winL foreignObject div::before,.winR foreignObject div::before{{
width:11px;height:11px;margin:-5.5px;border-radius:50%;background-color:var(--c);box-shadow:0 0 10px var(--c),0 0 2px #fff}}
.winL foreignObject div::before,.winR foreignObject div::before{{width:17px;height:17px;margin:-8.5px;background-color:#ffd76a;box-shadow:0 0 18px #ffb020,0 0 3px #fff}}
.projR .nodeLabel,.winR .nodeLabel{{transform:translate(14px,-50%) scaleY({SQUASH:.3f})}}
.projL .nodeLabel,.winL .nodeLabel{{transform:translate(calc(-100% - 14px),-50%) scaleY({SQUASH:.3f});text-align:right}}
.nodeLabel i{{display:block;position:absolute;top:100%;margin-top:6px;width:max-content;max-width:560px;white-space:normal;text-align:left;font:400 25px/1.4 {FONTS};font-style:normal;color:#c9d4f2;
background-color:#060a14ee;padding:8px 12px;border-radius:6px;border-left:3px solid var(--c);text-shadow:none;opacity:0;transform:translateY(-6px);transition:opacity .25s,transform .25s;pointer-events:none}}
.projR .nodeLabel i,.winR .nodeLabel i{{left:0}}
.cr .nodeLabel i{{left:auto!important;right:0}}
.cl .nodeLabel i{{right:auto!important;left:0}}
.cu .nodeLabel i{{top:auto;bottom:100%;margin:0 0 6px}}
.nodes:has(.projL:hover,.projR:hover,.winL:hover,.winR:hover) .hub{{opacity:.18}}
.projL .nodeLabel i,.winL .nodeLabel i{{right:0;border-left:0;border-right:3px solid var(--c)}}
.projL:hover .nodeLabel i,.projR:hover .nodeLabel i,.winL:hover .nodeLabel i,.winR:hover .nodeLabel i{{opacity:1;transform:none}}
.winL .nodeLabel,.winR .nodeLabel{{color:#ffd76a!important;font-size:29px;text-shadow:0 0 14px #ffb02099,0 0 3px #000}}
.projL:hover .nodeLabel,.projR:hover .nodeLabel,.winL:hover .nodeLabel,.winR:hover .nodeLabel{{color:#fff!important;text-shadow:0 0 12px var(--c),0 0 4px var(--c)}}
.projL,.projR,.winL,.winR{{cursor:pointer}}
.node foreignObject div::before{{transition:scale .35s {EASE}}}
.projL:hover foreignObject div::before,.projR:hover foreignObject div::before,.winL:hover foreignObject div::before,.winR:hover foreignObject div::before{{scale:1.7}}
.hub foreignObject div::after{{top:50%;bottom:auto;width:70px;height:70px;aspect-ratio:auto;margin:-35px;border:2px solid var(--c);border-radius:50%;transform:none;animation:ripple 4s ease-out infinite}}
@keyframes ripple{{from{{scale:.3;opacity:.8}}to{{scale:3.2;opacity:0}}}}
.hub foreignObject div::before{{width:26px;height:26px;margin:-13px;border-radius:50%;background-image:radial-gradient(circle,#fff 0,var(--c) 45%,transparent 72%);box-shadow:0 0 36px 10px var(--c);animation:breathe 5s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{scale:1}}50%{{scale:1.3}}}}
.hub .nodeLabel{{font-size:34px;letter-spacing:.08em;text-transform:uppercase;color:#fff!important;transform:translate(-50%,calc(-50% - 40px)) scaleY({SQUASH:.3f});text-shadow:0 0 16px var(--c),0 0 3px #000}}
a,a:hover,a *,a:hover *{{text-decoration:none!important}}
"""
    theme_css = (base + "\n".join(css)).replace("\n", " ")
    assert "'" not in theme_css and '"' not in theme_css, "a quote makes GitHub drop the whole init directive"
    init = {"theme": "base", "flowchart": {"htmlLabels": True, "nodeSpacing": 14, "rankSpacing": 14, "padding": 4},
            "themeVariables": {"fontFamily": "Segoe UI"}, "themeCSS": theme_css}
    return "%%{init: " + json.dumps(init, separators=(",", ":")) + "}%%\n" + "\n".join(lines) + "\n"


if __name__ == "__main__":
    out = mermaid()
    print(len(out), "chars", file=sys.stderr)
    print(out)
