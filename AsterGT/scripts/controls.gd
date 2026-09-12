class_name GTControls
extends RefCounted
enum Context {MENU, ONBOARDING, DRIVING, PAUSED, REBIND_CAPTURE, PHOTO_ORBIT}
const SCHEMA_VERSION=4
static var registry: Dictionary={}
static var bindings: Dictionary={}
static var held: Dictionary={}
static var context: int=Context.MENU
static var language: String="ko"
static var last_event: String="—"
static var last_action: String="—"
static var load_message: String=""
static func initialize() -> void:
 registry=JSON.parse_string(FileAccess.get_file_as_string("res://config/control_actions.json")).actions
 reset_defaults("",false)
 if not FileAccess.file_exists("user://controls.json"):return
 var saved=JSON.parse_string(FileAccess.get_file_as_string("user://controls.json"))
 if not valid_document(saved):
  var err=GTSafeStore.quarantine("user://controls.json")
  load_message="키 설정 손상: 기본값 복구. controls.json.corrupt-*.bak 백업." if err==OK else "키 설정 백업 실패. 원본 유지, 기본값 사용: "+error_string(err)
  return
 bindings=saved.bindings;apply_map()
static func default_slot(key: String) -> Dictionary:
 if key.is_empty():return {}
 return {"key":OS.find_keycode_from_string(key),"ctrl":false,"alt":false,"shift":false,"meta":false,"location":1 if key=="Shift" else 0}
static func reset_defaults(category: String="",persist: bool=true) -> Error:
 var proposal=bindings.duplicate(true)
 for a in registry:
  if category.is_empty() or registry[a].category==category:proposal[a]=[default_slot(registry[a].default_primary),default_slot(registry[a].default_secondary)]
 if not category.is_empty():
  for a in registry:
   if registry[a].category!=category:continue
   for s in proposal[a]:
    for b in registry:
     if registry[b].category==category:continue
     for i in range(2):
      if same_slot(s,proposal[b][i]):proposal[b][i]={}
 var err=GTSafeStore.save_json("user://controls.json",{"schema_version":SCHEMA_VERSION,"bindings":proposal}) if persist else OK
 if err==OK:bindings=proposal;apply_map()
 return err
static func valid_slot(s) -> bool:
 if not s is Dictionary:return false
 if s.is_empty():return true
 if not (s.get("key") is float or s.get("key") is int):return false
 if not is_finite(float(s.key)) or float(s.key)!=floor(float(s.key)):return false
 var location=s.get("location",0)
 if not (location is int or location is float) or not is_finite(float(location)):return false
 var key=int(s.key)
 var special=[KEY_ESCAPE,KEY_TAB,KEY_BACKTAB,KEY_BACKSPACE,KEY_ENTER,KEY_KP_ENTER,KEY_INSERT,KEY_DELETE,KEY_PAUSE,KEY_PRINT,KEY_HOME,KEY_END,KEY_LEFT,KEY_UP,KEY_RIGHT,KEY_DOWN,KEY_PAGEUP,KEY_PAGEDOWN,KEY_SHIFT,KEY_CTRL,KEY_META,KEY_ALT,KEY_CAPSLOCK,KEY_NUMLOCK,KEY_SCROLLLOCK]
 if not ((key>=32 and key<=126) or (key>=KEY_F1 and key<=KEY_F35) or key in special or OS.get_keycode_string(key).begins_with("Kp ")):return false
 for m in ["ctrl","alt","shift","meta"]:
  if not s.get(m) is bool:return false
 return int(s.get("location",0)) in [0,1,2]
static func valid_document(d) -> bool:
 if not d is Dictionary or d.get("schema_version")!=SCHEMA_VERSION or not d.get("bindings") is Dictionary:return false
 var occupied=[]
 for a in registry:
  if not d.bindings.get(a) is Array or d.bindings[a].size()!=2:return false
  for s in d.bindings[a]:
   if not valid_slot(s):return false
   if s.is_empty():continue
   for old in occupied:
    if same_slot(old,s):return false
   occupied.append(s)
 return true
