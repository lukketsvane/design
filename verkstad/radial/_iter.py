"""Fast iteration helper: build one variant and render it small for feedback.
Usage: python3 _iter.py <variant> [elev] [size] [ss]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np, trimesh, render
import radial as R

name = sys.argv[1] if len(sys.argv) > 1 else "vertebra"
elev = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
render.SIZE = int(sys.argv[3]) if len(sys.argv) > 3 else 820
ss = int(sys.argv[4]) if len(sys.argv) > 4 else 1

render.FILAMENT["radial"] = np.array([0.66, 0.83, 0.77])   # celadon
render.SHEEN = 0.26
render.SHEEN_POW = 12
render.LIGHTS = render.porcelain_lights()                  # soft studio rig
render.BACKDROP = (0.90, 0.82)                             # grey gradient
mesh = R.build(R.VARIANTS[name])
out = f"/home/user/design/verkstad/renders/_r-{name}.png"
render.render_png(mesh, "radial", out, az_deg=32, el_deg=elev, ss=ss)
print(f"{name}: {len(mesh.faces)} tris -> {out}")
