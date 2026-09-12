class_name GTQA
extends Node
static var instance: GTQA
var game
var enabled: bool=false
var file: FileAccess
var accumulator: float=0
var flush_clock: float=0
var queue: Array[Dictionary]=[]
var log_path: String=""
static func record(kind: String,data: Dictionary) -> void:
 if instance and instance.enabled:
  if instance.queue.size()<2048:instance.queue.append({"schema_version":4,"kind":kind,"data":data.duplicate(true)})
func _ready() -> void:
 instance=self
 for arg in OS.get_cmdline_user_args():
  if arg=="--telemetry-logging":enabled=true
 if enabled:
  DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("user://qa-v4"))
  log_path="user://qa-v4/session-"+str(Time.get_unix_time_from_system())+".jsonl"
  file=FileAccess.open(log_path,FileAccess.WRITE)
  if not file:enabled=false;game.hud.notify("텔레메트리 저장 실패: "+error_string(FileAccess.get_open_error()))
  else:record("session",{"engine":Engine.get_version_info().string,"physics_hz":Engine.physics_ticks_per_second,"profile":game.car.cfg.profile,"scope":"instrumentation; not a QA verdict"})
func _physics_process(dt: float) -> void:
 if not enabled:return
 accumulator+=dt;flush_clock+=dt
 if accumulator>=.1:
  accumulator=0
  var data=game.car.telemetry();data["time_s"]=game.car.simulation_time;data["tick"]=Engine.get_physics_frames();data["profile"]=game.car.cfg.profile
  record("player",data)
  for item in game.traffic.cars:
   if item.body is GTTrafficBody:record("traffic",item.body.telemetry())
 for row in queue:file.store_line(JSON.stringify(row))
 queue.clear()
 if flush_clock>=1:
  file.flush();flush_clock=0
  if file.get_error()!=OK:enabled=false;game.hud.notify("텔레메트리 저장 오류: "+error_string(file.get_error()))
func _exit_tree() -> void:
 if file:file.flush();file.close()
 instance=null
