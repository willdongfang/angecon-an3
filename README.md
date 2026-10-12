# angecon-an3

AN3 官网单页原型：方向二「宏观网络 · 神经唤醒」。纯静态部署到 GitHub Pages，全部运行时代码与依赖均由仓库本地提供，不调用 CDN。

## 本地运行

需要 Node.js 18 或更新版本。仓库根目录执行：

```powershell
node -e "require('http').createServer((q,s)=>require('fs').createReadStream('.'+(q.url==='/'?'/index.html':q.url)).on('error',()=>{s.statusCode=404;s.end()}).pipe(s)).listen(8080)"
```

访问 `http://localhost:8080/`。`file://` 不能用于验证 ES module/import map。

## 技术与依赖

- Three.js **0.186.1**（MIT），来源：`https://cdn.jsdelivr.net/npm/three@0.186.1/`。保留官方 `build/three.module.js` 与 `examples/jsm/postprocessing/`、`examples/jsm/shaders/` 原目录相对引用结构。
- GSAP / ScrollTrigger **3.15.0**（GSAP Standard License），来源：`https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/`；以 UMD 脚本加载。
- 静态主画布用原生 Three shader、EffectComposer 与 UnrealBloomPass。桌面 800 节点，触屏/窄屏 240 节点并关闭 Bloom；`prefers-reduced-motion` 停止穿梭与发光流动。GSAP ScrollTrigger scrub 驱动段落显隐，滚动保持原生。
- WebGL 初始化异常时显示静态深色标题降级画面；不依赖远程字体、图片或 API。

运行态可在浏览器控制台读取 `window.__AN3_STATS__`：`nodes`、`lines`、`mobile`、`bloomOn`、`reducedMotion`、`fps`（约每 60 帧更新）。
