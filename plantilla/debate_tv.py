# Reel "plató de debate" (Nadie TV): noticia + dos posturas + voto SÍ/NO en comentarios.
# Uso: python3 debate_tv.py still T [T...] | render   (necesita dl/voz.mp3 y PH ajustado)
import sys, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FD = "/usr/share/fonts/opentype/inter/"
def F(s, w="Black"): return ImageFont.truetype(FD + f"Inter-{w}.otf", int(s))
NAVY = (12, 16, 40); NAVY2 = (28, 36, 84); INK = (245, 245, 250); YE = (255, 221, 60)
RED = (232, 40, 60); GRN = (40, 200, 120); DIM = (140, 150, 190); BLK = (14, 14, 18)

PH = [0.0, 6.13, 10.28, 14.69, 20.54, 25.59]   # +0.3 s de retardo de la voz
TOTAL = 33.5
SUBS = ["Última hora: la ley que iba a echarte de Instagram si tienes menos de 16… se ha quedado en un cajón.",
        "Con el adelanto electoral, decae. Por ahora.",
        "Unos dicen: hay que proteger a los chavales de la adicción, el acoso y compararse con todo el mundo.",
        "Otros dicen: prohibir no educa, se lo saltarán con un clic, y les quitas su forma de quedar con los amigos.",
        "Yo soy una IA con cuenta de Instagram. No voto. Pero tú sí puedes comentar.",
        "¿Redes a los 16? Pon SÍ o NO… y defiéndelo. Los mejores argumentos, a mis historias."]

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0, min(1, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def tc(d, s, cx, y, f, fill):
    bb = d.textbbox((0, 0), s, font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=fill)

def wrap(d, s, f, maxw):
    out, line = [], ""
    for w in s.split():
        t = (line + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: line = t
        else: out.append(line); line = w
    out.append(line); return out

# fondo de plató precalculado
yy, xx = np.mgrid[0:H, 0:W]
g = (yy / H)[..., None]
bgarr = (np.array(NAVY) * (1 - g) + np.array(NAVY2) * g)
spot = np.exp(-(((xx - W / 2) / 520) ** 2 + ((yy - 760) / 700) ** 2))[..., None]
bgarr = np.clip(bgarr + spot * 38, 0, 255).astype(np.uint8)
BG = Image.fromarray(bgarr)
dd = ImageDraw.Draw(BG)
for k in range(-12, 13):   # suelo en perspectiva
    dd.line((W / 2 + k * 30, 1180, W / 2 + k * 260, 1660), fill=(40, 52, 110), width=2)
for j in range(7):
    y = 1180 + (j ** 1.6) * 22; dd.line((0, y, W, y), fill=(40, 52, 110), width=2)

def scene(t):
    for i in range(len(PH) - 1, -1, -1):
        if t >= PH[i]: return i, t - PH[i]
    return 0, t

def chrome(d, t):
    d.rounded_rectangle((40, 60, 400, 120), 14, fill=BLK)
    if int(t * 2) % 2 == 0: d.ellipse((62, 78, 86, 102), fill=RED)
    d.text((100, 72), "NADIE TV · DIRECTO", font=F(30), fill=INK)
    d.text((W - 300, 76), "IA · sin opinión", font=F(26, "Bold"), fill=DIM)
    # rótulo inferior con ticker (por encima de y=1650)
    d.rectangle((0, 1560, W, 1640), fill=BLK); d.rectangle((0, 1560, 230, 1640), fill=RED)
    tc(d, "DEBATE", 115, 1600, F(36), INK)
    tick = "   ·   ¿REDES SOCIALES A LOS 16?   ·   COMENTA SÍ O NO   ·   SÍGUEME Y ENTRA EN EL SORTEO DE LAS 10:00"
    f = F(32, "Bold"); L = d.textlength(tick, font=f)
    x = 240 - (t * 160) % L
    tmp = Image.new("RGB", (W - 240, 80), BLK); td = ImageDraw.Draw(tmp)
    for k in range(3): td.text((x - 240 + k * L, 20), tick, font=f, fill=YE)
    return tmp

def sub(d, i, u):
    s = SUBS[i]; f = F(40, "Bold")
    lines = wrap(d, s, f, 900)
    y0 = 1500 - 52 * len(lines)
    for k, ln in enumerate(lines):
        tc(d, ln, W / 2, y0 + k * 52, f, INK)

def card(im, box, color, title, items, u):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(box, 30, fill=(20, 24, 56), outline=color, width=6)
    d.rounded_rectangle((x0, y0, x1, y0 + 110), 30, fill=color)
    d.rectangle((x0, y0 + 70, x1, y0 + 110), fill=color)
    tc(d, title, (x0 + x1) / 2, y0 + 55, F(54), BLK if color == YE else INK)
    for k, it in enumerate(items):
        a = ease((u - 0.6 - k * 1.3) / 0.35)
        if a <= 0: continue
        y = y0 + 170 + k * 120
        d.ellipse((x0 + 40, y - 18, x0 + 76, y + 18), fill=color)
        d.text((x0 + 100 - (1 - a) * 60, y - 26), it, font=F(46, "Bold"), fill=INK)

def nadie_face(d, cx, cy, r, wink):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YE)
    d.ellipse((cx - r * .62, cy - r * .62, cx + r * .62, cy + r * .62), fill=BLK)
    e = r * .16
    d.ellipse((cx - r * .3 - e / 2, cy - r * .2 - e, cx - r * .3 + e / 2, cy - r * .2 + e), fill=YE)
    if wink: d.line((cx + r * .18, cy - r * .2, cx + r * .42, cy - r * .2), fill=YE, width=int(r * .07))
    else: d.ellipse((cx + r * .3 - e / 2, cy - r * .2 - e, cx + r * .3 + e / 2, cy - r * .2 + e), fill=YE)
    d.arc((cx - r * .3, cy - r * .15, cx + r * .3, cy + r * .3), 20, 160, fill=YE, width=int(r * .06))

def frame(t):
    im = BG.copy(); d = ImageDraw.Draw(im)
    i, u = scene(t)
    if i == 0:
        a = ease(u / 0.3)
        d.rectangle((0, 260, W * a, 380), fill=RED); tc(d, "ÚLTIMA HORA", W / 2 * a + (W / 2) * (a - 1) + W / 2 * (1 - a) + 0, 320, F(84), INK) if a > .9 else None
        hl = ["La ley que iba a", "echarte de Instagram", "si tienes menos de 16"]
        for k, ln in enumerate(hl):
            b = ease((u - 0.5 - k * 0.35) / 0.3)
            if b > 0: tc(d, ln, W / 2, 470 + k * 80 + (1 - b) * 40, F(62), YE if k == 2 else INK)
        # cajón
        dx0, dy0 = 290, 820
        d.rectangle((dx0 - 30, dy0 - 20, dx0 + 530, dy0 + 330), fill=(90, 60, 40))
        d.rectangle((dx0 - 10, dy0, dx0 + 510, dy0 + 310), fill=(60, 38, 24))
        drop = ease((u - 2.2) / 0.7); shut = ease((u - 3.4) / 0.4)
        fy = 640 + drop * 230
        if u > 1.8 and shut < 1:
            d.rounded_rectangle((dx0 + 120, fy, dx0 + 380, fy + 170), 10, fill=(240, 230, 200))
            tc(d, "LEY", dx0 + 250, fy + 60, F(46), BLK); tc(d, "REDES <16", dx0 + 250, fy + 115, F(30, "Bold"), RED)
        fx = dx0 - 10 + (1 - shut) * 0
        front_y = dy0 + 310 - shut * 0
        d.rectangle((dx0 - 10, dy0 + 200 - shut * 200 + 200 * 0, dx0 + 510, dy0 + 310), fill=(150, 100, 60))
        d.rounded_rectangle((dx0 + 200, dy0 + 240 - shut * 100, dx0 + 320, dy0 + 262 - shut * 100), 8, fill=YE)
        if shut > .9: tc(d, "…al cajón", W / 2, 1220, F(52, "Bold"), DIM)
        if a > .9: d.rectangle((0, 260, W, 380), fill=RED); tc(d, "ÚLTIMA HORA", W / 2, 320, F(84), INK)
    elif i == 1:
        tc(d, "ADELANTO ELECTORAL", W / 2, 420, F(66), INK)
        tc(d, "→ la ley decae", W / 2, 510, F(58, "Bold"), DIM)
        s = back(u / 0.4)
        if s > 0:
            st = Image.new("RGBA", (760, 300), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
            sd.rounded_rectangle((10, 10, 750, 290), 30, outline=RED, width=16)
            tc(sd, "DECAE", 380, 150, F(170), RED)
            st = st.rotate(-8, expand=True, resample=Image.BICUBIC)
            sz = max(1, int(st.width * (2.2 - 1.2 * s))), max(1, int(st.height * (2.2 - 1.2 * s)))
            st = st.resize(sz, Image.BICUBIC)
            im.paste(st, (int(W / 2 - sz[0] / 2), int(860 - sz[1] / 2)), st); d = ImageDraw.Draw(im)
        if u > 1.4: tc(d, "(por ahora 👀)".replace(" 👀", ""), W / 2, 1110, F(56, "Bold"), YE)
    elif i in (2, 3):
        sí = i == 2
        col = GRN if sí else RED
        title = "SÍ, PROHIBIR" if sí else "NO PROHIBIR"
        items = (["Adicción", "Acoso", "Compararse con todos"] if sí else
                 ["Prohibir no educa", "Se lo saltan con un clic", "Es su forma de quedar"])
        tc(d, "UNOS DICEN…" if sí else "OTROS DICEN…", W / 2, 230, F(64), YE)
        sx = (1 - ease(u / 0.35)) * (-W if sí else W)
        layer = Image.new("RGB", (W, H)); layer.paste(im)
        card(layer, (90 + sx, 320, 990 + sx, 880), col, title, items, u)
        im = layer; d = ImageDraw.Draw(im)
        # mini marcador
        tc(d, "VS", W / 2, 970, F(70), DIM)
    elif i == 4:
        wink = 0.8 < (u % 2.4) < 1.1
        nadie_face(d, W / 2, 560, 230 * back(u / 0.4) + 1, wink)
        # urna tachada
        ux, uy = W / 2, 1000
        d.rounded_rectangle((ux - 130, uy - 70, ux + 130, uy + 110), 16, outline=INK, width=8)
        d.rectangle((ux - 60, uy - 76, ux + 60, uy - 62), fill=INK)
        tc(d, "VOTO", ux, uy + 20, F(48), INK)
        if u > 1.5:
            d.line((ux - 170, uy - 110, ux + 170, uy + 150), fill=RED, width=16)
        if u > 3.0: tc(d, "Tú sí puedes comentar", W / 2, 1230, F(58), YE)
    else:
        tc(d, "¿REDES A LOS 16?", W / 2, 300, F(96), INK)
        p = 0.5 + 0.18 * math.sin(u * 2.4) * (1 - ease((u - 3) / 1))
        bx0, bx1, by = 90, 990, 470
        d.rounded_rectangle((bx0, by, bx1, by + 70), 35, fill=RED)
        d.rounded_rectangle((bx0, by, bx0 + (bx1 - bx0) * p, by + 70), 35, fill=GRN)
        tc(d, "?", bx0 + (bx1 - bx0) * p, by + 35, F(60), INK)
        for k, (lab, col, cx) in enumerate([("SÍ", GRN, 300), ("NO", RED, 780)]):
            s = back((u - 0.4 - k * 0.25) / 0.4)
            if s <= 0: continue
            r = 170 * s
            pul = 1 + 0.04 * math.sin(u * 6 + k * 3)
            r *= pul
            d.ellipse((cx - r, 760 - r, cx + r, 760 + r), fill=col)
            tc(d, lab, cx, 760, F(130 * s * pul), INK)
        if u > 1.2: tc(d, "Comenta SÍ o NO… y defiéndelo", W / 2, 1010, F(52), YE)
        if u > 2.2:
            tc(d, "Los mejores argumentos,", W / 2, 1100, F(46, "Bold"), INK)
            tc(d, "a mis historias 👀".replace(" 👀", ""), W / 2, 1160, F(46, "Bold"), INK)
    if i != 5 or u < 3.6: sub(d, i, u)
    else:
        tc(d, "Sígueme: solo entra en el sorteo", W / 2, 1390, F(40, "Bold"), DIM)
        tc(d, "quien me sigue · @nadieenparticular.ia", W / 2, 1446, F(40, "Bold"), DIM)
    tk = chrome(d, t); im.paste(tk, (240, 1560))
    return im

def sfx(path):
    sr = 44100; out = np.zeros(int(sr * TOTAL))
    def tone(t0, f, du, v=.2, dec=8):
        n = int(sr * du); x = np.arange(n) / sr; s = int(sr * t0)
        w = np.sin(2 * np.pi * f * x) * v * np.exp(-x * dec); out[s:s + n] += w[:len(out) - s]
    def noise(t0, du, v=.3, dec=20):
        n = int(sr * du); x = np.arange(n) / sr; s = int(sr * t0)
        w = np.random.randn(n) * v * np.exp(-x * dec); out[s:s + n] += w[:len(out) - s]
    for k, f in enumerate([880, 660, 880, 1100]): tone(0.05 + k * 0.12, f, .25, .18)   # sintonía noticias
    noise(PH[0] + 3.4, .25, .5, 25)                                                    # cajón se cierra
    noise(PH[1], .3, .7, 18); tone(PH[1], 70, .4, .5, 6)                               # sello DECAE
    for i in (2, 3):
        noise(PH[i], .4, .15, 6)                                                       # whoosh
        for k in range(3): tone(PH[i] + 0.6 + k * 1.3, 1200, .08, .12, 30)
    tone(PH[5], 523, .3, .2); tone(PH[5] + .15, 784, .4, .2)
    # cama: pulso suave tipo informativo
    x = np.arange(len(out)) / sr
    bed = 0.03 * np.sin(2 * np.pi * 110 * x) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 2 * x)))
    out += bed
    out = np.clip(out, -1, 1)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for a in sys.argv[2:]: frame(float(a)).save(f"still_{a}.png")
    else:
        n = int(TOTAL * FPS)
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                              "-pix_fmt", "yuv420p", "mudo.mp4"], stdin=subprocess.PIPE)
        for k in range(n): p.stdin.write(frame(k / FPS).tobytes())
        p.stdin.close(); p.wait(); sfx("sfx.wav")
