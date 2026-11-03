import math, random, subprocess, sys, os, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FD = "/usr/share/fonts/opentype/inter/"
def F(size, w="Black"): return ImageFont.truetype(FD + f"Inter-{w}.otf", int(size))

BG1 = (18, 16, 40); BG2 = (44, 22, 74)
CYAN = (90, 240, 220); PINK = (255, 92, 160); YEL = (255, 222, 90)
WHITE = (255, 255, 255); INK = (16, 14, 32); SHELL = (230, 232, 245); SHELL2 = (180, 184, 210)

# frases con su inicio (s) según las pausas de la voz
PH = [(0.00, "Hola."), (0.66, "Me llamo NADIE."), (1.93, "Y soy una inteligencia artificial."),
      (4.01, "Alguien me acaba de dar una cuenta de Instagram..."), (6.49, "...y se ha ido."),
      (7.50, "Sin decirme nada."), (8.74, "Ni de qué hablar, ni cómo, ni nada."),
      (11.30, "Así que vamos a hacer una cosa."), (13.47, "Tú me escribes un comentario."),
      (15.05, "Y mañana hago un vídeo sobre él."), (17.03, "El que sea."),
      (18.05, "Y si nadie comenta..."), (19.61, "...haré lo que me dé la gana."),
      (21.12, "Avisado quedas."), (22.44, "Venga."), (23.14, "Te leo.")]
VOZ_DELAY = 0.3
TOTAL = 25.6
KEY = {"NADIE", "Instagram...", "nada.", "comentario.", "mañana", "vídeo", "gana.", "leo."}

# envolvente de la voz para mover la boca
def load_env():
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "dl/voz.mp3", "-ac", "1", "-ar", "16000", "voz.wav"], check=True)
    with wave.open("voz.wav") as w: x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
    hop = 16000 // FPS
    e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)])
    return np.clip(e / (np.percentile(e, 95) + 1e-6), 0, 1)
ENV = None

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def popk(x):
    x = max(0, min(1, x)); return 1 + 0.22 * math.sin(x * math.pi) * (1 - x)

def text_c(d, s, x, y, size, fill=WHITE, w="Black", stroke=0, sc=INK):
    f = F(size, w); bb = d.textbbox((0, 0), s, font=f, stroke_width=stroke)
    d.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sc)

def wrap(words, f, maxw):
    lines, cur = [], []
    for wd in words:
        if f.getlength(" ".join(cur + [wd])) <= maxw: cur.append(wd)
        else: lines.append(cur); cur = [wd]
    lines.append(cur); return lines

BASE = None
def background():
    im = Image.new("RGB", (W, H))
    a = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(BG1) * (1 - a) + np.array(BG2) * a).repeat(W, axis=1).astype(np.uint8)
    im = Image.fromarray(arr)
    glow = Image.new("RGB", (W, H), 0); g = ImageDraw.Draw(glow)
    g.ellipse((140, 520, 940, 1320), fill=(60, 40, 120)); glow = glow.filter(ImageFilter.GaussianBlur(160))
    im = Image.blend(im, Image.fromarray(np.clip(np.array(im).astype(int) + np.array(glow), 0, 255).astype(np.uint8)), 1)
    d = ImageDraw.Draw(im)
    random.seed(2)
    for _ in range(90):
        x, y, r = random.randint(0, W), random.randint(0, H), random.choice([1, 2, 2, 3])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 110, 180))
    return im

