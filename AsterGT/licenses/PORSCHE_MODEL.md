# Porsche 992 GT3 R — model attribution and changes

Model: **porsche_992_gt3_r**, by **MattDoesBlender**.

- Author: https://sketchfab.com/MattDoesBlender
- Source: https://sketchfab.com/3d-models/porsche-992-gt3-r-03ea07f7972648aa9350853b2a1a942a
- License: **Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International (CC BY-NC-SA 4.0)** — https://creativecommons.org/licenses/by-nc-sa/4.0/
- Legal code: https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode

The user supplied `2024-porsche-992-gt3-r.zip`. The author, source and license above are recorded in the original GLB asset.extras metadata. The modified model and its packed Blender source are provided under the same CC BY-NC-SA 4.0 license. Credit the author, link the license, indicate modifications, use the licensed material only for noncommercial purposes, and distribute adaptations under the same license. This is not a commercial-use asset clearance. Brand names and marks belong to their respective owners; no affiliation or endorsement is claimed.

Modifications made for ASTER GT on 2026-09-09: scene transform converted to meters and Godot orientation; four wheel/disc pivots, separate caliper pivots and steering pivot; eight redundant static/blur rim nodes omitted from the active scene; missing material colors and PBR scalar parameters adjusted; runtime axle mount symmetry, suspension, rotation, steering, lights and dashboard integration; sunstrip/banner meshes hidden only in cockpit view. The original vertex/index/UV/normal/image BIN buffer is retained byte for byte in the adapted GLB. No body redesign or remeshing was performed.

Files: `assets/porsche_992_gt3_r.glb`, `assets/porsche_rig.json`, `blender/porsche_992_gt3_r_rigged.blend`, and the model embedded in the Windows executable. The rest of the project has separate provenance described in ASSET_SOURCES.md; the model's license must not be confused with Godot's MIT license.

한국어 안내: 업로드된 차량의 메타데이터에 저작자표시·비영리·동일조건변경허락 조건이 있습니다. 이 차량이 포함된 게임/수정 모델을 상업 용도로 사용하려면 해당 권리를 별도로 확보해야 합니다. 원저작자·원본 링크·라이선스·수정 내역을 함께 보존하십시오.

## v4 modifications

BlenderMCP used for 4.619m length / 2.507m wheelbase correction, wheel radius / symmetric pivots and fixed suspension references, PBR scalar correction, normal/tangent export, material/mesh consolidation, four LODs, six compound convex proxies and four-direction damage morphs. New files: assets/v4/porsche_lod0.glb through porsche_lod3.glb and blender/v4/porsche_gt3_v4.blend. Original vehicle files remain preserved. These adaptations retain MattDoesBlender credit, the source link and CC BY-NC-SA 4.0 (noncommercial, attribution, share-alike).
