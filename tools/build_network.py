"""Build the project network as a Mermaid block for the profile README.

Eight domain hubs sit on a board, placed so related domains are neighbours. Each project
sits next to its main domain, or between domains when it belongs to several, and a
right-angled connector runs to every domain it belongs to, in that domain's colour.
Positions are computed here and applied with CSS; the board is tilted in perspective.
Every project is a Mermaid `click` link, so it opens its repo.

Rules learnt on github.com:
- a single quote anywhere in the init JSON makes GitHub drop the whole directive;
- every rule is scoped under #diagram, so the root <svg> itself cannot be styled;
- the CSS is re-serialized by the browser: no multi-layer `background` shorthand with var();
- clickable nodes sit in an <a> that carries Mermaid's own position: cancel it;
- the viewBox is measured after this CSS applies (first frame), so geometry must not animate;
- keep the block under Mermaid's 50,000-character limit.
"""
import math, sys, json, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from projects import CLUSTERS, HUBS, PROJECTS

GH = "https://github.com/Marc-Dvci/"
TILT = 38
COS = math.cos(math.radians(TILT))
SQUASH = 1 / COS
FONT = 24
INK = "#e6edf3"
BG = "#0b0f17"
GOLD = "#fcd34d"
EASE = "cubic-bezier(.16,1,.3,1)"
FONTS = "Segoe UI Variable Text,Segoe UI,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"
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
    return len(name) * FONT * (0.57 if win else 0.53) + 30


HUB_LIFT = 44                     # the domain name sits this far above its glowing core


def hub_box(k):
    label = CLUSTERS[k][0]
    return len(label) * 23 + 60, 70


def layout(seed=11):
    rnd = random.Random(seed)
    pos, meta = {}, {}
    singles = {k: [p for p in PROJECTS if p[2] == k and not p[3]] for k in CLUSTERS}
    for k, members in singles.items():
        hx, hy = HUBS[k]
        n = len(members)
        base = rnd.uniform(0, math.pi)
        for j, p in enumerate(members):
            a = base + 2 * math.pi * j / max(n, 1)
            r = 190 + 50 * (j % 2)
            pos[p[0]] = [hx + r * math.cos(a), hy + r * math.sin(a) * 0.9]
    for repo, name, k, others, result in PROJECTS:
        meta[repo] = dict(name=name, k=k, others=others, win=result is not None, result=result)
        if others:
            ks = [k, k, k] + others         # the main domain pulls three times as hard
            ax = sum(HUBS[q][0] for q in ks) / len(ks)
            ay = sum(HUBS[q][1] for q in ks) / len(ks)
            pos[repo] = [ax + rnd.uniform(-60, 60), ay + rnd.uniform(-50, 50)]
    anchor = {r: list(v) for r, v in pos.items()}

    def box(r):
        x, y = pos[r]
        w = label_w(meta[r]["name"], meta[r]["win"])
        left = x < HUBS[meta[r]["k"]][0]
        return (x - w - 6, x + 6) if left else (x - 6, x + w + 6), y * COS

    keys = list(pos)
    for _ in range(500):
        moved = False
        for i, a in enumerate(keys):
            (a0, a1), ay = box(a)
            for b in keys[i + 1:]:
                (b0, b1), by = box(b)
                ox = min(a1, b1) - max(a0, b0) + 14
                oy = FONT * 1.45 + 8 - abs(ay - by)
                if ox > 0 and oy > 0:
                    moved = True
                    if oy < ox:
                        d = 1 if pos[a][1] >= pos[b][1] else -1
                        s = oy / COS / 2 + 1
                        pos[a][1] += d * s; pos[b][1] -= d * s
                    else:
                        d = 1 if (a0 + a1) >= (b0 + b1) else -1
                        s = ox / 2 + 1
                        pos[a][0] += d * s; pos[b][0] -= d * s
            # keep clear of the hub tags
            for k in CLUSTERS:
                hx, hy = HUBS[k]
                hw, hh = hub_box(k)
                ox = min(a1, hx + hw / 2) - max(a0, hx - hw / 2) + 10
                oy = (hh / 2 + FONT) - abs(ay - (hy - HUB_LIFT) * COS)
                if ox > 0 and oy > 0:
                    moved = True
                    pos[a][1] += (1 if pos[a][1] >= hy - HUB_LIFT else -1) * (oy / COS + 1)
        # stay near the anchor (between its domains, or on its domain's ring)
        for a in keys:
            dx, dy = pos[a][0] - anchor[a][0], pos[a][1] - anchor[a][1]
            d = math.hypot(dx, dy)
            lim = 170
            if d > lim:
                pos[a] = [anchor[a][0] + dx * lim / d, anchor[a][1] + dy * lim / d]
        if not moved:
            break
    return pos, meta


def arc(x, y, tx, ty, flip=False):
    """Connector from a project at (x, y) to a hub at (tx, ty): a tapered arc (rounded top border), rotated into place."""
    L = math.hypot(tx - x, ty - y)
    ang = math.degrees(math.atan2(ty - y, tx - x))
    return f"width:{L:.0f}px;transform:rotate({ang:.0f}deg){' scaleY(-1)' if flip else ''}"


