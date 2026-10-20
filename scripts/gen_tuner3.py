# -*- coding: utf-8 -*-
"""生成单胞体调参页 tuner.html —— 直接复用正式页渲染管线"""
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'index.html'
OUT = SRC.with_name('tuner.html')

html = SRC.read_text(encoding='utf-8')

# 错误捕获必须最先注入
ERR_HOOK = '<script>window.__ERRS__=[];window.addEventListener("error",function(e){window.__ERRS__.push((e.message||"")+" @"+(e.filename||"")+":"+(e.lineno||0));});</script>'
html = html.replace('<head>', '<head>' + ERR_HOOK, 1)

CSS = """
<style id="tuner-style">
  header, footer, main, nav, aside, #scroll-cue, #readout, #intro, #intro-skip, #progress,
  #footer-vision, #fallback-content, #motion-notice, #quiet-glow, #unit-layer, #unit-leader,
  #language-toast, .section-float, .cluster-index, .info-dialog, .topbar, .footer {
    visibility: hidden !important; pointer-events: none !important;
  }
  body { background:#02060f !important; }
  #tuner-panel {
    position:fixed; top:16px; right:16px; z-index:99999;
    width:286px; padding:14px 16px; border-radius:10px;
    background:rgba(6,18,28,.93); border:1px solid rgba(45,224,106,.28);
    color:#cfe6dc; font:12px/1.5 ui-monospace,Consolas,monospace;
    backdrop-filter:blur(8px); box-shadow:0 10px 40px rgba(0,0,0,.55);
  }
  #tuner-panel h3 { margin:0 0 10px; font-size:12px; letter-spacing:1px; color:#2de06a; font-weight:600; }
  #tuner-panel .row { margin:9px 0; }
  #tuner-panel .row label { display:flex; justify-content:space-between; margin-bottom:3px; color:#8fb3a5; }
  #tuner-panel .row label b { color:#eafff5; font-weight:600; }
  #tuner-panel input[type=range] { width:100%; accent-color:#2de06a; height:16px; }
  #tuner-panel .hint { margin-top:10px; color:#5d7d70; font-size:11px; line-height:1.45; }
  #tuner-panel button {
    margin-top:10px; width:100%; padding:6px; border-radius:6px; cursor:pointer;
    background:rgba(45,224,106,.12); border:1px solid rgba(45,224,106,.35); color:#9bf7c4;
    font:11px ui-monospace,monospace;
  }
  #tuner-panel button:hover { background:rgba(45,224,106,.22); }
</style>
"""
html = html.replace('</head>', CSS + '</head>', 1)

HASH = """
    // ===== TUNER: hash 参数覆盖 =====
    (function(){
      const H = new URLSearchParams(location.hash.slice(1));
      const num = function(k, fb){ const v = parseFloat(H.get(k)); return Number.isFinite(v) ? v : fb; };
      form.ringTubeRadius = num('tube', form.ringTubeRadius);
      form.rootRingRatio = 5.5;
      form.contactAngle = THREE.MathUtils.clamp(num('angle',90),35,145);
      form.contactSmooth = THREE.MathUtils.clamp(num('smooth',.5),0,1);
      form.tipRadius      = num('tip', form.tipRadius);
      form.ringScale      = num('scale', form.ringScale);
      window.__TUNER__ = { tube: form.ringTubeRadius, angle: form.contactAngle, smooth: form.contactSmooth, tip: form.tipRadius, scale: form.ringScale };
    })();
"""
anchor = "const growthRandom=netSeeded(NET_CONFIG.seed),form=NET_CONFIG.form;"
html = html.replace(anchor, anchor + "\n" + HASH, 1)

