"""Build the project network as a Mermaid block for the profile README.

Eight domain hubs sit on a board, placed so related domains are neighbours. Each project
sits next to its main domain, or between domains when it belongs to several, and a
curved connector runs to every domain it belongs to, in that domain's colour.
The board is tilted in perspective, and the projection is computed here: the browser
draws a flat picture, so text keeps its sharp antialiasing at every zoom level.
The board is drawn 1:1 for GitHub's 846 px README column.
Every project is a Mermaid `click` link, so it opens its repo.

Rules learnt on github.com:
- a single quote anywhere in the init JSON makes GitHub drop the whole directive;
- every rule is scoped under #diagram, so the root <svg> itself cannot be styled;
- the CSS is re-serialized by the browser: no multi-layer `background` shorthand with var();
- clickable nodes sit in an <a> that carries Mermaid's own position: cancel it;
- the viewBox is measured after this CSS applies (first frame), so geometry must not animate;
- a CSS 3D transform makes Chrome draw the board as a texture, which blurs the text;
- GitHub sets the svg height to the viewBox height: a viewBox wider than the column leaves
  empty space under the drawing, and its zoom buttons then zoom toward that space;
- keep the block under Mermaid's 50,000-character limit.
"""
import math, sys, json, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from projects import CLUSTERS, HUBS, PROJECTS, CAPTIONS

GH = "https://github.com/Marc-Dvci/"
COLUMN = 846                       # width of the README column on the profile page
PAD = 48                           # GitHub's flowchart diagramPadding around the measured box
EDGE = 14                          # breathing room between the outermost label and the frame
TILT = 38
SIN, COS = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
DIST = 1500                        # viewer distance, in board pixels
GAMMA = 0.5                        # labels shrink with depth by k ** GAMMA (dots and glows by k)
FONT = 13                          # project label size at mid depth, in screen pixels
HUB_FONT = 14.5
HUB_LIFT = 20                      # the domain name sits this far above its glowing core
GAP = 10                           # space between a project's dot and its label
ZOOM = (.55, 3)                    # Shift + wheel zooms the map between these scales
CELLS = (16, 12)                   # hover grid that moves the zoom centre to the pointer
GLIDE = "1.1s cubic-bezier(.22,.61,.36,1)"   # how the view follows the pointer while zoomed
BUTTONS = (124, 120)               # GitHub's zoom and pan buttons cover this much of the bottom right
INK = "#e6edf3"
BG = "#0b0f17"
GOLD = "#fcd34d"
EASE = "cubic-bezier(.16,1,.3,1)"
FONTS = "Segoe UI Variable Text,Segoe UI,-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif"
DESC_FILE = Path(__file__).parent / "descriptions.json"


def descriptions():
    """Profile caption if set in projects.CAPTIONS, else the first sentence of the repo description."""
    raw = {r["name"]: (r["description"] or "") for r in json.loads(DESC_FILE.read_text(encoding="utf-8"))}
    out = {}
    for repo, text in raw.items():
        text = text.replace(" — ", ": ").strip()
        cut = text.find(". ")
        first = text[:cut + 1] if cut > 0 else text
        out[repo] = first
    out.update(CAPTIONS)
    return {r: t.replace('"', "").replace("#", "").replace(";", ",") for r, t in out.items()}


def label_w(name, win, f):
    return len(name) * f * (0.58 if win else 0.54) + GAP + 4


def hub_tag(label, k):
    f = HUB_FONT * k ** GAMMA
    return len(label) * f * 0.8 + 14, f * 1.5


def project(x, y):
    """Board point -> screen point and its depth scale k (k > 1 in front, k < 1 at the back)."""
    k = DIST / (DIST - y * SIN)
    return x * k, y * COS * k, k


