from pathlib import Path
p=Path(r'C:/Users/admin/Documents/Codex/2026-09-08/fable-5-1-vs-fable-at-4-pre-qa/outputs/AsterGT')
t=p/'tests/preqa/contact_regression.gd';s=t.read_text();s=s.replace('for fixture in case.pair:fixture.other.queue_free()','for fixture in case.pair:\n   fixture.other.queue_free();fixture.physics.free()');t.write_text(s,encoding='utf8')
