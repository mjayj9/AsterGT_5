extends SceneTree
# Keep production telemetry methods; skip unrelated rendering/vehicle simulation.
class PlayerSnapshot extends GTCar:
 func _ready() -> void:pass
 func _integrate_forces(_state: PhysicsDirectBodyState3D) -> void:pass
class TrafficSnapshot extends GTTrafficBody:
 func _ready() -> void:pass
 func _integrate_forces(_state: PhysicsDirectBodyState3D) -> void:pass
 func _process(_dt: float) -> void:pass
func _initialize() -> void:call_deferred("run")
func v(a: Array) -> Vector3:return Vector3(a[0],a[1],a[2])
func arr(a: Vector3) -> Array:return [a.x,a.y,a.z]
func run() -> void:
 var rows=[];var passed=true
 for offset in [Vector3.ZERO,Vector3(4096,0,-2048)]:
  var parent=Node3D.new();parent.position=offset;root.add_child(parent)
  var player=PlayerSnapshot.new();player.process_mode=Node.PROCESS_MODE_DISABLED;player.position=Vector3(8,2,8);parent.add_child(player);player.linear_velocity=Vector3(0,0,-25)
  var traffic=TrafficSnapshot.new();traffic.process_mode=Node.PROCESS_MODE_DISABLED;traffic.position=Vector3(8.5,2,4.5);parent.add_child(traffic);traffic.linear_velocity=Vector3(0,0,3)
  var a=player.telemetry();var b=traffic.telemetry()
  var error_a=v(a.position).distance_to(player.global_position);var error_b=v(b.position_m).distance_to(traffic.global_position)
  passed=passed and error_a<.001 and error_b<.001
  rows.append({"parent_translation_m":arr(offset),"player_reported_position":a.position,"player_world_position":arr(player.global_position),"player_position_error_m":error_a,"traffic_reported_position":b.position_m,"traffic_world_position":arr(traffic.global_position),"traffic_position_error_m":error_b})
  parent.queue_free()
 var report={"scope":"coordinate-only production telemetry regression","pass":passed,"samples":rows}
 var output="res://tests/preqa/telemetry_regression.json"
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--output="):output=arg.trim_prefix("--output=")
 var file=FileAccess.open(output,FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
 print("PREQA_TELEMETRY_COORDINATES "+JSON.stringify(report))
 await process_frame
 quit(0 if passed else 1)
