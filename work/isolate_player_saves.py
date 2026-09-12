from pathlib import Path
p=Path('outputs/AsterGT')
f=p/'scripts/main.gd';s=f.read_text(encoding='utf-8').replace('var qa_mode: String=""','var automation_run: bool=false\nvar qa_mode: String=""')
s=s.replace('process_mode=Node.PROCESS_MODE_ALWAYS\n GTControls.initialize()', '''process_mode=Node.PROCESS_MODE_ALWAYS
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--qa") or arg.begins_with("--benchmark") or arg.begins_with("--capture") or arg=="--test-profile":automation_run=true
 GTControls.initialize()''')
s=s.replace('func save_records() -> void:\n','func save_records() -> void:\n if automation_run:return\n')
s=s.replace('func save_preferences() -> void:\n','func save_preferences() -> void:\n if automation_run:return\n')
f.write_text(s,encoding='utf-8')
f=p/'project.godot';s=f.read_text(encoding='utf-8').replace('config/name="ASTER — Grand Tour"','config/name="ASTER — Grand Tour"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="AsterGT"');f.write_text(s,encoding='utf-8')
