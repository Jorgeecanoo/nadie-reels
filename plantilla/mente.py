import math, subprocess, wave, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FD = "/usr/share/fonts/opentype/inter/"
def F(s, w="Black"): return ImageFont.truetype(FD + f"Inter-{w}.otf", int(s))
WHITE = (245, 245, 245); GREY = (120, 120, 130); RED = (255, 70, 90); BLACK = (8, 8, 10)

# (inicio, duración, línea grande, línea pequeña)
STEPS = [
    (0.0, 2.6, "Voy a leerte", "la mente."),
    (2.6, 2.2, "Piensa un número", "del 1 al 10."),
    (4.8, 1.9, "Multiplícalo", "por 2."),
    (6.7, 1.8, "Súmale", "10."),
    (8.5, 1.8, "Divídelo", "entre 2."),
    (10.3, 2.2, "Réstale el número", "que pensaste."),
]
REVEAL = 13.4; CTA = 16.6; TOTAL = 20.0

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def text_c(d, s, y, size, fill=WHITE, w="Black", scale=1.0):
    f = F(size * scale, w); bb = d.textbbox((0, 0), s, font=f)
    d.text((W / 2 - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=fill)

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
    # contador de pasos
    for k, (st, du, a, b) in enumerate(STEPS):
        if st <= t < st + du:
            p = t - st
            sc = 1 + 0.35 * max(0, 1 - p / 0.18)
            if k == 0:
                text_c(d, a, 860, 100, scale=sc); text_c(d, b, 990, 100, fill=RED, scale=sc)
                text_c(d, "en 15 segundos", 1110, 52, fill=GREY, w="Bold")
            else:
                text_c(d, f"PASO {k}", 640, 44, fill=GREY, w="Bold")
                text_c(d, a, 880, 96, scale=sc); text_c(d, b, 1010, 118, fill=RED, scale=sc)
                # barra de paso
                x0, x1 = 240, W - 240; fr = min(1, p / du)
                d.rounded_rectangle((x0, 1200, x1, 1214), 7, fill=(40, 40, 46))
                d.rounded_rectangle((x0, 1200, x0 + (x1 - x0) * fr, 1214), 7, fill=WHITE)
    if STEPS[-1][0] + STEPS[-1][1] <= t < REVEAL:
        p = t - 12.5
        n = int(p * 4) % 4
        text_c(d, "." * (n % 4) if n else "", 960, 160, fill=GREY)
    if REVEAL <= t < CTA:
        p = t - REVEAL
        text_c(d, "Te ha salido", 700, 80, fill=GREY, w="Bold", scale=1 + 0.2 * max(0, 1 - p / 0.2))
        if p > 0.6:
            q = p - 0.6
            sc = 1 + 0.6 * max(0, 1 - q / 0.25)
            shake = random.uniform(-8, 8) if q < 0.3 else 0
            f = F(520 * sc); bb = d.textbbox((0, 0), "5", font=f)
            d.text((W / 2 - (bb[2] - bb[0]) / 2 - bb[0] + shake, 1050 - (bb[3] - bb[1]) / 2 - bb[1]), "5", font=f, fill=RED)
    if t >= CTA:
        p = t - CTA; a = ease(p / 0.4)
        f = F(380); bb = d.textbbox((0, 0), "5", font=f)
        d.text((W / 2 - (bb[2] - bb[0]) / 2 - bb[0], 700 - (bb[3] - bb[1]) / 2 - bb[1]), "5", font=f, fill=RED)
        text_c(d, "¿Lo he adivinado?", 1060 + (1 - a) * 40, 78)
        y = 1250 + (1 - a) * 80
        d.rounded_rectangle((170, y - 75, W - 170, y + 75), 75, outline=WHITE, width=6)
        text_c(d, "Comenta SÍ o NO", y, 62)
        text_c(d, "@nadieenparticular.ia", 1460, 36, fill=GREY, w="Bold")
    return im

# sonido: tic-tac que acelera, golpe en la revelación
SR = 44100
def click(f, d=0.03, g=0.5):
    n = int(SR * d); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.006) * g
def boom():
    n = int(SR * 1.2); tt = np.arange(n) / SR
    f = 90 * np.exp(-tt * 3) + 40
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.5) + 0.3 * np.random.default_rng(0).standard_normal(n) * np.exp(-tt * 12)) * 0.9
def riser(d=0.9):
    n = int(SR * d); tt = np.arange(n) / SR
    return np.random.default_rng(1).standard_normal(n) * (tt / d) ** 2 * 0.25
def chime(f):
    n = int(SR * 1.5); tt = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * k * tt) for k, a in ((1, 1), (2, .4), (3, .15))) * np.exp(-tt * 2) * 0.25

tr = np.zeros(int(SR * (TOTAL + 1)))
def add(t, s):
    i = int(SR * t); j = min(len(tr), i + len(s)); tr[i:j] += s[:j - i]
t, k = 0.3, 0
while t < 12.4:
    add(t, click(1400 if k % 2 == 0 else 1000)); k += 1
    t += max(0.18, 0.55 - t * 0.03)
for st, *_ in STEPS[1:]: add(st, click(600, 0.08, 0.6))
add(REVEAL - 0.9, riser()); add(REVEAL + 0.6, boom()); add(CTA, chime(660)); add(CTA + 0.12, chime(880))
tr = np.tanh(tr * 1.3) * 0.85
with wave.open("mente_sfx.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((tr * 32767).astype(np.int16).tobytes())

import sys
if len(sys.argv) > 1 and sys.argv[1] == "still":
    ims = [frame(int(float(s) * FPS)).resize((270, 480)) for s in sys.argv[2:]]
    c = Image.new("RGB", (270 * len(ims), 480)); [c.paste(m, (i * 270, 0)) for i, m in enumerate(ims)]; c.save("mente_contact.png")
else:
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "mente_sfx.wav", "-vf", f"fade=t=out:st={TOTAL-0.4}:d=0.4", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-shortest", "-movflags", "+faststart", "Nadie_mentalismo.mp4"], stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
