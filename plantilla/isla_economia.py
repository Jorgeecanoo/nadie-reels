# Reel extra 2026-11-05: "Cómo funciona la economía" para @mako_pk (petición de Jorge).
# Estilo: ilustración plana tipo libro infantil/explainer, una isla con 3 personajes. Sin voz.
# Uso: python3 isla_economia.py still 6.5 14 | render | sfx
import math, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
K = 2                       # supermuestreo de la capa de dibujo
TOTAL = 60.5
NAVY = (22, 33, 62); WHITE = (255, 255, 255); YEL = (255, 221, 60); RED = (239, 68, 68)
SKY1 = (120, 205, 250); SKY2 = (226, 246, 255); SEA1 = (40, 170, 230); SEA2 = (10, 95, 170)
SAND = (250, 214, 140); SAND2 = (232, 186, 110); PALM = (40, 160, 100); TRUNK = (150, 100, 60)
ANA = (255, 112, 112); BETO = (52, 190, 130); CECI = (130, 100, 255)
SHELL = (255, 170, 190); GOLD = (255, 200, 40); BROWN = (170, 110, 60)
GF = "/usr/share/fonts/truetype/google-fonts/"
def POP(s, w="Bold"): return ImageFont.truetype(GF + f"Poppins-{w}.ttf", int(s))
_fc = {}
def F(s, w="Bold"):
    k = (int(s), w)
    if k not in _fc: _fc[k] = POP(s, w)
    return _fc[k]

def cl(x): return max(0.0, min(1.0, x))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def inout(x): x = cl(x); return x * x * (3 - 2 * x)
def back(x):
    x = cl(x); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u
def mix(c1, c2, u): return tuple(int(lerp(a, b, u)) for a, b in zip(c1, c2))

# escenas: (inicio, fin)
T = [0, 7.6, 13.55, 20.95, 27.6, 34.6, 41.95, 50.6, 55.85, TOTAL]
def scene(t):
    for i in range(len(T) - 1):
        if t < T[i + 1]: return i, t - T[i]
    return len(T) - 2, t - T[-2]

# ---------- fondo fijo ----------
MY0, MY1 = 560, 1440        # franja dibujada con supermuestreo
def make_bg():
    a = np.zeros((H, W, 3))
    hz = 1150
    for y in range(H):
        if y < hz: a[y] = np.array(mix(SKY1, SKY2, y / hz))
        else: a[y] = np.array(mix(SEA1, SEA2, (y - hz) / (H - hz)))
    im = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.ellipse((800, 80, 980, 260), fill=(255, 236, 140))   # sol
    for (x, y, s) in ((150, 640, 1.0), (760, 520, .8)):      # nubes
        for dx, dy, r in ((0, 0, 50), (55, -20, 60), (115, 0, 48)):
            d.ellipse((x + dx * s - r * s, y + dy * s - r * s, x + dx * s + r * s, y + dy * s + r * s), fill=(255, 255, 255))
    return im
BG = make_bg()

class D2:
    """ImageDraw con coordenadas de salida (1080x1920), dibujando en la capa x2."""
    def __init__(self, im): self.d = ImageDraw.Draw(im)
    def p(self, x, y): return (x * K, (y - MY0) * K)
    def box(self, b): return (b[0] * K, (b[1] - MY0) * K, b[2] * K, (b[3] - MY0) * K)
    def ellipse(self, b, **kw):
        if "width" in kw: kw["width"] = int(kw["width"] * K)
        self.d.ellipse(self.box(b), **kw)
    def rrect(self, b, r, **kw):
        if "width" in kw: kw["width"] = int(kw["width"] * K)
        self.d.rounded_rectangle(self.box(b), radius=r * K, **kw)
    def rect(self, b, **kw): self.d.rectangle(self.box(b), **kw)
    def poly(self, pts, **kw): self.d.polygon([self.p(*q) for q in pts], **kw)
    def line(self, pts, width, **kw): self.d.line([self.p(*q) for q in pts], width=int(width * K), joint="curve", **kw)
    def pie(self, b, a0, a1, **kw): self.d.pieslice(self.box(b), a0, a1, **kw)
    def circle(self, cx, cy, r, **kw): self.ellipse((cx - r, cy - r, cx + r, cy + r), **kw)
    def text(self, x, y, s, size, fill, w="Bold", anchor="mm"):
        self.d.text(self.p(x, y), s, font=F(size * K, w), fill=fill, anchor=anchor)

