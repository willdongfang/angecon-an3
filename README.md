# 安集协康 · 研究网络

M4b 单页原型：五区共 20 枚内容胞体（5+4+5+4+2），覆盖关于我们、技术平台、研发管线、科学数据与关注我们。原生滚动切换分区；桌面鼠标小幅环视，hover/focus 显示主题，click 打开详情。移动与减少动态效果模式使用固定取景，五区均可访问。

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

## 自测与交付

非浏览器自测 **19/19 通过**：

```powershell
node D:\will\cache\scratch\an3\m4b\selftest.mjs
node --check D:\will\cache\scratch\an3\m4b\syntax-1.cjs
node --check D:\will\cache\scratch\an3\m4b\syntax-2.mjs
git diff --check
```

证据：`D:\will\cache\scratch\an3\m4b\selftest-report.json`。使用本地 Three.js CPU 几何/矩阵与实际模块帧循环，DOM 与渲染器为替身；覆盖全部文案、20 条开关与已读、五区可达、移动命中间距、极限环视、焦面采样、降级顺序、模态冻结、减动画选择及故障兜底。修改前备份为同目录 `index.html.before` 与 `README.md.before`。

按 Will 本轮指令未跑浏览器自测，未生成截图。真实 shader 编译/控制台、GPU 调用与 60fps、375px 排版/遮挡/触屏、实际键盘与滚动恢复、reduce 三层视觉、二维码扫码和浏览器网络请求由 HEBE 独立验收；每区侧写/详情共 ≥8 张截图由 HEBE 补齐。

未提交、未推送 Git；任务卡与 STATUS 已回写为实施完成、待 HEBE 验收。HEBE 验收通过后发布。