# v2: landing stays fixed, only outgoing direction changes.
html = html.replace('ringTube=b.radius*form.ringTubeRadius,lead=.18;', 'ringTube=b.radius*form.ringTubeRadius,lead=THREE.MathUtils.lerp(.06,.42,form.contactSmooth);')
html = html.replace('const frame=b.membraneFrame,start=frame.point.clone().addScaledVector(frame.out,.12),root=start.clone().addScaledVector(frame.out,lead),tangent=frame.out;', 'const frame=b.membraneFrame,tangent=frame.out.clone().applyAxisAngle(frame.z,THREE.MathUtils.degToRad(form.contactAngle-90)),start=frame.point.clone().addScaledVector(frame.out,.12),root=start.clone().addScaledVector(tangent,lead);b.contactDirection=tangent;b.contactStart=start;')
html = html.replace('handle=root.distanceTo(end)*.34;', 'handle=root.distanceTo(end)*THREE.MathUtils.lerp(.18,.62,form.contactSmooth);')
html = html.replace('b.lead=neck.getLength();b.root=root;', 'b.lead=neck.getLength();b.root=root;b.contactMetrics={lead,neckLength:neck.getLength(),collarLength:collar.getLength(),handle,handleRatio:THREE.MathUtils.lerp(.18,.62,form.contactSmooth),landing:frame.point.toArray(),direction:tangent.toArray()};')
html = html.replace('d1=b.membraneFrame.out.clone().multiplyScalar(.12)', 'd1=b.contactDirection.clone().multiplyScalar(THREE.MathUtils.lerp(.06,.42,form.contactSmooth))')
html = html.replace('lead+.06])', 'lead+.06,...Array.from({length:65},(_,i)=>i/64)])')
html = html.replace('path.frame.normal.clone():', 'path.frame.normal.clone().addScaledVector(tangents[0],-path.frame.normal.dot(tangents[0])).normalize():')