# ---------- dibujos ----------
def island(d, t):
    # olas en la orilla
    for i in range(3):
        off = math.sin(t * 1.6 + i) * 14
        d.ellipse((60 - i * 30 + off, 1160 + i * 34, 1020 + i * 30 + off, 1290 + i * 34), outline=(190, 235, 255), width=5)
    d.ellipse((70, 1080, 1010, 1290), fill=SAND2)
    d.ellipse((80, 1070, 1000, 1270), fill=SAND)
    # palmera
    sw = math.sin(t * 1.3) * 6
    d.line([(980, 1130), (990, 1000), (1000 + sw * .3, 870), (1010 + sw, 760)], 26, fill=TRUNK)
    for ang in (200, 240, 285, 330, 20):
        a = math.radians(ang + sw)
        x0, y0 = 1010 + sw, 760
        x1, y1 = x0 + math.cos(a) * 170, y0 + math.sin(a) * 90 + 40
        d.poly([(x0, y0 - 10), (x1, y1), (x0 + 10, y0 + 18)], fill=PALM)

def person(d, cx, foot, col, name, s, mood="ok", arm=0.0, t=0.0):
    if s <= 0.01: return
    bob = math.sin(t * 3 + cx) * 4
    s *= 1.3
    h = 150 * s; bw = 110 * s
    top = foot - h + bob
    # brazo levantado (arm 0..1)
    if arm > 0:
        d.line([(cx + bw * .4, top + 40 * s), (cx + bw * .4 + 40 * s, top + 10 * s - 70 * s * arm)], 22 * s, fill=col)
        d.circle(cx + bw * .4 + 40 * s, top + 10 * s - 70 * s * arm, 16 * s, fill=col)
    d.rrect((cx - bw / 2, top, cx + bw / 2, foot), 40 * s, fill=col)
    hr = 62 * s; hy = top - hr * .75
    d.circle(cx, hy, hr, fill=mix(col, WHITE, .35))
    ex = 22 * s
    for sx in (-1, 1): d.circle(cx + sx * ex, hy - 6 * s, 9 * s, fill=NAVY)
    if mood == "ok":
        d.d.arc(d.box((cx - 24 * s, hy - 4 * s, cx + 24 * s, hy + 30 * s)), 20, 160, fill=NAVY, width=int(6 * s * K))
    elif mood == "no":
        d.d.arc(d.box((cx - 22 * s, hy + 16 * s, cx + 22 * s, hy + 44 * s)), 200, 340, fill=NAVY, width=int(6 * s * K))
    elif mood == "wow":
        d.circle(cx, hy + 22 * s, 11 * s, fill=NAVY)
    d.text(cx, foot + 34, name, 30 * s, NAVY)

def fish(d, cx, cy, s, col=(255, 150, 60)):
    s *= 1.4
    if s <= 0.01: return
    d.poly([(cx + 40 * s, cy), (cx + 80 * s, cy - 32 * s), (cx + 80 * s, cy + 32 * s)], fill=col)
    d.ellipse((cx - 60 * s, cy - 32 * s, cx + 52 * s, cy + 32 * s), fill=col)
    d.circle(cx - 30 * s, cy - 8 * s, 7 * s, fill=NAVY)

def banana(d, cx, cy, s):
    s *= 1.4
    if s <= 0.01: return
    pts_o, pts_i = [], []
    for i in range(21):
        a = math.radians(200 + i * 7)
        pts_o.append((cx + math.cos(a) * 70 * s, cy - 40 * s - math.sin(a) * 70 * s))
        pts_i.append((cx + math.cos(a) * 46 * s, cy - 30 * s - math.sin(a) * 50 * s))
    d.poly(pts_o + pts_i[::-1], fill=(255, 215, 50), outline=(200, 150, 20))
    d.circle(pts_o[0][0], pts_o[0][1], 7 * s, fill=(110, 80, 30))

