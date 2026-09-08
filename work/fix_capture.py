from pathlib import Path
p=Path('outputs/AsterGT/scripts/main.gd');s=p.read_text(encoding='utf-8').replace(' await RenderingServer.frame_post_draw\n DirAccess.make_dir_recursive_absolute',' RenderingServer.force_draw(false)\n DirAccess.make_dir_recursive_absolute');p.write_text(s,encoding='utf-8')
