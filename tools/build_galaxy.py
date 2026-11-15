"""Build the project galaxy as a Mermaid block for the profile README.

GitHub renders Mermaid in a sandboxed page that allows top navigation, so `click`
links open repos. `themeCSS` is passed through, so CSS places every node (overriding
the layout Mermaid computes), tilts the plane in perspective and animates the orbits.

Rules learnt on github.com:
- a single quote anywhere in the init JSON makes GitHub drop the whole directive;
- every rule is scoped under #diagram, so the root <svg> itself cannot be styled;
- clickable nodes sit in an <a> that carries Mermaid's own position: cancel it;
- the viewBox is measured after this CSS applies, so it wraps the galaxy.
"""
import math, sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from projects import CLUSTERS, PROJECTS

GH = "https://github.com/Marc-Dvci/"
TILT = 54                       # degrees the galaxy plane leans back
SQUASH = 1 / math.cos(math.radians(TILT))
COLORS = {"health": "#ff7a45", "audit": "#5b9dff", "agents": "#b07cff", "money": "#25d0a6",
          "edge": "#ffc23d", "science": "#ff5fa8", "consumer": "#8fe04a"}
SHORT = {"health": "Health", "audit": "Audit", "agents": "Agents", "money": "Crypto",
         "edge": "Robotics", "science": "Science", "consumer": "Consumer"}

HUB_RING_X, HUB_RING_Y = 470, 425
ORBIT0, ORBIT_STEP, PER_ORBIT = 80, 46, 4
CHAIN = 5


def plane_layout():
    keys = list(CLUSTERS)
    hubs, planets = {}, []
    for i, k in enumerate(keys):
        t = 2 * math.pi * i / len(keys) - math.pi / 2
        hubs[k] = (HUB_RING_X * math.cos(t), HUB_RING_Y * math.sin(t))
        members = [p for p in PROJECTS if p[2] == k]
        for j, p in enumerate(members):
            ring = j // PER_ORBIT
            on_ring = min(PER_ORBIT, len(members) - ring * PER_ORBIT)
            slot = j % PER_ORBIT
            phase = 360 * slot / on_ring + 45 * ring + 31 * i
            planets.append(dict(repo=p[0], name=p[1], k=k, win=p[3] is not None,
                                r=ORBIT0 + ORBIT_STEP * ring, phase=phase,
                                period=80 + 30 * ring))      # outer orbits are slower
    return hubs, planets


def n_rings(k, planets):
    return 1 + (sum(1 for p in planets if p["k"] == k) - 1) // PER_ORBIT


def stars():
    """A few layers of tiny dots, written without quotes."""
    layers, sizes = [], []
    seeds = [(37, 61, 210, 170, "#ffffffaa"), (113, 19, 260, 230, "#cfe0ff88"), (171, 143, 330, 290, "#ffffff66"),
             (59, 211, 400, 350, "#ffe6c066")]
    for x, y, w, h, c in seeds:
        layers.append(f"radial-gradient(1.4px 1.4px at {x}px {y}px,{c} 50%,transparent 51%)")
        sizes.append(f"{w}px {h}px")
    return ",".join(layers), ",".join(sizes)