def basket(d, cx, cy, s):
    s *= 1.4
    if s <= 0.01: return
    d.d.arc(d.box((cx - 45 * s, cy - 75 * s, cx + 45 * s, cy + 5 * s)), 180, 360, fill=BROWN, width=int(10 * s * K))
    d.poly([(cx - 65 * s, cy - 30 * s), (cx + 65 * s, cy - 30 * s), (cx + 45 * s, cy + 40 * s), (cx - 45 * s, cy + 40 * s)], fill=(200, 140, 70))
    for k in (-1, 0, 1): d.line([(cx - 55 * s, cy - 8 * s + k * 18 * s), (cx + 55 * s, cy - 8 * s + k * 18 * s)], 4 * s, fill=BROWN)

def shell(d, cx, cy, s, col=SHELL):
    s *= 1.3
    if s <= 0.01: return
    d.pie((cx - 34 * s, cy - 34 * s, cx + 34 * s, cy + 34 * s), 180, 360, fill=col, outline=mix(col, NAVY, .3))
    d.rect((cx - 10 * s, cy - 2 * s, cx + 10 * s, cy + 12 * s), fill=mix(col, NAVY, .2))
    for a in (200, 235, 270, 305, 340):
        r = math.radians(a)
        d.line([(cx, cy), (cx + math.cos(r) * 32 * s, cy + math.sin(r) * 32 * s)], 3 * s, fill=mix(col, NAVY, .35))

def chest(d, cx, cy, s, open_=0.0):
    if s <= 0.01: return
    d.rrect((cx - 90 * s, cy - 40 * s, cx + 90 * s, cy + 60 * s), 12 * s, fill=BROWN)
    lid = -60 * s * open_
    d.rrect((cx - 95 * s, cy - 85 * s + lid, cx + 95 * s, cy - 35 * s + lid), 20 * s, fill=(140, 85, 45))
    d.rect((cx - 14 * s, cy - 20 * s, cx + 14 * s, cy + 20 * s), fill=GOLD)

def boat(d, cx, cy, s, t):
    if s <= 0.01: return
    cy += math.sin(t * 2.2) * 6
    d.poly([(cx - 110 * s, cy), (cx + 110 * s, cy), (cx + 75 * s, cy + 50 * s), (cx - 75 * s, cy + 50 * s)], fill=(190, 90, 50))
    d.line([(cx, cy), (cx, cy - 170 * s)], 8 * s, fill=NAVY)
    d.poly([(cx + 6 * s, cy - 165 * s), (cx + 100 * s, cy - 30 * s), (cx + 6 * s, cy - 30 * s)], fill=WHITE)
    d.text(cx + 45 * s, cy - 70 * s, "CECI", 22 * s, CECI)

def tag(d, cx, cy, s, txt, col=WHITE):
    s *= 1.5
    if s <= 0.01: return
    w = 70 * s + len(txt) * 15 * s
    d.line([(cx - w / 2 - 30 * s, cy - 40 * s), (cx - w / 2 + 6 * s, cy - 6 * s)], 4 * s, fill=NAVY)
    d.rrect((cx - w / 2, cy - 36 * s, cx + w / 2, cy + 36 * s), 14 * s, fill=col, outline=NAVY, width=4 * s)
    d.text(cx, cy, txt, 30 * s, NAVY)

def bubble(d, cx, cy, txt, s, size=34):
    if s <= 0.01: return
    w = F(size * K).getlength(txt) / K + 60
    d.rrect((cx - w / 2 * s, cy - 45 * s, cx + w / 2 * s, cy + 45 * s), 30 * s, fill=WHITE, outline=NAVY, width=4)
    d.poly([(cx - 20 * s, cy + 40 * s), (cx + 10 * s, cy + 40 * s), (cx - 30 * s, cy + 80 * s)], fill=WHITE)
    d.text(cx, cy, txt, size * s, NAVY)

