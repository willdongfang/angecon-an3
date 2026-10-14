# 安集协康 · 研究网络

M5 单页原型：五区共 20 枚内容胞体（5+4+5+4+2），覆盖关于我们、技术平台、研发管线、科学数据与关注我们。原生滚动切换分区；桌面鼠标小幅环视，hover/focus 显示主题，click 打开详情。移动与减少动态效果模式使用固定取景，五区均可访问。

## 本地运行

需要 Node.js 18 或更新版本，在仓库根目录运行：

```powershell
node -e "require('http').createServer((q,s)=>require('fs').createReadStream('.'+(q.url==='/'?'/index.html':decodeURIComponent(q.url.split('?')[0]))).on('error',()=>{s.statusCode=404;s.end()}).pipe(s)).listen(8080)"
```

浏览器访问 `http://localhost:8080/`。ES modules 需要 HTTP 服务，不能使用 `file://` 验证。

## 内容与交互

`index.html` 内 `CONTENT_UNITS` 为内容单一来源，20 条均启用。新增 15 条标题与正文逐字采用 M4b 任务卡；原有 ID、seed、anchor 保持不变。更新文案只改 title/body。桌面沿用世界锚点，移动初始化时依据分区中心与固定槽位生成可读布局；`unitAnchors` 同时提供原 anchor 与实际 world 坐标。

五区分别使用放射、双向、长轴突、密短枝与成对枝形态；仅表示栏目布局，不表示解剖、因果或疗效关系。所有胞体、内核、细环及树突初始化时合批生成，分区切换只更新实例矩阵和 shader 参数。只有当前分区的内容可命中，背景不接受输入；主题、按钮与详情引线均从同一世界坐标投影。

打开详情即时显示文字并冻结环视/焦面/idle，支持 ×、遮罩、Esc 和 Tab 焦点圈定；关闭后恢复触发焦点与原滚动位置。首次打开把内容 ID 放入会话内 Set，保留 DOM 空心已读环及 aria「已阅读」；桌面正常性能下额外点亮该胞体邻接支路的短段。移动与性能降级时仅保留 DOM 环，reduce 直接置位；刷新清空，无后端或埋点。

5-1 详情与静态兜底均显示带名称的双公众号二维码，原素材逐字节复制到 `assets/qr-angecon.jpg`、`assets/qr-anku.png`，无远程资源与跳转链接。双列自适应宽度，详情超过屏高时卡片内部滚动。

## 光学切片与性能

桌面滚动以本区进度控制视空间焦面距离，背景 Points 与远景线段按离焦距离调整亮度，点大小模拟离焦；不新增全屏景深后处理。内容胞体不接受焦面衰减，始终保留内核、描边与最低亮度。相机按既有五簇路径分区取景，桌面环视绕相机自身轻微偏转，跨区即时切换本区内容，避免镜头过渡让内容脱离视口。

桌面背景初始 800 点，移动 240 点；移动关闭 Bloom 与环视，焦面固定。像素比初始上限桌面 1.5、移动 1.15。连续三个采样窗口低于 45fps 后依次关闭 Bloom、像素比降至 1、减少背景密度；第一层降级即固定焦面，仅亮度分层，始终保留 20 条内容。

20 胞体树突总三角形：桌面 **4160**，移动 **1600**；新增主场景对象合批 **3**（胞体/内核实例、细环实例、树突）。这些为 CPU 几何计数与工程批次，实际 GPU 调用及 60fps 由 HEBE 复测。每帧不重建几何。

保留原生滚动、纯文字品牌、深蓝 `#02060f` 与品牌绿 `#2de06a`；本地 Three.js 0.186.1、EffectComposer、RenderPass、UnrealBloomPass 均在 vendor 内。入场、80–240ms 单枝传导与 6 秒后单背景点 idle 延续 M4a。系统减少动态效果保留静谧微光、提示条、会话主动开启/知道了三层；默认跳过传导与入场，五区相机和焦面固定，滚动仅即时切换分区。

