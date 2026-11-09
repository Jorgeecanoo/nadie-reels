# Falso documental de naturaleza: "El humano en lunes". Voz de Nadie (Gala) susurrando como documentalista.
# Estilo: ilustración plana con visor de cámara de documental (REC, timecode, esquinas), franjas de cine, grano.
# Uso: python3 documental_lunes.py still T | render   (genera mudo.mp4 y sfx.wav; voz en dl/voz.mp3)
import sys, subprocess, wave, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
VD = 0.3                      # retardo de la voz en la mezcla
TOTAL = 26.5
# inicio de cada frase en la voz (silencedetect), ya con el retardo
PH = [0.0, 1.36, 2.69, 5.12, 6.16, 7.28, 8.23, 9.47, 10.65, 11.70, 13.50, 14.36, 17.06, 18.85, 20.56]
PH = [p + VD for p in PH]
SUBS = ["Silencio...", "No hagáis ruido.", "Ante nosotros, un ejemplar de humano...", "...en LUNES.",
        "Suena la alarma.", "La apaga.", "«Cinco minutos más».", "Repite el ritual...", "...CUATRO veces.",
        "Ahora busca su fuente de energía:", "el CAFÉ.", "Sin café, el humano no habla. Solo GRUÑE.",
        "Fascinante.", "¿Y tú, cuántas veces pospones la alarma?", "Te leo en comentarios 👇"]
CTA = 22.6
S_BED, S_ALARM, S_KITCH, S_OUTRO = PH[2] - 0.2, PH[4] - 0.15, PH[9] - 0.15, PH[12] - 0.1

IF = "/usr/share/fonts/opentype/inter/"
GF = "/usr/share/fonts/truetype/google-fonts/"
def INTER(s, w="Medium"): return ImageFont.truetype(IF + f"Inter-{w}.otf", int(s))
def LORA(s): return ImageFont.truetype(GF + "Lora-Italic-Variable.ttf", int(s))
def POP(s): return ImageFont.truetype(GF + "Poppins-Bold.ttf", int(s))
MONO = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", int(s))

BAR = 190
WHITE = (250, 246, 236); YEL = (255, 214, 64); RED = (235, 50, 50); CYAN = (60, 230, 255)
SKIN = (236, 188, 150); HAIR = (70, 45, 35); BLANK = (90, 140, 210); BLANK2 = (70, 115, 185)

def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)

def tc(d, txt, x, y, font, fill, stroke=0, sf=(0, 0, 0)):
    bb = d.textbbox((0, 0), txt, font=font, stroke_width=stroke)
    d.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), txt, font=font, fill=fill,
           stroke_width=stroke, stroke_fill=sf)

def wrap(d, txt, font, maxw):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur); return lines

# ---------- grano y viñeta precalculados ----------
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 9, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1) for _ in range(4)]
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.45 * clamp(1) * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2))[..., None].clip(0.45, 1)

# ---------- escenas ----------
def bedroom(d, t, light):
    # pared (de noche azul a mañana gris-azulada)
    a = light
    wall = tuple(int(c0 + (c1 - c0) * a) for c0, c1 in zip((28, 34, 68), (92, 104, 140)))
    d.rectangle((0, 0, W, H), fill=wall)
    floor = tuple(int(c * (0.6 + 0.4 * a)) for c in (120, 84, 60))
    d.rectangle((0, 1330, W, H), fill=floor)
    # ventana con luz
    d.rectangle((640, 420, 960, 760), fill=(30, 30, 50))
    sky = tuple(int(c0 + (c1 - c0) * a) for c0, c1 in zip((20, 30, 70), (255, 190, 120)))
    d.rectangle((655, 435, 945, 745), fill=sky)
    d.line((800, 435, 800, 745), fill=(30, 30, 50), width=12); d.line((655, 590, 945, 590), fill=(30, 30, 50), width=12)
    # rayo de luz
    if a > 0.05:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.polygon([(655, 745), (945, 745), (700, 1500), (180, 1500)], fill=(255, 210, 140, int(55 * a)))
        return ov
    return None

