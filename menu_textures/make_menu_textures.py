"""Procedural textures for the lobby menu (ink fade, wood planks, ivy vines, distressed title).
Run: python3 make_menu_textures.py  -> writes the PNGs next to this script."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import zoom, gaussian_filter

OUT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(1337)


def noise(h, w, cells_y, cells_x, seed=None):
    r = np.random.default_rng(seed) if seed is not None else rng
    a = r.random((max(2, cells_y), max(2, cells_x)))
    z = zoom(a, (h / a.shape[0], w / a.shape[1]), order=3)
    return z[:h, :w]


def fitz(a, h, w, order=3):
    z = zoom(a, (h / a.shape[0], w / a.shape[1]), order=order)
    z = z[:h, :w]
    if z.shape != (h, w):
        z = np.pad(z, ((0, h - z.shape[0]), (0, w - z.shape[1])), mode="edge")
    return z


def fbm(h, w, base_y, base_x, octaves=5, seed=None):
    r = np.random.default_rng(seed)
    out, amp, tot = np.zeros((h, w)), 1.0, 0.0
    for o in range(octaves):
        a = r.random((max(2, base_y * 2 ** o), max(2, base_x * 2 ** o)))
        z = zoom(a, (h / a.shape[0], w / a.shape[1]), order=3)[:h, :w]
        out += z * amp
        tot += amp
        amp *= 0.5
    out /= tot
    return (out - out.min()) / (out.max() - out.min() + 1e-9)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p, optimize=True)
    print(name, img.size, os.path.getsize(p) // 1024, "KB")


# ---------------------------------------------------------------- ink fade
def make_ink(seed=5):
    H, W = 1024, 1024
    x = np.linspace(0, 1, W)[None, :].repeat(H, 0)
    y = np.linspace(0, 1, H)[:, None].repeat(W, 1)
    tongues = fbm(H, W, 14, 3, 5, seed)             # long horizontal tongues of ink
    blobs = fbm(H, W, 4, 4, 5, seed + 1)
    edge = x + (tongues - 0.5) * 0.55 + (blobs - 0.5) * 0.25
    alpha = 1 - smoothstep(0.30, 0.95, edge)
    alpha = np.clip(alpha ** 0.85, 0, 1)
    # ink pools at the top and bottom
    vign = np.maximum(smoothstep(0.30, 0.0, y), smoothstep(0.70, 1.0, y)) * (1 - smoothstep(0.0, 0.8, x))
    alpha = np.maximum(alpha, vign * 0.85)
    # brushed / wet texture inside the ink
    tex = fbm(H, W, 40, 6, 4, seed + 2)
    alpha = np.clip(alpha * (0.90 + 0.10 * tex), 0, 1)
    solid = smoothstep(0.0, 0.12, 0.32 - x)  # fully black hard edge on the far left
    alpha = np.maximum(alpha, solid)
    rgb = np.stack([6 + 5 * tex, 8 + 6 * tex, 7 + 5 * tex], -1)
    img = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    # a few splatters flying off the edge
    im = Image.fromarray(img, "RGBA")
    d = ImageDraw.Draw(im)
    for _ in range(90):
        cx = rng.uniform(0.45, 0.85) * W
        cy = rng.uniform(0, H)
        r = rng.uniform(1.5, 7) * (1.4 - (cx / W))
        d.ellipse([cx - r, cy - r * rng.uniform(0.7, 1.3), cx + r, cy + r], fill=(6, 8, 7, int(rng.uniform(120, 230))))
    return im.filter(ImageFilter.GaussianBlur(0.6))


# ---------------------------------------------------------------- wood plank
def make_plank(seed, w=1024, h=256, nails=(0.07, 0.93)):
    r = np.random.default_rng(seed)
    # colour
    g1 = fbm(h, w, 3, 3, 4, seed) * 0.5
    fine = fitz(r.random((h * 2, 6)), h, w, 1) * 0.30
    mid = fitz(r.random((h // 3, 12)), h, w, 3) * 0.30
    grain = np.clip(g1 + fine + mid, 0, 1)
    dark, light = np.array([44, 34, 26]), np.array([98, 82, 64])
    col = dark + (light - dark) * grain[..., None]
    # grey weathering
    weather = fbm(h, w, 2, 6, 4, seed + 3)[..., None]
    col = col * (0.75 + 0.35 * weather) + np.array([10, 10, 10]) * weather * 0.5
    # moss / damp stains
    stain = smoothstep(0.62, 0.8, fbm(h, w, 3, 8, 4, seed + 4))
    moss = np.array([38, 54, 30])
    col = col * (1 - stain[..., None] * 0.22) + moss * stain[..., None] * 0.22
    dirt = smoothstep(0.55, 0.9, fbm(h, w, 6, 12, 5, seed + 5))
    col *= (1 - 0.5 * dirt[..., None])
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    # knots
    for _ in range(2):
        kx, ky = r.uniform(0.15, 0.85) * w, r.uniform(0.3, 0.7) * h
        for i in range(6):
            rr = 26 - i * 4
            tone = 20 + i * 7
            d.ellipse([kx - rr * 1.6, ky - rr * 0.7, kx + rr * 1.6, ky + rr * 0.7], outline=(tone, tone - 6, tone - 12, 200), width=2)
        d.ellipse([kx - 7, ky - 4, kx + 7, ky + 4], fill=(14, 10, 8, 230))
    # cracks (random walks with branches)
    def crack(x0, y0, ang, length, width):
        x_, y_ = x0, y0
        pts = [(x_, y_)]
        for _ in range(int(length)):
            ang += r.normal(0, 0.28)
            x_ += math.cos(ang) * 5
            y_ += math.sin(ang) * 5
            pts.append((x_, y_))
            if r.random() < 0.05 and width > 1:
                crack(x_, y_, ang + r.choice([-0.9, 0.9]), length * 0.3, 1)
        d.line([(px + 1, py + 1) for px, py in pts], fill=(120, 105, 85, 70), width=max(1, width))   # lit lip
        d.line(pts, fill=(6, 5, 4, 235), width=width + 1)
    for _ in range(4):
        crack(r.uniform(0.1, 0.9) * w, r.choice([16, h - 16]), r.choice([math.pi / 2, -math.pi / 2]) + r.normal(0, 0.3), r.uniform(8, 22), 2)
    for _ in range(3):
        crack(r.choice([30, w - 30]), r.uniform(0.3, 0.7) * h, r.choice([0, math.pi]) + r.normal(0, 0.2), r.uniform(20, 46), 3)
    # long horizontal grain scratches
    for _ in range(14):
        yy = r.uniform(12, h - 12)
        x0 = r.uniform(0, w * 0.7)
        d.line([(x0, yy), (x0 + r.uniform(80, 300), yy + r.normal(0, 3))], fill=(12, 9, 7, int(r.uniform(60, 130))), width=1)
    # nails + rust streaks
    for nx in nails:
        cx, cy = nx * w, h * 0.5 + r.uniform(-6, 6)
        streak = np.zeros((h, w))
        sx = int(cx)
        L = int(r.uniform(50, 100))
        for k in range(L):
            a = (1 - k / L) ** 1.5 * 0.7
            yy = int(cy + 8 + k)
            if 0 <= yy < h:
                streak[yy, max(0, sx - 3):sx + 4] = a
        streak = gaussian_filter(streak, 1.6)
        arr = np.array(im).astype(float)
        rust = np.array([120, 58, 26, 255.0])
        arr[..., :3] = arr[..., :3] * (1 - streak[..., None] * 0.9) + rust[:3] * streak[..., None] * 0.9
        im = Image.fromarray(arr.astype(np.uint8), "RGBA")
        d = ImageDraw.Draw(im, "RGBA")
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(8, 6, 5, 190))   # dent
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(70, 68, 64, 255), outline=(14, 12, 10, 255), width=2)
        d.ellipse([cx - 6, cy - 7, cx + 1, cy], fill=(130, 128, 120, 200))
        d.ellipse([cx + 1, cy + 1, cx + 7, cy + 7], fill=(90, 46, 22, 200))
    # bevel / edge wear
    arr = np.array(im).astype(float)
    yy = np.arange(h)[:, None]
    edge_d = np.minimum(yy, h - 1 - yy)[:, :1].repeat(w, 1)
    arr[..., :3] *= (0.55 + 0.45 * smoothstep(0, 14, edge_d))[..., None]
    arr[..., :3] += (smoothstep(4, 0, np.abs(yy - 3)) * 22)[..., None].repeat(w, 1)
    # silhouette: wavy long edges, splintered ends
    top = 6 + fbm(1, w, 2, 40, 4, seed + 7)[0] * 10
    bot = h - 6 - fbm(1, w, 2, 40, 4, seed + 8)[0] * 10
    mask = ((yy >= top[None, :]) & (yy <= bot[None, :])).astype(float)
    xx = np.arange(w)[None, :]
    lend = 10 + fbm(h, 1, 30, 2, 3, seed + 9)[:, 0] * 46 * (r.random(h) > 0.15)
    rend = w - 10 - fbm(h, 1, 30, 2, 3, seed + 10)[:, 0] * 46 * (r.random(h) > 0.15)
    mask *= ((xx >= lend[:, None]) & (xx <= rend[:, None])).astype(float)
    mask = gaussian_filter(mask, 0.9)
    arr[..., 3] = np.clip(mask * 255, 0, 255)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- ivy vines
def ivy_leaf(size, hue_seed):
    S = size * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    cx, cy = S / 2, S * 0.62
    # three lobes + heart base, pointing up
    d.ellipse([cx - S * 0.13, cy - S * 0.52, cx + S * 0.13, cy + S * 0.02], fill=255)                 # tip lobe
    for sgn in (-1, 1):
        d.ellipse([cx + sgn * S * 0.27 - S * 0.17, cy - S * 0.30 - S * 0.09, cx + sgn * S * 0.27 + S * 0.17, cy - S * 0.30 + S * 0.09], fill=255)
        d.ellipse([cx + sgn * S * 0.20 - S * 0.17, cy - S * 0.07 - S * 0.10, cx + sgn * S * 0.20 + S * 0.17, cy - S * 0.07 + S * 0.10], fill=255)
    d.polygon([(cx - S * 0.34, cy - S * 0.05), (cx + S * 0.34, cy - S * 0.05), (cx, cy + S * 0.40)], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(S * 0.008))
    r = np.random.default_rng(hue_seed)
    g = fbm(S, S, 5, 5, 4, hue_seed)
    base = np.array([r.uniform(20, 30), r.uniform(34, 50), r.uniform(18, 26)])
    col = base[None, None, :] * (0.65 + 0.7 * g[..., None])
    # lighter towards the tip, darker at the edges
    yy = np.linspace(0, 1, S)[:, None]
    col *= (0.75 + 0.5 * (1 - yy))[..., None]
    arr = np.dstack([col, np.array(m)]).astype(np.uint8)
    im = Image.fromarray(arr, "RGBA")
    dd = ImageDraw.Draw(im)
    # veins
    vc = (150, 175, 110, 110)
    dd.line([(cx, cy + S * 0.36), (cx, cy - S * 0.48)], fill=vc, width=max(2, S // 60))
    for sgn in (-1, 1):
        for t, ln in ((0.02, 0.32), (0.16, 0.30)):
            dd.line([(cx, cy - S * t + S * 0.02), (cx + sgn * S * ln, cy - S * (t + 0.24))], fill=vc, width=max(1, S // 90))
    # edge darkening
    edge = Image.fromarray(np.array(m)).filter(ImageFilter.GaussianBlur(S * 0.03))
    ea = np.array(edge).astype(float) / 255
    arr2 = np.array(im).astype(float)
    arr2[..., :3] *= (0.55 + 0.45 * ea)[..., None]
    im = Image.fromarray(arr2.astype(np.uint8), "RGBA")
    return im.resize((size, size), Image.LANCZOS)


def bezier(p0, p1, p2, p3, n=60):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def make_vines(W, H, stems, seed):
    SS = 2
    im = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(seed)
    leaves = []
    leaf_cache = [ivy_leaf(96, seed + i) for i in range(6)]

    def draw_stem(pts, w0, depth):
        n = len(pts)
        for i in range(n - 1):
            t = i / n
            w = max(1.2, w0 * (1 - 0.7 * t)) * SS
            a, b = pts[i] * SS, pts[i + 1] * SS
            d.line([tuple(a + 1.5 * SS), tuple(b + 1.5 * SS)], fill=(4, 6, 4, 150), width=int(w) + 1)      # shadow
            d.line([tuple(a), tuple(b)], fill=(28, 24, 16, 255), width=int(w))
            d.line([tuple(a - 0.5 * SS), tuple(b - 0.5 * SS)], fill=(66, 58, 38, 200), width=max(1, int(w * 0.35)))   # highlight
            if i % 3 == 0 and r.random() < 0.55:
                ang = math.atan2(*(b - a)[::-1]) + r.choice([-1, 1]) * r.uniform(0.7, 1.3)
                sz = r.uniform(0.7, 1.25) * (46 + 32 * (1 - t)) * (0.7 if depth else 1)
                leaves.append((pts[i], ang, sz))
            if depth == 0 and i % 9 == 4 and r.random() < 0.6 and i > 5:
                # side branch
                dirv = (pts[i + 1] - pts[i]); dirv /= (np.linalg.norm(dirv) + 1e-9)
                side = r.choice([-1, 1]); perp = np.array([-dirv[1], dirv[0]]) * side
                L = r.uniform(60, 150)
                p0 = pts[i]; p3 = p0 + perp * L + dirv * r.uniform(20, 70)
                br = bezier(p0, p0 + perp * L * 0.4, p3 - dirv * 30 + perp * 10, p3, 24)
                draw_stem(br, w0 * 0.45, 1)

    for (p0, p1, p2, p3, w0) in stems:
        pts = bezier(np.array(p0, float), np.array(p1, float), np.array(p2, float), np.array(p3, float), 90)
        pts += np.stack([np.sin(np.linspace(0, 14, len(pts))) * 3, np.cos(np.linspace(0, 11, len(pts))) * 3], 1)
        draw_stem(pts, w0, 0)
        # curly tendril at the end
        end = pts[-1]
        cur = [end + np.array([math.cos(a) * a * 3, math.sin(a) * a * 3]) for a in np.linspace(0, 9, 30)]
        d.line([tuple(p * SS) for p in cur], fill=(30, 30, 18, 255), width=SS)
    # leaves are pasted after the stems so they overlap the vine
    for (pos, ang, sz) in leaves:
        lf = leaf_cache[r.integers(len(leaf_cache))].resize((int(sz * SS), int(sz * SS)), Image.LANCZOS)
        lf = lf.rotate(-math.degrees(ang) - 90 + 90, resample=Image.BICUBIC, expand=True)
        # soft shadow
        sh = Image.new("RGBA", lf.size, (0, 0, 0, 0))
        sh.putalpha(lf.getchannel("A").point(lambda v: int(v * 0.5)))
        px, py = int(pos[0] * SS - lf.width / 2), int(pos[1] * SS - lf.height / 2)
        im.alpha_composite(sh, (max(px + 3, 0), max(py + 4, 0))) if px >= 0 and py >= 0 else None
        # clip when it leaves the canvas
        tmp = Image.new("RGBA", im.size, (0, 0, 0, 0))
        tmp.paste(lf, (px, py))
        im = Image.alpha_composite(im, tmp)
    im = im.resize((W, H), Image.LANCZOS)
    return im


def make_title(text="HORROR", w=1024, h=300, seed=11):
    r = np.random.default_rng(seed)
    S = 2
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf", 196 * S)
    m = Image.new("L", (w * S, h * S), 0)
    d = ImageDraw.Draw(m)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # widen letters by drawing each one, with tight uneven spacing (hand-cut lettering)
    x = (w * S - tw) / 2 - bbox[0]
    y = (h * S - th) / 2 - bbox[1] - 10
    for i, ch in enumerate(text):
        jy = r.integers(-8, 9) * S
        d.text((x, y + jy), ch, font=font, fill=255)
        x += d.textlength(ch, font=font) - 6 * S
    a = np.array(m).astype(float) / 255
    # rough edges: displace with noise, then threshold
    dx = (fbm(h * S, w * S, 30, 40, 3, seed) - 0.5) * 10 * S
    dy = (fbm(h * S, w * S, 30, 40, 3, seed + 1) - 0.5) * 10 * S
    yy, xx = np.mgrid[0:h * S, 0:w * S]
    from scipy.ndimage import map_coordinates
    a = map_coordinates(a, [np.clip(yy + dy, 0, h * S - 1), np.clip(xx + dx, 0, w * S - 1)], order=1)
    a = gaussian_filter(a, 1.4 * S)
    a = smoothstep(0.42, 0.58, a)
    # scratches / worn holes
    wear = smoothstep(0.66, 0.78, fbm(h * S, w * S, 20, 50, 5, seed + 2))
    a *= 1 - wear * 0.9
    for _ in range(26):
        x0, y0 = r.uniform(0, w * S), r.uniform(0, h * S)
        ang = r.normal(-0.5, 0.25)
        ln = r.uniform(60, 240) * S
        sc = Image.new("L", (w * S, h * S), 0)
        ImageDraw.Draw(sc).line([(x0, y0), (x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln)], fill=255, width=S)
        a *= 1 - np.array(sc).astype(float) / 255 * 0.85
    # colour: bone paint, worn & stained
    tex = fbm(h * S, w * S, 8, 20, 5, seed + 3)
    bone = np.array([214, 204, 184])
    col = bone[None, None, :] * (0.55 + 0.6 * tex[..., None])
    stain = smoothstep(0.55, 0.85, fbm(h * S, w * S, 5, 12, 4, seed + 4))[..., None]
    col = col * (1 - stain * 0.5) + np.array([120, 20, 18]) * stain * 0.5
    ink = (a * 255)
    rgb = np.dstack([col, ink]).astype(np.uint8)
    face = Image.fromarray(rgb, "RGBA")
    # blood drips under the letters
    drips = Image.new("RGBA", face.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(drips)
    edge = (np.array(m) > 128)
    ys = np.where(edge.any(0), edge.shape[0] - 1 - np.argmax(edge[::-1], 0), -1)
    for cx in r.choice(np.where(ys > 0)[0], 9, replace=False):
        ln = r.uniform(30, 120) * S
        wd = r.uniform(3, 7) * S
        top = ys[cx] - 10 * S
        dd.rounded_rectangle([cx - wd / 2, top, cx + wd / 2, top + ln], radius=wd / 2, fill=(120, 14, 14, 235))
        dd.ellipse([cx - wd * 0.8, top + ln - wd, cx + wd * 0.8, top + ln + wd], fill=(140, 18, 16, 240))
    drips = drips.filter(ImageFilter.GaussianBlur(0.8 * S))
    # dark shadow + red ghost offset
    sha = Image.new("RGBA", face.size, (0, 0, 0, 0))
    sha.putalpha(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6 * S)))
    ghost = Image.new("RGBA", face.size, (150, 22, 22, 0))
    ghost.putalpha(Image.fromarray((a * 150).astype(np.uint8)))
    out = Image.new("RGBA", face.size, (0, 0, 0, 0))
    out.alpha_composite(sha, (4 * S, 6 * S))
    out.alpha_composite(ghost, (5 * S, 5 * S))
    out.alpha_composite(drips)
    out.alpha_composite(face)
    return out.resize((w, h), Image.LANCZOS)


if __name__ == "__main__":
    save(make_ink(), "ink_fade.png")
    for i, sd in enumerate((21, 34, 47), 1):
        save(make_plank(sd), f"plank_{i}.png")
    # left edge vine climbing the whole height + a second one over it
    save(make_vines(512, 1024, [
        ((60, 1040), (10, 800), (120, 520), (40, -20), 12),
        ((150, 1040), (60, 900), (210, 700), (120, 430), 8),
        ((30, 700), (140, 560), (60, 380), (170, 220), 6),
    ], 3), "vines_left.png")
    # hanging from the top edge
    save(make_vines(1024, 512, [
        ((-20, 20), (200, 120), (380, 20), (560, 200), 9),
        ((330, -20), (360, 140), (300, 240), (380, 400), 7),
        ((80, -20), (60, 150), (150, 250), (100, 380), 6),
    ], 9), "vines_top.png")
    save(make_title(), "title_horror.png")