def layout(sx, sy, avoid=None, seed=11):
    """avoid: (x, y) corner of the zone GitHub's zoom buttons cover, at the bottom right."""
    rnd = random.Random(seed)
    yc = (min(v[1] for v in HUBS.values()) + max(v[1] for v in HUBS.values())) / 2
    board = {k: (x * sx, (y - yc) * sy) for k, (x, y) in HUBS.items()}
    plane, meta = {}, {}
    singles = {k: [p for p in PROJECTS if p[2] == k and not p[3]] for k in CLUSTERS}
    for k, members in singles.items():
        hx, hy = board[k]
        n = len(members)
        base = rnd.uniform(0, math.pi)
        for j, p in enumerate(members):
            a = base + 2 * math.pi * j / max(n, 1)
            r = 62 + 18 * (j % 2)
            plane[p[0]] = (hx + r * math.cos(a), hy + r * math.sin(a) * 1.15)
    for repo, name, k, others, result in PROJECTS:
        meta[repo] = dict(name=name, k=k, others=others, win=result is not None, result=result)
        if others:
            ks = [k, k, k] + others         # the main domain pulls three times as hard
            ax = sum(board[q][0] for q in ks) / len(ks)
            ay = sum(board[q][1] for q in ks) / len(ks)
            plane[repo] = (ax + rnd.uniform(-22, 22), ay + rnd.uniform(-26, 26))

    hubs = {k: project(*board[k]) for k in CLUSTERS}
    pos, depth = {}, {}
    for r, (x, y) in plane.items():
        X, Y, k = project(x, y)
        pos[r], depth[r] = [X, Y], k
    anchor = {r: list(v) for r, v in pos.items()}
    font = {r: FONT * depth[r] ** GAMMA for r in pos}

    def box(r):
        x, y = pos[r]
        w = label_w(meta[r]["name"], meta[r]["win"], font[r])
        left = x < hubs[meta[r]["k"]][0]
        return ((x - w, x + 6) if left else (x - 6, x + w)), y

    def under_buttons(r):
        """How far the label must move left, or up, to clear the button zone (0, 0 if clear)."""
        if not avoid:
            return 0, 0
        (a0, a1), ay = box(r)
        ox, oy = a1 - avoid[0] + 4, ay + font[r] * 0.7 - avoid[1]
        return (ox, oy) if ox > 0 and oy > 0 else (0, 0)

    keys = list(pos)
    for r in keys:                       # anchors start clear of the buttons
        ox, oy = under_buttons(r)
        if ox or oy:
            if ox < oy:
                pos[r][0] -= ox; anchor[r][0] -= ox
            else:
                pos[r][1] -= oy; anchor[r][1] -= oy
    for _ in range(800):
        moved = False
        for i, a in enumerate(keys):
            ox, oy = under_buttons(a)
            if ox or oy:
                moved = True
                if ox < oy:
                    pos[a][0] -= ox + .5
                else:
                    pos[a][1] -= oy + .5
            (a0, a1), ay = box(a)
            for b in keys[i + 1:]:
                (b0, b1), by = box(b)
                ox = min(a1, b1) - max(a0, b0) + 6
                oy = (font[a] + font[b]) * 0.68 + 3 - abs(ay - by)
                if ox > 0 and oy > 0:
                    moved = True
                    if oy < ox:
                        d = 1 if pos[a][1] >= pos[b][1] else -1
                        pos[a][1] += d * (oy / 2 + .5); pos[b][1] -= d * (oy / 2 + .5)
                    else:
                        d = 1 if (a0 + a1) >= (b0 + b1) else -1
                        pos[a][0] += d * (ox / 2 + .5); pos[b][0] -= d * (ox / 2 + .5)
            # keep clear of the domain names and their glowing cores
            for k in CLUSTERS:
                hx, hy, hk = hubs[k]
                hw, hh = hub_tag(CLUSTERS[k][0], hk)
                ty = hy - HUB_LIFT * hk
                for cx, cy, w2, h2 in ((hx, ty, hw / 2, hh / 2), (hx, hy, 12 * hk, 12 * hk)):
                    ox = min(a1, cx + w2) - max(a0, cx - w2) + 4
                    oy = (h2 + font[a] * 0.7) - abs(ay - cy)
                    if ox > 0 and oy > 0:
                        moved = True
                        pos[a][1] += (1 if pos[a][1] >= cy else -1) * (oy + .5)
        # stay near the anchor (between its domains, or on its domain's ring)
        for a in keys:
            dx, dy = pos[a][0] - anchor[a][0], pos[a][1] - anchor[a][1]
            d = math.hypot(dx, dy)
            if d > 58:
                pos[a] = [anchor[a][0] + dx * 58 / d, anchor[a][1] + dy * 58 / d]
        if not moved:
            break
    return pos, meta, hubs, depth, font


