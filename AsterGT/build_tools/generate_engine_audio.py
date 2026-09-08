"""Deterministic, seamless six-cylinder engine layers. No external recordings."""
from pathlib import Path
import numpy as np,wave,json
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'assets/audio';out.mkdir(exist_ok=True)
rate=48000;rng=np.random.default_rng(992);report={}
def save(name,x):
 x=np.asarray(x,dtype=np.float64);x-=x.mean();x/=max(1.0,np.max(np.abs(x))/.84)
 with wave.open(str(out/(name+'.wav')),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes((x*32767).astype('<i2').tobytes())
 report[name]={'samples':len(x),'rate':rate,'peak':float(np.max(np.abs(x))),'rms':float(np.sqrt(np.mean(x*x))),'boundary_step':float(abs(x[-1]-x[0]))}
for rpm in [850,1800,3000,4500,6000,7500]:
 cycles=round(rpm/60);n=round(rate*120/rpm*cycles);phase=np.arange(n)/n*cycles*2*np.pi
 for on in [False,True]:
  # Six combustion pulses per two crank revolutions, with alternating-bank character.
  x=np.zeros(n)
  for h in range(1,33):
   frequency=h*rpm/20;resonance=1+.7*np.exp(-((frequency-420)/220)**2)+.55*np.exp(-((frequency-1100)/440)**2)
   amplitude=np.exp(-h/(10 if on else 5))/h**(.8 if on else 1.15)
   x+=amplitude*resonance*np.sin(phase*6*h+.22*h)
  x+=.14*np.sin(phase*3)+.10*np.sin(phase*9)+.06*np.sin(phase*12+.8)
  frequencies=np.fft.rfftfreq(n,1/rate);noise=np.fft.rfft(rng.standard_normal(n));shape=np.exp(-((frequencies-1300)/1400)**2)/(1+frequencies/400)
  noise=np.fft.irfft(noise*shape,n);noise/=max(.001,noise.std())
  x=x*.20+noise*(.025 if on else .010)
  x=np.tanh(x*(1.35 if on else .95))*.58
  save(f'engine_{rpm}_{"on" if on else "off"}',x)
# Starter and stall events have attack/release envelopes, and are not looped.
for name,duration in [('starter',.55),('stall',.42),('gear',.12)]:
 t=np.arange(int(rate*duration))/rate
 if name=='starter':x=(np.sin(2*np.pi*74*t)+.3*np.sin(2*np.pi*148*t))*np.minimum(t/.03,1)*np.minimum((duration-t)/.12,1)*.22
 elif name=='stall':x=np.sin(2*np.pi*(55*t-45*t*t))*np.exp(-t*8)*.35
 else:x=(rng.standard_normal(len(t))*.12+np.sin(2*np.pi*220*t)*.25)*np.exp(-t*55)
 save(name,x)
(ROOT/'tests/audio_asset_results.json').write_text(json.dumps({'method':'Periodic six-cylinder harmonic/pulse synthesis, load/coast layers, deterministic band-limited noise, no recordings','layers':report,'checks':{'no_clipping':all(v['peak']<.85 for v in report.values()),'finite_rms':all(.001<v['rms']<.5 for v in report.values()),'all_12_engine_layers':len([k for k in report if k.startswith('engine_')])==12}},indent=2),encoding='utf-8')
print('Generated',len(report),'audio clips')
