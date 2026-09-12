from pathlib import Path
import json
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4/outputs/AsterGT')
f=p/'scripts/controls.gd';s=f.read_text(encoding='utf8')
s=s.replace(' var key=int(s.key)\n if key<=0 or key==KEY_UNKNOWN or OS.get_keycode_string(key).is_empty():return false',''' if not is_finite(float(s.key)) or float(s.key)!=floor(float(s.key)):return false
 var location=s.get("location",0)
 if not (location is int or location is float) or not is_finite(float(location)):return false
 var key=int(s.key)
 var special=[KEY_ESCAPE,KEY_TAB,KEY_BACKTAB,KEY_BACKSPACE,KEY_ENTER,KEY_KP_ENTER,KEY_INSERT,KEY_DELETE,KEY_PAUSE,KEY_PRINT,KEY_HOME,KEY_END,KEY_LEFT,KEY_UP,KEY_RIGHT,KEY_DOWN,KEY_PAGEUP,KEY_PAGEDOWN,KEY_SHIFT,KEY_CTRL,KEY_META,KEY_ALT,KEY_CAPSLOCK,KEY_NUMLOCK,KEY_SCROLLLOCK]
 if not ((key>=32 and key<=126) or (key>=KEY_F1 and key<=KEY_F35) or key in special or OS.get_keycode_string(key).begins_with("Kp ")):return false''')
a=s.index('static func recognize(');b=s.index('static func value(',a)
s=s[:a]+'''static func find_binding(s: Dictionary) -> Dictionary:
 for a in registry:
  for binding in bindings[a]:
   if same_slot(s,binding):return {"action":a,"binding":binding}
 return {}
static func recognize(e: InputEventKey,diagnostic: bool=false) -> String:
 var s=event_slot(e);last_event=slot_text(s);last_action="—"
 var found=find_binding(s)
 if found.is_empty():
  # A standalone hold modifier (default: clutch) must coexist with W/Q/E.
  # Explicit modifier chords always win before this fallback.
  var relaxed=s.duplicate()
  for a in registry:
   if registry[a].type!="hold":continue
   for binding in bindings[a]:
    if binding.is_empty():continue
    if binding.ctrl or binding.alt or binding.shift or binding.meta:continue
    for pair in [[KEY_SHIFT,"shift"],[KEY_CTRL,"ctrl"],[KEY_ALT,"alt"],[KEY_META,"meta"]]:
     if int(binding.key)==pair[0]:relaxed[pair[1]]=false
  found=find_binding(relaxed)
 if found.is_empty():return ""
 var action: String=found.action;last_action=action
 if diagnostic:return action
 if not Context.keys()[context] in registry[action].contexts:return ""
 if e.pressed and not e.echo and registry[action].type in ["hold","axis"]:held[action]=found.binding
 return action if e.pressed and not e.echo else ""
'''+s[b:]
f.write_text(s,encoding='utf8')
f=p/'scripts/driving_ui.gd';s=f.read_text(encoding='utf8')
s=s.replace('row.button.text=GTControls.slot_text','row.button.text=("Primary · " if row.slot==0 else "Secondary · ")+GTControls.slot_text')
s=s.replace('if game.car.brake>.2:practiced.brake=true','if game.car.brake>.2 and GTControls.value("brake")>.5:practiced.brake=true')
s=s.replace('if game.car.throttle>.15 and game.car.speed_kph>1:','if game.car.throttle>.15 and GTControls.value("throttle")>.5 and game.car.speed_kph>1:')
s=s.replace('if absf(game.car.steering)>.15 and game.car.speed_kph>1:','if absf(game.car.steering)>.15 and (GTControls.value("left")>.5 or GTControls.value("right")>.5) and game.car.speed_kph>1:')
f.write_text(s,encoding='utf8')
f=p/'scripts/car.gd';s=f.read_text(encoding='utf8')
s=s.replace(' cache_details()',' cache_details()\n cache_lod_lamps()',1)
s=s.replace('item.material.emission_energy_multiplier=intensity','item.material.emission_energy_multiplier=intensity*(1-damage.state.lights)')
s=s.replace(' if dashboard:dashboard.text=', ' if dashboard:dashboard.modulate=Color("ff643d") if rpm>cfg.redline_rpm else Color("d8f7ec")\n if dashboard:dashboard.text=')
s+='''\nfunc cache_lod_lamps() -> void:
 for model in lod_visuals:
  for mesh in model.find_children("*","MeshInstance3D",true,false):
   for surface in range(mesh.mesh.get_surface_count()):
    var old=mesh.mesh.surface_get_material(surface)
    if not old is StandardMaterial3D:continue
    var kind="head" if "emissive_light_front" in old.resource_name.to_lower() else "tail" if "emissive_light_rear" in old.resource_name.to_lower() else ""
    if kind.is_empty():continue
    var material=old.duplicate();material.emission_enabled=true
    material.emission=Color(.9,.96,1) if kind=="head" else Color(1,.035,.015)
    mesh.set_surface_override_material(surface,material);visual_lamps.append({"material":material,"kind":kind,"side":0})
 # Explicit inexpensive direction lamps for all camera LODs.
 for side in [-1,1]:
  for z in [-2.22,2.22]:
   var node=MeshInstance3D.new();var shape=BoxMesh.new();shape.size=Vector3(.13,.06,.02);node.mesh=shape;node.position=Vector3(side*.78,-.23,z)
   var material=StandardMaterial3D.new();material.albedo_color=Color(.5,.15,.01);material.emission_enabled=true;material.emission=Color(1,.3,.01);node.material_override=material
   add_child(node);visual_lamps.append({"material":material,"kind":"signal","side":side})
'''
f.write_text(s,encoding='utf8')
f=p/'scripts/main.gd';s=f.read_text(encoding='utf8')
a=s.index(' for node in car.body_visual.find_children(',s.index('func set_paint('));b=s.index('func power_hp()',a)
block=s[a:b]
s=s[:a]+''' var paint_roots=[car.body_visual];paint_roots.append_array(car.lod_visuals)
 for paint_root in paint_roots:
'''+''.join(' '+line.replace('car.body_visual.find_children','paint_root.find_children')+'\n' for line in block.splitlines())+s[b:]
f.write_text(s,encoding='utf8')
f=p/'scripts/traffic.gd';s=f.read_text(encoding='utf8').replace('  cars.append({"body":body,','  var speed=rng.randf_range(19,29)\n  cars.append({"body":body,').replace('"speed":rng.randf_range(19,29)','"speed":speed').replace('"velocity":-tr.basis.z*24','"velocity":-tr.basis.z*speed')
f.write_text(s,encoding='utf8')
f=p/'scripts/traffic_body.gd';s=f.read_text(encoding='utf8').replace('var wheel_spin: float=0','var wheel_spin: float=0\nvar radius_m: float=.34')
s=s.replace(' mass=spec.mass_kg;', ' radius_m=tuning.wheel_radius_m*spec.size_m[1]/1.45\n mass=spec.mass_kg;')
s=s.replace('var radius=float(tuning.wheel_radius_m)','var radius=radius_m')
s=s.replace('-.33+rest-mass*9.81','-.33*spec.size_m[1]/1.45+rest-mass*9.81')
s=s.replace('wheels[i].position.y=mount.y-length_m','wheels[i].position.y=(mount.y-length_m)/visual.scale.y')
s=s.replace('/tuning.wheel_radius_m*dt','/radius_m*dt')
f.write_text(s,encoding='utf8')
print('modifier coexistence, corrupt-input validation and visual connections tightened')
