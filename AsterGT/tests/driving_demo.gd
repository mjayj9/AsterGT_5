extends SceneTree
var game
func _initialize() -> void:call_deferred("run")
func seconds(t: float) -> void:
 for i in range(roundi(t*30)):await process_frame
func run() -> void:
 game=load("res://scenes/main.tscn").instantiate();root.add_child(game);current_scene=game
 game.graphics.resolution=0;game.graphics.vsync=false;game.graphics.cap=0;game.apply_graphics()
 await seconds(2)
 game.start_drive("Free Drive");game.car.test_input={"throttle":.35};game.cam.mode=4;game.cam.orbit_yaw=1.10;game.cam.orbit_distance=5.2;game.cam.orbit_pitch=.06;game.cam.first=true
 await seconds(5)
 game.car.test_input={"throttle":.8};game.cam.mode=0;game.cam.first=true;game.cam.update_visibility()
 await seconds(4)
 game.cam.mode=3;game.cam.first=true;game.cam.update_visibility();game.car.test_input={"throttle":.35}
 await seconds(4)
 game.car.test_input={"brake":1.0};game.cam.mode=4;game.cam.first=true;game.cam.update_visibility()
 await seconds(3)
 game.finish()
