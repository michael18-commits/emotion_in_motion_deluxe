# art_engine.py (rich patterns & color system)
import numpy as np
import matplotlib.pyplot as plt
from noise import pnoise2
import io, random, colorsys

# ---------- Color Utilities ----------
def hex_to_rgb01(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16)/255.0 for i in (0,2,4))

def clamp01(x): return max(0.0, min(1.0, float(x)))

def tweak_hsv(rgb, s_mul=1.0, v_mul=1.0):
    r,g,b = rgb
    h,s,v = colorsys.rgb_to_hsv(r,g,b)
    s = clamp01(s * s_mul)
    v = clamp01(v * v_mul)
    return colorsys.hsv_to_rgb(h,s,v)

def rotate_hue(rgb, delta):  # delta in [0..1]
    r,g,b = rgb
    h,s,v = colorsys.rgb_to_hsv(r,g,b)
    h = (h + delta) % 1.0
    return colorsys.hsv_to_rgb(h,s,v)

# ---------- Palette Builder ----------
BASE_PALETTES = {
    "calm":      ["#A7C7E7", "#6B9AC4", "#294C60"],
    "joyful":    ["#F6AD55", "#ED8936", "#DD6B20"],
    "anxious":   ["#2D3748", "#805AD5", "#4C51BF"],
    "tired":     ["#718096", "#A0AEC0", "#CBD5E0"],
    "focused":   ["#22543D", "#38A169", "#9AE6B4"],
    "blue":      ["#1A365D", "#2C5282", "#4299E1"]
}

def build_palette(mood, color_mode, colorfulness, saturation, brightness, custom_hex=None, rng=None):
    rng = rng or random.Random()
    base = [hex_to_rgb01(c) for c in BASE_PALETTES.get(mood, BASE_PALETTES["calm"])]
    if custom_hex:
        base = [hex_to_rgb01(custom_hex)]

    palette = []
    if color_mode == "Mood":
        palette = base[:]
    elif color_mode == "Mood + Complement":
        palette = base[:] + [rotate_hue(c, 0.5) for c in base]
    elif color_mode == "Triadic":
        palette = base[:] + [rotate_hue(base[0], 1/3), rotate_hue(base[0], 2/3)]
    elif color_mode == "Analogous":
        palette = [rotate_hue(base[0], d) for d in (-0.06, -0.03, 0, 0.03, 0.06)]
    elif color_mode == "Custom":
        palette = base[:] + [rotate_hue(base[0], d) for d in (0.12, 0.24)]

    # inflate palette for more variety
    out = []
    for c in palette:
        for _ in range(max(2, int(3 + colorfulness*5))):
            out.append(tweak_hsv(c, s_mul=(0.7 + saturation*0.8),
                                 v_mul=(0.7 + brightness*0.8)))
    return out

# ---------- Background helpers ----------
def draw_gradient(ax, top_rgb, bottom_rgb, steps=180, alpha=0.6):
    for i in range(steps):
        t = i / (steps-1)
        r = top_rgb[0]*(1-t) + bottom_rgb[0]*t
        g = top_rgb[1]*(1-t) + bottom_rgb[1]*t
        b = top_rgb[2]*(1-t) + bottom_rgb[2]*t
        ax.add_patch(plt.Rectangle((0, t-0.01), 1, 0.02, color=(r,g,b), alpha=alpha, linewidth=0))

def add_vignette(ax, strength=0.25, res=800):
    y,x = np.ogrid[-1:1:complex(0,res), -1:1:complex(0,res)]
    d = np.sqrt(x*x + y*y)
    mask = np.clip((d-0.6)*2.2, 0, 1)**2 * strength
    ax.imshow(np.dstack([np.zeros_like(mask)]*3 + [mask]), extent=[0,1,0,1])

def add_grain(ax, amount=0.15, res=600):
    noise = (np.random.rand(res, res)-0.5) * amount
    tex = np.dstack([noise+0.5]*3)
    ax.imshow(tex, extent=[0,1,0,1], alpha=amount*0.6, interpolation="bilinear")

