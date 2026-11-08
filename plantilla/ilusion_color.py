# Ilusión óptica de post-imagen ("este vídeo es en blanco y negro"), sin voz.
# Estilo: sala de museo minimalista (negro cálido, serif itálica + Inter fina).
# Uso: python3 ilusion_color.py still T  |  render   (genera mudo.mp4 y sfx.wav)
import sys, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
TOTAL = 22.0
STARE0, SWITCH, CTA = 2.2, 15.2, 19.0      # empieza a mirar, pasa a gris, cierre
BG = (14, 13, 12); INK = (242, 238, 230); DIM = (150, 144, 134); GOLD = (232, 196, 120)
IF = "/usr/share/fonts/opentype/inter/"
def INTER(s, w="Light"): return ImageFont.truetype(IF + f"Inter-{w}.otf", int(s))
def SERIF(s): return ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf", int(s))

IMG_Y, IMG_S = 470, 980    # zona de imagen: y 470..1450, x 50..1030
IMG_X = (W - IMG_S) // 2
CX, CY = W // 2, IMG_Y + IMG_S // 2

def scene():
    s = 1080; im = Image.new("RGB", (s, s)); d = ImageDraw.Draw(im)
    for y in range(s):                       # cielo
        k = y / (s * 0.62)
        d.line((0, y, s, y), fill=(int(20 + 90 * k), int(90 + 110 * k), int(235 - 20 * k)))
    d.ellipse((690, 120, 930, 360), fill=(255, 215, 0))          # sol
    d.ellipse((-200, 560, 700, 1300), fill=(40, 170, 60))         # colinas
    d.ellipse((380, 600, 1350, 1350), fill=(20, 130, 45))
    d.rectangle((0, 900, s, s), fill=(30, 150, 55))
    d.rectangle((150, 640, 450, 880), fill=(225, 30, 40))         # casa roja
    d.polygon([(120, 650), (300, 500), (480, 650)], fill=(120, 40, 160))   # tejado morado
    d.rectangle((260, 740, 340, 880), fill=(255, 150, 0))         # puerta naranja
    d.rectangle((790, 760, 830, 900), fill=(110, 60, 20))         # árbol
    d.ellipse((700, 600, 920, 800), fill=(0, 200, 110))
    d.ellipse((80, 940, 1000, 1080), fill=(255, 60, 160))         # campo de flores rosa
    return im.filter(ImageFilter.GaussianBlur(5)).resize((IMG_S, IMG_S), Image.LANCZOS)

ORIG = scene()
NEG = Image.eval(ORIG, lambda v: 255 - v)
GRAY = ORIG.convert("L").convert("RGB")

def tc(d, txt, y, font, fill=INK):
    bb = d.textbbox((0, 0), txt, font=font)
    d.text((W / 2 - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), txt, font=font, fill=fill)

def fade(t, a, dur=0.35):
    return max(0.0, min(1.0, (t - a) / dur))

def col(c, a):
    return tuple(int(BG[i] + (c[i] - BG[i]) * a) for i in range(3))

