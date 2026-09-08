from pathlib import Path
p=Path('outputs/AsterGT/tests/dynamics_test.gd');s=p.read_text(encoding='utf-8').replace(' car.test_input={}\nfunc check',' car.test_input={}\n await frames(2)\nfunc check');p.write_text(s,encoding='utf-8')
