import numpy as np, wave
import reel
SR=44100; rng=np.random.default_rng(1)
def env(n,a,r): t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/r)
def pop(f0,f1,d=0.08):
    n=int(SR*d); t=np.arange(n)/SR; f=f0+(f1-f0)*t/d
    return np.sin(2*np.pi*np.cumsum(f)/SR)*env(n,0.002,d/3)*0.5
def ding(f,d=0.8):
    n=int(SR*d); t=np.arange(n)/SR
    return sum(a*np.sin(2*np.pi*f*k*t) for k,a in ((1,1),(2.01,.4),(3.02,.2)))*env(n,0.002,0.25)*0.3
def whoosh(d=0.4):
    n=int(SR*d); x=rng.standard_normal(n); y=np.zeros(n); a=0
    for i in range(n): c=0.02+0.2*np.sin(np.pi*i/n); a+=c*(x[i]-a); y[i]=a
    return y*np.sin(np.pi*np.arange(n)/n)**2
def blip(f=880):
    n=int(SR*0.05); t=np.arange(n)/SR; return np.sign(np.sin(2*np.pi*f*t))*env(n,0.001,0.02)*0.12
tr=np.zeros(int(SR*(reel.TOTAL+1)))
def add(t,s,g=1):
    i=int(SR*t); j=min(len(tr),i+len(s)); tr[i:j]+=s[:j-i]*g
D=reel.VOZ_DELAY
add(0.0,whoosh(0.6),0.9)
for st,_ in reel.PH: add(st+D,blip(700+rng.integers(0,500)),1)
add(4.0+D,pop(500,1300,0.12)); add(4.1+D,ding(1320),0.7)
for q in range(4): add(7.5+D+q*0.25,pop(600+q*120,1200+q*120),0.7)
add(13.4+D,pop(400,1200,0.12)); add(13.45+D,ding(988),0.6)
add(21.0+D,whoosh(),0.7); add(21.3+D,ding(1046),0.6); add(21.45+D,ding(1318),0.5)
tr=np.tanh(tr*1.2)*0.8
with wave.open("sfx.wav","wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((tr*32767).astype(np.int16).tobytes())