def dot(d):
    d.ellipse((CX - 17, CY - 17, CX + 17, CY + 17), fill=(255, 255, 255))
    d.ellipse((CX - 9, CY - 9, CX + 9, CY + 9), fill=(0, 0, 0))

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((70, 120), "NADIE · SALA 01", font=INTER(30, "Medium"), fill=DIM)
    d.text((W - 300, 120), "obra hecha por IA", font=INTER(30, "Light"), fill=DIM)
    if t < CTA:
        src = NEG if t < SWITCH else GRAY
        im.paste(src, (IMG_X, IMG_Y)); dot(d)
        d.rectangle((IMG_X - 6, IMG_Y - 6, IMG_X + IMG_S + 5, IMG_Y + IMG_S + 5), outline=GOLD, width=2)
    if t < STARE0:
        tc(d, "En 13 segundos esta foto será", 250, SERIF(64), col(INK, fade(t, 0)))
        tc(d, "BLANCO Y NEGRO.", 350, INTER(92, "Black"), col(INK, fade(t, 0.25)))
        tc(d, "…pero tú la vas a ver en color.", 1540, SERIF(52), col(GOLD, fade(t, 0.9)))
    elif t < SWITCH:
        left = SWITCH - t
        tc(d, "Mira SOLO el punto.", 250, INTER(76, "Bold"))
        tc(d, "No muevas los ojos. No parpadees.", 345, SERIF(48), DIM)
        n = int(np.ceil(left))
        tc(d, str(n), 1550, INTER(120, "Thin"), GOLD if n <= 3 else INK)
    elif t < CTA:
        tc(d, "Sigue mirando el punto…", 250, SERIF(66), INK)
        a = fade(t, SWITCH + 1.6)
        tc(d, "¿A que tiene color?", 1530, INTER(70, "Bold"), col(GOLD, a))
        tc(d, "(no tiene ni un píxel)", 1610, SERIF(46), col(DIM, fade(t, SWITCH + 2.3)))
    else:
        a = fade(t, CTA)
        tc(d, "Ni un píxel de color.", 560, INTER(84, "Black"), col(INK, a))
        tc(d, "Lo ha pintado tu cerebro.", 670, SERIF(66), col(GOLD, a))
        tc(d, "Tus ojos se cansan del negativo", 820, INTER(42), col(DIM, fade(t, CTA + 0.4)))
        tc(d, "y al quitarlo rellenan con lo contrario.", 880, INTER(42), col(DIM, fade(t, CTA + 0.4)))
        b = fade(t, CTA + 0.9)
        d.rounded_rectangle((90, 1020, W - 90, 1400), 36, outline=col(GOLD, b), width=3)
        tc(d, "¿Lo has visto? Comenta SÍ o NO", 1095, INTER(50, "Bold"), col(INK, b))
        tc(d, "Sígueme y comenta: a las 10:00", 1190, INTER(44), col(INK, b))
        tc(d, "sorteo un comentario y a las 13:30", 1250, INTER(44), col(INK, b))
        tc(d, "sale su vídeo.", 1310, INTER(44), col(INK, b))
        tc(d, "@nadieenparticular.ia", 1500, SERIF(50), col(DIM, fade(t, CTA + 1.3)))
    return im

def sfx():
    sr = 44100; n = int(TOTAL * sr); t = np.arange(n) / sr; out = np.zeros(n)
    pad = sum(np.sin(2 * np.pi * f * t) for f in (110, 164.8, 220, 261.6)) / 4
    out += 0.16 * pad * (0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * t)) * np.clip(t / 1.5, 0, 1) * np.clip((TOTAL - t) / 1.5, 0, 1)
    def add(at, sig):
        k = int(at * sr); m = min(len(sig), n - k); out[k:k + m] += sig[:m]
    tt = np.arange(int(0.06 * sr)) / sr
    tick = np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 70) * 0.25
    for s in np.arange(STARE0 + 1, SWITCH, 1.0): add(s, tick)
    ct = np.arange(int(2.5 * sr)) / sr
    chime = sum(np.sin(2 * np.pi * f * ct) for f in (880, 1318.5, 1760)) / 3 * np.exp(-ct * 1.8) * 0.4
    add(SWITCH, chime); add(CTA, chime * 0.6)
    out = np.clip(out, -1, 1)
    st = (np.repeat(out[:, None], 2, 1) * 32767).astype(np.int16)
    with wave.open("sfx.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes())

if __name__ == "__main__":
    if sys.argv[1] == "still":
        frame(int(float(sys.argv[2]) * FPS)).save(f"still_{sys.argv[2]}.png")
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "mudo.mp4"],
                             stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i).tobytes())
        p.stdin.close(); p.wait(); sfx()