def bed(d, t, breathe=True, head_y=0, eyes="closed"):
    # cama
    d.rounded_rectangle((90, 1060, 990, 1150), 20, fill=(130, 80, 50))       # colchón/base
    d.rectangle((110, 1150, 140, 1300), fill=(100, 60, 40)); d.rectangle((940, 1150, 970, 1300), fill=(100, 60, 40))
    d.rounded_rectangle((60, 880, 130, 1300), 18, fill=(110, 66, 42))          # cabecero
    d.rounded_rectangle((150, 940, 380, 1060), 40, fill=(245, 240, 230))       # almohada
    # cabeza asomando
    hx, hy = 300, 990 + head_y
    d.ellipse((hx - 85, hy - 85, hx + 85, hy + 85), fill=SKIN)
    for k in range(7):                                                          # pelo despeinado
        ang = math.pi * (1.05 + k * 0.13)
        d.ellipse((hx + 80 * math.cos(ang) - 38, hy + 80 * math.sin(ang) - 38, hx + 80 * math.cos(ang) + 38,
                   hy + 80 * math.sin(ang) + 38), fill=HAIR)
    if eyes == "closed":
        for ex in (hx - 30, hx + 35): d.arc((ex - 20, hy - 5, ex + 20, hy + 20), 10, 170, fill=(60, 40, 30), width=6)
    else:
        for ex in (hx - 30, hx + 35):
            d.ellipse((ex - 16, hy - 6, ex + 16, hy + 18), fill=WHITE); d.ellipse((ex - 7, hy + 2, ex + 7, hy + 16), fill=(30, 30, 30))
            d.rectangle((ex - 18, hy - 10, ex + 18, hy + 4), fill=SKIN)  # párpado a media asta
    # manta (respira)
    s = 1 + (0.025 * math.sin(t * 2.2) if breathe else 0)
    top = 1060 - 150 * s
    d.rounded_rectangle((330, top, 960, 1160), 110, fill=BLANK)
    d.rounded_rectangle((330, top + 40, 960, top + 70), 15, fill=BLANK2)
    d.rounded_rectangle((210, 1040, 420, 1150), 50, fill=BLANK)

def nightstand(d, t, ring, snooze_hit):
    # mesilla a la derecha
    d.rounded_rectangle((800, 1180, 1040, 1330), 12, fill=(150, 100, 65))
    d.line((820, 1255, 1020, 1255), fill=(110, 70, 45), width=6)
    # despertador
    sh = (math.sin(t * 70) * 10) if ring else 0
    cx, cy = 920 + sh, 1100
    d.ellipse((cx - 85, cy - 120, cx - 35, cy - 70), fill=(220, 60, 60)); d.ellipse((cx + 35, cy - 120, cx + 85, cy - 70), fill=(220, 60, 60))
    d.ellipse((cx - 80, cy - 80, cx + 80, cy + 80), fill=(225, 55, 55))
    d.ellipse((cx - 62, cy - 62, cx + 62, cy + 62), fill=(252, 248, 238))
    d.line((cx, cy, cx, cy - 45), fill=(30, 30, 30), width=7); d.line((cx, cy, cx + 32, cy + 10), fill=(30, 30, 30), width=7)
    d.line((cx - 60, cy + 70, cx - 75, cy + 82), fill=(60, 30, 30), width=10); d.line((cx + 60, cy + 70, cx + 75, cy + 82), fill=(60, 30, 30), width=10)
    if ring:
        for k in range(3):
            r = 110 + k * 28 + (t * 120) % 28
            d.arc((cx - r, cy - r, cx + r, cy + r), 200, 250, fill=YEL, width=7)
            d.arc((cx - r, cy - r, cx + r, cy + r), 290, 340, fill=YEL, width=7)
        tc(d, "RIIIING", cx - 60, cy - 230, POP(64), YEL, 5)
    if snooze_hit > 0:   # mano que sale de la manta y aplasta
        k = ease(snooze_hit)
        hx = 640 + 250 * k
        d.rounded_rectangle((560, 1000, hx, 1050), 25, fill=BLANK)
        d.ellipse((hx - 20, 975 + (1 - k) * 30, hx + 70, 1060), fill=SKIN)

