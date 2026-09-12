from pathlib import Path
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4-pre-qa/outputs/AsterGT')
t=p/'scripts/contact_damage.gd';s=t.read_text(encoding='utf-8-sig')
old='  var r=point-physics.transform.origin-physics.center_of_mass'
new='''  # GodotPhysics3D center_of_mass is a world-axis OFFSET from the body origin.
  # Contact points are world positions. Keep both lever-arm endpoints in world space.
  var world_center_of_mass=physics.transform.origin+physics.center_of_mass
  var r=point-world_center_of_mass'''
assert old in s;s=s.replace(old,new)
old='   var r2=point-other.global_position-other.global_basis*other.center_of_mass'
new='''   # RigidBody3D.center_of_mass is body-local (both vehicle classes use CUSTOM).
   var other_world_center_of_mass=other.global_transform*other.center_of_mass
   var r2=point-other_world_center_of_mass'''
assert old in s;s=s.replace(old,new);t.write_text(s,encoding='utf8')
for name in ['car.gd','traffic_body.gd']:
 t=p/'scripts'/name;s=t.read_text(encoding='utf-8-sig')
 old='[position.x,position.y,position.z]';new='[global_position.x,global_position.y,global_position.z]'
 assert s.count(old)==1
 s=s.replace(old,new);t.write_text(s,encoding='utf8')
t=p/'export_presets.cfg';s=t.read_text(encoding='utf-8-sig')
s=s.replace('export_path="../Windows-v4/AsterGT-v4.exe"','export_path="../Windows-v4-pre-qa/AsterGT-v4-pre-qa.exe"')
t.write_text(s,encoding='utf8')
print('Updated contact endpoint names, two world-coordinate telemetry fields, and separate export destination only.')
