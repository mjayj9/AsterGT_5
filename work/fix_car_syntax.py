from pathlib import Path
f=Path('outputs/AsterGT/scripts/car.gd');s=f.read_text(encoding='utf-8-sig');s=s.replace('func build_visuals()\n cache_details() -> void:','func build_visuals() -> void:');f.write_text(s,encoding='utf-8')