# ---------- Pattern generators ----------
def flow_field(ax, rng, palette, density, path_len, stroke_min, stroke_max, scale, octaves, flow_strength):
    for _ in range(density):
        x, y = rng.random(), rng.random()
        xs, ys = [x], [y]
        for _ in range(path_len):
            dx = pnoise2(x*flow_strength, y*flow_strength, octaves=octaves)
            dy = pnoise2(y*flow_strength, x*flow_strength, octaves=octaves)
            x += dx * scale
            y += dy * scale
            if not (0 <= x <= 1 and 0 <= y <= 1): break
            xs.append(x); ys.append(y)
        c = rng.choice(palette)
        lw = rng.uniform(stroke_min, stroke_max)
        ax.plot(xs, ys, color=c, alpha=0.7, linewidth=lw, solid_capstyle="round")

def ribbons(ax, rng, palette, count, length, stroke_min, stroke_max, flow_strength):
    for _ in range(count):
        x, y = rng.random(), rng.random()
        vx, vy = 0.0, 0.0
        xs, ys = [x], [y]
        for _ in range(length):
            angle = pnoise2(x*flow_strength*0.6, y*flow_strength*0.6, octaves=2) * np.pi*2
            vx = 0.92*vx + 0.08*np.cos(angle)
            vy = 0.92*vy + 0.08*np.sin(angle)
            x += vx*0.9; y += vy*0.9
            if not (0 <= x <= 1 and 0 <= y <= 1): break
            xs.append(x); ys.append(y)
        c = rng.choice(palette)
        lw = rng.uniform(stroke_min*0.8, stroke_max*1.2)
        ax.plot(xs, ys, color=c, alpha=0.5, linewidth=lw, solid_capstyle="round")

def bubbles(ax, rng, palette, count):
    for _ in range(count):
        cx, cy = rng.random(), rng.random()
        r = rng.uniform(0.01, 0.12)
        c = rng.choice(palette)
        ax.add_patch(plt.Circle((cx, cy), r, color=c, alpha=0.22, linewidth=0))

# ---------- Public API ----------
def generate_art(
    seed: int,
    steps: int,
    heart_rate: float,
    sleep: float,
    fatigue: float,
    mood: str,
    pattern: str = "Flow Field",
    bg_gradient: bool = True,
    vignette: float = 0.25,
    grain: float = 0.15,
    color_mode: str = "Mood",
    colorfulness: float = 0.7,
    saturation: float = 0.85,
    brightness: float = 0.9,
    custom_hex: str | None = None,
    density: int = 400,
    path_length: int = 400,
    stroke_min: float = 0.6,
    stroke_max: float = 1.6,
    noise_octaves: int = 3,
    flow_strength: float = 1.2,
    size=(1200, 800),
):
    rng = random.Random(seed)
    np.random.seed(seed)

    # data → dynamics
    scale = 0.008 + heart_rate/2200.0
    density = int(density * (0.7 + steps/30000.0))
    path_length = int(path_length * (0.7 + sleep/12.0))
    stroke_max = max(stroke_min+0.1, stroke_max) * (1.0 - 0.4*fatigue)

    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")

    # palette
    palette = build_palette(mood, color_mode, colorfulness, saturation, brightness, custom_hex, rng)

    # background
    if bg_gradient:
        top = palette[0]
        bot = palette[min(4, len(palette)-1)]
        draw_gradient(ax, top, bot, steps=200, alpha=0.55)

    # patterns
    if pattern == "Flow Field":
        flow_field(ax, rng, palette, density, path_length, stroke_min, stroke_max, scale, noise_octaves, flow_strength)
    elif pattern == "Ribbon Trails":
        ribbons(ax, rng, palette, int(density*0.6), int(path_length*0.9), stroke_min, stroke_max, flow_strength)
    elif pattern == "Bubble Bloom":
        bubbles(ax, rng, palette, int(density*0.7))
        flow_field(ax, rng, palette, int(density*0.4), int(path_length*0.7), stroke_min*0.8, stroke_max, scale*0.9, noise_octaves, flow_strength*0.8)
    else:  # Hybrid
        flow_field(ax, rng, palette, int(density*0.7), int(path_length*0.9), stroke_min, stroke_max, scale, noise_octaves, flow_strength)
        ribbons(ax, rng, palette, int(density*0.35), int(path_length*0.7), stroke_min, stroke_max, flow_strength*0.9)
        bubbles(ax, rng, palette, int(density*0.35))

    # overlays
    if vignette > 0: add_vignette(ax, strength=vignette)
    if grain > 0: add_grain(ax, amount=grain)

    fig.tight_layout(pad=0)
    return fig

def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=220, bbox_inches="tight", pad_inches=0.0)
    buf.seek(0)
    return buf.getvalue()