def big_x(d, cx, cy, s):
    if s <= 0.01: return
    r = 70 * s
    d.line([(cx - r, cy - r), (cx + r, cy + r)], 26 * s, fill=RED)
    d.line([(cx + r, cy - r), (cx - r, cy + r)], 26 * s, fill=RED)

def arrow(d, x0, y0, x1, y1, u, col=NAVY):
    if u <= 0: return
    xe, ye = lerp(x0, x1, u), lerp(y0, y1, u)
    d.line([(x0, y0), (xe, ye)], 10, fill=col)
    a = math.atan2(ye - y0, xe - x0)
    d.poly([(xe + math.cos(a) * 26, ye + math.sin(a) * 26), (xe + math.cos(a + 2.4) * 26, ye + math.sin(a + 2.4) * 26),
            (xe + math.cos(a - 2.4) * 26, ye + math.sin(a - 2.4) * 26)], fill=col)

# ---------- texto (a 1x) ----------
def tokens(s):
    out = []
    for w_ in s.split():
        hot = w_.startswith("*")
        out.append((w_.replace("*", ""), hot))
    return out

def rich(d, s, cx, cy, f, col, hotcol, maxw, lh=1.22, alpha=1.0):
    toks = tokens(s); lines, cur = [], []
    sp = f.getlength(" ")
    for tk in toks:
        trial = cur + [tk]
        if sum(f.getlength(x[0]) for x in trial) + sp * (len(trial) - 1) > maxw and cur:
            lines.append(cur); cur = [tk]
        else: cur = trial
    lines.append(cur)
    hh = f.size * lh; y = cy - hh * (len(lines) - 1) / 2
    for ln in lines:
        wtot = sum(f.getlength(x[0]) for x in ln) + sp * (len(ln) - 1)
        x = cx - wtot / 2
        for word, hot in ln:
            d.text((x, y), word, font=f, fill=hotcol if hot else col, anchor="lm")
            x += f.getlength(word) + sp
        y += hh

STEPS = {
 1: ("1 · CADA UNO HACE UNA COSA", "Una isla. Ana pesca, Beto cultiva plátanos y Ceci hace cestas.",
     "Nadie lo hace todo: cada uno se *especializa* en lo suyo."),
 2: ("2 · EL TRUEQUE", "Ana quiere plátanos. Le ofrece un pescado a Beto…",
     "Cambiar cosa por cosa casi nunca encaja. Falta algo que *todos* acepten."),
 3: ("3 · EL DINERO", "Aparecen las conchas: raras, bonitas y fáciles de llevar.",
     "Valen porque todos se fían de que valen. Eso es el *dinero:* un acuerdo."),
 4: ("4 · LOS PRECIOS", "Mala cosecha: queda un plátano y todos lo quieren.",
     "Hay poco y mucha gente lo quiere: el precio *sube.* Oferta y demanda."),
 5: ("5 · AHORRO E INVERSIÓN", "Ana guarda conchas y se las presta a Ceci para un barco.",
     "Ceci pesca el triple y devuelve lo prestado + un extra: el *interés.*"),
 6: ("6 · LA INFLACIÓN", "¡Alguien encuentra un cofre lleno de conchas!",
     "Más conchas, los mismos plátanos: todo cuesta más. Eso es la *inflación.*"),
}