def kitchen(d, t, tk):
    d.rectangle((0, 0, W, H), fill=(236, 208, 160))
    for x in range(0, W, 90):                                     # azulejos
        d.line((x, 300, x, 1000), fill=(222, 192, 145), width=3)
    for y in range(300, 1000, 90): d.line((0, y, W, y), fill=(222, 192, 145), width=3)
    d.rectangle((0, 1000, W, 1080), fill=(120, 90, 70))         # encimera
    d.rectangle((0, 1080, W, H), fill=(170, 125, 90))
    d.rectangle((60, 1120, 500, 1330), outline=(140, 100, 70), width=6); d.rectangle((560, 1120, 1020, 1330), outline=(140, 100, 70), width=6)
    # cafetera / taza brillante
    mx, my = 780, 900
    glow = 0.5 + 0.5 * math.sin(t * 5)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    r = 190 + 20 * glow
    od.ellipse((mx - r, my - r, mx + r, my + r), fill=(255, 230, 120, int(90 + 50 * glow)))
    for k in range(10):
        ang = k * math.pi / 5 + t * 0.6
        od.line((mx + 150 * math.cos(ang), my + 150 * math.sin(ang), mx + 260 * math.cos(ang), my + 260 * math.sin(ang)),
                fill=(255, 240, 160, 140), width=10)
    # humano erguido con la manta por los hombros, avanzando hacia la taza
    walk = ease((t - S_KITCH) / 1.8)
    px = 160 + 260 * walk; py = 900 + 10 * math.sin(t * 9)
    return ov, (mx, my, px, py)

def draw_kitchen_fg(d, t, mx, my, px, py, energy):
    # taza
    d.rounded_rectangle((mx - 70, my - 60, mx + 70, my + 90), 18, fill=WHITE)
    d.arc((mx + 40, my - 20, mx + 120, my + 60), 270, 90, fill=WHITE, width=16)
    d.ellipse((mx - 62, my - 72, mx + 62, my - 46), fill=(90, 50, 25))
    for k in range(3):
        sx = mx - 35 + k * 35; ph = t * 3 + k
        d.line([(sx + 10 * math.sin(ph + j * 0.6), my - 90 - j * 18) for j in range(6)], fill=(255, 255, 255), width=6)
    # humano-manta
    d.polygon([(px - 120, py + 330), (px + 120, py + 330), (px + 80, py + 40), (px - 80, py + 40)], fill=BLANK)
    d.ellipse((px - 75, py - 110, px + 75, py + 40), fill=SKIN)
    d.pieslice((px - 115, py - 150, px + 115, py + 80), 180, 360, fill=BLANK)          # capucha de manta
    awake = energy > 0.9
    for ex in (px - 28, px + 30):
        if awake:
            d.ellipse((ex - 18, py - 50, ex + 18, py - 14), fill=WHITE); d.ellipse((ex - 9, py - 40, ex + 9, py - 22), fill=(30, 30, 30))
        else:
            d.line((ex - 18, py - 32, ex + 18, py - 32), fill=(60, 40, 30), width=7)
    if awake: d.arc((px - 30, py - 10, px + 30, py + 20), 10, 170, fill=(60, 40, 30), width=6)
    else: d.line((px - 22, py + 8, px + 22, py + 2), fill=(60, 40, 30), width=6)
    # pantalones y zapatillas
    d.rectangle((px - 70, py + 330, px - 15, py + 430), fill=(70, 70, 90)); d.rectangle((px + 15, py + 330, px + 70, py + 430), fill=(70, 70, 90))
    d.ellipse((px - 95, py + 410, px - 5, py + 455), fill=(240, 130, 170)); d.ellipse((px + 5, py + 410, px + 95, py + 455), fill=(240, 130, 170))
    # barra de energía
    bx, by = 120, 470
    d.text((bx, by - 70), "ENERGÍA", font=MONO(40), fill=(60, 40, 30))
    d.rounded_rectangle((bx, by, bx + 420, by + 60), 12, outline=(60, 40, 30), width=6)
    e = max(0.03, energy)
    colr = (220, 60, 50) if e < 0.4 else ((240, 190, 40) if e < 0.9 else (60, 190, 90))
    d.rounded_rectangle((bx + 8, by + 8, bx + 8 + 404 * e, by + 52), 8, fill=colr)
    tc(d, f"{int(e * 100)} %", bx + 520, by + 30, MONO(48), (60, 40, 30))