# 原生成段逐字封装，随机流及累积数组每次新建。
start=html.index("    const growthRandom=netSeeded(NET_CONFIG.seed),form=NET_CONFIG.form;")
end=html.index("    // 编排状态按簇固定分配",start)
generation=html[start:end].replace("const growthRandom=netSeeded(NET_CONFIG.seed),form=NET_CONFIG.form;","const growthRandom=netSeeded(NET_CONFIG.seed);").replace(HASH, "")
names="growthRandom,networkPaths,linePositions,lineDistances,lineRoots,lineClusters,lineRoutes,lineBridges,lineLevels,unitAttachments,terminalStars,clusterSomas,somaBranches,connections,contentSomas,membraneJunctions,membraneRanges,unitWorld,L,rootCount,maxDepth"
html=html[:start]+"    const form=NET_CONFIG.form;\n"+HASH+"\nfunction generateNetwork(){\n"+generation+"\nreturn {"+names+"};\n}\nlet {"+names+"}=generateNetwork();\n"+html[end:]
a=html.index("      const lg=new THREE.BufferGeometry();")
b=html.index("      const lmat=new THREE.ShaderMaterial",a)
packing=html[a:b]
# 几何打包外壳：与原1e-10量化键完全等价，避免每顶点切片/字符串/属性枚举。
wa=packing.index('      const welded=new Map()')
wb=packing.index('      lg.setIndex(indices);',wa)+len('      lg.setIndex(indices);')
packing=packing[:wa]+"""
      const attributes=Object.entries(lg.attributes),count=lg.attributes.position.count;
      const unique=attributes.map(([name,attr])=>new Float32Array(count*attr.itemSize));
      const indices=new Uint32Array(count),buckets=new Map(),next=new Int32Array(count),coords=new Float64Array(count*3);let uniqueCount=0;
      for(let i=0;i<count;i++){
        const x=Math.round(linePositions[i*3]*1e10),y=Math.round(linePositions[i*3+1]*1e10),z=Math.round(linePositions[i*3+2]*1e10);
        const hash=(Math.imul(x|0,73856093)^Math.imul(y|0,19349663)^Math.imul(z|0,83492791))>>>0;
        let index=buckets.get(hash);if(index===undefined)index=-1;
        while(index!==-1&&(coords[index*3]!==x||coords[index*3+1]!==y||coords[index*3+2]!==z))index=next[index];
        if(index===-1){index=uniqueCount++;next[index]=buckets.get(hash)??-1;buckets.set(hash,index);coords.set([x,y,z],index*3);
          for(let a=0;a<attributes.length;a++){const attr=attributes[a][1],size=attr.itemSize;for(let j=0;j<size;j++)unique[a][index*size+j]=attr.array[i*size+j];}
        }
        indices[i]=index;
      }
      attributes.forEach(([name,attr],i)=>lg.setAttribute(name,new THREE.BufferAttribute(unique[i].subarray(0,uniqueCount*attr.itemSize),attr.itemSize)));
      lg.setIndex(new THREE.BufferAttribute(uniqueCount>65535?indices:new Uint16Array(indices),1));
"""+packing[wb:]
html=html[:a]+"function packNetwork(){\n"+packing+"return lg;\n}\nconst lg=packNetwork();\n"+html[b:]
rebuild="""
window.__TUNER_METRICS__={builds:[],renders:0,details:[]};
function buildNetwork(overrides={}){
 const started=performance.now();Object.assign(form,overrides);form.rootRingRatio=5.5;
 ({NAMES}=generateNetwork());
 const generated=performance.now();const geometry=packNetwork(),old=lines.geometry;const packed=performance.now();
 lines.geometry=geometry;old.dispose();
 for(const attr of Object.values(points.geometry.attributes))attr.needsUpdate=true;
 Object.assign(window.__TUNER__,{tube:form.ringTubeRadius,angle:form.contactAngle,smooth:form.contactSmooth,tip:form.tipRadius,scale:form.ringScale});
 if(composer)composer.render();else renderer.render(scene,camera);
 const ms=performance.now()-started;
 window.__TUNER_METRICS__.details.push({ms,generate:generated-started,pack:packed-generated});window.__TUNER_METRICS__.builds.push(ms);window.__TUNER_METRICS__.renders++;
 console.log('[tuner] rebuild '+ms.toFixed(2)+'ms; generate '+(generated-started).toFixed(2)+'; pack '+(packed-generated).toFixed(2));return ms;
}
window.__REBUILD__=buildNetwork;
""".replace('NAMES',names)
needle="const lines=new THREE.Mesh(lg,lmat);scene.add(lines);"
assert needle in html
html=html.replace(needle,needle+rebuild,1)

# 相机覆盖：正式页的相机由滚动驱动，调参页每帧强制对准第一个胞体
CAM_HOOK = """
window.__TUNER_CAM__ = { p: [-37, 19, 10], t: [-44, 15, -2] };
"""
html = html.replace("    const form=NET_CONFIG.form;", "    const form=NET_CONFIG.form;\n" + CAM_HOOK, 1)

cam_after = "viewTarget.copy(regularTarget).lerp(panoramaTarget,panoramaBlend);camera.lookAt(viewTarget);"
cam_patch = cam_after + "\n          if(window.__TUNER_CAM__){camera.position.set(window.__TUNER_CAM__.p[0],window.__TUNER_CAM__.p[1],window.__TUNER_CAM__.p[2]);viewTarget.set(window.__TUNER_CAM__.t[0],window.__TUNER_CAM__.t[1],window.__TUNER_CAM__.t[2]);camera.lookAt(viewTarget);}"
if cam_after in html:
    html = html.replace(cam_after, cam_patch, 1)
else:
    raise RuntimeError("相机钩子未匹配")

# 调试探针：暴露 scene/camera/renderer
dbg_anchor = "renderer=new THREE.WebGLRenderer("
if dbg_anchor in html:
    html = html.replace(
        "renderer.setAnimationLoop(",
        "window.__DBG__={get scene(){return scene},get camera(){return camera},get renderer(){return renderer},get composer(){return composer},get lines(){return lines},get network(){return {networkPaths,clusterSomas,membraneRanges,linePositions,lineDistances,lineRoots,lineClusters,lineRoutes,lineBridges,lineLevels}}};\n      renderer.setAnimationLoop(",
        1,
    )