CAPT = {1: 3.6, 2: 4.6, 3: 2.0, 4: 3.8, 5: 3.2, 6: 3.4}
def overlay_text(im, n, lt):
    chip, head, cap = STEPS[n]
    d = ImageDraw.Draw(im)
    u = ease(lt / .45)
    f = F(36)
    w = f.getlength(chip) + 64
    y = 210 - (1 - u) * 40
    if u > 0:
        d.rounded_rectangle((540 - w / 2, y - 36, 540 + w / 2, y + 36), radius=36, fill=NAVY)
        d.text((540, y), chip, font=f, fill=YEL, anchor="mm")
    u2 = ease((lt - .25) / .5)
    if u2 > 0:
        rich(d, head, 540, 360 + (1 - u2) * 30, F(56), NAVY, NAVY, 940)
    u3 = back((lt - CAPT[n]) / .45)
    if u3 > 0.01:
        cw, ch = 960 * u3, 230 * u3
        d.rounded_rectangle((540 - cw / 2, 1525 - ch / 2, 540 + cw / 2, 1525 + ch / 2), radius=34, fill=NAVY)
        if u3 > .8: rich(d, cap, 540, 1525, F(47, "Medium"), WHITE, YEL, 880)

# ---------- fotograma ----------
XA, XB, XC, FOOT = 230, 530, 820, 1140

def mid_layer(t):
    lay = Image.new("RGBA", (W * K, (MY1 - MY0) * K), (0, 0, 0, 0))
    d = D2(lay)
    n, lt = scene(t)
    island(d, t)
    if n == 0: return lay
    # aparición de personajes (sincronizada con la voz)
    sA = back((t - T[1] - .15) / .4); sB = back((t - T[1] - 1.0) / .4); sC = back((t - T[1] - 2.55) / .4)
    moodA = moodB = moodC = "ok"; armA = armC = 0.0
    if n == 2 and lt > 3.1: moodB = "no"
    if n == 4: armA = armC = ease((lt - 2.9) / .4); moodA = moodC = "wow" if lt > 2.9 else "ok"
    if n == 6 and lt > 2.4: moodA = moodB = moodC = "wow"
    if n == 5 and lt > 4.6: moodA = "wow"
    person(d, XA, FOOT, ANA, "ANA", sA, moodA, armA, t)
    person(d, XB, FOOT, BETO, "BETO", sB, moodB, 0, t)
    if not (n == 5 and lt > 2.5):
        person(d, XC, FOOT, CECI, "CECI", sC, moodC, armC, t)
    else:
        boat(d, XC + 40, 1300, ease((lt - 2.5) / .5), t)
    IY = 720   # altura de los objetos
    if n == 1:
        fish(d, XA, IY, back((lt - .45) / .35))
        banana(d, XB, IY + 40, back((lt - 1.3) / .35))
        basket(d, XC, IY, back((lt - 2.85) / .35))
    elif n == 2:
        u = inout((lt - 1.3) / 1.1)
        fish(d, lerp(XA, XB - 130, u), IY - math.sin(u * math.pi) * 80, 1.0)
        banana(d, XB, IY + 40, 1.0)
        bubble(d, XB + 140, 600, "¿Pescado? Lo odio.", back((lt - 3.1) / .35))
        big_x(d, (XA + XB) / 2 + 10, IY, back((lt - 4.0) / .3))
    elif n == 3:
        for i, x in enumerate((XA, XB, XC)):
            for j in range(3):
                k = back((lt - .6 - i * .2 - j * .12) / .35)
                shell(d, x - 50 + j * 50, 1040 - (1 - k) * 160, k * .9)
        u = inout((lt - 2.2) / 1.2)
        shell(d, lerp(XA, XB, u), IY - math.sin(u * math.pi) * 90, 1.0 if lt > 2.0 else 0)
        banana(d, lerp(XB, XA, u), IY + 40 + math.sin(u * math.pi) * 60, 1.0 if lt > 2.0 else 0)
        if lt > 3.5: bubble(d, XB + 140, 600, "¡Trato!", back((lt - 3.5) / .3))
    elif n == 4:
        banana(d, XB, IY + 40, 1.0)
        up = lt >= 4.5
        price = "5 conchas" if up else "2 conchas"
        tag(d, XB + 190, IY - 110, back((lt - 1.8) / .35) * (1 + .25 * max(0, 1 - abs(lt - 4.5) / .25)), price, YEL if up else WHITE)
        if up: arrow(d, XB + 400, IY - 30, XB + 400, IY - 190, ease((lt - 4.5) / .4), RED)
        for x in (XA, XC): shell(d, x + 90, 800, back((lt - 3.0) / .3) * .8)
    elif n == 5:
        for j in range(3):
            u = inout((lt - 1.4 - j * .15) / 1.0)
            if 1.3 < lt < 2.9: shell(d, lerp(XA, XC, u), IY - math.sin(u * math.pi) * 110 + j * 20, .9)
        for j in range(3):
            fish(d, XC - 60 + j * 70, 1000 - j * 18, back((lt - 3.3 - j * .2) / .3) * .7, (255, 150, 60))
        for j in range(4):
            u = inout((lt - 4.6 - j * .15) / 1.0)
            if lt > 4.6:
                shell(d, lerp(XC, XA + (j - 1.5) * 45, u), lerp(IY, IY + 80, u) - math.sin(u * math.pi) * 120, .9, GOLD if j == 3 else SHELL)
        if lt > 6.5: tag(d, XA + 60, IY - 130, back((lt - 6.5) / .3), "+1 interés", YEL)
    elif n == 6:
        chest(d, 540, 1325, .7 * back((lt - 1.8) / .35), ease((lt - 2.3) / .3))
        rnd = random.Random(4)
        for j in range(26):
            st = 2.4 + rnd.random() * .9; vx = rnd.uniform(-420, 60); vy = rnd.uniform(-650, -420)
            u = lt - st
            if u > 0:
                x = 540 + vx * u * .9 + 180 * u; y = 1240 + vy * u + 620 * u * u
                if y < 1235 or u < .4: shell(d, x, y, .6)
                else: shell(d, x, 1235 + (j % 4) * 10, .6)
        banana(d, XB, IY + 40, 1.0)
        up = lt >= 6.1
        tag(d, XB + 10, IY - 120, 1 + .3 * max(0, 1 - abs(lt - 6.1) / .25), "15 conchas" if up else "5 conchas", RED if up else WHITE)
    return lay

