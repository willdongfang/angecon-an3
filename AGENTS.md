# Cain · AN3 开发约定

- 这是静态双语网站：中文 `index.html`，英文 `en/index.html`，资源在 `assets/` 与 `vendor/`；没有 npm 构建步骤。
- 需要项目背景时先查 `docs/PROJECT_STATE.md`，定位相关段落；README 的 M4–M8 章节是历史实施记录，不代表当前待办。
- 只读取任务相关文件和日志。小改动直接实施；复杂改动先列简短计划。不要为每次修改重读全部任务卡、整个仓库或重新跑所有历史测试。
- 修改页面后运行 `python scripts/check_project.py`。仅修改规则/文档时核对事实与 `git diff --check` 即可；修改检查器时另运行 `python -B -m unittest discover -s scripts -p "test_check_project.py" -v`。
- 检查器只证明静态资源、脚本语法、双语结构/数据及导航引用。布局、触屏、弹窗、二维码实扫、WebGL 和帧率需要按改动范围做浏览器验证，报告中区分未测项。
- 中英内容单元保持 ID、分组、seed、anchor、sourceIds 一致；审定文案仅按任务修改。`vendor/` 与原始图片默认复用。
- GitHub Pages 使用 `/angecon-an3/` 项目路径，路径和语言互切须兼容此前缀；HTTP 方式预览，不能用 `file://` 验证模块。
- 完成开发后更新 `docs/PROJECT_STATE.md` 的必要变化；过程和证据追加到 `docs/WORKLOG.md`。有任务卡则回写对应卡与 Cain 条目，避免更新其他成员的状态。
- Will 直接交办直接向 Will 汇报；HEBE 交办按其任务约定验收。提交、推送和发布遵循当前任务授权。
