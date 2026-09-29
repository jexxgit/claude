"""LULLABY loading sprite: a syringe that slowly fills with white liquid, then drips (grey / white / black only).
Sheet: 4 x 4 frames of 256 px = 1024 x 1024, transparent background, frames read left->right, top->bottom.
Frames 0-11 = filling (0 -> 100 %), 12-13 = droplet forms at the needle, 14 = droplet falls, 15 = empty again (loop point).
Run: python3 make_syringe_sprite.py  -> syringe_sheet.png + raw/syringe_sheet.rgba (raw RGBA for the Studio EditableImage upload)."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

OUT = os.path.dirname(os.path.abspath(__file__))
F, S, COLS = 256, 4, 4          # frame px, supersample, columns
W = F * S
rng = np.random.default_rng(42)

def g(v, a=255): return (v, v, v, a)

def frame(i):
    fill = min(i, 11) / 11 if i < 15 else 0.0
    drop = {12: 0.35, 13: 0.8, 14: 1.6}.get(i, 0)     # droplet at needle tip
    H = int(W * 1.35)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = W // 2
    bx0, bx1 = cx - 0.11 * W, cx + 0.11 * W           # barrel
    by0, by1 = 0.36 * W, 0.78 * W
    # needle + hub
    hub0, hub1 = by1, by1 + 0.05 * W
    nx0, nx1, ny1 = cx - 0.006 * W, cx + 0.006 * W, hub1 + 0.17 * W
    d.polygon([(nx0, hub1), (nx1, hub1), (cx, ny1)], fill=g(215))
    d.rounded_rectangle([cx - 0.05 * W, by1 - 4, cx + 0.05 * W, hub1], radius=10, fill=g(120), outline=g(45), width=6)
    # liquid + stopper position: stopper rises as it fills
    stop_y = by1 - 0.03 * W - fill * (by1 - by0 - 0.10 * W)
    # barrel glass
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=g(105, 210), outline=g(30), width=8)
    liq = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(liq)
    ld.rectangle([bx0 + 8, stop_y, bx1 - 8, by1 - 6], fill=g(248))
    # meniscus / sheen
    ld.rectangle([bx0 + 30, stop_y + 12, bx0 + 52, by1 - 12], fill=g(200))
    img.alpha_composite(liq)
    d = ImageDraw.Draw(img)
    # graduations
    for k in range(9):
        y = by0 + 0.05 * W + k * (by1 - by0 - 0.1 * W) / 8
        ln = 0.06 * W if k % 2 == 0 else 0.035 * W
        d.line([bx1 - 8 - ln, y, bx1 - 8, y], fill=g(235 if y < stop_y else 40), width=5)
    # plunger: stopper, rod, thumb disc
    d.rounded_rectangle([bx0 + 8, stop_y - 0.045 * W, bx1 - 8, stop_y], radius=8, fill=g(38), outline=g(12), width=4)
    rod_top = stop_y - 0.26 * W
    d.rectangle([cx - 0.018 * W, rod_top, cx + 0.018 * W, stop_y - 0.045 * W], fill=g(170), outline=g(45), width=4)
    d.rectangle([cx - 0.05 * W, rod_top + 0.02 * W, cx + 0.05 * W, rod_top + 0.03 * W], fill=g(150), outline=g(45), width=3)   # rod cross
    d.rounded_rectangle([cx - 0.13 * W, rod_top - 0.035 * W, cx + 0.13 * W, rod_top + 0.005 * W], radius=14, fill=g(225), outline=g(35), width=7)
    # flange (finger grip) at the top of the barrel
    d.rounded_rectangle([cx - 0.19 * W, by0 - 0.03 * W, cx + 0.19 * W, by0 + 0.01 * W], radius=12, fill=g(232), outline=g(35), width=7)
    # glass highlights
    d.rounded_rectangle([bx0 + 16, by0 + 20, bx0 + 28, by1 - 20], radius=6, fill=g(255, 150))
    # droplet
    if drop:
        r = 0.034 * W * min(drop, 1.0) + 6
        dy = ny1 + (r if drop <= 1 else r + (drop - 1) * 0.16 * W)
        d.ellipse([cx - r, dy - r * 1.2, cx + r, dy + r * 1.2], fill=g(250), outline=g(30), width=4)
        d.ellipse([cx - r * 0.45, dy - r * 0.8, cx - r * 0.1, dy - r * 0.3], fill=g(150))
    # tilt for a dynamic pose
    img = img.rotate(-24, resample=Image.BICUBIC, center=(cx, H * 0.5))
    return img

def finish(img, box):
    img = img.crop(box)
    # soft dark halo behind (reads on any background) + film grain on the colour only
    a = np.array(img).astype(np.float32)
    halo = gaussian_filter(a[..., 3], 22) * 0.55
    small = img.resize((F, F), Image.LANCZOS)
    a = np.array(small).astype(np.float32)
    halo_s = np.array(Image.fromarray(halo.clip(0, 255).astype(np.uint8)).resize((F, F), Image.LANCZOS)).astype(np.float32)
    alpha = np.maximum(a[..., 3], halo_s * 0.7)
    rgb = a[..., :3] * (a[..., 3:4] / 255) + 0.0
    grain = rng.normal(0, 5, (F, F, 1))
    rgb = np.clip(rgb + grain * (a[..., 3:4] / 255), 0, 255)
    out = np.dstack([rgb, alpha]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out)

sheet = Image.new("RGBA", (F * COLS, F * COLS), (0, 0, 0, 0))
hi = [frame(i) for i in range(16)]
bbs = [im.getchannel("A").getbbox() for im in hi]
x0, y0 = min(b[0] for b in bbs), min(b[1] for b in bbs)
x1, y1 = max(b[2] for b in bbs), max(b[3] for b in bbs)
side = int(max(x1 - x0, y1 - y0) * 1.04)
cxm, cym = (x0 + x1) // 2, (y0 + y1) // 2
box = (cxm - side // 2, cym - side // 2, cxm + side // 2, cym + side // 2)   # same box for every frame: no jitter
for i, im in enumerate(hi):
    sheet.paste(finish(im, box), ((i % COLS) * F, (i // COLS) * F))
sheet.save(os.path.join(OUT, "syringe_sheet.png"))
os.makedirs(os.path.join(OUT, "raw"), exist_ok=True)
open(os.path.join(OUT, "raw", "syringe_sheet.rgba"), "wb").write(np.array(sheet).tobytes())
# preview on a dark hospital background
bg = Image.new("RGBA", sheet.size, (28, 32, 36, 255)); bg.alpha_composite(sheet); bg.convert("RGB").save(os.path.join(OUT, "preview.png"))
print("ok", sheet.size)
