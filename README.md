# 安集协康 · 研究网络

「窥探大脑」沉浸式单页原型：桌面以五个神经元簇呈现关于我们、技术平台、研发管线、科学数据与关注我们。原生滚动驱动既有镜头路径，鼠标环视叠加在路径相机之外；接近分区时网络渐亮并显示区名，信息点由点击打开说明。移动端使用 240 节点并关闭 Bloom；系统减少动态效果时默认静谧显示提示条，保留无位移微光呼吸并可由用户主动开启本会话完整动效。WebGL 不可用时显示可读静态内容。

## 本地运行

需要 Node.js 18 或更新版本。在仓库根目录启动：

```powershell
node -e "require('http').createServer((q,s)=>require('fs').createReadStream('.'+(q.url==='/'?'/index.html':decodeURIComponent(q.url.split('?')[0]))).on('error',()=>{s.statusCode=404;s.end()}).pipe(s)).listen(8080)"
```

访问 `http://localhost:8080/`。ES modules 需要 HTTP 服务，不能使用 `file://` 验证。

## 本地依赖

- Three.js 0.186.1 与 EffectComposer、RenderPass、UnrealBloomPass 使用仓库 vendor 本地文件，不访问 CDN。
- 点云 shader 绘制节点、连线、脉冲及当前分区聚焦；环视父级 rig 只在桌面、非 reduced-motion 下启用。
- 分区说明来自现有章节内容拆分；具体管线进展和科学数据以安集协康官方发布为准。

## 运行态诊断

控制台读取 `window.__NET_STATS__`：

```js
window.__NET_STATS__
// { nodes, lines, mobile, bloomOn, reducedMotion, motionEnabled,
//   motionOverride, noticeShown, fps, introDone, activeCluster,
//   pulses, cam: [x, y, z], gazeEnabled, gaze: [yaw, pitch],
//   clusterFocus, proximity, clusters }
```

`activeCluster` 为 0–4；`gaze` 为弧度；`proximity` 为当前分区渐亮系数；`clusters` 提供 16 个信息点条目。

## 浏览器验收

本次按任务卡要求未运行浏览器自测；桌面视觉/60fps、375px 溢出与命中、弹窗三种关闭及滚动锁定、reduced-motion 交互、shader/控制台、滚动五区进入与外链请求由 HEBE 独立复测。
