"""Fast lattice iteration: build + render one variant.
Usage: python3 _lat.py <variant> [elev] [size] [ss]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, render
import lattice as L

name = sys.argv[1] if len(sys.argv) > 1 else "coral"
elev = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
render.SIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 820
ss = int(sys.argv[4]) if len(sys.argv) > 4 else 1

render.FILAMENT["radial"] = np.array([0.66, 0.83, 0.77])
render.SHEEN = 0.30
render.SHEEN_POW = 10
render.LIGHTS = render.porcelain_lights()
render.BACKDROP = (0.93, 0.86)
mesh = L.build(L.VARIANTS[name])
out = f"/home/user/design/verkstad/renders/_lat-{name}.png"
render.render_png(mesh, "radial", out, az_deg=26, el_deg=elev, ss=ss)
print(f"{name}: {len(mesh.faces)} tris -> {out}")
