# angecon-an3

AN3 官网单页原型：方向二「内容即网络」。桌面以五个神经元簇承载五个内容章节，滚动驱动章节切换与镜头接近、环绕、俯冲和拉远。页面使用 WebGL 点云、突触脉冲 shader、玻璃 HUD 和开场网络生长；移动端使用 240 节点并关闭 Bloom，系统减少动态效果时停止生长、脉冲、呼吸与镜头动画。WebGL 不可用时显示可读的静态内容。原生页面滚动，不拦截滚轮或触摸输入。

## 本地运行

需要 Node.js 18 或更新版本。在仓库根目录启动：

```powershell
node -e "require('http').createServer((q,s)=>require('fs').createReadStream('.'+(q.url==='/'?'/index.html':decodeURIComponent(q.url.split('?')[0]))).on('error',()=>{s.statusCode=404;s.end()}).pipe(s)).listen(8080)"
```

访问 `http://localhost:8080/`。ES modules 需要 HTTP 服务，不能使用 `file://` 验证。

## 本地依赖

- Three.js 0.186.1、EffectComposer、RenderPass、UnrealBloomPass 与 GSAP/ScrollTrigger 沿用 M1 仓库本地 vendor 文件；本页仅使用 Three.js 本地模块和后处理文件，不访问 CDN。
- 顶点 shader 驱动节点渐进显现、呼吸和脉冲亮度；片元 shader 渲染节点光晕、连线信号和微闪，不逐帧遍历节点。
- 五个章节文字摘自本地 AN1 现文，最多两句，并提供来源页面链接。科学数据章节使用技术平台页的研究体系原文。

## 运行态诊断

控制台读取 `window.__AN3_STATS__`：

```js
window.__AN3_STATS__
// { nodes, lines, mobile, bloomOn, reducedMotion, fps,
//   introDone, activeCluster, pulses, cam: [x, y, z] }
```

`activeCluster` 为 0–4；`pulses` 是活跃脉冲数量；`cam` 为相机位置；`fpsSamples` 保存最近 60 个每秒采样值。

## M2 验收记录

- 截图与 JSON 证据归档于本机 `D:\will\cache\scratch\an3\m2-evidence\`，不进入站点仓库：桌面首屏、五个章节、两张脉冲瞬间、375px 移动端及 reduced-motion 共 11 张 PNG；另有章节统计、相机位置、移动端统计和同源请求记录。
- 本机 Chrome headless 使用 ANGLE SwiftShader 软件 WebGL：移动端约 57–61 FPS；桌面样本约 3–10 FPS。该桌面数值是软件渲染数据，不能代表用户硬件，故桌面 ≥45 FPS 需在真实 GPU/HEBE 复测。
- 验证覆盖五章节 `activeCluster` 0→4、相机位置变化、pulse 活跃、移动端 240 节点与零横向溢出、reduced-motion 停止脉冲且相机静止、零外部网络请求、无滚动劫持与 WebGL fallback。