普通脚本先生成 20 条静态清单与双码，默认显示；三维初始化成功后才隐藏兜底。模块导入失败、WebGL 不可用或上下文丢失时恢复完整清单。

## 运行态诊断

控制台读取 `window.__NET_STATS__`：

- `unitsActive / unitsVisible`：启用数 20 / 当前区可见数。
- `unitHover / unitSelected / transmission`：悬停、选中 ID 与单支真实累计距离传导。
- `visited`：会话已读 ID 列表；关闭保留，刷新清空。
- `focusDepth / focusMode / scrollProgress`：视空间焦面距离、scroll/fixed 模式、原生滚动进度。
- `performanceTier / backgroundVisible`：降级层数 0–3 / 减密后的背景点数。
- `unitTreeTriangles / unitDrawCalls / unitPaths / unitAnchors`：树突预算、工程合批、支路距离与稳定锚点/实际世界坐标。
- `nodes / lines / mobile / bloomOn / fps / fpsSamples / activeCluster / cam / gaze / introDone / idlePulse / fallback`：场景与故障诊断。
- `reducedMotion / motionEnabled / motionOverride / noticeShown / gazeEnabled`：系统及会话动效选择。

旧信息列表字段已移除；不以诊断预算代替 GPU 实测。

## M4d 左侧文字与字号调整

新增左侧纯文字悬浮组：透明填充与 1px 描边区名、英文分区名、全部单元标题。启动时按 `CONTENT_UNITS.sectionId` 读取并缓存五组 DOM；随 `setCluster` 与 `activeCluster` 同步显示，不在每帧重建内容，也不改写源数据。各区标题数保持真实数据的 5 / 4 / 5 / 4 / 2；关注我们不会补造条目。

左块无底板、无边框、无阴影，禁用指针交互；层级高于画布，低于胞体标签与弹窗。桌面区名字号 64–84px，9 秒上下 ±6px 浮动，切换 500ms 淡入轻滑。移动端仅显示 42px 区名与 11px 英文，隐藏清单并降低不透明度；系统减少动态效果时取消左块全部浮动与切换动画，原有减少动态效果三层保留。

滚动提示采用方案 A：改为左下横排。桌面索引保持右侧，读数保持右下；移动索引改为底部可换行文字导航，索引/提示/读数分别距底 118 / 78 / 18px，预留分离空间。真实包围盒与 ≥24px 间距待 HEBE 实测。

| 元素 | 桌面字号 | ≤700px 字号 |
|---|---|---|
| 顶栏导航 | 14px | 12px |
| 顶栏品牌 | 14px | 13px |
| 分区索引 | 15px | 15px |
| 滚动提示 | 11px | 11px |
| 底部读数标签与数值 | 12px | 10px |
| 胞体悬停标签 | 14px | 14px |
| 详情正文 | 17px | 16px |
| 兜底清单正文 | 15px | 15px |

以上为源码声明值，移动值按卡片的原值上调要求调整；未以浏览器 `getComputedStyle` 实测。

## 自测与交付

M4d 非浏览器自测 **22/22 通过**：

```powershell
node D:\will\cache\scratch\an3\m4d\selftest.mjs
node D:\will\cache\scratch\an3\m4d\quality-check.mjs
node --check D:\will\cache\scratch\an3\m4d\browser-acceptance.js
git diff --check
```

自测证据：`D:\will\cache\scratch\an3\m4d\selftest-report.json` 与 `quality-report.json`。使用 Node VM、DOM/渲染器替身与本地 Three.js CPU 几何/矩阵及实际模块循环；覆盖五区左块数据和切换、八类字号与降级 CSS 声明、20 条原数据完整不变、胞体/弹窗/双码/记忆环逻辑、五区可达、reduce 与性能三层、模块/WebGL 失败兜底。本地 HTTP 资源与两段脚本语法检查通过。备份位于同目录 `index.html.before`、`README.md.before`，测试脚本不放进网站仓库。

