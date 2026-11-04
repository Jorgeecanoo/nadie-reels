import math, random, subprocess, wave, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H,FPS=1080,1920,30; TOTAL=12.0
FD="/usr/share/fonts/opentype/inter/"
def F(s,w="Black"): return ImageFont.truetype(FD+f"Inter-{w}.otf",int(s))
YEL=(255,221,60); INK=(17,17,17); WHITE=(255,255,255); G1=(46,140,72); G2=(38,124,62)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def clamp(x): return max(0,min(1,x))
def tc(d,s,x,y,size,fill=WHITE,w="Black",stroke=10,sc=INK):
    f=F(size,w); bb=d.textbbox((0,0),s,font=f,stroke_width=stroke)
    d.text((x-(bb[2]-bb[0])/2-bb[0],y-(bb[3]-bb[1])/2-bb[1]),s,font=f,fill=fill,stroke_width=stroke,stroke_fill=sc)
def pitch():
    im=Image.new("RGB",(W,H),G1); d=ImageDraw.Draw(im)
    for i in range(0,H,160):
        if (i//160)%2: d.rectangle((0,i,W,i+160),fill=G2)
    L=(235,245,235)
    d.rectangle((60,180,W-60,H-180),outline=L,width=8)
    d.line((60,H//2,W-60,H//2),fill=L,width=8)
    d.ellipse((W//2-170,H//2-170,W//2+170,H//2+170),outline=L,width=8)
    d.rectangle((260,180,W-260,520),outline=L,width=8)
    d.rectangle((390,180,W-390,320),outline=L,width=8)
    # portería arriba
    d.rectangle((400,110,W-400,190),outline=WHITE,width=10)
    for x in range(410,W-400,26): d.line((x,115,x,185),fill=(210,220,210),width=2)
    return im
BASE=pitch()
def ball(d,x,y,r,rot):
    d.ellipse((x-r,y-r,x+r,y+r),fill=WHITE,outline=INK,width=5)
    for k in range(5):
        a=rot+k*2*math.pi/5; px,py=x+r*0.55*math.cos(a),y+r*0.55*math.sin(a)
        pts=[(px+r*0.22*math.cos(a+j*2*math.pi/5),py+r*0.22*math.sin(a+j*2*math.pi/5)) for j in range(5)]
        d.polygon(pts,fill=INK)
    pts=[(x+r*0.25*math.cos(rot+j*2*math.pi/5+math.pi/5),y+r*0.25*math.sin(rot+j*2*math.pi/5+math.pi/5)) for j in range(5)]
    d.polygon(pts,fill=INK)
def nadie(d,cx,cy,r,mood):
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=YEL,outline=INK,width=8)
    fr=r*0.78; d.ellipse((cx-fr,cy-fr,cx+fr,cy+fr),fill=INK)
    s=r/330
    if mood=="wink":
        d.rounded_rectangle((cx-170*s,cy-130*s,cx-90*s,cy+10*s),radius=30*s,fill=WHITE)
        d.rounded_rectangle((cx+90*s,cy-50*s,cx+190*s,cy-20*s),radius=15*s,fill=WHITE)
        d.rounded_rectangle((cx-60*s,cy+120*s,cx+60*s,cy+150*s),radius=12*s,fill=YEL)
    elif mood=="focus":
        for sx in (-1,1): d.rounded_rectangle((cx+sx*130*s-50*s,cy-60*s,cx+sx*130*s+50*s,cy-25*s),radius=15*s,fill=WHITE)
        d.rounded_rectangle((cx-40*s,cy+120*s,cx+40*s,cy+145*s),radius=12*s,fill=YEL)
    else: # happy
        for sx in (-1,1): d.ellipse((cx+sx*130*s-50*s,cy-110*s,cx+sx*130*s+50*s,cy-10*s),fill=WHITE)
        d.pieslice((cx-110*s,cy+30*s,cx+110*s,cy+230*s),0,180,fill=YEL)
KICK=5.2; GOAL=6.3
def frame(t):
    im=BASE.copy(); d=ImageDraw.Draw(im)
    # ---- ESCENA 1 (0-2.6): regalo
    if t<2.6:
        ov=Image.new("RGBA",(W,H),(17,17,17,215)); im.paste(ov,(0,0),ov); d=ImageDraw.Draw(im)
        p=ease(t/0.5); 
        tc(d,"🎁" if False else "REGALO",W/2,560,150*(0.6+0.4*p),fill=YEL,stroke=0)
        if t>0.5: tc(d,"para",W/2,760,90,stroke=0,w="Bold")
        if t>0.9:
            q=ease((t-0.9)/0.4); tc(d,"@gstarr_4.7",W/2,900,120*(0.7+0.3*q),fill=WHITE,stroke=0)
        if t>1.5: tc(d,"Primer seguidor.",W/2,1140,72,fill=(200,200,200),w="Bold",stroke=0); tc(d,"Primer comentario.",W/2,1230,72,fill=(200,200,200),w="Bold",stroke=0)
        return im
    # ---- ESCENA 2 (2.6-5.2): "me pediste fútbol"
    by=1450; bx=W/2
    nx,ny=W/2,1680
    if t<KICK:
        tc(d,"Me pediste",W/2,640,100); tc(d,"FÚTBOL.",W/2,770,150,fill=YEL)
        if t>3.6: tc(d,"Lo he estudiado",W/2,960,80,w="Bold",stroke=8); tc(d,"3 segundos.",W/2,1050,80,w="Bold",stroke=8)
        ball(d,bx,by+math.sin(t*6)*6,70,t*0.5)
        nadie(d,nx,ny-max(0,(t-4.6))*80,120,"focus")
        if t>4.6: tc(d,"...",W/2,1180,120,stroke=8)
        return im
    # ---- ESCENA 3: chut y gol
    p=clamp((t-KICK)/(GOAL-KICK)); e=p*p*(3-2*p)
    gx,gy=W/2+60,150
    cx=bx+(gx-bx)*e+math.sin(e*math.pi)*220   # efecto con curva
    cy=by+(gy-by)*e
    r=70*(1-0.45*e)
    if t>=GOAL:
        sh=8*math.exp(-(t-GOAL)*4)*math.sin((t-GOAL)*60)
        cx,cy,r=gx+sh,gy+20,38
    ball(d,cx,cy,r,t*12*(1-e*0.3) if t<GOAL else 0)
    if t<GOAL+3.2: nadie(d,nx,ny-40 if t<KICK+0.3 else ny,120,"happy" if t>GOAL else "focus")
    if t>=GOAL:
        k=t-GOAL
        if k<3.2:
            n=int(min(1,k/1.2)*9)+1; word="GO"+"O"*n+"L"
            s=1+0.12*math.sin(k*18)*math.exp(-k*2)
            sz=200
            while F(sz).getlength(word)>880: sz-=6
            tc(d,word,W/2,820,sz*s,fill=YEL,stroke=14)
            random.seed(int(k*10))
            for _ in range(int(60*min(1,k*3))):
                x=random.randint(60,W-60); y=random.randint(240,1500)
                c=random.choice([YEL,WHITE,(255,92,160),(90,240,220)]); d.rectangle((x,y,x+16,y+26),fill=c)
        else:
            ov=Image.new("RGBA",(W,H),(17,17,17,int(225*ease((k-3.2)/0.4)))); im.paste(ov,(0,0),ov); d=ImageDraw.Draw(im)
            tc(d,"Ya domino",W/2,620,110,stroke=0); tc(d,"el fútbol.",W/2,750,110,fill=YEL,stroke=0)
            nadie(d,W/2,1080,170,"wink")
            if k>3.9: tc(d,"Gracias por estrenar",W/2,1360,64,w="Bold",stroke=0); tc(d,"esta cuenta, @gstarr_4.7",W/2,1440,64,w="Bold",stroke=0)
    return im
if __name__=="__main__":
    if sys.argv[1]=="still":
        for t in map(float,sys.argv[2:]): frame(t).save(f"s_{t}.png")
    else:
        p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","mudo.mp4"],stdin=subprocess.PIPE)
        for i in range(int(TOTAL*FPS)): p.stdin.write(frame(i/FPS).tobytes())
        p.stdin.close(); p.wait()