def mermaid():
    pos, meta = layout()
    desc = descriptions()
    repos = list(pos)
    keys = list(CLUSTERS)
    lines = ["flowchart LR", '  sky[" "]:::sky'] + [f'  c{q}[" "]:::corner' for q in range(4)]
    css = []

    # secondary connectors: one invisible node per extra domain, painted under the projects
    extra = [(r, k2) for r in repos for k2 in meta[r]["others"]]
    for j, (r, k2) in enumerate(extra):
        lines.append(f'  s{j}[" "]:::conn')
    for n, r in enumerate(repos):
        m = meta[r]
        side = "L" if pos[r][0] < HUBS[m["k"]][0] else "R"
        cap = desc.get(r, "")
        if m["win"]:
            cap = f"<b>{m['result']}</b>" + cap
        lines.append(f'  p{n}["{m["name"]}<i>{cap}</i>"]:::{"w" if m["win"] else "p"}{side.lower()}')
    for i, k in enumerate(keys):
        lines.append(f'  h{i}["{CLUSTERS[k][0]}"]:::hub')
    ids = ["sky"] + [f"c{q}" for q in range(4)] + [f"s{j}" for j in range(len(extra))] + \
          [f"p{n}" for n in range(len(repos))] + [f"h{i}" for i in range(len(keys))]
    for a in range(0, len(ids), 6):              # invisible chains keep Mermaid's own layout compact
        lines.append("  " + " ~~~ ".join(ids[a:a + 6]))
    for n, r in enumerate(repos):
        lines.append(f'  click p{n} "{GH}{r}"')
    # membership classes: m3 marks everything that belongs to domain 3
    for i, k in enumerate(keys):
        mem = [f"p{n}" for n, r in enumerate(repos) if meta[r]["k"] == k or k in meta[r]["others"]]
        mem += [f"s{j}" for j, (r, k2) in enumerate(extra) if k2 == k]
        lines.append(f"  class {','.join(mem)} m{i}")

    # owner classes: o12 marks the extra connectors of project 12, so its hover can light them
    owners = {}
    for j, (r, k2) in enumerate(extra):
        owners.setdefault(repos.index(r), []).append(f"s{j}")
    for n, sj in owners.items():
        lines.append(f"  class {','.join(sj)} o{n}")
        css.append(f".nodes:has([id*=t-p{n}-]:hover) .o{n}{{opacity:1!important}}")

    # board extent: invisible corners so the measured viewBox includes every label
    xs, ys = [], []
    for r in repos:
        x, y = pos[r]
        w = label_w(meta[r]["name"], meta[r]["win"])
        xs += [x - w - 30, x + w + 30]; ys += [y]
    for k in keys:
        xs += [HUBS[k][0] - hub_box(k)[0] / 2 - 20, HUBS[k][0] + hub_box(k)[0] / 2 + 20]; ys.append(HUBS[k][1])
    x0, x1, y0, y1 = min(xs), max(xs), min(ys) - 70, max(ys) + 60
    for q, (cx, cy) in enumerate([(x0, y0), (x1, y0), (x0, y1), (x1, y1)]):
        css.append(f"[id*=t-c{q}-]{{transform:translate({cx:.0f}px,{cy:.0f}px)}}")

    for i, k in enumerate(keys):
        hx, hy = HUBS[k]
        css.append(f"[id*=t-h{i}-]{{transform:translate({hx}px,{hy}px);--c:{CLUSTERS[k][1]}}}")
        css.append(f".nodes:has([id*=t-h{i}-]:hover) .node:not(.sky,.corner,.m{i},[id*=t-h{i}-]){{opacity:.1}}")
    for n, r in enumerate(repos):
        x, y = pos[r]
        hx, hy = HUBS[meta[r]["k"]]
        css.append(f"[id*=t-p{n}-]{{transform:translate({x:.0f}px,{y:.0f}px);--c:{CLUSTERS[meta[r]['k']][1]}}}")
        css.append(f"[id*=t-p{n}-] div::after{{{arc(x, y, hx, hy, n % 2 == 1)}}}")
    for j, (r, k2) in enumerate(extra):
        x, y = pos[r]
        hx, hy = HUBS[k2]
        css.append(f"[id*=t-s{j}-]{{transform:translate({x:.0f}px,{y:.0f}px);--c:{CLUSTERS[k2][1]}}}")
        css.append(f"[id*=t-s{j}-] div::after{{{arc(x, y, hx, hy, j % 2 == 0)}}}")

    # captions open toward the inside of the board near its edges
    flips = {"cr": [], "cl": [], "cu": []}
    for n, r in enumerate(repos):
        x, y = pos[r]
        right = x >= HUBS[meta[r]["k"]][0]
        if right and x + 620 > x1:
            flips["cr"].append(f"p{n}")
        if not right and x - 620 < x0:
            flips["cl"].append(f"p{n}")
        if y + 260 > y1:
            flips["cu"].append(f"p{n}")
    for cls, members in flips.items():
        if members:
            lines.append(f"  class {','.join(members)} {cls}")

    P = ".pl,.pr,.wl,.wr"
    base = f"""
.edgePaths,.edgeLabels{{display:none}}
.nodes a{{transform:none!important}}
.nodes{{transform-box:fill-box;transform-origin:50% 50%;transform:perspective(2600px) rotateX({TILT}deg);animation:intro 1.6s {EASE} both}}
@keyframes intro{{from{{opacity:0;filter:blur(10px)}}to{{opacity:1;filter:blur(0)}}}}
.node{{transition:opacity .35s {EASE}}}
.node foreignObject{{overflow:visible}}
.node foreignObject div{{position:relative;overflow:visible!important}}
.node rect,.node polygon,.node circle{{fill:none!important;stroke:none!important}}
.node div::before,.node div::after{{content:counter(x);color:transparent;font-size:0;position:absolute;left:50%;top:50%;pointer-events:none}}
.sky,.corner,.conn{{pointer-events:none}}
.corner div::before,.corner div::after,.sky div::after,.conn div::before,.hub div::after{{display:none}}
.sky div::before{{width:6000px;height:5200px;margin:-2600px -3000px;background-color:{BG};background-image:radial-gradient(ellipse 40% 40% at 50% 50%,#151c2b,transparent)}}
.node div::after{{left:50%;top:auto;bottom:50%;height:auto;aspect-ratio:6/1;transform-origin:0 100%;border-top:2.5px solid var(--c);border-radius:50%/100% 100% 0 0;opacity:.62;z-index:-1;transition:opacity .35s {EASE}}}
.conn div::after{{aspect-ratio:8/1;border-top:2px dashed var(--c);opacity:.5}}
{P.replace(',', ' div::before,')} div::before{{width:13px;height:13px;margin:-6.5px;background-color:var(--c);border-radius:50%;box-shadow:0 0 0 3px {BG},0 0 12px var(--c)}}
.wl div::before,.wr div::before{{width:16px;height:16px;margin:-8px;background-color:{GOLD};border-radius:50%;box-shadow:0 0 0 3px {BG},0 0 0 5px {GOLD},0 0 16px {GOLD}}}
.node .nodeLabel{{position:absolute;left:50%;top:50%;display:block;font:500 {FONT}px/1.25 {FONTS};white-space:nowrap;color:{INK}!important;text-shadow:0 0 6px {BG},0 0 2px {BG};transition:color .25s}}
.node .nodeLabel p{{margin:0;color:inherit!important}}
.pr .nodeLabel,.wr .nodeLabel{{transform:translate(18px,-50%) scaleY({SQUASH:.3f})}}
.pl .nodeLabel,.wl .nodeLabel{{transform:translate(calc(-100% - 18px),-50%) scaleY({SQUASH:.3f});text-align:right}}
.wl .nodeLabel,.wr .nodeLabel{{color:#fde68a!important;font-weight:650}}
{P.replace(',', ':hover .nodeLabel,')}:hover .nodeLabel{{color:#fff!important}}
{P}{{cursor:pointer}}
{P.replace(',', ':hover div::after,')}:hover div::after{{opacity:.95}}
.nodes:has({P.replace(',', ':hover,')}:hover) .conn div::after{{opacity:.9}}
.nodes:has({P.replace(',', ':hover,')}:hover) .node:not(:hover,.sky,.corner,.hub){{opacity:.28}}
.nodes:has({P.replace(',', ':hover,')}:hover) .hub{{opacity:.35}}
.nodeLabel i{{display:block;position:absolute;top:100%;left:0;margin-top:8px;width:max-content;max-width:640px;white-space:normal;text-align:left;font:400 26px/1.45 {FONTS};font-style:normal;color:#c9d1d9;
background-color:#0d1117f2;padding:12px 16px;border:1px solid #30363d;border-left:4px solid var(--c);border-radius:6px;text-shadow:none;opacity:0;transform:translateY(-4px);transition:opacity .2s,transform .2s {EASE};pointer-events:none}}
.nodeLabel i b{{display:block;margin-bottom:6px;font-weight:650;color:{GOLD}}}
.pl .nodeLabel i,.wl .nodeLabel i{{left:auto;right:0}}
.cr .nodeLabel i{{left:auto!important;right:0}}
.cl .nodeLabel i{{right:auto!important;left:0}}
.cu .nodeLabel i{{top:auto;bottom:100%;margin:0 0 8px}}
{P.replace(',', ':hover .nodeLabel i,')}:hover .nodeLabel i{{opacity:1;transform:none}}
.hub div::before{{display:block;width:30px;height:30px;margin:-15px;border-radius:50%;background-image:radial-gradient(circle,#fff 0,var(--c) 42%,transparent 72%);box-shadow:0 0 40px 12px var(--c)}}
.hub .nodeLabel{{transform:translate(-50%,calc(-50% - {HUB_LIFT}px)) scaleY({SQUASH:.3f});font:700 30px/1 {FONTS};letter-spacing:.1em;text-transform:uppercase;color:#fff!important;text-shadow:0 0 14px var(--c),0 0 3px {BG},0 0 8px {BG}}}
.hub{{transition:opacity .35s {EASE}}}
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