def extent(pos, meta, hubs, font):
    xs, ys = [], []
    for r, (x, y) in pos.items():
        w = label_w(meta[r]["name"], meta[r]["win"], font[r])
        left = x < hubs[meta[r]["k"]][0]
        xs += [x - w if left else x - 8, x + 8 if left else x + w]
        ys += [y - font[r], y + font[r]]
    for k, (hx, hy, hk) in hubs.items():
        hw, hh = hub_tag(CLUSTERS[k][0], hk)
        xs += [hx - hw / 2, hx + hw / 2]
        ys += [hy - HUB_LIFT * hk - hh, hy + 24 * hk]
    return min(xs) - EDGE, max(xs) + EDGE, min(ys) - EDGE, max(ys) + EDGE


# GitHub's Mermaid measures a node with a label as 152 x 24 and an empty one as 32 x 24, then pads
# the union of all boxes by PAD to make the viewBox. Boxes near the edge would widen it past the
# column, so a node's box moves inside the frame and its drawing moves back by the same amount.
BOX_LABEL, BOX_EMPTY = (76, 12), (16, 12)


def inside(x, y, half, frame):
    x0, x1, y0, y1 = frame
    hw, hh = half
    dx = max(0, x0 + PAD + hw - x) - max(0, x + hw - (x1 - PAD))
    dy = max(0, y0 + PAD + hh - y) - max(0, y + hh - (y1 - PAD))
    return dx, dy


def place(x, y, half, frame):
    """CSS for a node drawn at (x, y): its box sits inside the frame, its drawing at (x, y)."""
    dx, dy = inside(x, y, half, frame)
    rule = f"transform:translate({x + dx:.0f}px,{y + dy:.0f}px)"
    if dx or dy:
        rule += f";--ox:{-dx:.0f}px;--oy:{-dy:.0f}px"
    return rule


def fitted_layout():
    """Spread the board until its viewBox is exactly the README column, so it is drawn 1:1."""
    sx, sy = 0.30, 0.66
    avoid = None
    for _ in range(16):
        pos, meta, hubs, depth, font = layout(sx, sy, avoid)
        x0, x1, y0, y1 = extent(pos, meta, hubs, font)
        settled = avoid is not None and abs(avoid[0] - (x1 - BUTTONS[0])) < 1 and abs(avoid[1] - (y1 - BUTTONS[1])) < 1
        avoid = (x1 - BUTTONS[0], y1 - BUTTONS[1])
        if COLUMN - 1.5 <= x1 - x0 <= COLUMN and settled:
            break
        sx *= 1 + ((COLUMN - .75 - (x1 - x0)) / COLUMN) * 1.6
    return pos, meta, hubs, depth, font, (x0, x1, y0, y1)


def arc(x, y, tx, ty, flip=False):
    """Connector from a project at (x, y) to a hub at (tx, ty): a tapered arc (rounded top border), rotated into place."""
    L = math.hypot(tx - x, ty - y)
    ang = math.degrees(math.atan2(ty - y, tx - x))
    return f"width:{L:.0f}px;transform:rotate({ang:.0f}deg){' scaleY(-1)' if flip else ''}"