按 Will 本轮指令未跑浏览器自测，未生成截图或真实包围盒数值表。待 HEBE 独立验收：1440px 与 375px 零溢出/零裁切/零遮挡；至少六个滚动位置三类固定元素两两间距 ≥24px；八类字号实测；五区与首屏共六张截图；reduce 左块静止与原三层视觉；真实 shader/控制台零错误、GPU 60fps、悬停/键盘/触屏/弹窗/双码/记忆环回归。

HEBE 可在两个视口分别通过控制台或 CDP 执行 `D:\will\cache\scratch\an3\m4d\browser-acceptance.js`，采样结果存入 `window.__M4D_ACCEPTANCE__`（包含包围盒、间距、字号及左块内容）。该辅助脚本只通过语法检查，Cain 未在浏览器运行；截图、视觉与交互仍需 HEBE 单独完成。

未提交、未推送 Git；任务卡与 STATUS 回写为实施完成、待 HEBE 独立验收。验收通过后由 HEBE 发布。

## M5 / M5b 网络造型与光效（M5c 收尾）

`index.html` 模块脚本中的 `NET_CONFIG` 为集中调优表，搜索名称即可定位。`growBranch` 用受约束二叉 L-system 和二次曲线生成渐细带状树突，跨簇采用 Catmull-Rom 曲线；`createLightClock` 编排五簇错相事件；`lightGLSL` 按真实累计距离传播。节点、带状网格与微尘各自合批。已有内容和交互区保持原接口。

| 配置位置 | 当前值与用途 |
|---|---|
| `seed / desktopNodes / mobileNodes` | 20261014 / 800 / 240，确定性生长与节点预算 |
| `form.desktopRoots / mobileRoots / desktopArms` | 每簇 2 / 1 个主核，每核 3 路主枝 |
| `form.desktopDepth / mobileDepth` | 4 / 1（从 0 计，即 5 / 2 层） |
| `form.length / lengthDecay / width / widthDecay` | 6 / 0.59 / 0.17 / 0.56，层级缩短与变细 |
| `form.tipTaper / terminalLight / levelLightDecay` | 0.72 / 0.22 / 0.73，末梢渐细、弱光与层级明暗 |
| `light.interval / phaseStep / jitter` | 2.65s / 0.47s / 0.38s，错相与间隔抖动 |
| `light.spikeCore / spikeTravel / spikeTailSamples` | 0.24s / 0.28s / 8，尖峰亮芯与拖尾 |
| `light.converge / cascade / cascadeRelays` | 2.1s / 2.6s / 3，汇聚与变速回折接力 |
| `light.stormMin / stormMax / stormDuration` | 12s / 18s / 2.5s，风暴间隔与传播时长 |
| `light.stormPulse / stormFade / bridgeGain` | 0.10 / 0.85s / 1.5，簇脉冲、衰减与桥接增亮 |
| `light.breathAmplitude / breathPeriod / hoverGain` | ±3% / 8s / 0.12，呼吸与光标近邻增亮 |
| `atmosphere.desktopDust / mobileDust / dustOpacity` | 每簇 48 / 16 / 0.09，轻微微尘 |
| `budget.maxEvents / meshFraction` | 40 条有界日志 / 降级保留 60% 网格顶点（完整三角形） |

诊断 `window.__NET_STATS__` 新增 `lightEvents`、`lightDirections`、`lightEventLog`、`lightActive`、`lightPaused`、`networkPaths`、`networkTriangles`、`networkRoots`、`networkDepth`、`lightConfig`；`pulses` 合计旧 idle 点与当前光效活动数。`lines` / `networkPaths` 现在表示曲线路径数，桌面 934 条；桌面网络 10936 三角形，内容树突另计 4160；移动网络 880、内容树突 1600。真实 GPU 调用和性能须浏览器实测。

### M5c 非浏览器复验