PANEL = """
<div id="tuner-panel">
  <h3>NEURON TUNER</h3>
  <div class="row"><label>环粗细 ringTubeRadius <b id="v-tube"></b></label>
    <input id="s-tube" type="range" min="0.008" max="0.045" step="0.001"></div>
  <div class="row"><label>接触角度 contactAngle <b id="v-angle"></b></label>
    <input id="s-angle" aria-label="接触角度" type="range" min="35" max="145" step="1"></div>
  <div class="row"><label>接触平滑度 contactSmooth <b id="v-smooth"></b></label>
    <input id="s-smooth" aria-label="接触平滑度" type="range" min="0" max="1" step="0.01"></div>
  <div class="row"><label>枝末端 tipRadius <b id="v-tip"></b></label>
    <input id="s-tip" type="range" min="0.010" max="0.045" step="0.001"></div>
  <div class="row"><label>环大小 ringScale <b id="v-scale"></b></label>
    <input id="s-scale" type="range" min="1.00" max="1.45" step="0.01"></div>
  <button id="t-copy">复制当前参数</button>
  <div class="hint">拖动即重建，参数写进地址栏，可直接分享。</div>
</div>
<script>
window.addEventListener('load', function(){ setTimeout(function(){ window.scrollTo({top: 480, behavior:'instant'}); }, 900); });
(function(){
  function init(){
    var T = window.__TUNER__;
    if (!T || !window.__REBUILD__) { setTimeout(init, 120); return; }
    // 自驱动渲染：正式页的 setAnimationLoop 在剥离滚动后会停，这里手动跑
    setInterval(function(){
      var d = window.__DBG__;
      if (!d || !d.renderer) return;
      var cam = d.camera;
      cam.position.fromArray(window.__TUNER_CAM__.p);
      cam.lookAt(...window.__TUNER_CAM__.t);
      try { if (d.composer) d.composer.render(); else d.renderer.render(d.scene, cam); } catch(e) { window.__ERRS__.push(e.stack||String(e));console.error(e); }
    }, 33);
    var map = {tube:'v-tube', angle:'v-angle', smooth:'v-smooth', tip:'v-tip', scale:'v-scale'};
    var sliders = {tube:'s-tube', angle:'s-angle', smooth:'s-smooth', tip:'s-tip', scale:'s-scale'};
    var fmt = function(v){ return v < 1 ? v.toFixed(3) : v.toFixed(2); };
    var pending={},frame=0;
    var fields={tube:'ringTubeRadius',angle:'contactAngle',smooth:'contactSmooth',tip:'tipRadius',scale:'ringScale'};
    Object.keys(map).forEach(function(k){
      var el = document.getElementById(sliders[k]);
      el.value = T[k];
      document.getElementById(map[k]).textContent = k==='angle'?T[k]+'°':k==='smooth'?T[k].toFixed(2):fmt(T[k]);
      el.addEventListener('input', function(){
        var v = parseFloat(el.value);
        document.getElementById(map[k]).textContent = k==='angle'?v+'°':k==='smooth'?v.toFixed(2):fmt(v);
        T[k]=v;pending[fields[k]]=v;
        var H = new URLSearchParams(location.hash.slice(1));
        H.delete('ratio');Object.keys(fields).forEach(function(key){ H.set(key,T[key]); });
        history.replaceState(null,'','#'+H.toString());
        if(!frame)frame=requestAnimationFrame(function(){
          frame=0;var changes=pending;pending={};window.__REBUILD__(changes);
        });
      });
    });
    document.getElementById('t-copy').addEventListener('click', function(){
      var H = new URLSearchParams(location.hash.slice(1));
      var text = Object.keys(fields).map(function(k){return fields[k]+'='+T[k]}).join('  ');
      var btn = document.getElementById('t-copy');
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(function(){ btn.textContent='已复制 ✓'; }).catch(function(){ btn.textContent=text; });
      else btn.textContent = text;
      setTimeout(function(){ btn.textContent='复制当前参数'; }, 1600);
    });
  }
  init();
})();
</script>
"""
html = html.replace('</body>', PANEL + '</body>', 1)