def mermaid():
    pos, meta, hubs, depth, font, (x0, x1, y0, y1) = fitted_layout()
    desc = descriptions()
    repos = list(pos)
    keys = list(CLUSTERS)
    # hover cells, then an <hr>: the HTML parser closes the <p> before it, so it becomes the
    # scroller's own child, the element the zoom starts on (x1, halfway along the scroll range)
    cells = "<em></em>" * (CELLS[0] * CELLS[1]) + "<hr>"
    lines = ["flowchart LR", '  bg[" "]:::bg', f'  sky["{cells}"]:::sky'] + [f'  c{q}[" "]:::corner' for q in range(4)]
    css = []

    # secondary connectors: one invisible node per extra domain, painted under the projects
    extra = [(r, k2) for r in repos for k2 in meta[r]["others"]]
    for j, (r, k2) in enumerate(extra):
        lines.append(f'  s{j}[" "]:::conn')
    for n, r in enumerate(repos):
        m = meta[r]
        side = "L" if pos[r][0] < hubs[m["k"]][0] else "R"
        cap = desc.get(r, "")
        if m["win"]:
            cap = f"<b>{m['result']}</b>" + cap
        lines.append(f'  p{n}["{m["name"]}<i>{cap}</i>"]:::{"w" if m["win"] else "p"}{side.lower()}')
    for i, k in enumerate(keys):
        lines.append(f'  h{i}["{CLUSTERS[k][0]}"]:::hub')
    ids = ["bg", "sky"] + [f"c{q}" for q in range(4)] + [f"s{j}" for j in range(len(extra))] + \
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

    # board extent: invisible corners, inset by GitHub's padding, so the viewBox is the board itself
    frame = (x0, x1, y0, y1)
    ix, iy = PAD + BOX_EMPTY[0], PAD + BOX_EMPTY[1]
    for q, (cx, cy) in enumerate([(x0 + ix, y0 + iy), (x1 - ix, y0 + iy), (x0 + ix, y1 - iy), (x1 - ix, y1 - iy)]):
        css.append(f"[id*=t-c{q}-]{{transform:translate({cx:.0f}px,{cy:.0f}px)}}")
    cx, cy, W, H = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    css.append(f"[id*=t-bg-],[id*=t-sky-]{{transform:translate({cx:.0f}px,{cy:.0f}px)}}")
    # zoom centre: the hovered cell, mapped so the edge cells zoom on the edges of the board
    C, R = CELLS
    for i in range(C):
        css.append(f".nodes:has(em:nth-child({C}n+{i + 1}):hover){{--zx:{x0 + W * i / (C - 1):.0f}px}}")
    for j in range(R):
        css.append(f".nodes:has(em:nth-child(n+{j * C + 1}):nth-child(-n+{(j + 1) * C}):hover){{--zy:{y0 + H * j / (R - 1):.0f}px}}")

    for i, k in enumerate(keys):
        hx, hy, hk = hubs[k]
        css.append(f"[id*=t-h{i}-]{{{place(hx, hy, BOX_LABEL, frame)};--c:{CLUSTERS[k][1]};--k:{hk:.2f};--s:{hk ** GAMMA:.2f}}}")
        css.append(f".nodes:has([id*=t-h{i}-]:hover) .node:not(.bg,.sky,.corner,.m{i},[id*=t-h{i}-]){{opacity:.1}}")
    for n, r in enumerate(repos):
        x, y = pos[r]
        hx, hy, _ = hubs[meta[r]["k"]]
        css.append(f"[id*=t-p{n}-]{{{place(x, y, BOX_LABEL, frame)};--c:{CLUSTERS[meta[r]['k']][1]};--k:{depth[r]:.2f};--s:{depth[r] ** GAMMA:.2f}}}")
        css.append(f"[id*=t-p{n}-] div::after{{{arc(x, y, hx, hy, n % 2 == 1)}}}")
    for j, (r, k2) in enumerate(extra):
        x, y = pos[r]
        hx, hy, _ = hubs[k2]
        css.append(f"[id*=t-s{j}-]{{{place(x, y, BOX_EMPTY, frame)};--c:{CLUSTERS[k2][1]}}}")
        css.append(f"[id*=t-s{j}-] div::after{{{arc(x, y, hx, hy, j % 2 == 0)}}}")

    # captions open toward the inside of the board near its edges
    flips = {"cr": [], "cl": [], "cu": []}
    for n, r in enumerate(repos):
        x, y = pos[r]
        right = x >= hubs[meta[r]["k"]][0]
        if right and x + 330 > x1:
            flips["cr"].append(f"p{n}")
        if not right and x - 330 < x0:
            flips["cl"].append(f"p{n}")
        if y + 130 > y1:
            flips["cu"].append(f"p{n}")
    for cls, members in flips.items():
        if members:
            lines.append(f"  class {','.join(members)} {cls}")

    P = ".pl,.pr,.wl,.wr"
    base = f"""
.edgePaths,.edgeLabels{{display:none}}
.nodes a{{transform:none!important}}
.nodes{{animation:intro 1.4s {EASE} backwards}}
@keyframes intro{{from{{opacity:0;filter:blur(6px)}}to{{opacity:1;filter:blur(0)}}}}
.node foreignObject{{overflow:visible}}
.node foreignObject div{{position:relative;overflow:visible!important;translate:var(--ox,0px) var(--oy,0px)}}
.node rect,.node polygon,.node circle{{fill:none!important;stroke:none!important}}
.node div::before,.node div::after{{content:counter(x);color:transparent;font-size:0;position:absolute;left:50%;top:50%;pointer-events:none}}
.bg,.corner,.conn{{pointer-events:none}}
.corner div::before,.corner div::after,.bg div::after,.sky div::before,.sky div::after,.conn div::before,.hub div::after{{display:none}}
.bg div::before{{width:3000px;height:2400px;margin:-1200px -1500px;background-color:{BG};background-image:radial-gradient(ellipse 22% 26% at 50% 50%,#151c2b,transparent)}}
.node div::after{{left:50%;top:auto;bottom:50%;height:auto;aspect-ratio:6/1;transform-origin:0 100%;border-top:1.4px solid var(--c);border-radius:50%/100% 100% 0 0;opacity:.62;z-index:-1;transition:opacity .35s {EASE}}}
.conn div::after{{aspect-ratio:8/1;border-top:1.1px dashed var(--c);opacity:.5}}
{P.replace(',', ' div::before,')} div::before{{width:calc(7px*var(--k));height:calc(7px*var(--k));margin:calc(-3.5px*var(--k));background-color:var(--c);border-radius:50%;box-shadow:0 0 0 2px {BG},0 0 7px var(--c)}}
.wl div::before,.wr div::before{{width:calc(8px*var(--k));height:calc(8px*var(--k));margin:calc(-4px*var(--k));background-color:{GOLD};border-radius:50%;box-shadow:0 0 0 2px {BG},0 0 0 3px {GOLD},0 0 9px {GOLD}}}
.node .nodeLabel{{position:absolute;left:50%;top:50%;display:block;font:500 calc({FONT}px*var(--s))/1.25 {FONTS};white-space:nowrap;color:{INK}!important;text-shadow:0 0 4px {BG},0 0 1px {BG};transition:color .25s}}
.node .nodeLabel p{{margin:0;color:inherit!important}}
.pr .nodeLabel,.wr .nodeLabel{{transform:translate({GAP}px,-50%)}}
.pl .nodeLabel,.wl .nodeLabel{{transform:translate(calc(-100% - {GAP}px),-50%);text-align:right}}
.wl .nodeLabel,.wr .nodeLabel{{color:#fde68a!important;font-weight:650}}
{P.replace(',', ':hover .nodeLabel,')}:hover .nodeLabel{{color:#fff!important}}
{P}{{cursor:pointer}}
{P.replace(',', ':hover div::after,')}:hover div::after{{opacity:.95}}
.nodes:has({P.replace(',', ':hover,')}:hover) .conn div::after{{opacity:.9}}
.nodes:has({P.replace(',', ':hover,')}:hover) .node:not(:hover,.bg,.sky,.corner,.hub){{opacity:.28}}
.nodes:has({P.replace(',', ':hover,')}:hover) .hub{{opacity:.35}}
.nodeLabel i{{display:block;position:absolute;top:100%;left:0;margin-top:5px;width:max-content;max-width:310px;white-space:normal;text-align:left;font:400 13px/1.45 {FONTS};font-style:normal;color:#c9d1d9;
background-color:#0d1117f2;padding:7px 10px;border:1px solid #30363d;border-left:3px solid var(--c);border-radius:5px;text-shadow:none;opacity:0;transform:translateY(-3px);transition:opacity .2s,transform .2s {EASE};pointer-events:none}}
.nodeLabel i b{{display:block;margin-bottom:3px;font-weight:650;color:{GOLD}}}
.pl .nodeLabel i,.wl .nodeLabel i{{left:auto;right:0}}
.cr .nodeLabel i{{left:auto!important;right:0}}
.cl .nodeLabel i{{right:auto!important;left:0}}
.cu .nodeLabel i{{top:auto;bottom:100%;margin:0 0 5px}}
{P.replace(',', ':hover .nodeLabel i,')}:hover .nodeLabel i{{opacity:1;transform:none}}
.hub div::before{{display:block;width:calc(16px*var(--k));height:calc(16px*var(--k));margin:calc(-8px*var(--k));border-radius:50%;background-image:radial-gradient(circle,#fff 0,var(--c) 42%,transparent 72%);box-shadow:0 0 calc(22px*var(--k)) calc(6px*var(--k)) var(--c)}}
.hub .nodeLabel{{transform:translate(-50%,calc(-50% - {HUB_LIFT}px*var(--k)));font:700 calc({HUB_FONT}px*var(--s))/1 {FONTS};letter-spacing:.1em;text-transform:uppercase;color:#fff!important;text-shadow:0 0 8px var(--c),0 0 2px {BG},0 0 5px {BG}}}
.hub{{transition:opacity .35s {EASE}}}
a,a:hover,a *,a:hover *{{text-decoration:none!important}}
.nodes{{timeline-scope:--z}}
.node{{transform-box:view-box;transform-origin:var(--zx,{cx:.0f}px) var(--zy,{cy:.0f}px);transition:opacity .35s {EASE},transform-origin 1ms 99999s}}
.nodes:has(em:hover) .node{{transition:opacity .35s {EASE},transform-origin {GLIDE}}}
.node:not(.bg,.sky){{animation:z 1e9s linear both;animation-timeline:--z}}
@keyframes z{{to{{scale:{ZOOM[1]}}}}}
@keyframes z2{{0%{{scale:{ZOOM[0]}}}50%{{scale:1}}to{{scale:{ZOOM[1]}}}}}
@supports (scroll-initial-target:nearest){{.node:not(.bg,.sky){{animation-name:z2}}.sky hr{{scroll-initial-target:nearest;scroll-snap-align:center}}}}
.sky foreignObject div{{position:absolute!important;left:50%;top:50%;display:block!important;width:0;height:0;max-width:none!important}}
.sky .nodeLabel{{position:absolute!important;left:0;top:0;display:flex!important;width:{W:.0f}px;height:{H:.0f}px;translate:{-W / 2:.0f}px {-H / 2:.0f}px;transform:none!important;overflow:scroll hidden;direction:rtl;scrollbar-width:none;scroll-timeline:--z x;overscroll-behavior-x:contain}}
.sky .nodeLabel p{{flex:none;position:sticky;left:0;right:0;direction:ltr;display:grid;grid-template:repeat({CELLS[1]},1fr)/repeat({CELLS[0]},1fr);width:{W:.0f}px;height:{H:.0f}px}}
.sky hr{{flex:none;width:{W:.0f}px;height:{H:.0f}px;margin:0 {W:.0f}px 0 {2 * W:.0f}px;border:0;padding:0}}
.sky .nodeLabel hr~p{{display:none}}
.sky em{{display:block}}
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
