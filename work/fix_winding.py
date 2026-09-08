from pathlib import Path
p=Path('outputs/AsterGT/scripts/world.gd')
s=p.read_text(encoding='utf-8')
s=s.replace('[[a,Vector2(left/3,i*8/3.0)],[b,Vector2(right/3,i*8/3.0)],[c,Vector2(left/3,(i+1)*8/3.0)],[b,Vector2(right/3,i*8/3.0)],[d,Vector2(right/3,(i+1)*8/3.0)],[c,Vector2(left/3,(i+1)*8/3.0)]]','[[a,Vector2(left/3,i*8/3.0)],[c,Vector2(left/3,(i+1)*8/3.0)],[b,Vector2(right/3,i*8/3.0)],[b,Vector2(right/3,i*8/3.0)],[c,Vector2(left/3,(i+1)*8/3.0)],[d,Vector2(right/3,(i+1)*8/3.0)]]')
s=s.replace('[Vector2(0,0),Vector2(0,1),Vector2(1,0),Vector2(1,0),Vector2(0,1),Vector2(1,1)]','[Vector2(0,0),Vector2(1,0),Vector2(0,1),Vector2(1,0),Vector2(1,1),Vector2(0,1)]')
p.write_text(s,encoding='utf-8')