html=html.replace('}catch(e){fallback()}', '}catch(e){window.__ERRS__.push(e.stack||String(e));console.error(e);fallback()}')
# 调参页保持当前文档，隐藏的正式语言按钮也不可触发跳转。
html=html.replace("location.href='./en/';", "return; // tuner keeps the current document")
def replace_once(old,new):
    global html
    assert html.count(old)==1,(old[:100],html.count(old))
    html=html.replace(old,new,1)
# v4: the angle belongs to the membrane opening, not the trunk profile.
replace_once("num('angle',90),35,145", "num('angle',45),20,150")
html=html.replace('接触角度','根部张角（环上开口）').replace('接触平滑度','过渡圆润度').replace('min="35" max="145"','min="20" max="150"')
replace_once("tangent=frame.out.clone().applyAxisAngle(frame.z,THREE.MathUtils.degToRad(form.contactAngle-90))", "tangent=frame.out.clone()")
replace_once("lead=THREE.MathUtils.lerp(.06,.42,form.contactSmooth)", "lead=.18")
replace_once("handle=root.distanceTo(end)*THREE.MathUtils.lerp(.18,.62,form.contactSmooth)", "handle=root.distanceTo(end)*.4")
replace_once("handleRatio:THREE.MathUtils.lerp(.18,.62,form.contactSmooth)", "handleRatio:.4")
replace_once("path.frame={normal:b.membraneFrame.tangent.clone().addScaledVector(b.membraneFrame.z,-1).normalize()};", "path.frame={normal:b.membraneFrame.tangent.clone()};")
replace_once("vertexStart=linePositions.length/3,t=soma.radius*form.ringTubeRadius*form.rootRingRatio", "vertexStart=linePositions.length/3,t=soma.radius*form.ringTubeRadius")
replace_once("const radial=8,along=4,steps=12,delta=2.2*t/R,beta=Math.PI/2;\n      const branches=[...soma.branches].sort((a,b)=>a.angle-b.angle);", """const radial=8,along=4,steps=12,beta=Math.PI/2;
      const branches=[...soma.branches].sort((a,b)=>a.angle-b.angle);
      const gaps=branches.map((b,i)=>branches[(i+1)%branches.length].angle-b.angle+(i===branches.length-1?Math.PI*2:0));
      const minGap=Math.min(...gaps),requested=THREE.MathUtils.degToRad(form.contactAngle);
      const delta=requested/2;
      soma.contactOpening={requested:form.contactAngle,effective:THREE.MathUtils.radToDeg(2*delta),minGap:THREE.MathUtils.radToDeg(minGap),gaps:gaps.map(a=>THREE.MathUtils.radToDeg(a))};""")
replace_once("derivatives.push(d.multiplyScalar(.04))", "derivatives.push(d.multiplyScalar(THREE.MathUtils.lerp(.01,.10,form.contactSmooth)))")
html=html.replace('clusterSomas,membraneRanges,linePositions', 'clusterSomas,membraneJunctions,membraneRanges,linePositions')
html=html.replace('<div class="hint">拖动即重建', '<div class="hint" id="contact-effective"></div><div class="hint">拖动即重建')
html=html.replace('    var pending={},frame=0;', '''    function showOpening(){
      document.getElementById('contact-effective').textContent='设定值（无限幅） '+T.angle+'°';
    }
    showOpening();
    var pending={},frame=0;''')
