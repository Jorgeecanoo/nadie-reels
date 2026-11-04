# Reto de atención estilo arcade pixel art, sin voz. Uso: python3 reto_pixel.py still T | render
import sys, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

LW, LH, S, FPS = 270, 480, 4, 30          # se dibuja a 270x480 y se escala x4 sin suavizado
FD = "/usr/share/fonts/opentype/inter/"
def F(s, w="Black"): return ImageFont.truetype(FD + f"Inter-{w}.otf", int(s))
BG = (22, 12, 44); INK = (240, 236, 255); CY = (60, 230, 255); YE = (255, 214, 60); PK = (255, 70, 150); DIM = (120, 100, 170)

# (nivel, inicio, fin del reto, letra normal, letra intrusa, fila, columna)
LEVELS = [(1, 1.6, 6.6, "O", "Q", 6, 2), (2, 9.0, 14.0, "8", "B", 3, 5)]
REVEAL = 1.2; CTA = 15.4; TOTAL = 19.5
COLS, ROWS, X0, Y0, CELL = 8, 10, 23, 104, 28

def tc(d, s, y, size, fill=INK, w="Black"):
    f = F(size, w); bb = d.textbbox((0, 0), s, font=f)
    d.text((LW / 2 - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=fill)

def grid(d, a, b, r, c, t):
    f = F(19)
    for i in range(ROWS):
        for j in range(COLS):
            ch = b if (i, j) == (r, c) else a
            bb = d.textbbox((0, 0), ch, font=f)
            x = X0 + j * CELL + CELL / 2 - (bb[2] - bb[0]) / 2 - bb[0]
            y = Y0 + i * CELL + CELL / 2 - (bb[3] - bb[1]) / 2 - bb[1]
            d.text((x, y), ch, font=f, fill=INK)

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (LW, LH), BG); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, LW, 22), fill=(34, 20, 64)); d.text((8, 5), "NADIE  ARCADE", font=F(10), fill=CY)
    d.text((LW - 72, 5), "IA  ·  1P", font=F(10), fill=DIM)
    if t < LEVELS[0][1]:
        blink = int(t * 4) % 2 == 0
        tc(d, "¿LO VES EN", 170, 30, YE); tc(d, "5 SEGUNDOS?", 208, 30, YE)
        tc(d, "Encuentra la letra intrusa", 262, 13, INK, "Bold")
        if blink: tc(d, "PRESS START", 330, 16, CY)
    for (n, st, en, a, b, r, c) in LEVELS:
        if st <= t < en + REVEAL:
            tc(d, f"NIVEL {n}", 50, 20, PK); tc(d, "Hay una intrusa", 82, 13, INK, "Bold")
            grid(d, a, b, r, c, t)
            if t < en:
                left = en - t; fr = left / (en - st)
                d.rectangle((23, 400, 220, 410), outline=DIM)
                d.rectangle((25, 402, 25 + 193 * fr, 408), fill=YE if left > 2 else PK)
                d.text((230, 395), str(int(left) + 1), font=F(16), fill=YE if left > 2 else PK)
            else:
                p = t - en; cx = X0 + c * CELL + CELL / 2; cy = Y0 + r * CELL + CELL / 2
                rad = 15 + 30 * max(0, 1 - p / 0.25)
                for k in range(2):
                    d.ellipse((cx - rad - k, cy - rad - k, cx + rad + k, cy + rad + k), outline=PK)
                tc(d, f"¡ERA LA {b}!", 399, 22, PK)
    if LEVELS[0][2] + REVEAL <= t < LEVELS[1][1]:
        tc(d, "NIVEL 2", 200, 34, YE); tc(d, "más difícil", 240, 16, INK, "Bold")
    if t >= CTA:
        tc(d, "GAME OVER?", 92, 30, PK)
        tc(d, "¿Cuántas has visto?", 150, 16, INK, "Bold")
        tc(d, "Comenta 0, 1 o 2", 176, 18, YE)
        d.rectangle((20, 222, 250, 330), outline=CY)
        tc(d, "Sígueme y comenta:", 242, 13, CY, "Bold")
        tc(d, "a las 10:00 sorteo", 266, 14, INK, "Bold")
        tc(d, "un comentario y a las", 288, 14, INK, "Bold")
        tc(d, "13:30 sale su vídeo", 310, 14, INK, "Bold")
        tc(d, "@nadieenparticular.ia", 372, 11, DIM, "Bold")
    big = im.resize((LW * S, LH * S), Image.NEAREST)
    a = np.asarray(big).copy(); a[::S] = (a[::S] * 0.8).astype(np.uint8)   # scanlines
    return Image.fromarray(a)

def sfx(path):
    sr = 44100; out = np.zeros(int(sr * TOTAL))
    def sq(t0, f, du, v=0.25):
        n = int(sr * du); x = np.arange(n) / sr
        w = np.sign(np.sin(2 * np.pi * f * x)) * v * np.exp(-x * 6)
        s = int(sr * t0); out[s:s + n] += w[:len(out) - s]
    for k in range(4): sq(k * 0.25, 440 if k % 2 else 660, 0.1, 0.15)
    for (n, st, en, *_ ) in LEVELS:
        sq(st, 880, 0.12)
        for s in range(5): sq(st + s, 520 if en - st - s > 2 else 780, 0.06, 0.18)
        for k, f in enumerate([660, 880, 1320]): sq(en + k * 0.08, f, 0.15, 0.22)
    for k, f in enumerate([523, 659, 784, 1047]): sq(CTA + k * 0.12, f, 0.2, 0.2)
    pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "w") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for v in sys.argv[2:]: frame(int(float(v) * FPS)).save(f"still_{v}.png")
    else:
        sfx("sfx_pixel.wav")
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{LW*S}x{LH*S}", "-r", str(FPS), "-i", "-",
                              "-i", "sfx_pixel.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                              "-shortest", "-movflags", "+faststart", "reto_pixel.mp4"], stdin=subprocess.PIPE)
        for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i).tobytes())
        p.stdin.close(); p.wait()