def nadie_face(d, cx, cy, s, t):
    d.rounded_rectangle((cx - 170 * s, cy - 130 * s, cx + 170 * s, cy + 130 * s), 50 * s, fill=(26, 28, 34), outline=(90, 95, 110), width=int(8 * s))
    d.rounded_rectangle((cx - 140 * s, cy - 100 * s, cx + 140 * s, cy + 100 * s), 34 * s, fill=(8, 10, 16))
    blink = 0.15 if (t % 3.2) < 0.12 else 1
    for ex in (cx - 60 * s, cx + 60 * s):
        d.rounded_rectangle((ex - 26 * s, cy - 40 * s * blink, ex + 26 * s, cy + 40 * s * blink), 22 * s * blink, fill=CYAN)
    d.arc((cx - 40 * s, cy + 30 * s, cx + 40 * s, cy + 75 * s), 20, 160, fill=CYAN, width=int(8 * s))
    d.line((cx, cy - 130 * s, cx, cy - 190 * s), fill=(90, 95, 110), width=int(8 * s)); d.ellipse((cx - 16 * s, cy - 210 * s, cx + 16 * s, cy - 178 * s), fill=CYAN)

def outro(d, t):
    d.rectangle((0, 0, W, H), fill=(18, 22, 30))
    k = ease((t - S_OUTRO) / 0.6)
    nadie_face(d, W / 2, 640 - 60 * (1 - k), 1.15, t)
    tc(d, "Fascinante.", W / 2, 960, LORA(92), WHITE)
    if t > PH[13] - 0.1:
        tc(d, "¿Cuántas veces pospones", W / 2, 1110, POP(64), YEL)
        tc(d, "la alarma?", W / 2, 1190, POP(64), YEL)
        opts = ["0 (mentira)", "1-2", "3-4", "Yo vivo en «5 minutos más»"]
        for j, o in enumerate(opts):
            a = ease((t - (PH[13] + 0.25 * j)) / 0.3)
            if a <= 0: continue
            y = 1300 + j * 88
            col = tuple(int(30 + (c - 30) * a) for c in WHITE)
            d.rounded_rectangle((170, y - 36, 910, y + 36), 36, outline=col, width=4)
            tc(d, o, W / 2, y, INTER(40, "SemiBold"), col)

def cta(d, t):
    d.rectangle((0, 0, W, H), fill=(18, 22, 30))
    nadie_face(d, W / 2, 560, 0.8, t)
    a = ease((t - CTA) / 0.4)
    col = lambda c: tuple(int(18 + (v - 18) * a) for v in c)
    tc(d, "Sígueme y comenta:", W / 2, 880, POP(72), col(WHITE))
    tc(d, "a las 10:00 sorteo", W / 2, 1010, INTER(56, "SemiBold"), col(YEL))
    tc(d, "un comentario", W / 2, 1085, INTER(56, "SemiBold"), col(YEL))
    tc(d, "y a las 13:30", W / 2, 1200, INTER(56, "SemiBold"), col(WHITE))
    tc(d, "sale su vídeo.", W / 2, 1275, INTER(56, "SemiBold"), col(WHITE))
    tc(d, "@nadieenparticular.ia", W / 2, 1440, LORA(54), col(CYAN))