def mermaid():
    hubs, planets = plane_layout()
    keys = list(CLUSTERS)
    lines = ["flowchart LR"]
    css = []

    # paint order: sky, orbit rings, planets, hubs on top
    lines.append('  sky[" "]:::sky')
    for i, k in enumerate(keys):
        lines.append(f'  r{i}[" "]:::ring')
    for n, p in enumerate(planets):
        label = ("★ " if p["win"] else "") + p["name"]
        lines.append(f'  p{n}["{label}"]:::{"win" if p["win"] else "planet"}')
    for i, k in enumerate(keys):
        lines.append(f'  h{i}(("{SHORT[k]}")):::hub')
    ids = ["sky"] + [f"r{i}" for i in range(len(keys))] + [f"p{n}" for n in range(len(planets))] + [f"h{i}" for i in range(len(keys))]
    for a in range(0, len(ids), CHAIN):       # invisible chains keep Mermaid's own layout compact
        lines.append("  " + " ~~~ ".join(ids[a:a + CHAIN]))
    for n, p in enumerate(planets):
        lines.append(f'  click p{n} "{GH}{p["repo"]}"')

    # geometry
    for i, k in enumerate(keys):
        hx, hy = hubs[k]
        c = COLORS[k]
        rings = n_rings(k, planets)
        rmax = ORBIT0 + ORBIT_STEP * (rings - 1)
        stops = []
        for q in range(rings):
            r = ORBIT0 + ORBIT_STEP * q
            stops += [f"transparent {r - 1}px", f"{c}66 {r - 1}px", f"{c}66 {r + 1}px", f"transparent {r + 1}px"]
        css.append(f"[id*=flowchart-r{i}-]{{transform:translate({hx:.0f}px,{hy:.0f}px)}}")
        css.append(f"[id*=flowchart-r{i}-] foreignObject div::before{{width:{2 * rmax + 4}px;height:{2 * rmax + 4}px;"
                   f"margin:{-rmax - 2}px;background:radial-gradient(circle,{c}40 0,{c}10 46px,transparent 70px,{','.join(stops)})}}")
        css.append(f"[id*=flowchart-h{i}-]{{transform:translate({hx:.0f}px,{hy:.0f}px);--c:{c}}}")
    for n, p in enumerate(planets):
        hx, hy = hubs[p["k"]]
        delay = -p["period"] * p["phase"] / 360
        css.append(f"[id*=flowchart-p{n}-]{{--x:{hx:.0f}px;--y:{hy:.0f}px;--r:{p['r']}px;--c:{COLORS[p['k']]};"
                   f"animation-duration:{p['period']}s;animation-delay:{delay:.1f}s}}")
    # hovering a hub lights its system and dims the rest
    for i, k in enumerate(keys):
        members = ",".join(f"[id*=flowchart-p{n}-]" for n, p in enumerate(planets) if p["k"] == k)
        css.append(f".nodes:has([id*=flowchart-h{i}-]:hover) .node:not(.sky,[id*=flowchart-h{i}-],[id*=flowchart-r{i}-],{members}){{opacity:.1}}")

    star_bg, star_size = stars()
    base = f"""
.edgePaths,.edgeLabels{{display:none}}
.nodes a{{transform:none!important}}
.nodes{{transform-box:fill-box;transform-origin:50% 50%;animation:cam 26s ease-in-out infinite alternate}}
@keyframes cam{{from{{transform:perspective(2400px) rotateX({TILT - 3}deg) rotateZ(-3deg)}}to{{transform:perspective(2400px) rotateX({TILT + 3}deg) rotateZ(3deg)}}}}
.nodes:hover,.nodes:hover .node{{animation-play-state:paused}}
.node{{transition:opacity .35s}}
.node foreignObject{{overflow:visible}}
.node foreignObject div{{transform:scaleY({SQUASH:.3f});transform-origin:50% 50%}}
.node .nodeLabel,.node .nodeLabel p{{font:600 19px/1.2 Segoe UI,Helvetica,Arial,sans-serif;white-space:nowrap;color:#dbe4ff!important}}
.sky rect,.ring rect{{fill:none!important;stroke:none!important}}
.ring{{pointer-events:none}}
.sky foreignObject div::before,.ring foreignObject div::before{{content:counter(x);color:transparent;font-size:0;position:absolute;left:50%;top:50%;border-radius:50%;transform:scaleY({1 / SQUASH:.3f})}}
.sky foreignObject div::before{{width:3000px;height:2600px;margin:-1300px -1500px;border-radius:0;
background:{star_bg},radial-gradient(ellipse at 50% 50%,#17223f 0,#0a1020 45%,#05070d 75%);background-size:{star_size},100% 100%}}
.planet rect,.win rect{{fill:transparent!important;stroke:none!important}}
.planet foreignObject div::before,.win foreignObject div::before{{content:counter(x);color:transparent;font-size:0;display:inline-block;
width:12px;height:12px;margin-right:8px;border-radius:50%;vertical-align:middle;background:var(--c);box-shadow:0 0 12px var(--c);transform:scaleY({1 / SQUASH:.3f})}}
.planet .nodeLabel{{text-shadow:0 0 10px #000,0 0 3px #000}}
.win .nodeLabel,.win .nodeLabel p{{color:#ffd76a!important;font-size:24px!important;text-shadow:0 0 14px #ffb02099,0 0 3px #000}}
.win foreignObject div::before{{width:16px;height:16px;background:#ffd76a;box-shadow:0 0 18px #ffb020}}
.planet,.win{{animation:orbit 90s linear infinite;cursor:pointer}}
@keyframes orbit{{from{{transform:translate(var(--x),var(--y)) rotate(0deg) translateX(var(--r)) rotate(0deg)}}to{{transform:translate(var(--x),var(--y)) rotate(360deg) translateX(var(--r)) rotate(-360deg)}}}}
.planet:hover .nodeLabel,.win:hover .nodeLabel,.planet:hover .nodeLabel p,.win:hover .nodeLabel p{{color:#fff!important;text-shadow:0 0 14px var(--c),0 0 4px var(--c)}}
.planet:hover foreignObject div,.win:hover foreignObject div{{transform:scaleY({SQUASH:.3f}) scale(1.18)}}
.hub circle{{r:44px;fill:#0b1222!important;stroke:var(--c)!important;stroke-width:3px!important;filter:drop-shadow(0 0 18px var(--c))}}
.hub .nodeLabel,.hub .nodeLabel p{{font-size:20px!important;letter-spacing:.06em;text-transform:uppercase;color:#fff!important;text-shadow:0 0 12px var(--c),0 0 3px #000}}
.hub:hover circle{{fill:var(--c)!important}}
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