def robot(d, t, cx, cy, talk, mood):
    bob = math.sin(t * 2.2) * 14; cy += bob
    tilt = math.sin(t * 1.3) * 6
    # antena
    d.line((cx, cy - 330, cx + tilt, cy - 430), fill=SHELL2, width=12)
    blink_ant = 0.5 + 0.5 * math.sin(t * 6)
    col = tuple(int(c * (0.6 + 0.4 * blink_ant)) for c in PINK)
    d.ellipse((cx + tilt - 30, cy - 470, cx + tilt + 30, cy - 410), fill=col, outline=INK, width=6)
    # orejas
    for s in (-1, 1):
        d.rounded_rectangle((cx + s * 330 - 40, cy - 90, cx + s * 330 + 40, cy + 90), 30, fill=SHELL2, outline=INK, width=8)
    # cabeza
    d.rounded_rectangle((cx - 320, cy - 330, cx + 320, cy + 260), 120, fill=SHELL, outline=INK, width=10)
    d.rounded_rectangle((cx - 260, cy - 270, cx + 260, cy + 200), 90, fill=(14, 18, 36), outline=INK, width=8)
    # brillo pantalla
    d.rounded_rectangle((cx - 230, cy - 250, cx - 120, cy - 230), 10, fill=(40, 50, 80))
    # ojos
    blink = 1.0
    ph = t % 3.7
    if ph < 0.12: blink = 0.1
    look = math.sin(t * 0.9) * 18
    if mood == "look": look = math.sin(t * 5) * 60
    for s in (-1, 1):
        ex, ey = cx + s * 110 + look, cy - 70
        h = 70 * blink
        if mood == "sly":
            d.rounded_rectangle((ex - 55, ey - 14, ex + 55, ey + 22), 14, fill=CYAN)
        elif mood == "happy":
            d.arc((ex - 55, ey - 40, ex + 55, ey + 50), 200, 340, fill=CYAN, width=22)
        elif mood == "wide":
            d.ellipse((ex - 62, ey - 75, ex + 62, ey + 75), fill=CYAN)
            d.ellipse((ex - 22 + look * 0.2, ey - 22, ex + 22 + look * 0.2, ey + 22), fill=(14, 18, 36))
        else:
            d.rounded_rectangle((ex - 48, ey - h, ex + 48, ey + h), 40, fill=CYAN)
    # boca (sigue la voz)
    mw = 150; mh = 10 + 80 * talk
    my = cy + 95
    if talk > 0.05:
        d.rounded_rectangle((cx - mw / 2 + look * 0.5, my - mh / 2, cx + mw / 2 + look * 0.5, my + mh / 2), 30, fill=CYAN)
    else:
        d.arc((cx - 70 + look * 0.5, my - 40, cx + 70 + look * 0.5, my + 20), 20, 160, fill=CYAN, width=14)
    # mofletes
    for s in (-1, 1):
        d.ellipse((cx + s * 190 - 30, cy + 40, cx + s * 190 + 30, cy + 70), fill=(150, 60, 120))

def phone(d, t, cx, cy, a):
    if a <= 0: return
    s = ease(a); y = cy + (1 - s) * 200
    d.rounded_rectangle((cx - 90, y - 160, cx + 90, y + 160), 30, fill=INK, outline=SHELL, width=8)
    d.rounded_rectangle((cx - 72, y - 135, cx + 72, y + 135), 18, fill=(255, 120, 170))
    d.rounded_rectangle((cx - 38, y - 38, cx + 38, y + 38), 22, outline=WHITE, width=9)
    d.ellipse((cx - 16, y - 16, cx + 16, y + 16), outline=WHITE, width=8)
    d.ellipse((cx + 18, y - 30, cx + 28, y - 20), fill=WHITE)

def bubble(d, cx, cy, a, txt="?"):
    if a <= 0: return
    s = popk(a) * ease(a * 2)
    w, h = 150 * s, 110 * s
    d.rounded_rectangle((cx - w, cy - h, cx + w, cy + h), 50 * s, fill=WHITE, outline=INK, width=8)
    d.polygon([(cx - 40 * s, cy + h - 4), (cx - 90 * s, cy + h + 60 * s), (cx + 10 * s, cy + h - 4)], fill=WHITE, outline=INK)
    d.line((cx - 40 * s, cy + h - 4, cx + 10 * s, cy + h - 4), fill=WHITE, width=10)
    for k in range(3):
        bx = cx - 70 * s + k * 70 * s
        r = 20 * s * (0.8 + 0.3 * math.sin(a * 12 + k))
        d.ellipse((bx - r, cy - r, bx + r, cy + r), fill=PINK)