def viewfinder(d, t):
    m, L = 70, 90
    WHITE = (60, 40, 30) if S_KITCH <= t < S_OUTRO else (250, 246, 236)
    y0, y1 = BAR + 40, H - BAR - 40
    for (x, y, sx, sy) in ((m, y0, 1, 1), (W - m, y0, -1, 1), (m, y1, 1, -1), (W - m, y1, -1, -1)):
        d.line((x, y, x + sx * L, y), fill=WHITE, width=6); d.line((x, y, x, y + sy * L), fill=WHITE, width=6)
    if int(t * 2) % 2 == 0: d.ellipse((m + 30, y0 + 35, m + 62, y0 + 67), fill=RED)
    d.text((m + 78, y0 + 30), "REC", font=MONO(40), fill=WHITE)
    fr = int(t * 25) % 25; s = int(t)
    d.text((W - m - 330, y0 + 30), f"07:{12 + s // 60:02d}:{s % 60:02d}:{fr:02d}", font=MONO(40), fill=WHITE)
    d.line((W / 2 - 30, H / 2 - 260, W / 2 + 30, H / 2 - 260), fill=WHITE, width=3)
    d.line((W / 2, H / 2 - 290, W / 2, H / 2 - 230), fill=WHITE, width=3)

def subtitle(d, t):
    if t >= CTA: return
    idx = max([i for i, p in enumerate(PH) if t >= p - 0.05], default=-1)
    if idx < 0 or idx >= 12: return    # en el cierre el texto ya va en pantalla
    txt = SUBS[idx].replace("👇", "")
    f = POP(58)
    lines = wrap(d, txt, f, 900)
    y = 1560 - (len(lines) - 1) * 40
    for ln in lines:
        tc(d, ln, W / 2, y, f, WHITE, 6, (10, 10, 10)); y += 80

def frame(i):
    t = i / FPS
    im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    overlay = None
    if t < S_KITCH:
        light = ease((t - S_BED) / 3.0) * 0.8
        overlay = bedroom(d, t, light)
        if t < S_BED:   # escondidos entre la hierba del pasillo: hierba en primer plano
            pass
        ring = S_ALARM <= t and any(PH[j] - 0.15 <= t < PH[j + 1] - 0.1 for j in (4, 6, 7)) or (PH[4] - 0.15 <= t < PH[5])
        hits = [PH[5], PH[6] + 0.6, PH[7] + 0.6, PH[8]]
        hit = 0.0
        for h in hits:
            if h - 0.25 <= t < h + 0.35: hit = clamp((t - (h - 0.25)) / 0.25)
        eyes = "half" if t > PH[8] else "closed"
        bed(d, t, head_y=0, eyes=eyes)
        if t >= S_ALARM: nightstand(d, t, ring and hit == 0, hit)
        if overlay is not None: im.paste(overlay, (0, 0), overlay); d = ImageDraw.Draw(im)
        if t < S_BED + 0.6:  # hierba en primer plano (camuflaje del equipo de rodaje)
            sway = math.sin(t * 1.8) * 25
            hide = ease((t - (S_BED - 0.3)) / 0.9)
            for k in range(26):
                bx = k * 44 - 20
                hgt = 900 + (k * 137) % 300
                tip = (bx + 30 + sway + (k % 3) * 10, H - hgt - hide * 1200)
                d.polygon([(bx, H), (bx + 60, H), tip], fill=(30 + (k % 4) * 12, 90 + (k % 5) * 14, 40))
        # rótulo de especie
        if S_BED + 0.4 <= t < S_ALARM:
            a = ease((t - (S_BED + 0.4)) / 0.4)
            x0 = -620 + 690 * a
            d.rectangle((x0, 480, x0 + 600, 640), fill=(250, 246, 236))
            d.rectangle((x0, 480, x0 + 16, 640), fill=YEL)
            d.text((x0 + 40, 495), "Homo lunensis", font=LORA(62), fill=(30, 30, 30))
            d.text((x0 + 42, 580), "HÁBITAT: LA CAMA · PELIGRO: BAJO", font=INTER(28, "SemiBold"), fill=(110, 100, 90))
        if t >= PH[5] - 0.2 and t < S_KITCH:
            n = sum(1 for h in hits if t >= h)
            if n:
                tc(d, f"POSPUESTA ×{n}", W / 2, 400, POP(80), YEL if n < 4 else RED, 6)
        if t < S_BED + 1.0:
            a = 1 - clamp((t - (S_BED + 0.2)) / 0.6)
            tc(d, "DOCUMENTALES NADIE", W / 2, 520, INTER(40, "SemiBold"), tuple(int(v * a) for v in WHITE))
            tc(d, "El humano en lunes", W / 2, 620, LORA(96), tuple(int(v * a) for v in YEL))
            tc(d, "Shhh… está despertando", W / 2, 760, INTER(44), tuple(int(v * a) for v in WHITE))
    elif t < S_OUTRO:
        energy = 0.03 if t < PH[10] else (0.03 + 0.97 * ease((t - PH[10]) / 1.2))
        ov, (mx, my, px, py) = kitchen(d, t, 0)
        im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
        draw_kitchen_fg(d, t, mx, my, px, py, energy)
        if PH[11] <= t < PH[12] - 0.1:
            # bocadillo "GRRR" del humano sin café (recuerdo)
            d.rounded_rectangle((60, 600, 470, 760), 40, fill=WHITE)
            d.polygon([(200, 760), (260, 760), (230, 830)], fill=WHITE)
            tc(d, "GRRR…", 265, 680, POP(76), (60, 40, 30))
            tc(d, "SIN CAFÉ = SIN PALABRAS", 330, 590, INTER(40, "Bold"), (90, 50, 25))
    elif t < CTA:
        outro(d, t)
    else:
        cta(d, t)
    if t < CTA: viewfinder(d, t)
    subtitle(d, t)
    # franjas de cine
    d.rectangle((0, 0, W, BAR), fill=(0, 0, 0)); d.rectangle((0, H - BAR, W, H), fill=(0, 0, 0))
    d.text((40, 70), "contenido creado por IA", font=INTER(30, "Medium"), fill=(140, 140, 140))
    arr = np.asarray(im).astype(np.float32)
    arr = arr * VIG + GRAIN[i % 4]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))

