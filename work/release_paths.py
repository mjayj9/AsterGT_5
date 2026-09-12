from pathlib import Path
p=Path('outputs/AsterGT/scripts/main.gd');s=p.read_text(encoding='utf-8').replace('var qa_mode: String=""','var qa_mode: String=""\nvar qa_directory: String="res://tests"')
s=s.replace('for argument in OS.get_cmdline_user_args():','if not OS.has_feature("editor"):qa_directory="user://qa"\n for argument in OS.get_cmdline_user_args():\n  if argument.begins_with("--qa-output="):qa_directory=argument.trim_prefix("--qa-output=")')
s=s.replace('var image=get_viewport().get_texture().get_image();image.save_png("res://tests/"+label+".png")\n print("CAPTURED ",label)','''DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(qa_directory))
 var image=get_viewport().get_texture().get_image();var error=image.save_png(qa_directory+"/"+label+".png")
 print("CAPTURED " if error==OK else "CAPTURE_FAILED ",label," ",error)''')
s=s.replace('FileAccess.open("res://tests/"+qa_mode+".json",FileAccess.WRITE)','FileAccess.open(qa_directory+"/"+qa_mode+".json",FileAccess.WRITE)')
p.write_text(s,encoding='utf-8')
