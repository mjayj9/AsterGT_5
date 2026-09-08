from pathlib import Path
p=Path('outputs/AsterGT/scripts/car.gd')
s=p.read_text();s=s.replace('linear_damp=0; angular_damp=0.25','linear_damp=0; linear_damp_mode=RigidBody3D.DAMP_MODE_REPLACE; angular_damp=0.25; angular_damp_mode=RigidBody3D.DAMP_MODE_REPLACE')
s=s.replace('if shift_timer>0: target_rpm=maxf(cfg.idle_rpm,rpm-4500*dt)','if shift_timer>0: target_rpm=maxf(cfg.idle_rpm,axle_rpm if (automatic or rev_match) else rpm-900)')
s=s.replace('if rpm>up_at and gear<6 and engagement>0.9:', 'if rpm>up_at and gear<6 and engagement>0.9 and brake<0.05 and throttle>0.05:')
s=s.replace('grounded=0;max_slip=0;abs_active=false','grounded=0;max_slip=0;abs_active=false\n var omega_snapshot: Array[float]=[]\n for w in wheels:omega_snapshot.append(w.omega)')
s=s.replace('var partner=wheels[i^1].omega','var partner=omega_snapshot[i^1]')
p.write_text(s)
