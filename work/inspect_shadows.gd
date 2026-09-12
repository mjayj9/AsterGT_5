extends SceneTree
func _initialize():
 for m in ClassDB.class_get_method_list("RenderingServer"):
  if m.name in ["directional_shadow_atlas_set_size","directional_soft_shadow_filter_set_quality"]:print(m)
 quit()
