shader_type spatial;
render_mode blend_mix, depth_draw_never, cull_back;
uniform mat4 mesh_to_body;
uniform int patch_count=0;
uniform vec4 hits[16];
uniform vec4 directions[16];
uniform vec4 axes[16];
uniform vec4 channels[16];
uniform bool composite_body=true;
varying vec3 body_pos;
varying vec3 body_normal;
float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 p){vec2 i=floor(p);vec2 f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
void vertex(){
 body_pos=(mesh_to_body*vec4(VERTEX,1.0)).xyz;
 body_normal=normalize(transpose(inverse(mat3(mesh_to_body)))*NORMAL);
 VERTEX+=NORMAL*0.0007;
}
void fragment(){
 vec3 color=vec3(0);float opacity=0.0;float metal=0.0;
 for(int i=0;i<patch_count;i++){
  vec3 delta=body_pos-hits[i].xyz;float radius=hits[i].w;
  if(length(delta)>radius || dot(normalize(body_normal),directions[i].xyz)<0.12)continue;
  vec3 side=normalize(cross(directions[i].xyz,axes[i].xyz));
  vec2 uv=vec2(dot(delta,axes[i].xyz),dot(delta,side))/radius;
  float edge=1.0-smoothstep(0.58,1.0,length(delta)/radius);
  float grain=noise(uv*37.0+float(i)*7.0);
  // Broad dragged scuffs, not microscopic clearcoat scratches.
  float bands=smoothstep(0.61,0.78,noise(vec2(uv.x*2.2,uv.y*44.0)));
  float scuff=bands*edge*channels[i].x*(1.0-smoothstep(.22,.52,abs(uv.y)));
  float chip=smoothstep(.74-channels[i].y*.10,.81-channels[i].y*.10,grain)*edge*channels[i].y;
  // Jagged branching fracture through a composite/plastic bumper skin.
  float angle=atan(uv.y,uv.x);float r=length(uv);
  float branch=abs(sin(angle*2.5+sin(r*24.0)*.19+float(i)))*r;
  float crack=(1.0-smoothstep(.009,.025,branch))*smoothstep(.04,.10,r)*(1.0-smoothstep(.25+channels[i].w*.40,.42+channels[i].w*.44,r))*channels[i].w;
  vec3 substrate=(directions[i].w>.5 || composite_body)?vec3(.055,.065,.067):vec3(.38,.40,.41);
  float alpha=max(max(scuff*.8,chip*.98),crack);
  vec3 paint_mark=mix(vec3(.27,.30,.29),substrate,chip/max(.001,max(chip,scuff)));
  paint_mark=mix(paint_mark,vec3(.007,.009,.010),crack);
  color=mix(color,paint_mark,alpha/max(.001,alpha+opacity));opacity=max(opacity,alpha);
  metal=max(metal,(!composite_body && directions[i].w<.5)?chip*.65:0.0);
 }
 if(opacity<.035)discard;
 ALBEDO=color;ALPHA=opacity;ROUGHNESS=.90;METALLIC=metal;
}
