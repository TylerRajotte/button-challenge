import profiles from '../public/click-profiles.json';
// All variants use measured silhouette envelopes. The default interactive click
// uses the third full press; replay also preserves the shorter first press.
export function clickCompression(age,profile=2){
  const curve=profiles[profile]?.curve??profiles[2].curve;
  if(age<0||age>curve.at(-1).dt+.035)return 0;
  const at=curve.findIndex(p=>p.dt>=age);
  if(at<0)return (1-(curve.at(-1).scaleX+curve.at(-1).scaleY)/2)*Math.max(0,1-(age-curve.at(-1).dt)/.035);
  const b=curve[at],a=curve[Math.max(0,at-1)];
  const mix=a.dt===b.dt?0:(age-a.dt)/(b.dt-a.dt);
  return 1-((a.scaleX+a.scaleY)*(1-mix)+(b.scaleX+b.scaleY)*mix)/2;
}