def yellow_card(lines, sub=None, face=False):
    im = Image.new("RGB", (W, H), YEL); d = ImageDraw.Draw(im)
    return im, d

def face(d, cx, cy, r, wink=0.0):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=NAVY)
    d.ellipse((cx - r * .45 - 16, cy - r * .3 - 22, cx - r * .45 + 16, cy - r * .3 + 22), fill=YEL)
    if wink > .5: d.line((cx + r * .3, cy - r * .3, cx + r * .6, cy - r * .3), fill=YEL, width=12)
    else: d.ellipse((cx + r * .45 - 16, cy - r * .3 - 22, cx + r * .45 + 16, cy - r * .3 + 22), fill=YEL)
    d.arc((cx - r * .5, cy - r * .2, cx + r * .5, cy + r * .55), 20, 160, fill=YEL, width=12)

def hook(lt):
    im = Image.new("RGB", (W, H), YEL); d = ImageDraw.Draw(im)
    u = ease(lt / .4)
    d.text((540, 430 - (1 - u) * 30), "@mako_pk me ha dicho:", font=F(52), fill=NAVY, anchor="mm")
    u2 = back((lt - .35) / .45)
    if u2 > .01:
        bw, bh = 940 * u2, 380 * u2
        d.rounded_rectangle((540 - bw / 2, 760 - bh / 2, 540 + bw / 2, 760 + bh / 2), radius=46, fill=WHITE, outline=NAVY, width=6)
        d.polygon([(220, 940), (300, 940), (190, 1020)], fill=WHITE, outline=None)
        if u2 > .85:
            rich(d, "«¿Me haces un vídeo de cómo funciona la *economía?* Pero un reel, no una historia, porfa»",
                 540, 760, F(50, "Medium"), NAVY, (230, 70, 120), 820)
    u3 = back((lt - 4.8) / .4)
    if u3 > .01:
        rich(d, "Vale, vale. Te lo explico con *una* *isla.*", 540, 1180, F(int(70 * u3)), NAVY, (230, 70, 120), 900)
    if lt > 5.6:
        face(d, 540, 1420, 90, 1.0 if 6.2 < lt < 6.6 else 0.0)
    return im

