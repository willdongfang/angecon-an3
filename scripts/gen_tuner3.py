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
replace_once("num('angle',90),35,145", "num('angle',45),20,120")
html=html.replace('接触角度','根部张角（环上开口）').replace('接触平滑度','过渡圆润度').replace('min="35" max="145"','min="20" max="120"')
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
      const delta=Math.min(requested,minGap*.9)/2;
      soma.contactOpening={requested:form.contactAngle,effective:THREE.MathUtils.radToDeg(2*delta),minGap:THREE.MathUtils.radToDeg(minGap),gaps:gaps.map(a=>THREE.MathUtils.radToDeg(a))};""")
replace_once("derivatives.push(d.multiplyScalar(.04))", "derivatives.push(d.multiplyScalar(THREE.MathUtils.lerp(.01,.10,form.contactSmooth)))")
html=html.replace('clusterSomas,membraneRanges,linePositions', 'clusterSomas,membraneJunctions,membraneRanges,linePositions')
html=html.replace('<div class="hint">拖动即重建', '<div class="hint" id="contact-effective"></div><div class="hint">拖动即重建')
html=html.replace('    var pending={},frame=0;', '''    function showOpening(){
      var values=window.__DBG__.network.clusterSomas.flat().filter(function(s){return s.isContent}).map(function(s){return s.contactOpening.effective});
      document.getElementById('contact-effective').textContent='实际环上开口 '+Math.min(...values).toFixed(1)+'°–'+Math.max(...values).toFixed(1)+'°；按邻根间隔的90%自动限幅。';
    }
    showOpening();
    var pending={},frame=0;''')
html=html.replace('window.__REBUILD__(changes);', 'window.__REBUILD__(changes);showOpening();')
html=html.replace('if (!T || !window.__REBUILD__)', 'if (!T || !window.__REBUILD__ || !window.__DBG__)')
OUT.write_text(html, encoding='utf-8')
print("written:", OUT, len(html))