static func apply_map() -> void:
 clear_held()
 for a in registry:
  if not InputMap.has_action(a):InputMap.add_action(a)
  InputMap.action_erase_events(a)
  for s in bindings[a]:
   if s.is_empty():continue
   var e=InputEventKey.new();e.physical_keycode=int(s.key);e.ctrl_pressed=s.ctrl;e.alt_pressed=s.alt;e.shift_pressed=s.shift;e.meta_pressed=s.meta
   InputMap.action_add_event(a,e)
static func text_for(a: String,field: String="name") -> String:return str(registry.get(a,{}).get(field+"_"+language,a))
static func slot_text(s: Dictionary) -> String:
 if s.is_empty():return "—"
 var parts: Array[String]=[]
 for m in ["ctrl","alt","shift","meta"]:
  if s.get(m,false):parts.append(m.capitalize())
 var side=("왼쪽 " if language=="ko" else "Left ") if int(s.get("location",0))==1 else ("오른쪽 " if language=="ko" else "Right ") if int(s.get("location",0))==2 else ""
 var key_label=OS.get_keycode_string(int(s.key))
 if language=="ko":key_label={"Up":"↑","Down":"↓","Left":"←","Right":"→"}.get(key_label,key_label)
 parts.append(side+key_label)
 return "+".join(parts)
static func key_text(a: String) -> String:
 var parts: Array[String]=[]
 for s in bindings.get(a,[]):
  if not s.is_empty():parts.append(slot_text(s))
 return " / ".join(parts) if not parts.is_empty() else ("미지정" if language=="ko" else "Unbound")
static func event_slot(e: InputEventKey) -> Dictionary:
 return {"key":int(e.physical_keycode),"ctrl":e.ctrl_pressed and e.physical_keycode!=KEY_CTRL,"alt":e.alt_pressed and e.physical_keycode!=KEY_ALT,"shift":e.shift_pressed and e.physical_keycode!=KEY_SHIFT,"meta":e.meta_pressed and e.physical_keycode!=KEY_META,"location":int(e.location) if e.physical_keycode in [KEY_SHIFT,KEY_CTRL,KEY_ALT,KEY_META] else 0}
static func same_slot(a: Dictionary,b: Dictionary) -> bool:
 if a.is_empty() or b.is_empty() or int(a.key)!=int(b.key):return false
 for m in ["ctrl","alt","shift","meta"]:
  if a.get(m,false)!=b.get(m,false):return false
 return int(a.get("location",0))==0 or int(b.get("location",0))==0 or int(a.location)==int(b.location)
static func conflict(a: String,index: int,s: Dictionary) -> Dictionary:
 for b in bindings:
  for i in range(2):
   if a==b and i==index:continue
   if same_slot(s,bindings[b][i]):return {"action":b,"slot":i}
 return {}
static func assign(a: String,index: int,s: Dictionary,policy: String="cancel") -> Error:
 if not valid_slot(s):return ERR_INVALID_DATA
 var other=conflict(a,index,s)
 if not other.is_empty() and policy=="cancel":return ERR_ALREADY_EXISTS
 var proposal=bindings.duplicate(true)
 if not other.is_empty():proposal[other.action][other.slot]=proposal[a][index] if policy=="swap" else {}
 proposal[a][index]=s
 var err=GTSafeStore.save_json("user://controls.json",{"schema_version":SCHEMA_VERSION,"bindings":proposal})
 if err==OK:bindings=proposal;apply_map()
 return err
static func set_context(value: int) -> void:
 if context!=value:clear_held()
 context=value
static func clear_held() -> void:
 held.clear()
 for a in registry:
  if InputMap.has_action(a):Input.action_release(a)
static func driving() -> bool:return context in [Context.DRIVING,Context.ONBOARDING,Context.PHOTO_ORBIT]
static func release_event(e: InputEventKey) -> void:
 if not e.pressed:
  for a in held.keys():
   if int(held[a].key)==int(e.physical_keycode):held.erase(a)
 for a in held.keys():
  var s=held[a]
  if (s.ctrl and not e.ctrl_pressed) or (s.alt and not e.alt_pressed) or (s.shift and not e.shift_pressed) or (s.meta and not e.meta_pressed):held.erase(a)
static func find_binding(s: Dictionary) -> Dictionary:
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
static func value(a: String) -> float:return 1.0 if driving() and held.has(a) else 0.0
