import numpy as np
import matplotlib.pyplot as plt
from noise import pnoise2
import io, random

def generate_fluid_art(seed, steps, heart_rate, sleep, fatigue, mood, size=(1000,700)):
    random.seed(seed)
    np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.axis("off")

    palettes = {
        "calm": ["#A7C7E7", "#6B9AC4", "#294C60"],
        "joyful": ["#F6AD55", "#ED8936", "#DD6B20"],
        "anxious": ["#2D3748", "#805AD5", "#4C51BF"],
        "tired": ["#718096", "#A0AEC0", "#CBD5E0"],
        "focused": ["#22543D", "#38A169", "#9AE6B4"]
    }
    colors = palettes.get(mood, ["#90CDF4", "#2B6CB0", "#1A365D"])

    scale = 0.01 + (heart_rate / 2000)
    density = int(100 + steps / 300)
    alpha = np.clip(1 - fatigue, 0.2, 0.9)
    flow_strength = np.clip(sleep / 8, 0.5, 1.5)

    for _ in range(density):
        x, y = np.random.rand(2)
        path_x, path_y = [x], [y]
        for _ in range(300):
            dx = pnoise2(x*flow_strength, y*flow_strength, octaves=2)
            dy = pnoise2(y*flow_strength, x*flow_strength, octaves=2)
            x += dx * scale
            y += dy * scale
            if not (0 <= x <= 1 and 0 <= y <= 1):
                break
            path_x.append(x)
            path_y.append(y)
        c = random.choice(colors)
        ax.plot(path_x, path_y, color=c, alpha=alpha, linewidth=0.8)

    fig.tight_layout(pad=0)
    return fig

def fig_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight", pad_inches=0.0)
    buf.seek(0)
    return buf.getvalue()