html=html.replace('window.__REBUILD__(changes);', 'window.__REBUILD__(changes);showOpening();')
html=html.replace('if (!T || !window.__REBUILD__)', 'if (!T || !window.__REBUILD__ || !window.__DBG__)')
# v5: overlapping openings are independent patches. Only emit forward ellipse
# gaps; a covered gap must not become a reversed or zero-area strip.
replace_once('const samples=Math.ceil((end-a)*R/t/2);', 'if(end<=a)continue;\n        const samples=Math.max(1,Math.ceil((end-a)*R/t/2));')
# Wide collars can bend across a cell diagonal. Orient each face toward the
# outside of its local cross section instead of inheriting a folded grid winding.
replace_once('}strip(collar,path);', '''}
        const centers=collar.map(row=>row.slice(0,n).reduce((c,v)=>c.add(v),new THREE.Vector3()).multiplyScalar(1/n));
        let correctedFaces=0;
        for(let i=0;i<collar.length-1;i++)for(let j=0;j<n;j++){
          for(const ids of [[[i,j],[i+1,j],[i,j+1]],[[i+1,j],[i+1,j+1],[i,j+1]]]){
            const vertices=ids.map(([r,c])=>collar[r][c]),out=new THREE.Vector3();
            const gpu=vertices.map(v=>new THREE.Vector3(Math.fround(v.x),Math.fround(v.y),Math.fround(v.z)));
            ids.forEach(([r,c],k)=>out.add(gpu[k].clone().sub(centers[r])));
            const normal=gpu[1].clone().sub(gpu[0]).cross(gpu[2].clone().sub(gpu[0]));
            if(normal.dot(out)<0){[vertices[1],vertices[2]]=[vertices[2],vertices[1]];correctedFaces++;}
            emit(...vertices,path);
          }
        }
        b.collarCorrectedFaces=correctedFaces;''')