def ending(lt, n):
    im = Image.new("RGB", (W, H), YEL); d = ImageDraw.Draw(im)
    if n == 7:
        d.text((540, 420), "RESUMEN", font=F(40), fill=(230, 70, 120), anchor="mm")
        rich(d, "La economía es *gente* *decidiendo* qué hacer con cosas que *no* *alcanzan* *para* *todos.*",
             540, 760, F(70), NAVY, (230, 70, 120), 920, alpha=1)
        u = ease((lt - 1.2) / .5)
        if u > 0:
            rich(d, "Especializarse · dinero · precios · interés · inflación", 540, 1120 + (1 - u) * 20, F(36, "Medium"), NAVY, NAVY, 920)
        # miniaturas de la isla
        for i, (col) in enumerate((ANA, BETO, CECI)):
            x = 360 + i * 180; y = 1330
            d.ellipse((x - 46, y - 46, x + 46, y + 46), fill=col)
    else:
        u = back(lt / .45)
        rich(d, "¿Lo has pillado o te lo repito *más* *despacio?*", 540, 560, F(int(68 * max(u, .01))), NAVY, (230, 70, 120), 920)
        face(d, 540, 900, 120, 1.0 if 1.0 < lt < 1.5 else 0.0)
        u2 = ease((lt - .8) / .5)
        if u2 > 0:
            rich(d, "Comenta tu próxima pregunta.", 540, 1160 + (1 - u2) * 20, F(54), NAVY, NAVY, 920)
            rich(d, "Si me sigues, entras en el *sorteo* del reel de mañana.", 540, 1290 + (1 - u2) * 20, F(42, "Medium"), NAVY, (230, 70, 120), 900)
    return im

def frame(t):
    n, lt = scene(t)
    if n == 0 and lt < T[1] - .4: return hook(lt)
    if n >= 7:
        im = ending(lt, n)
        if n == 7 and lt < .45:   # cortinilla: el amarillo sube
            base = island_frame(t)
            hgt = int(H * ease(lt / .45))
            base.paste(im.crop((0, H - hgt, W, H)), (0, H - hgt))
            return base
        return im
    im = island_frame(t)
    if n == 0:   # el gancho sale hacia arriba
        hk = hook(lt)
        off = int(H * ease((lt - (T[1] - .4)) / .4))
        im.paste(hk.crop((0, off, W, H)), (0, 0))
    return im

def island_frame(t):
    n, lt = scene(t)
    im = BG.copy()
    lay = mid_layer(t).resize((W, MY1 - MY0), Image.LANCZOS)
    im.paste(lay, (0, MY0), lay)
    if 1 <= n <= 6: overlay_text(im, n, lt)
    return im