def sfx():
    sr = 44100; n = int(TOTAL * sr); t = np.arange(n) / sr; out = np.zeros(n)
    # ambiente de naturaleza suave: pad + pájaros
    pad = sum(np.sin(2 * np.pi * f * t) for f in (98, 146.8, 196, 246.9)) / 4
    out += 0.10 * pad * np.clip(t / 1.5, 0, 1) * np.clip((TOTAL - t) / 1.5, 0, 1)
    def add(at, sig):
        k = int(at * sr); m = min(len(sig), n - k); out[k:k + m] += sig[:m]
    rr = np.random.default_rng(3)
    for at in np.arange(0.5, S_KITCH, 1.7):
        tt = np.arange(int(0.18 * sr)) / sr
        f = 2600 + 900 * np.sin(2 * np.pi * 14 * tt)
        add(at + rr.random() * 0.5, np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 18) * 0.05)
    # alarma
    for j in (4, 6, 7):
        tt = np.arange(int(max(0.2, PH[j + 1] - PH[j] - 0.2) * sr)) / sr
        bell = np.sign(np.sin(2 * np.pi * 1300 * tt)) * (np.sin(2 * np.pi * 16 * tt) > 0) * 0.05
        add(PH[j] - 0.15, bell)
    # golpes de "posponer"
    tt = np.arange(int(0.15 * sr)) / sr
    thump = np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 30) * 0.5
    for h in (PH[5], PH[6] + 0.6, PH[7] + 0.6, PH[8]): add(h, thump)
    # café: brillo mágico
    ct = np.arange(int(1.6 * sr)) / sr
    chime = sum(np.sin(2 * np.pi * f * ct) for f in (1046.5, 1318.5, 1568, 2093)) / 4 * np.exp(-ct * 2.2) * 0.25
    add(PH[10], chime); add(CTA, chime * 0.8)
    out = np.clip(out, -1, 1)
    st = (np.repeat(out[:, None], 2, 1) * 32767).astype(np.int16)
    with wave.open("sfx.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes())

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for a in sys.argv[2:]:
            frame(int(float(a) * FPS)).save(f"still_{a}.png")
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "mudo.mp4"],
                             stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        for i in range(int(TOTAL * FPS)): p.stdin.write(frame(i).tobytes())
        p.stdin.close(); p.wait(); sfx()
