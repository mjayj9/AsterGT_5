from pathlib import Path
p=Path('outputs/AsterGT')
f=p/'scripts/vehicle_config.gd';s=f.read_text(encoding='utf-8').replace('@export var mass_kg:', '''@export var center_of_mass: Vector3 = Vector3(0,-0.12,0.05)
@export var inertia_at_reference_mass: Vector3 = Vector3(640,2350,650)
@export var reference_mass: float = 1520.0
@export var steering_speed_factor: float = 0.072
@export var longitudinal_stiffness: float = 9.0
@export var lateral_stiffness: float = 7.0
@export var locked_grip_loss: float = 0.35
@export var drivetrain_efficiency: float = 0.92
@export var air_density: float = 1.225
@export var creep_throttle: float = 0.10
@export var parking_brake_torque: float = 6200.0
@export var esc_yaw_gain: float = 1900.0
@export var esc_max_torque: float = 2800.0
@export var mass_kg:''');f.write_text(s,encoding='utf-8')
f=p/'scripts/car.gd';s=f.read_text(encoding='utf-8').replace('center_of_mass=Vector3(0,-0.12,0.05)','center_of_mass=cfg.center_of_mass').replace('inertia=Vector3(640,2350,650)','inertia=cfg.inertia_at_reference_mass*cfg.mass_kg/cfg.reference_mass')
s=s.replace('mass=cfg.mass_kg\n var basis','if mass!=cfg.mass_kg:\n  mass=cfg.mass_kg;inertia=cfg.inertia_at_reference_mass*cfg.mass_kg/cfg.reference_mass\n var basis')
s=s.replace('absf(forward_speed)*0.072','absf(forward_speed)*cfg.steering_speed_factor').replace('maxf(throttle,0.10)','maxf(throttle,cfg.creep_throttle)').replace('torque*ratio*0.92','torque*ratio*cfg.drivetrain_efficiency').replace('maxf(brake_demand,6200)','maxf(brake_demand,cfg.parking_brake_torque)').replace('tanh(lat_angle*7.0)','tanh(lat_angle*cfg.lateral_stiffness)').replace('tanh(slip*9.0)*(1.0-.35*','tanh(slip*cfg.longitudinal_stiffness)*(1.0-cfg.locked_grip_loss*').replace('*0.5*1.225*cfg.drag_area','*0.5*cfg.air_density*cfg.drag_area')
s=s.replace('var target_yaw=forward_speed*tan(steer_angle)/cfg.wheelbase','''var target_yaw=forward_speed*tan(steer_angle)/cfg.wheelbase
 var yaw_limit=9.81*minf(cfg.grip_front,cfg.grip_rear)*(1-wetness*.33)/maxf(absf(forward_speed),1.0)
 target_yaw=clampf(target_yaw,-yaw_limit,yaw_limit)''').replace('(target_yaw-yaw)*1900*cfg.esc_strength,-2800,2800','(target_yaw-yaw)*cfg.esc_yaw_gain*cfg.esc_strength,-cfg.esc_max_torque,cfg.esc_max_torque');f.write_text(s,encoding='utf-8')
f=p/'tests/dynamics_test.gd';s=f.read_text(encoding='utf-8').replace('await reset();car.test_input={"throttle":1.0};var maxspeed','await frames(180)\n check("high_speed_corner_stays_upright",car.global_basis.y.dot(Vector3.UP)>.8 and absf(car.angular_velocity.y)<1.2)\n await reset();car.test_input={"throttle":1.0};var maxspeed');f.write_text(s,encoding='utf-8')
