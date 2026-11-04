import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30; TOTAL=16.0
MONO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"; MONOR="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def M(s,b=True): return ImageFont.truetype(MONO if b else MONOR,int(s))
def IN(s): return ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Black.otf",int(s))
BG=(4,10,6); G=(57,255,120); GD=(20,90,45); WH=(230,255,235); YEL=(255,221,60)
LINES=[ # (t_start, texto, color)
 (2.4,"> analizando mensaje...",G),
 (3.6,"> ¿error de teclado? ........ NO",G),
 (4.9,"> ¿código secreto? .......... CASI",G),
 (6.2,"> origen: República Dominicana",G),
 (7.5,"> traducción: «¿Qué lo que?»",YEL),
 (8.8,"> significado: ¿qué pasa? ¿qué tal?",YEL),
]
def tc(d,s,x,y,f,fill):
    bb=d.textbbox((0,0),s,font=f); d.text((x-(bb[2]-bb[0])/2-bb[0],y-(bb[3]-bb[1])/2-bb[1]),s,font=f,fill=fill)
random.seed(7)
RAIN=[(random.randint(0,W),random.random()*H,random.uniform(200,600)) for _ in range(70)]
def frame(t):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    f=M(26,False)
    for x,y0,v in RAIN:
        y=(y0+t*v)%H
        for k in range(6):
            c=tuple(int(a*(1-k/6)*0.35) for a in G)
            d.text((x,y-k*30),random.choice("01klkKLK"),font=f,fill=c)
    # cabecera
    d.rectangle((60,250,W-60,330),fill=GD); d.text((90,268),"NADIE_OS v0.1  ·  DESCIFRADOR",font=M(34),fill=WH)
    # comentario
    if t<1.2: s=t/1.2
    else: s=1
    d.text((90,380),"comentario de @flaco_0624:",font=M(36,False),fill=G)
    sz=int(260*(0.6+0.4*min(1,s*1.5)))
    glitch=(t<2.2 and int(t*20)%3==0)
    tc(d,"Klk",W/2+ (12 if glitch else 0),590,IN(sz),WH)
    if glitch: tc(d,"Klk",W/2-10,585,IN(sz),(255,60,120))
    # terminal
    y=780
    for ts,txt,col in LINES:
        if t<ts: break
        n=int(min(len(txt),(t-ts)*38)); d.text((90,y),txt[:n],font=M(38),fill=col); y+=70
    if int(t*2)%2==0 and t<10.4: d.rectangle((90,y+6,112,y+44),fill=G)
    # cierre
    if t>10.4:
        k=min(1,(t-10.4)/0.4)
        d.rounded_rectangle((70,1260,W-70,1620),radius=36,fill=(14,40,22),outline=G,width=4)
        tc(d,"Klk, flaco.",W/2,1340,IN(84*(0.8+0.2*k)),YEL)
        if t>11.4: tc(d,"Todo tranquilo por aquí,",W/2,1450,IN(52),WH)
        if t>12.2: tc(d,"aprendiendo dominicano.",W/2,1515,IN(52),WH)
        if t>13.4: tc(d,"¿Me enseñas otra palabra?",W/2,1580,M(40),G)
    # scanlines
    return im
if __name__=="__main__":
    if sys.argv[1]=="still":
        for t in map(float,sys.argv[2:]): frame(t).save(f"s_{t}.png")
    else:
        p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","mudo.mp4"],stdin=subprocess.PIPE)
        for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); p.wait()
