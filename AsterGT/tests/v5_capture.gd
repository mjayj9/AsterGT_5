extends SceneTree
var game
var out="res://tests/v5-captures"
func _initialize() -> void:call_deferred("run")
func settle() -> void:
 for i in range(8):await process_frame
 await RenderingServer.frame_post_draw
func shot(name: String) -> void:
 await settle();root.get_texture().get_image().save_png(out+"/"+name+".png");print("CAPTURE ",name)
func run() -> void:
 DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out))
 game=load("res://scenes/main.tscn").instantiate();root.add_child(game)
 await create_timer(2).timeout
 game.hud.set_beginner(true);GTControls.language="ko";game.hud.show_home()
 await shot("01-home-ko")
 game.start_drive("Free Drive");await create_timer(.5).timeout
 await shot("02-beginner")
 game.hud.help_button.pressed.emit();game.hud.help_category="gears";game.hud.show_guide()
 await shot("03-gears")
 game.hud.help_topic="reverse";game.hud.show_guide();await shot("04-reverse")
 game.hud.help_category="aids";game.hud.help_topic="abs";game.hud.show_guide();await shot("05-abs")
 game.hud.show_setup();await shot("06-setup")
 game.hud.show_performance();await shot("07-performance")
 GTControls.language="en";game.hud.help_topic="reverse";game.hud.help_category="gears";game.hud.show_guide();await shot("08-english")
 GTControls.language="ko";game.hud.set_beginner(false);game.resume();await shot("09-normal")
 game.hud.help_category="damage";game.hud.help_topic="damage";game.hud.show_guide();await shot("10-damage-help")
 # Fixed render pose for exact before/after/repair comparisons; no driving input claim.
 game.hud.hide();game.set_process(false);game.cam.set_process(false)
 game.car.body_visual.show();for lod in game.car.lod_visuals:lod.hide()
 for wheel in game.car.wheel_visuals:wheel.show()
 for caliper in game.car.calipers:caliper.show()
 var tr=game.car.global_transform
 game.cam.camera.global_position=tr*Vector3(-3.1,1.0,4.9)
 game.cam.camera.look_at(tr*Vector3(-.25,-.08,1.0),Vector3.UP)
 game.cam.camera.fov=47
 await shot("11-intact")
 game.car.damage.visuals.add_hit(Vector3(-.764893,-.184877,2.050853),Vector3.BACK,Vector3.RIGHT,48000,8)
 game.car.damage.apply_visuals(game.car.body_visual)
 await shot("12-local-damage")
 game.hud.repair_body();await shot("13-repaired")
 await game.world.stop_streaming();game.queue_free();await process_frame
 quit()
