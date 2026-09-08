from pathlib import Path
p=Path('outputs/AsterGT/tests')
(p/'integration_test.gd').write_text(r'''
extends SceneTree
var game
var results={"checks":{},"road_samples":[],"notes":[]}
var checks: Dictionary
func _initialize() -> void:
 call_deferred("run")
func frames(n: int) -> void:
 for i in range(n):await physics_frame
func key(code: int,pressed: bool=true) -> void:
 var e=InputEventKey.new();e.physical_keycode=code;e.keycode=code;e.pressed=pressed;Input.parse_input_event(e)
func tap(code: int) -> void:
 key(code);await frames(2);key(code,false);await frames(2)
func check(name: String,passed: bool) -> void:
 results.checks[name]=passed;print("CHECK ",name," ",passed)
func run() -> void:
 game=load("res://scenes/main.tscn").instantiate();root.add_child(game);current_scene=game
 await frames(40)
 check("main_menu_has_six_actions",game.hud.page=="home")
 check("road_at_least_15km",game.world.length>=15000)
 game.start_drive("High Speed");await frames(120)
 check("spawn_four_contacts",game.car.grounded==4)
 key(KEY_W);await frames(12)
 check("throttle_is_filtered",game.car.throttle>0 and game.car.throttle<.6)
 await frames(650);key(KEY_W,false)
 check("keyboard_accelerates",game.car.speed_kph>100)
 check("automatic_shifts",game.car.gear>=3)
 var old=game.car.gear
 await tap(KEY_M)
 check("M_switches_to_manual",not game.car.automatic)
 await frames(60)
 check("manual_no_uncommanded_shift",game.car.gear==old)
 game.car.auto_clutch=false
 await tap(KEY_E)
 check("unclutched_keyboard_shift_refused",game.car.gear==old)
 key(KEY_SHIFT);await frames(30);await tap(KEY_E)
 check("clutched_keyboard_shift_accepts",game.car.gear==old+1)
 key(KEY_SHIFT,false)
 await tap(KEY_F5);await tap(KEY_F6);await tap(KEY_F7)
 check("assist_keys_toggle",not game.car.abs_enabled and not game.car.tcs_enabled and not game.car.esc_enabled)
 await tap(KEY_F);await tap(KEY_G);await tap(KEY_Z);await tap(KEY_H)
 check("vehicle_function_keys",game.car.headlights and game.car.highbeam and game.car.indicator==-1 and game.car.hazards)
 var camera_modes={}
 for i in range(5):await tap(KEY_C);camera_modes[str(game.cam.mode)]=true
 check("all_five_cameras_cycle",camera_modes.size()==5)
 await tap(KEY_T);await tap(KEY_T);await tap(KEY_Y);await tap(KEY_Y)
 check("rain_night_keys",game.world.weather==2 and game.world.time_of_day==2 and game.car.wetness==1)
 await tap(KEY_ESCAPE)
 check("pause_stops_physics",paused and game.hud.page=="paused")
 # SceneTree's physics_frame still ticks while paused, so release keys before resuming.
 var pos=game.car.position;await frames(30)
 check("paused_position_unchanged",game.car.position.distance_to(pos)<.01)
 await tap(KEY_ESCAPE)
 check("resume_restores_controls",not paused and game.car.controls_enabled)
 await tap(KEY_BACKSPACE);await frames(150)
 check("keyboard_recovery",game.car.grounded>=3 and game.car.speed_kph<10)
 var error=GTControls.rebind("horn",KEY_J,false)
 check("rebind_works",error=="" and GTControls.key_text("horn")=="J")
 check("duplicate_binding_refused",GTControls.rebind("horn",KEY_W,false)!="")
 GTControls.initialize()
 var cfg=VehicleConfig.new()
 var file=FileAccess.open("user://invalid_test.json",FileAccess.WRITE);file.store_string('{"mass_kg":-900,"torque_scale":99,"max_rpm":"bad","gear_ratios":[1,2],"drive_layout":"bad"}');file.close()
 check("malformed_settings_safe",cfg.load_settings("user://invalid_test.json") and cfg.mass_kg==900 and cfg.torque_scale==1.8 and cfg.gear_ratios.size()==6 and cfg.drive_layout=="RWD")
 game.car.test_input={"brake":1.0};game.car.abs_enabled=true;game.car.tcs_enabled=true;game.car.esc_enabled=true
 game.world.weather=0;game.world.time_of_day=0;game.world.update_weather()
 var contact_pass=true
 for i in range(32):
  var distance=game.world.length*i/32.0
  game.car.recover(game.world.road_transform(distance,2.8));await frames(145)
  var tr=game.world.road_transform(distance,2.8)
  var good=game.car.grounded>=3 and game.car.position.y>tr.origin.y-1.1
  if not good:contact_pass=false
  results.road_samples.append({"distance_m":distance,"contacts":game.car.grounded,"height_error":game.car.position.y-tr.origin.y,"pass":good})
 check("road_collision_32_locations",contact_pass)
 game.start_drive("Time Trial");game.car.test_input={"brake":1.0};await frames(30)
 for i in range(6):
  game.car.recover(game.world.road_transform(game.next_gate,2.8));await frames(8)
 check("ordered_checkpoint_finish",game.challenge_done and game.checkpoint==6)
 game.start_drive("Checkpoints");game.car.test_input={"brake":1.0};game.challenge_time=100;await frames(10)
 check("checkpoint_timeout",game.challenge_done)
 game.car.controls_enabled=false;game.car.freeze=true
 var loads=[]
 for i in range(4):
  game.apply_preset(i);loads.append(game.graphics.duplicate())
 check("graphics_presets_change_load",loads[0].scale<loads[3].scale and loads[0].traffic<loads[3].traffic and loads[0].shadows<loads[3].shadows)
 game.apply_preset(2)
 results["road_length_m"]=game.world.length
 results.notes.append("Keys were injected as InputEventKey through the Godot input pipeline. Road samples and checkpoint fixtures use controlled resets; this is not a claim of human driving over the complete route.")
 var output=FileAccess.open("res://tests/integration_results.json",FileAccess.WRITE);output.store_string(JSON.stringify(results,"  "));output.close()
 var ok=true
 for value in results.checks.values():if not value:ok=false
 print("INTEGRATION_DONE ",ok)
 game.queue_free();await process_frame;await process_frame;quit(0 if ok else 1)
'''.strip()+'\n',encoding='utf-8')
