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

## M4a：内容胞体与数据链

`index.html` 中的 `CONTENT_UNITS` 是本阶段内容单一来源，共 20 条（5+4+5+4+2），包含 `id / sectionId / title / body / sourceIds / seed / anchor`。关于我们五条按任务卡原文启用；其余 15 条正文留空，待 M4b 定稿启用。其他四区保留 M3 原有信息点与文案，本阶段不升级为内容胞体。

修改文案只改 `title / body`，保持 `id / seed / anchor`。五枚圆润胞体、内核、细环与三层分叉树突按 seed 一次生成；桌面树突 4,320 个三角形，移动 1,740 个，新增主场景绘制三批（胞体/内核实例、细环实例、树突合批）。帧循环只更新状态与投影，不重建树突。品牌区采用纯文字「安集协康 / ANGECON」，移除原自绘标记。

每帧更新相机矩阵后，把同一世界锚点投影到 CSS 像素，用于按钮、主题标签和详情引线；屏幕外/相机背后按钮隐藏。桌面命中 48px，移动 44px。hover/focus 即时显示主题和亮环，80–240ms 的光段沿预计算累计距离向胞体收拢；移出取消。触屏一次点击直接打开主题与详情。详情正文立即写入，打开时冻结相机环视与 idle，支持 ×、遮罩、Esc，Tab 留在卡片内，关闭后恢复触发焦点和滚动位置。

入场分树突（250–650ms）、组织（650–1000ms）两段，品牌和内容胞体即时可见；可点「跳过入场」，任何输入也会跳过，不覆盖或阻挡页面。无操作 6 秒后，桌面每 4–7 秒只激活一个背景点及其直接邻接线；输入、弹窗、隐藏标签页取消。移动关闭 idle，关于我们采用固定取景，五枚胞体在窄屏内可达。系统减少动态效果默认跳过传导、入场和自动相机运动，保留 M3 静谧微光、提示条与会话主动开启动效入口。

兜底清单由普通脚本先从同一数据源生成，默认显示；仅三维初始化成功后切换场景。因此本地模块导入失败、WebGL 不可用或上下文丢失时，五条内容仍能阅读。二维码保留 M3 现状，M4b 再归位。

`__NET_STATS__` 保留 M3 字段，并增加：

- `unitsActive / unitsVisible`：启用数与当前视口内数量。
- `unitHover / unitSelected`：内容 ID 或 `null`。
- `transmission`：`{ id, phase, distance }` 或 `null`，相位按真实树突累计距离更新。
- `introDone / idlePulse`：入场状态；背景信号 `{ node, phase }` 或 `null`。
- `unitDrawCalls / unitTreeTriangles / unitPaths / unitAnchors / fallback`：工程预算、支路累计距离、稳定锚点及兜底状态。`unitDrawCalls=3` 是主场景对象批次，Bloom 后处理的实际调用另由浏览器复测。

非浏览器自测脚本：`D:\will\cache\scratch\an3\m4a-selftest.mjs`；证据：同目录 `m4a-selftest-report.json`。运行 `node D:\will\cache\scratch\an3\m4a-selftest.mjs` 可复现数据、几何、矩阵投影、交互状态、故障兜底、入场/idle 时序与弹窗相机冻结检查。测试使用真实本地 Three.js CPU 几何和实际帧循环，DOM/渲染器使用替身，不构成浏览器或 GPU 验收。

## 浏览器验收

本次按 Will 指令未运行浏览器自测；桌面视觉/60fps、375px 实际溢出/遮挡与触屏命中、真实键盘焦点及滚动恢复、reduced-motion 提示条与主动开启、shader/控制台、滚动五区进入与外链请求由 HEBE 独立复测。激活态、详情态、兜底态、品牌区截图由 HEBE 补齐。本次不提交、不推送 Git，发布由 HEBE 验收通过后执行。
