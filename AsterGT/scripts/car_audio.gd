class_name GTAudio
extends Node
var car: GTCar
var players={}
var layers: Array[Dictionary]=[]
var last_shift: float=0
var last_engine_on: bool=false
var interior: bool=false
var muted: bool=false
var bus: int=-1
var bus_name: String
var mix_load: float=0
var flow_bus: String
var buffet_bus: String
var flow_filter: AudioEffectLowPassFilter
func _ready() -> void:
 bus=AudioServer.bus_count;AudioServer.add_bus();bus_name="EngineCabin_"+str(get_instance_id());AudioServer.set_bus_name(bus,bus_name)
 var lowpass=AudioEffectLowPassFilter.new();lowpass.cutoff_hz=16000;AudioServer.add_bus_effect(bus,lowpass)
 var compressor=AudioEffectCompressor.new();compressor.threshold=-10;compressor.ratio=3;compressor.attack_us=2500;compressor.release_ms=90;AudioServer.add_bus_effect(bus,compressor)
 for rpm in [850,1800,3000,4500,6000,7500,9250]:
  for state in ["on","off"]:
   var player=make_player(("res://assets/v4/" if rpm==9250 else "res://assets/audio/")+"engine_%d_%s.wav"%[rpm,state],true)
   layers.append({"player":player,"rpm":float(rpm),"load":state=="on"})
 for name in ["wind","roll","tire","rain","impact","shift","horn","starter","stall","gear"]:
  var path="res://assets/audio/"+name+".wav" if name in ["starter","stall","gear"] else "res://assets/"+name+".wav"
  players[name]=make_player(path,name in ["wind","roll","tire","rain","horn"])
 players["whine"]=make_player("res://assets/v4/whine.wav",true)
 flow_bus="AirTires_"+str(get_instance_id());var index=AudioServer.bus_count;AudioServer.add_bus();AudioServer.set_bus_name(index,flow_bus)
 flow_filter=AudioEffectLowPassFilter.new();AudioServer.add_bus_effect(index,flow_filter);players.wind.bus=flow_bus;players.roll.bus=flow_bus
 buffet_bus="BodyBuffet_"+str(get_instance_id());index=AudioServer.bus_count;AudioServer.add_bus();AudioServer.set_bus_name(index,buffet_bus)
 var body_filter=AudioEffectLowPassFilter.new();body_filter.cutoff_hz=180;AudioServer.add_bus_effect(index,body_filter)
 players["buffet"]=make_player("res://assets/v4/buffet.wav",true);players.buffet.bus=buffet_bus
func make_player(path: String,looped: bool) -> AudioStreamPlayer:
 var player=AudioStreamPlayer.new();var source=load(path) as AudioStreamWAV
 if not source:return player
 var stream=source.duplicate()
 if looped:stream.loop_mode=AudioStreamWAV.LOOP_FORWARD;stream.loop_end=stream.data.size()/2
 player.stream=stream;player.bus=bus_name;player.volume_db=-80;add_child(player)
 if looped:player.play()
 return player
func gain(player: AudioStreamPlayer,value: float,dt: float) -> void:
 var target=linear_to_db(maxf(.0001,value));player.volume_db=lerpf(player.volume_db,target,1-exp(-14*dt))
func _process(dt: float) -> void:
 if not car:return
 AudioServer.set_bus_mute(bus,muted or get_tree().paused)
 AudioServer.set_bus_mute(AudioServer.get_bus_index(flow_bus),muted or get_tree().paused)
 AudioServer.set_bus_mute(AudioServer.get_bus_index(buffet_bus),muted or get_tree().paused)
 flow_filter.cutoff_hz=lerpf(700,3200 if interior else 11000,clampf(car.speed_kph/340,0,1))
 gain(players.buffet,(absf(car.road_vibration)*.02+pow(car.speed_kph/340,3)*.06)*(.9 if interior else .3),dt)
 var lowpass=AudioServer.get_bus_effect(bus,0);lowpass.cutoff_hz=lerpf(lowpass.cutoff_hz,2600 if interior else 12000,1-exp(-8*dt))
 mix_load=lerpf(mix_load,car.engine_load,1-exp(-12*dt))
 var weights=[];var total=0.0
 for layer in layers:
  var ratio=maxf(car.rpm,350)/layer.rpm
  var weight=maxf(0,1-absf(log(ratio))/.57);weights.append(weight);total+=weight
 for i in range(layers.size()):
  var layer=layers[i];layer.player.pitch_scale=clampf(maxf(car.rpm,350)/layer.rpm,.5,2.0)
  var load_gain=sqrt(mix_load) if layer.load else sqrt(1-mix_load)*.68
  var amp=weights[i]/maxf(total*.5,.001)*load_gain*.85*(1 if car.engine_on else 0)
  gain(layer.player,amp,dt)
 gain(players.wind,pow(car.speed_kph/330,2.7)*(.42 if interior else .64),dt)
 players.wind.pitch_scale=lerpf(.55,1.8,clampf(car.speed_kph/340,0,1))
 players.whine.pitch_scale=clampf(car.rpm/4500,.35,2.3)
 gain(players.whine,(.025+.075*car.engine_load)*minf(car.speed_kph/80,1)*(0.2 if car.shift_cut else 1),dt)
 gain(players.roll,car.speed_kph/330*.18*(2 if car.wheels[0].surface=="grass" else 1),dt)
 players.roll.pitch_scale=(.7 if car.wheels[0].surface=="grass" else 1.0)*lerpf(.65,1.85,clampf(car.speed_kph/340,0,1))
 gain(players.tire,clampf((car.max_slip-.15)*.65,0,.4)*minf(car.speed_kph/35,1),dt)
 players.tire.pitch_scale=clampf(1+car.max_slip*.18,.8,1.7)
 gain(players.rain,.14 if car.wetness>.5 else 0,dt)
 gain(players.horn,.28 if GTControls.value("horn")>.5 and car.controls_enabled else 0,dt)
 if car.shift_timer<=0 and last_shift>0:players.shift.volume_db=-15;players.shift.play()
 if car.shift_timer>0 and last_shift<=0:players.gear.volume_db=-12;players.gear.play()
 last_shift=car.shift_timer
 if car.engine_on!=last_engine_on:
  var event=players.starter if car.engine_on else players.stall;event.volume_db=-11;event.play()
 last_engine_on=car.engine_on
 if car.collision_energy>.2 and not players.impact.playing:players.impact.volume_db=linear_to_db(car.collision_energy*.6);players.impact.play()
func _exit_tree() -> void:
 for name in [bus_name,flow_bus,buffet_bus]:
  var index=AudioServer.get_bus_index(name)
  if index>=0:AudioServer.remove_bus(index)
