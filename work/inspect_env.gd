extends SceneTree
func _initialize():
 for name in ClassDB.class_get_integer_constant_list("Environment"):
  if "REFLECT" in name:print(name," = ",ClassDB.class_get_integer_constant("Environment",name))
 quit()
