import {asset} from './urls.js';
import * as THREE from 'three';

function parameterTexture(values){
  const data=new Float32Array(40*13*4);
  for(let y=0;y<13;y++)for(let x=0;x<40;x++){
    const rgb=values[y][x];const i=(y*40+x)*4;
    data.set([rgb[0]/255,rgb[1]/255,rgb[2]/255,1],i);
  }
  const texture=new THREE.DataTexture(data,40,13,THREE.RGBAFormat,THREE.FloatType);
  texture.minFilter=texture.magFilter=THREE.NearestFilter;texture.needsUpdate=true;
  return texture;
}

export async function createSurfaceMaterial(uniforms){
  const response=await fetch(asset('material-calibration.json'));
  if(!response.ok)throw new Error('Material calibration unavailable');
  const data=await response.json();
  const lighting=await fetch(asset('lighting-calibration.json')).then(r=>r.json());
  const pulse=data.clickResponseFit;
  const refinement=data.clickPeakRefinement;
  Object.assign(uniforms,{
    uLightAgeAdvance:{value:new THREE.Vector4(...[408,562,637,776].map(f=>refinement.lightAgeAdvanceSeconds[f]))},
    uEarlyBoost:{value:refinement.boostAmount},
    uPulseGain:{value:parameterTexture(pulse.pulseGainRGB)},
    uPulseFront:{value:new THREE.Vector4(pulse.initialRadius720Px,pulse.speed720PxPerSecond,pulse.aheadSigma720Px,pulse.aheadSigmaGrowth720PxPerSecond)},
    uPulseBack:{value:new THREE.Vector4(pulse.behindWidth720Px,pulse.behindWidthGrowth720PxPerSecond,pulse.behindPower,pulse.growthSeconds)},
    uIdlePalette:{value:parameterTexture(data.idleCenterRGB)},
    uSeamPalette:{value:parameterTexture(data.hoverSeamResponseFit.idleFloorRGB)},
    uSeamBase:{value:parameterTexture(data.hoverSeamResponseFit.baseDeltaRGB)},
    uSeamRadial:{value:parameterTexture(data.hoverSeamResponseFit.radialDeltaRGB)},
    uHoverBase:{value:parameterTexture(data.hoverResponseFit.baseDeltaRGB)},
    uHoverRadial:{value:parameterTexture(data.hoverResponseFit.radialDeltaRGB)},
    uPitch:{value:new THREE.Vector2(...data.lattice.pitch720)},
    uOrigin:{value:new THREE.Vector2(data.lattice.origin720[0]-360,270-data.lattice.origin720[1])},
    uSigma:{value:data.hoverResponseFit.sigma720Px},
    // Inverse lighting calibration maps measured sRGB to material albedo. Lighting
    // still runs through MeshPhysicalMaterial; these constants are measured by
    // rendering black and grey swatches under the same lights.
    uLightingGain:{value:new THREE.Vector3(...lighting.linearGain)},
    uLightingFloor:{value:new THREE.Vector3(...lighting.linearFloor)},
    uCalibration:{value:-1},
    uSeamWidth:{value:1.04},
  });
  const material=new THREE.MeshPhysicalMaterial({color:0xffffff,roughness:.72,metalness:0,clearcoat:0,specularIntensity:.15});
  material.onBeforeCompile=shader=>{
    Object.assign(shader.uniforms,uniforms);
    shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vLocal;');
    shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvLocal=position;');
    shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`#include <common>
      varying vec3 vLocal;
      uniform float uTime,uHover,uSigma,uCalibration,uSeamWidth;
      uniform vec2 uPointer,uPitch,uOrigin;
      uniform vec3 uLightingGain,uLightingFloor;
      uniform vec4 uClicks[4],uPulseFront,uPulseBack,uLightAgeAdvance;
      uniform float uClickProfiles[4],uEarlyBoost;
      uniform sampler2D uIdlePalette,uSeamPalette,uSeamBase,uSeamRadial,uHoverBase,uHoverRadial,uPulseGain;
      vec3 sourceToLinear(vec3 c){return mix(c/12.92,pow((c+.055)/1.055,vec3(2.4)),step(vec3(.04045),c));}
    `);
    shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
      vec2 grid=vec2(vLocal.x-uOrigin.x,uOrigin.y-vLocal.y)/uPitch;
      vec2 cell=floor(grid),f=fract(grid);
      vec2 sampleUV=(clamp(cell,vec2(0.),vec2(39.,12.))+.5)/vec2(40.,13.);
      vec3 idle=texture2D(uIdlePalette,sampleUV).rgb;
      vec3 baseDelta=texture2D(uHoverBase,sampleUV).rgb;
      vec3 radialDelta=texture2D(uHoverRadial,sampleUV).rgb;
      vec2 center=uOrigin+vec2((cell.x+.5)*uPitch.x,-(cell.y+.5)*uPitch.y);
      float distanceToPointer=length(center-uPointer);
      float hotspot=exp(-distanceToPointer*distanceToPointer/(2.*uSigma*uSigma));
      vec3 face=idle+uHover*(baseDelta+radialDelta*hotspot);
      float clickWave=0.;
      for(int i=0;i<4;i++){
        float eventAge=uTime-uClicks[i].z;
        float age=eventAge+uLightAgeAdvance[int(uClickProfiles[i])];
        float safeAge=max(age,0.);
        float radius=uPulseFront.x+uPulseFront.y*age;
        float ahead=uPulseFront.z+uPulseFront.w*safeAge;
        float behind=uPulseBack.x+uPulseBack.y*safeAge;
        float d=length(center-uClicks[i].xy),offset=d-radius;
        float band=offset>=0.?exp(-offset*offset/(2.*ahead*ahead)):exp(-pow(-offset/behind,uPulseBack.z));
        float envelope=1.-exp(-safeAge/uPulseBack.w);
        float earlyBoost=1.+uEarlyBoost*smoothstep(.005,.04,safeAge)*(1.-smoothstep(.15,.27,safeAge));
        clickWave+=band*envelope*earlyBoost*step(0.,eventAge)*step(0.,age)*(1.-smoothstep(1.,1.25,age))*uClicks[i].w;
      }
      vec3 pulseGain=texture2D(uPulseGain,sampleUV).rgb;
      face+=pulseGain*clickWave;
      vec2 seamPhase=fract(grid+vec2(.13,.014)/uPitch);
      vec2 edge=min(seamPhase,1.-seamPhase)*uPitch;
      float edgeDistance=min(edge.x,edge.y);
      vec2 footprint=fwidth(grid)*uPitch;
      float aa=max(footprint.x,footprint.y)*.5;
      float seam=1.-smoothstep(uSeamWidth*.5-aa,uSeamWidth*.5+aa,edgeDistance);
      vec3 seamIdle=texture2D(uSeamPalette,sampleUV).rgb;
      vec3 seamBase=texture2D(uSeamBase,sampleUV).rgb;
      vec3 seamRadial=texture2D(uSeamRadial,sampleUV).rgb;
      vec3 seamRGB=seamIdle+uHover*(seamBase+seamRadial*hotspot)+seamRadial*clickWave*.8;
      vec3 desired=clamp(mix(face,seamRGB,seam),0.,1.);
      diffuseColor.rgb=max((sourceToLinear(desired)-uLightingFloor)/uLightingGain,0.);
      if(uCalibration>=0.)diffuseColor.rgb=vec3(uCalibration);
    `);
  };
  return material;
}