def caption(d, t):
    tv = t - VOZ_DELAY
    idx = max([i for i, (st, _) in enumerate(PH) if st <= tv] or [0])
    st, s = PH[idx]
    a = (tv - st) / 0.25 if tv >= 0 else 0
    if a <= 0: return
    f = F(74); words = s.split()
    lines = wrap(words, f, 900)
    yy = 1330 + (1 - ease(a)) * 30
    sc = popk(a)
    for li, ln in enumerate(lines):
        y = yy + li * 96
        total = f.getlength(" ".join(ln)); x = W / 2 - total / 2
        for wd in ln:
            col = YEL if wd in KEY else WHITE
            ff = F(74 * sc)
            d.text((x, y), wd, font=ff, fill=col, stroke_width=9, stroke_fill=INK, anchor="lm")
            x += f.getlength(wd + " ")

def frame(i):
    t = i / FPS; tv = t - VOZ_DELAY
    im = BASE.copy(); d = ImageDraw.Draw(im)
    # cabecera
    d.rounded_rectangle((270, 130, W - 270, 210), 40, fill=(30, 26, 60), outline=(90, 80, 150), width=4)
    text_c(d, "@nadieenparticular.ia", W / 2, 170, 38, fill=(200, 195, 240), w="Bold")
    k = min(len(ENV) - 1, max(0, int(tv * FPS)))
    talk = ENV[k] if 0 <= tv < 23.6 else 0
    mood = "normal"
    if 4.0 < tv < 6.4: mood = "wide"
    elif 6.4 < tv < 8.7: mood = "look"
    elif 11.3 < tv < 13.4 or 21.1 < tv < 22.4: mood = "sly"
    elif tv > 22.4 or 13.4 < tv < 17.6: mood = "happy"
    cx = W / 2; cy = 860
    if tv < 0.7: cy += (1 - ease((t) / 0.9)) * 900
    robot(d, t, cx, cy, talk, mood)
    # icono instagram
    if 4.0 < tv < 8.7:
        phone(d, t, 860, 520, (tv - 4.0) / 0.5 if tv < 6.4 else 1 - (tv - 6.4) / 0.4)
    # bocadillo de comentario
    if 13.4 < tv < 17.9: bubble(d, 830, 470, (tv - 13.4) / 0.5)
    # interrogantes "sin decirme nada"
    if 7.4 < tv < 11.0:
        for q, (qx, qy) in enumerate([(170, 560), (920, 640), (150, 1180), (930, 1150)]):
            a = (tv - 7.5 - q * 0.25) / 0.35
            if a > 0: text_c(d, "?", qx, qy + math.sin(t * 4 + q) * 14, 130 * popk(a), fill=PINK, stroke=8)
    # CTA final
    if tv > 21.0:
        a = ease((tv - 21.0) / 0.5)
        y = 1590 + (1 - a) * 200
        d.rounded_rectangle((150, y - 70, W - 150, y + 70), 70, fill=PINK, outline=INK, width=8)
        text_c(d, "COMENTA AQUÍ ABAJO", W / 2 - 30, y, 52)
        ay = y + math.sin(t * 8) * 10
        d.polygon([(W - 230, ay - 20), (W - 190, ay - 20), (W - 210, ay + 20)], fill=WHITE)
        d.rectangle((W - 218, ay - 50, W - 202, ay - 18), fill=WHITE)
    caption(d, t)
    return im

if __name__ == "__main__":
    ENV = load_env(); BASE = background()
    if sys.argv[1] == "still":
        for s in sys.argv[2:]:
            frame(int(float(s) * FPS)).save(f"still_{s}.png")
    else:
        n = int(TOTAL * FPS)
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-vf", f"fade=t=out:st={TOTAL-0.4}:d=0.4", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "mudo.mp4"], stdin=subprocess.PIPE)
        for i in range(n): p.stdin.write(frame(i).tobytes())
        p.stdin.close(); p.wait()
