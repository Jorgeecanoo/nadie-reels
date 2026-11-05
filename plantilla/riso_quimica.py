# Reel 2026-11-05: "Cómo funciona enamorarse" para @ssunpetal.
# Estilo fanzine risografía (papel crema, rosa flúor + azul, desregistro, grano). Sin voz.
# Uso: python3 riso_quimica.py still 1.0 | render | sfx
import math, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
TOTAL = 21.0
PAPER = (244, 236, 220); PINK = (255, 72, 168); BLUE = (0, 112, 190); INK = (34, 30, 58); YEL = (255, 214, 60)
GF = "/usr/share/fonts/truetype/google-fonts/"
def POP(s, w="Bold"): return ImageFont.truetype(GF + f"Poppins-{w}.ttf", int(s))
def INTER(s): return ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf", int(s))
_lc = {}
def LORA(s):
    s = int(s)
    if s not in _lc:
        f = ImageFont.truetype(GF + "Lora-Italic-Variable.ttf", s); f.set_variation_by_axes([700]); _lc[s] = f
    return _lc[s]

def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def back(x):
    x = max(0, min(1, x)); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- fondo: papel + grano + tramas ----------
rng = np.random.default_rng(5)
def make_paper():
    a = np.ones((H, W, 3)) * np.array(PAPER)
    a += rng.normal(0, 7, (H, W, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    # trama de puntos en esquinas (halftone)
    for (cx, cy, col, R) in ((W + 60, -40, PINK, 520), (-80, H - 260, BLUE, 560)):
        for y in range(0, H, 22):
            for x in range(0, W, 22):
                dist = math.hypot(x - cx, y - cy)
                if dist < R:
                    r = 8 * (1 - dist / R)
                    if r > 0.8: d.ellipse((x - r, y - r, x + r, y + r), fill=col)
    return im
PAPER_IM = make_paper()
GRAIN = [Image.fromarray(np.clip(rng.normal(0, 10, (H // 2, W // 2)), -30, 30).astype(np.int8).view(np.uint8)) for _ in range(4)]
GRAIN_ARR = [rng.normal(0, 6, (H, W, 1)).astype(np.int16) for _ in range(3)]

def riso_text(d, s, x, y, f, col, off=(7, 5), shadow=BLUE, anchor="mm"):
    if shadow: d.text((x + off[0], y + off[1]), s, font=f, fill=shadow, anchor=anchor)
    d.text((x, y), s, font=f, fill=col, anchor=anchor)

def wrap(s, f, maxw):
    lines, cur = [], ""
    for w_ in s.split():
        t = (cur + " " + w_).strip()
        if f.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    lines.append(cur); return lines

def para(d, s, x, y, f, col, maxw=900, lh=1.25, t=1.0, shadow=None):
    lines = wrap(s, f, maxw); hh = f.size * lh
    y0 = y - hh * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        k = ease((t - i * 0.12) * 3)
        if k <= 0: continue
        riso_text(d, ln, x, y0 + i * hh + (1 - k) * 30, f, col, shadow=shadow, off=(4, 3))

def rot_paste(base, layer, angle, cx, cy):
    r = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(r, (int(cx - r.width / 2), int(cy - r.height / 2)))

def stamp(base, text, cx, cy, size, col, angle, k):
    if k <= 0: return
    f = POP(size, "Bold"); bb = f.getbbox(text)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    L = Image.new("RGBA", (tw + 80, th + 70), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
    g.rounded_rectangle((6, 6, L.width - 6, L.height - 6), 18, outline=col, width=9)
    g.text((L.width / 2, L.height / 2), text, font=f, fill=col, anchor="mm")
    # textura gastada del sello
    a = np.array(L); m = rng.random(a.shape[:2]) < 0.10; a[m, 3] = 0; L = Image.fromarray(a)
    sc = 1 + 1.4 * (1 - ease(k * 1.6))
    L = L.resize((int(L.width * sc), int(L.height * sc)))
    rot_paste(base, L, angle, cx, cy)

def heart(d, cx, cy, s, col, off=None):
    pts = []
    for i in range(80):
        t = 2 * math.pi * i / 80
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s, cy - y * s))
    if off: d.polygon([(x + off[0], y + off[1]) for x, y in pts], fill=BLUE)
    d.polygon(pts, fill=col)

def die(d, cx, cy, s, ang):
    pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    ca, sa = math.cos(ang), math.sin(ang)
    P = [(cx + s * (x * ca - y * sa), cy + s * (x * sa + y * ca)) for x, y in pts]
    d.polygon(P, fill=PAPER, outline=INK, width=6)
    for px, py in ((-.5, -.5), (.5, .5), (0, 0), (.5, -.5), (-.5, .5)):
        X = cx + s * (px * ca - py * sa); Y = cy + s * (px * sa + py * ca)
        d.ellipse((X - 9, Y - 9, X + 9, Y + 9), fill=PINK)

def header(d, n, t):
    d.rectangle((0, 0, W, 150), fill=INK)
    d.text((60, 78), "LABORATORIO NADIE", font=POP(40, "Bold"), fill=PAPER, anchor="lm")
    d.text((W - 60, 78), f"INFORME Nº 001 · {n}/3" if n else "INFORME Nº 001", font=POP(30, "Medium"), fill=YEL, anchor="rm")
    # cinta de "tinta" bajo la cabecera
    d.rectangle((0, 150, W * min(1, t / TOTAL), 162), fill=PINK)

def chem_card(base, d, t, n, name, col, sub, line1, line2, kind):
    k = ease(t * 2.5)
    header(d, n, T_GLOBAL)
    # número gigante
    riso_text(d, str(n), 160, 330 + (1 - k) * 80, INTER(260), col, off=(12, 8), shadow=INK if col == YEL else BLUE if col == PINK else PINK)
    riso_text(d, name, W / 2 + 70, 330 + (1 - k) * 40, POP(84 if len(name) < 11 else 70, "Bold"), INK, off=(6, 5), shadow=col)
    d.text((W / 2 + 70, 420), sub, font=POP(36, "Medium"), fill=col if col != YEL else INK, anchor="mm")
    # visual
    if kind == "dopa":   # matraz que se llena
        cx, cy = W / 2, 860
        lvl = ease((t - 0.3) / 2.2)
        flask = [(cx - 70, cy - 300), (cx + 70, cy - 300), (cx + 70, cy - 120), (cx + 260, cy + 220), (cx - 260, cy + 220), (cx - 70, cy - 120)]
        top = cy + 220 - lvl * 420
        mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon(flask, fill=255)
        liq = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gl = ImageDraw.Draw(liq)
        wave_pts = [(x, top + 14 * math.sin(x / 50 + t * 6)) for x in range(int(cx - 280), int(cx + 281), 10)]
        gl.polygon(wave_pts + [(cx + 280, cy + 240), (cx - 280, cy + 240)], fill=PINK + (255,))
        for i in range(10):  # burbujas
            bx = cx - 180 + (i * 41) % 360; by = cy + 200 - ((t * 160 + i * 53) % 400)
            if by > top: gl.ellipse((bx - 10, by - 10, bx + 10, by + 10), outline=PAPER + (255,), width=4)
        base.paste(liq, (0, 0), Image.composite(liq.split()[3], Image.new("L", (W, H), 0), mask))
        d.line(flask + [flask[0]], fill=INK, width=10, joint="curve")
        d.rectangle((cx - 95, cy - 330, cx + 95, cy - 300), fill=INK)
        pct = int(lvl * 100)
        riso_text(d, f"{pct}%", cx + 300, cy - 60, POP(70, "Bold"), INK, shadow=PINK, off=(5, 4))
        d.text((cx + 300, cy + 5), "ENGANCHE", font=POP(28, "Medium"), fill=INK, anchor="mm")
    elif kind == "nora":  # corazón a mil + ECG + BPM
        bpm = 72 + (148 - 72) * ease((t - 0.2) / 2.0)
        ph = (t * bpm / 60) % 1
        beat = 1 + 0.16 * math.exp(-ph * 9)
        heart(d, W / 2, 780, 13 * beat, PINK, off=(10, 8))
        riso_text(d, f"{int(bpm)} BPM", W / 2, 1075, POP(78, "Bold"), INK, shadow=BLUE, off=(5, 4))
        # ECG
        y0 = 1190; pts = []
        for x in range(60, W - 60, 6):
            u = (x / 260 - t * bpm / 60 * 1.2) % 1
            v = 0
            if 0.40 < u < 0.44: v = -30
            elif 0.44 < u < 0.48: v = 110
            elif 0.48 < u < 0.52: v = -150
            elif 0.52 < u < 0.56: v = 40
            pts.append((x, y0 - v * 0.6))
        d.line(pts, fill=BLUE, width=8, joint="curve")
    elif kind == "sero":  # barra que baja + bucle
        lvl = 1 - 0.7 * ease((t - 0.2) / 1.8)
        bx, by, bw, bh = 150, 560, 110, 520
        d.rectangle((bx, by, bx + bw, by + bh), outline=INK, width=8)
        d.rectangle((bx + 12, by + bh - (bh - 24) * lvl - 12, bx + bw - 12, by + bh - 12), fill=BLUE)
        ax = bx + bw / 2; d.polygon([(ax - 45, by - 90), (ax + 45, by - 90), (ax + 45, by - 60), (ax + 75, by - 60), (ax, by - 10), (ax - 75, by - 60), (ax - 45, by - 60)], fill=PINK)
        # bucle giratorio de texto
        cx, cy, R = 650, 830, 230
        phrase = "no te la saco de la cabeza · " * 2
        f = POP(40, "Bold")
        n_ = len(phrase)
        for i, ch in enumerate(phrase):
            a = 2 * math.pi * i / n_ + t * 1.8
            L = Image.new("RGBA", (60, 60), (0, 0, 0, 0)); ImageDraw.Draw(L).text((30, 30), ch, font=f, fill=INK if i % 2 else PINK, anchor="mm")
            rot_paste(base, L, -math.degrees(a) - 90, cx + R * math.cos(a), cy + R * math.sin(a))
        heart(d, cx, cy + 10, 5.2, PINK, off=(5, 4))
        d.text((cx, cy + 290), "BUCLE MENTAL", font=POP(30, "Medium"), fill=BLUE, anchor="mm")
    # textos
    para(d, line1, W / 2, 1360, POP(56, "Bold"), INK, maxw=920, t=t - 0.4)
    para(d, line2, W / 2, 1520, LORA(52), BLUE if col != BLUE else PINK, maxw=900, t=t - 1.3)

T_GLOBAL = 0
def frame(t):
    global T_GLOBAL; T_GLOBAL = t
    im = PAPER_IM.copy().convert("RGBA"); d = ImageDraw.Draw(im)
    if t < 3.4:   # GANCHO
        header(d, 0, t)
        k = back(t * 3)
        riso_text(d, "@ssunpetal", W / 2, 330, POP(96 * max(0.55, k), "Bold"), PINK, off=(7, 5))
        d.text((W / 2, 430), "me ha preguntado:", font=POP(52, "Medium"), fill=INK, anchor="mm")
        k2 = ease((t - 0.25) * 3)
        if k2 > 0:
            for i, ln in enumerate(["«¿Cómo funciona", "eso de", "enamorarse?»"]):
                kk = ease((t - 0.25 - i * 0.12) * 3.5)
                riso_text(d, ln, W / 2 - (1 - kk) * 200, 640 + i * 150, LORA(118), INK, shadow=PINK, off=(8, 6))
        heart(d, W - 130, 1125 + math.sin(t * 7) * 8, 4, PINK, off=(5, 4))
        # dado del sorteo
        if t > 0.6:
            die(d, 210, 1130, 62, t * 2.5)
            d.text((300, 1130), "ha salido en el sorteo", font=POP(42, "Bold"), fill=BLUE, anchor="lm")
        stamp(im, "FÁCIL: ES QUÍMICA", W / 2, 1400, 74, PINK, 7, (t - 1.9) * 1.5)
    elif t < 7.6:
        chem_card(im, d, t - 3.4, 1, "DOPAMINA", PINK, "la del enganche",
                  "Tu cerebro se engancha a esa persona.", "Como a ese juego que no puedes soltar.", "dopa")
    elif t < 11.8:
        chem_card(im, d, t - 7.6, 2, "NORADRENALINA", BLUE, "la del susto bonito",
                  "Corazón a mil. Manos sudando.", "Hambre: cero. Sueño: poco.", "nora")
    elif t < 16.0:
        chem_card(im, d, t - 11.8, 3, "SEROTONINA", YEL, "la que BAJA",
                  "Y tu mente entra en bucle:", "no te la sacas de la cabeza.", "sero")
    elif t < 18.4:   # diagnóstico + Nadie
        u = t - 16.0
        header(d, 0, t)
        d.text((W / 2, 320), "DIAGNÓSTICO", font=POP(50, "Medium"), fill=BLUE, anchor="mm")
        riso_text(d, "Enamorarse =", W / 2, 470, LORA(104), INK, shadow=PINK, off=(7, 5))
        riso_text(d, "química + bucle", W / 2, 610, LORA(104), PINK, shadow=BLUE, off=(7, 5))
        # pantallita de Nadie guiñando
        cx, cy = W / 2, 980; k = back(u * 2.5)
        s = max(0.01, k)
        d.rounded_rectangle((cx - 230 * s, cy - 160 * s, cx + 230 * s, cy + 160 * s), int(70 * s), fill=(14, 18, 36), outline=INK, width=10)
        wink = 0.6 < u < 1.2
        for sx in (-1, 1):
            ex = cx + sx * 90 * s
            if wink and sx == 1: d.line((ex - 40 * s, cy - 10, ex + 40 * s, cy - 10), fill=(90, 240, 220), width=int(16 * s))
            else: d.rounded_rectangle((ex - 34 * s, cy - 70 * s, ex + 34 * s, cy + 40 * s), int(30 * s), fill=(90, 240, 220))
        d.arc((cx - 70 * s, cy + 20 * s, cx + 70 * s, cy + 110 * s), 20, 160, fill=(90, 240, 220), width=int(12 * s))
        para(d, "Yo eso no lo sufro.", W / 2, 1260, POP(64, "Bold"), INK, t=u - 0.4)
        para(d, "Ventajas de ser IA.", W / 2, 1370, LORA(70), PINK, t=u - 0.9, shadow=BLUE)
    else:   # CIERRE: mecánica
        u = t - 18.4
        header(d, 0, t)
        riso_text(d, "¿Quieres ser", W / 2, 330, LORA(100), INK, shadow=PINK, off=(7, 5))
        riso_text(d, "el próximo?", W / 2, 460, LORA(100), INK, shadow=PINK, off=(7, 5))
        rows = [("1", "Sígueme", PINK), ("2", "Comenta", BLUE), ("3", "10:00 · sorteo 1 comentario", INK), ("4", "13:30 · sale su vídeo", PINK)]
        for i, (n, s, c) in enumerate(rows):
            kk = ease((u - 0.15 * i) * 3)
            if kk <= 0: continue
            y = 660 + i * 170; x0 = 110 - (1 - kk) * 300
            d.ellipse((x0, y - 55, x0 + 110, y + 55), fill=c)
            d.text((x0 + 55, y), n, font=POP(64, "Bold"), fill=PAPER, anchor="mm")
            d.text((x0 + 150, y), s, font=POP(60 if len(s) < 14 else 48, "Bold"), fill=INK, anchor="lm")
        stamp(im, "SOLO SEGUIDORES", W / 2, 1420, 66, PINK, -6, (u - 0.8) * 1.5)
    # grano animado (efecto impresión)
    a = np.array(im.convert("RGB")).astype(np.int16) + GRAIN_ARR[int(t * 12) % 3]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ---------- sonido: base lo-fi + efectos, todo por código ----------
def sfx():
    SR = 44100; n = int(SR * TOTAL); tr = np.zeros(n); r = np.random.default_rng(3)
    def add(t0, s, g=1.0):
        i = int(SR * t0); j = min(n, i + len(s))
        if i < n: tr[i:j] += s[:j - i] * g
    def env(m, a, d): tt = np.arange(m) / SR; return np.minimum(1, tt / a) * np.exp(-tt / d)
    def kick():
        m = int(SR * .35); tt = np.arange(m) / SR; f = 50 + 90 * np.exp(-tt * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(m, .002, .12)
    def hat(): m = int(SR * .05); return r.standard_normal(m) * env(m, .001, .012) * .25
    def pluck(f, d=.6):
        m = int(SR * d); tt = np.arange(m) / SR
        return (np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt)) * env(m, .004, .18) * .22
    def pop(f0, f1, d=.09):
        m = int(SR * d); tt = np.arange(m) / SR; f = f0 + (f1 - f0) * tt / d
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(m, .002, d / 3) * .5
    def thud():
        m = int(SR * .25); tt = np.arange(m) / SR
        return np.sin(2 * np.pi * (45 + 40 * np.exp(-tt * 25)) * tt) * env(m, .003, .07)
    bpm = 96; b = 60 / bpm
    chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
    k = 0; t0 = 0.0
    while t0 < TOTAL - 0.3:
        beat = k % 4
        if not (7.6 <= t0 < 11.8): add(t0, kick(), .55 if beat in (0, 2) else .0)
        add(t0 + b / 2, hat(), 1); add(t0, hat(), .5)
        ch = chords[(k // 4) % 4]
        add(t0, pluck(ch[beat % 3] * (2 if beat == 3 else 1)), 1)
        add(t0 + b * .75, pluck(ch[(beat + 1) % 3] * 2, .3), .5)
        k += 1; t0 += b
    # latidos acelerando en la tarjeta 2
    t1 = 7.8
    while t1 < 11.7:
        u = (t1 - 7.6); bp = 72 + 76 * min(1, u / 2.2); add(t1, thud(), .9); add(t1 + .18 * 60 / bp, thud(), .6); t1 += 60 / bp
    for tt in (0.0, 0.3, 0.45, 0.6): add(tt, pop(500, 1300), .6)
    add(1.95, thud(), 1.2); add(1.95, pop(300, 120, .15), .8)          # sello
    for tt in (3.4, 7.6, 11.8, 16.0, 18.4): add(tt, pop(400, 1400, .12), .7)
    for i in range(12): add(3.8 + i * .18, pop(900 + i * 60, 1500 + i * 60, .05), .25)  # burbujas
    add(16.6, pop(1200, 1800, .07), .6)                                   # guiño
    for i in range(4): add(18.55 + i * .15, pop(600 + i * 150, 1200 + i * 150), .5)
    add(19.25, thud(), 1.0)
    fade = np.ones(n); m = int(SR * .8); fade[-m:] = np.linspace(1, 0, m)
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
                              "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium", "mudo.mp4"], stdin=subprocess.PIPE)
        for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
