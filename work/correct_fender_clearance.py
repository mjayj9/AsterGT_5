from pathlib import Path
p=Path('outputs/AsterGT/blender/build_models.py');s=p.read_text(encoding='utf-8').replace(':verts.append((x,y,z))', ''':
  arch_bump=max(math.exp(-((z+1.39)/.55)**2),math.exp(-((z-1.39)/.55)**2))
  shoulder_lift=.14*arch_bump*min(1,max(0,(abs(x)/w-.5)/.3)) if y>-.12 else 0
  verts.append((x,y+shoulder_lift,z))''').replace('(s*.68,.285,z)','(s*.68,.355,z)');p.write_text(s,encoding='utf-8')
p=Path('outputs/AsterGT/scripts/car.gd');s=p.read_text(encoding='utf-8').replace('preload("res://config/street.tres").duplicate()','preload("res://config/street.tres").duplicate(true)');p.write_text(s,encoding='utf-8')
p=Path('outputs/AsterGT/scripts/camera_rig.gd');s=p.read_text(encoding='utf-8').replace('clampf(a[1],-.1,6)','clampf(a[1],-.3,6)');p.write_text(s,encoding='utf-8')
p=Path('outputs/AsterGT/scripts/hud.gd');s=p.read_text(encoding='utf-8').replace('[-12,-.1,-12]','[-12,-.3,-12]');p.write_text(s,encoding='utf-8')