复用 M5b 自测读取当前页面，28/28 通过；使用 Node VM、实际本地 Three.js CPU 几何及 DOM/渲染器替身运行页面模块。模拟 60Hz 的 10s 事件为 spike-out 9 / converge 5 / cascade 5 / rare-storm 0；12s 为 10 / 9 / 5 / 0；120s 为 76 / 75 / 74 / 8。风暴按 12–18s 配置触发，前 10s 的三类覆盖来自外放、汇聚和回折。模拟不证明画面可见性或真实帧率。

```powershell
node D:\will\cache\scratch\an3\m5c\selftest.mjs
node D:\will\cache\scratch\an3\m5c\integrity.mjs
```

证据：同目录 `selftest-report.json`（28 项逻辑/几何/降级/交互回归）、`integrity-report.json`（当前 HTML 两段脚本 node --check、导入映射、直接本地资源、冲突/TODO、SHA256 和差异空白检查）。M5c 未修改页面字节，只补齐文档与任务记录。M5/M5b 原执行均在收尾被模型容量中断（任务卡记载 rc=1），本轮没有新增美学迭代。历史备份和诊断位于同级 `m5`、`m5b`；本轮备份位于 `m5c`。

本轮未跑浏览器自测：造型/光效可见性、与 HEBE 快照对比、真实 shader 编译/控制台、GPU 60fps、375px 溢出与遮挡、真实 hover/触屏/弹窗/扫码/记忆环和 reduce 视觉均待 HEBE 独立验收。卡中既有 60fps/0 错误为 HEBE 前轮实测背景，非本轮 Cain 测量。未提交或推送 Git，由 HEBE 验收后发布。


## M6 中文化、导航、弹窗与页脚避让

界面品牌、副标、读数、提示与兜底文案改为中文。保留审定内容的专有名词、事实标识与联系邮箱；任务指定的「中 / EN」为语言按钮例外。五项导航使用相同普通链接样式，语言按钮支持键盘聚焦，点击展示「英文站建设中，敬请期待」，1700ms 后淡出，不跳转。窄屏导航换行排列。

详情遮罩采用 32% 暗化与 3px 模糊，350ms 淡入淡出；面板从缩放 0.96、下移 14px、透明状态于 480ms 入场，280ms 关闭。公众号链接以 140ms 淡出、140ms 淡入切换双码内容，5-1 直接打开相同视图。二维码复用本地原资源。键盘焦点循环覆盖关闭按钮及公众号链接，关闭取消待执行切换并回收焦点；系统减少动态效果时过渡及内容切换瞬时完成。

页脚进入视口时，读数、滚动提示、左块、索引与簇标题淡出，离开恢复；读数/提示过渡 300ms，索引同时退出键盘焦点。通过 IntersectionObserver 监听，无此接口时使用被动滚动/resize 回退。20 条 CONTENT_UNITS 与内容几何保持逐字一致。

复验命令（测试与备份均在仓库外）：

```powershell
node D:\will\cache\scratch\an3\m6\selftest.mjs
python D:\will\cache\scratch\an3\m6\integrity.py
git diff --check
```

自测结果：38/38 非浏览器逻辑/几何回归通过（含原 28 项和新增 10 项），两段脚本语法、导入映射、界面文本白名单扫描、本地资源、零外链与差异空白检查通过。证据：`D:\will\cache\scratch\an3\m6\regression-report.json`、`integrity-report.json`；备份为同目录 `index.html.before`、`README.md.before`。测试使用 Node VM、真实 Three.js CPU 几何与 DOM/渲染器替身；模拟帧循环不代表真实 GPU 帧率。

按 Will 指令未跑浏览器自测。待 HEBE 独立验收：遮罩下网络可见性、实际动画采样、正文到双码的视觉切换与图片加载/扫码、键盘/触屏交互、页脚进入/离开时实际透明度与包围盒零重叠、375px 零溢出/遮挡、真实 shader/控制台、GPU 60fps、记忆环/光学切片及 reduce 视觉。未提交或推送 Git；验收通过后由 HEBE 发布。
