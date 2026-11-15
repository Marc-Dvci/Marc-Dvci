"""Build the 3D project graph as an ASCII STL that GitHub renders natively.

Nodes are spheres (winners bigger), cluster hubs are larger spheres, edges are thin
prisms, and every name is real 3D text so it reads inside GitHub's viewer.
"""
import math, sys
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

sys.path.insert(0, str(Path(__file__).parent))
from projects import CLUSTERS, PROJECTS

SIMPLIFY = 0.04
DEPTH = 0.0
FONT = FontProperties(family="DejaVu Sans", weight="bold")


def text_mesh(s, size, depth):
    path = TextPath((0, 0), s, size=size, prop=FONT)
    shape = None
    for ring in path.to_polygons():
        if len(ring) < 3:
            continue
        p = Polygon(ring).buffer(0)
        shape = p if shape is None else shape.symmetric_difference(p)
    if shape is None:
        return None
    shape = shape.simplify(size * SIMPLIFY)
    geoms = getattr(shape, "geoms", [shape])
    parts = []
    for g in geoms:
        if g.area <= 0:
            continue
        if depth > 0:
            parts.append(trimesh.creation.extrude_polygon(g, depth))
        else:
            v2, f = trimesh.creation.triangulate_polygon(g, engine="earcut")
            v3 = np.column_stack([v2, np.zeros(len(v2))])
            # front face plus a back face, so the label shows from both sides
            parts.append(trimesh.Trimesh(np.vstack([v3, v3]), np.vstack([f, f[:, ::-1] + len(v3)]), process=False))
    m = trimesh.util.concatenate(parts)
    # centre horizontally, stand the text up: x right, z up, facing -y
    m.apply_translation([-m.bounds[:, 0].mean(), 0, 0])
    m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    return m


def prism(a, b, r):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    L = np.linalg.norm(d)
    if L < 1e-6:
        return None
    m = trimesh.creation.cylinder(radius=r, height=L, sections=3)
    m.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], d / L))
    m.apply_translation((a + b) / 2)
    return m


def layout():
    keys = list(CLUSTERS)
    centers = {}
    for i, k in enumerate(keys):
        t = 2 * math.pi * i / len(keys)
        centers[k] = np.array([70 * math.cos(t), 70 * math.sin(t), 12 * math.sin(3 * t)])
    pos = {}
    for k in keys:
        members = [p for p in PROJECTS if p[2] == k]
        n = len(members)
        for j, p in enumerate(members):
            # golden spiral on a sphere around the hub
            y = 1 - 2 * (j + 0.5) / n
            rr = math.sqrt(1 - y * y)
            th = j * math.pi * (3 - math.sqrt(5))
            off = np.array([rr * math.cos(th), rr * math.sin(th), y]) * (16 + 2.5 * math.sqrt(n))
            pos[p[0]] = centers[k] + off
    return centers, pos


def build(label_all=True):
    centers, pos = layout()
    parts = []
    for k, c in centers.items():
        parts.append(trimesh.creation.icosphere(subdivisions=2, radius=4.0).apply_translation(c))
        t = text_mesh(CLUSTERS[k].upper(), size=5.0, depth=DEPTH)
        parts.append(t.apply_translation(c + [0, 0, 8]))
    for repo, name, k, result in PROJECTS:
        p = pos[repo]
        win = result is not None
        parts.append(trimesh.creation.icosphere(subdivisions=1 if win else 0, radius=2.6 if win else 1.4).apply_translation(p))
        e = prism(p, centers[k], 0.18)
        if e is not None:
            parts.append(e)
        if win or label_all:
            t = text_mesh(name, size=3.0 if win else 2.0, depth=DEPTH)
            parts.append(t.apply_translation(p + [0, 0, 3.2 if win else 2.2]))
    return trimesh.util.concatenate(parts)


def compact_stl(mesh, name="projects", scale=10):
    """Integer coordinates, no 'outer loop' lines: about 85 bytes a triangle."""
    out = [f"solid {name}"]
    V = np.rint(mesh.vertices * scale).astype(int)
    for f, n in zip(mesh.faces, mesh.face_normals + 0.0):
        a, b, c = V[f]
        out.append(f"facet normal {n[0]:.1g} {n[1]:.1g} {n[2]:.1g} vertex {a[0]} {a[1]} {a[2]} vertex {b[0]} {b[1]} {b[2]} vertex {c[0]} {c[1]} {c[2]} endfacet")
    out.append(f"endsolid {name}")
    return "\n".join(out) + "\n"


def ascii_stl(mesh, name="projects"):
    out = [f"solid {name}"]
    for tri, n in zip(mesh.triangles, mesh.face_normals):
        out.append(f"facet normal {n[0]:.1f} {n[1]:.1f} {n[2]:.1f}\nouter loop")
        for v in tri:
            out.append(f"vertex {v[0]:.1f} {v[1]:.1f} {v[2]:.1f}")
        out.append("endloop\nendfacet")
    out.append(f"endsolid {name}")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    m = build()
    s = ascii_stl(m)
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("graph.stl")
    dest.write_text(s, encoding="ascii")
    print(f"{len(m.faces)} triangles, {len(s)/1e6:.2f} MB")