# ---------- sonido ----------
def sfx():
    SR = 44100; n = int(SR * TOTAL); tr = np.zeros(n); r = np.random.default_rng(7)
    def add(t0, s, g=1.0):
        i = int(SR * t0); j = min(n, i + len(s))
        if 0 <= i < n: tr[i:j] += s[:j - i] * g
    def env(m, a, d): tt = np.arange(m) / SR; return np.minimum(1, tt / a) * np.exp(-tt / d)
    def kick():
        m = int(SR * .3); tt = np.arange(m) / SR; f = 55 + 80 * np.exp(-tt * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(m, .002, .1)
    def shaker(): m = int(SR * .06); return r.standard_normal(m) * env(m, .004, .015) * .18
    def uke(f, d=.5):
        m = int(SR * d); tt = np.arange(m) / SR
        return (np.sin(2 * np.pi * f * tt) + .5 * np.sin(4 * np.pi * f * tt) + .2 * np.sin(6 * np.pi * f * tt)) * env(m, .003, .14) * .16
    def marimba(f, d=.4):
        m = int(SR * d); tt = np.arange(m) / SR
        return (np.sin(2 * np.pi * f * tt) + .25 * np.sin(2 * np.pi * f * 4 * tt)) * env(m, .002, .12) * .3
    def pop(f0, f1, d=.09):
        m = int(SR * d); tt = np.arange(m) / SR; f = f0 + (f1 - f0) * tt / d
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(m, .002, d / 3) * .5
    def coin():
        m = int(SR * .35); tt = np.arange(m) / SR
        a = np.sin(2 * np.pi * 1975 * tt) * (tt < .07) + np.sin(2 * np.pi * 2637 * tt) * (tt >= .07)
        return a * env(m, .001, .12) * .25
    def buzz():
        m = int(SR * .35); tt = np.arange(m) / SR
        return np.sign(np.sin(2 * np.pi * 110 * tt)) * env(m, .005, .15) * .2
    def whoosh(d=.4):
        m = int(SR * d); x = r.standard_normal(m); x = np.convolve(x, np.ones(30) / 30, "same")
        return x * np.sin(np.linspace(0, np.pi, m)) * 1.2
    bpm = 112; b = 60 / bpm
    prog = [[261.6, 329.6, 392.0], [196.0, 246.9, 293.7], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6]]
    k = 0; t0 = 0.0
    while t0 < TOTAL - 0.5:
        beat = k % 4; ch = prog[(k // 4) % 4]
        if beat in (0, 2): add(t0, kick(), .45)
        add(t0, shaker(), 1); add(t0 + b / 2, shaker(), .7)
        add(t0, uke(ch[0] * 2 if beat % 2 == 0 else ch[2] * 2), 1)
        add(t0 + b / 2, uke(ch[1] * 2, .3), .6)
        k += 1; t0 += b
    def at(sc, lt0): return T[sc] + lt0
    for tt in (0.0, 0.35, 4.8, 5.6): add(tt, pop(500, 1300), .6)
    add(T[1] - .4, whoosh(), .8)
    for s0 in T[1:8]: add(s0, marimba(784), .7); add(s0 + .12, marimba(1047), .6)
    for lt0 in (.15, .45, 1.0, 1.3, 2.55, 2.85): add(at(1, lt0), pop(400, 1100), .5)
    add(at(2, 1.3), whoosh(.5), .5); add(at(2, 3.1), pop(900, 300, .2), .6); add(at(2, 4.0), buzz(), .8)
    for i in range(9): add(at(3, .6 + i * .14), coin(), .55)
    add(at(3, 2.2), whoosh(.5), .5); add(at(3, 3.5), marimba(1319), .7)
    add(at(4, 1.8), pop(500, 1100), .5); add(at(4, 4.5), pop(300, 1500, .3), .7)
    for j in range(3): add(at(5, 1.4 + j * .15), coin(), .5)
    add(at(5, 2.5), whoosh(), .5)
    for j in range(3): add(at(5, 3.3 + j * .2), pop(700, 1200), .4)
    for j in range(4): add(at(5, 4.6 + j * .15), coin(), .55)
    add(at(5, 6.5), marimba(1568), .8)
    add(at(6, 1.8), pop(200, 120, .2), .8)
    for j in range(20): add(at(6, 2.4 + j * .05), coin(), .3)
    add(at(6, 6.1), pop(300, 1800, .35), .8)
    add(T[7], whoosh(), .7)
    add(at(8, 1.0), pop(1200, 1800, .07), .6)
    fade = np.ones(n); m = int(SR * 1.0); fade[-m:] = np.linspace(1, 0, m)
    tr = np.tanh(tr * 1.1) * .85 * fade
    with wave.open("sfx.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((tr * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "still":
        for s in sys.argv[2:]: frame(float(s)).save(f"still_{s}.png")
    elif cmd == "sfx": sfx()
    elif cmd == "render":
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "veryfast", "mudo_tmp.mp4"], stdin=subprocess.PIPE)
        for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
        if p.returncode == 0: subprocess.run(["mv", "mudo_tmp.mp4", "mudo.mp4"])
