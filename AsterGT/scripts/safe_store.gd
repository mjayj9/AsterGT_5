class_name GTSafeStore
extends RefCounted
static var helper_ready: bool=false
static func save_json(file: String,data: Dictionary) -> Error:
 var f=FileAccess.open(file+".tmp",FileAccess.WRITE)
 if not f:return FileAccess.get_open_error()
 f.store_string(JSON.stringify(data,"  "));f.flush()
 var err=f.get_error();f.close()
 if err!=OK:return err
 var source=ProjectSettings.globalize_path(file+".tmp");var target=ProjectSettings.globalize_path(file)
 if OS.get_name()=="Windows":
  # Godot 4.6 DirAccessWindows removes the target before renaming; use ReplaceFileW.
  var helper="user://runtime-tools/AtomicReplace-v4.exe"
  if not helper_ready:
   err=DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("user://runtime-tools"))
   if err!=OK:return err
   var bytes=FileAccess.get_file_as_bytes("res://runtime_tools/AtomicReplace.exe")
   if bytes.is_empty():return ERR_FILE_NOT_FOUND
   var binary=FileAccess.open(helper,FileAccess.WRITE)
   if not binary:return FileAccess.get_open_error()
   binary.store_buffer(bytes);binary.flush();err=binary.get_error();binary.close()
   if err!=OK:return err
   helper_ready=true
  var result=OS.execute(ProjectSettings.globalize_path(helper),PackedStringArray([source,target]),[],true,false)
  return OK if result==0 else ERR_FILE_CANT_WRITE
 return DirAccess.rename_absolute(source,target)
static func quarantine(file: String) -> Error:
 if not FileAccess.file_exists(file):return OK
 return DirAccess.rename_absolute(ProjectSettings.globalize_path(file),ProjectSettings.globalize_path(file+".corrupt-"+str(Time.get_unix_time_from_system())+".bak"))