# v7: extended monotone easing; preserve the exact baseline at s=.5.
replace_once("num('smooth',.5),0,1", "num('smooth',.5),-4,5")
replace_once('min="0" max="1" step="0.01"', 'min="-4" max="5" step="0.01"')
easing = """
    function contactEase(t,s=form.contactSmooth){
      t=THREE.MathUtils.clamp(t,0,1);s=THREE.MathUtils.clamp(s,-4,5);
      const smooth=t*t*(3-2*t),quintic=t*t*t*(6*t*t-15*t+10);
      if(s<-.5)return Math.pow(t,2+(-s-.5)*2);
      if(s<0)return THREE.MathUtils.lerp(t,t*t,-2*s);
      if(s<=1)return THREE.MathUtils.lerp(t,smooth,s);
      if(s<=2)return THREE.MathUtils.lerp(smooth,quintic,s-1);
      return quintic;
    }
    function contactLengthScale(s=form.contactSmooth){
      s=THREE.MathUtils.clamp(s,-4,5);
      if(s<-.5)return THREE.MathUtils.lerp(.15,1,(s+4)/3.5);
      if(s<=2)return 1;
      if(s<=2.5)return 1+(s-2)*1.2;
      return THREE.MathUtils.lerp(1.6,3,(s-2.5)/2.5);
    }
    function contactHandle(low,base,high){
      const s=THREE.MathUtils.clamp(form.contactSmooth,-.5,2.5);
      // Length extends the collar endpoint; keep tangent handles bounded so
      // the wide-end setting cannot overshoot back through the ring surface.
      return (s<=.5?THREE.MathUtils.lerp(low,base,s+.5):THREE.MathUtils.lerp(base,high,(s-.5)/2))*Math.min(1,contactLengthScale());
    }
    function contactParameter(t){
      if(form.contactSmooth===.5||t===0||t===1)return t;
      const target=contactEase(t);let lo=0,hi=1;
      for(let i=0;i<48;i++){const mid=(lo+hi)/2;if(contactEase(mid,.5)<target)lo=mid;else hi=mid;}
      // Keep half the original spacing so flat quintic ends do not collapse
      // neighbouring rings after Float32 packing (world coordinates ~40).
      return (t+(lo+hi)/2)/2;
    }
    window.__TUNER_EASE__=contactEase;
    window.__TUNER_LENGTH_SCALE__=contactLengthScale;
"""
replace_once('    function membraneFrame(soma,angle){', easing+'    function membraneFrame(soma,angle){')
# The retained original tail (join <= .31, or .61 above s=2) bounds the whole
# curve, and the shortest trunk split is .25. Thus this cap is <= 60% of
# every resulting trunk, even before the neck/collar lengths are added.
replace_once('start=frame.point.clone().addScaledVector(frame.out,.12)', 'contactLength=Math.min(.12*contactLengthScale(),(original.getLength()-original.getLengths(200)[62])*.25*.60),start=frame.point.clone().addScaledVector(frame.out,contactLength)')
replace_once('derivatives.push(d.multiplyScalar(THREE.MathUtils.lerp(.01,.10,form.contactSmooth)))', 'derivatives.push(d.multiplyScalar(contactHandle(.01,.055,.10)))')
replace_once('b.contactDirection.clone().multiplyScalar(THREE.MathUtils.lerp(.06,.42,form.contactSmooth))', 'b.contactDirection.clone().multiplyScalar(contactHandle(.06,.24,.42))')
# Monotone parameter remapping preserves the default exactly. Positive handles
# also change the actual curve shape: acute at -.5, broad at 2.5.
replace_once('const u=(1-Math.cos(Math.PI*i/steps))/2,row=[];', 'const u=contactParameter((1-Math.cos(Math.PI*i/steps))/2),row=[];')
# At the sharp extreme a ruled collar avoids a tangent bulge into the annulus.
# Blend continuously from the v6 -.5 profile, keeping the .5 baseline untouched.
replace_once('row.push(i===0?inner[j]:i===steps?end:inner[j].clone().multiplyScalar(2*u*u*u-3*u*u+1).addScaledVector(derivatives[j],u*u*u-2*u*u+u).addScaledVector(end,-2*u*u*u+3*u*u).addScaledVector(d1,u*u*u-u*u));', '''const vertex=inner[j].clone().multiplyScalar(2*u*u*u-3*u*u+1).addScaledVector(derivatives[j],u*u*u-2*u*u+u).addScaledVector(end,-2*u*u*u+3*u*u).addScaledVector(d1,u*u*u-u*u);
            if(form.contactSmooth<-.5)vertex.lerp(inner[j].clone().lerp(end,u),(-form.contactSmooth-.5)/3.5);
            row.push(i===0?inner[j]:i===steps?end:vertex);''')
replace_once('while(join<.3&&original.getPoint(join)', 'while(join<(form.contactSmooth>2?.6:.3)&&original.getPoint(join)')
replace_once('let join=.08;', 'let join=.08+.12*THREE.MathUtils.clamp((form.contactSmooth-2)/3,0,1);')
# Use the shorter guaranteed retained tail when the soft extreme joins later.
replace_once('original.getLengths(200)[62]', 'original.getLengths(200)[form.contactSmooth>2?122:62]')
# Widen only the inner cut within the existing requested opening at the
# extended ends, leaving enough clearance between collar and torus annulus.
html=html.replace('delta*.66', 'delta*(.66+.068*THREE.MathUtils.clamp(Math.max(-form.contactSmooth-.5,form.contactSmooth-2)/3,0,1))')
html=html.replace('beta*Math.sin(alpha)', 'beta*(1+.2*THREE.MathUtils.clamp(Math.max(-form.contactSmooth-.5,form.contactSmooth-2)/3,0,1))*Math.sin(alpha)')
html=html.replace('拖动即重建，参数写进地址栏，可直接分享。', '圆润度 −4.00～5.00，默认0.50；过渡长度0.15～3.00倍，上限为路径60%。拖动即重建，参数写进地址栏，可直接分享。')
OUT.write_text(html, encoding='utf-8')
print("written:", OUT, len(html))
