# 既有风味文本轻度润色与样式调整

用户已确认：依据当前 toolkit 第 7 节，轻度润色六份中英本地化，以适度分段、中性强调和少量风险色改善阅读。保留标题、专名、剧情事实、规则和存档接口；不新增展示层脚本或 GUI。

## 实施尺度

- 共同体与四项常驻治理日志：轻调叙事；按各自机制分开规则、进退条件与失败后果，不统一套用模板。
- 十五项地区工程：突出建设重点，单列实际工程州的永久成果。
- 建国、边疆与复归日志：分开背景、行动条件和结算说明，保留期限及地理范围。
- 事件与提示：少量强调议题；冷却和战后安置成本独立成段。保留原有事件风味段、动态国家和前所有者引用。
- 中性数值使用 `#v`，核心短语使用 `#bold`；`#p` / `#n` 只描述有明确利弊的效果或状态。平衡值向中央或地方移动不按正负染色。

## 本地语法依据与覆盖边界

核对目标 Victoria 3 1.13.* 安装数据、Tech & Res（Workshop 3472248460，metadata 版本 `1.6'`）及 Firefall（Workshop 3768192009，版本 0.1.1）。两项上游均未提供替换 `textformatting.gui` 的文件。

- 游戏 `gui/textformatting.gui`：原生数值、收益、风险及字体样式。
- 游戏 `localization/simp_chinese/agitators_1_l_simp_chinese.yml` 的 `je_divided_monarchists_reason`：JE 正文 `#bold` 先例。
- 游戏 `localization/simp_chinese/ip4_cuba_l_simp_chinese.yml` 的 `je_cuba_independencia_reason`：分段、`#v` 与概念链接先例。
- 游戏 `localization/simp_chinese/tutorial_l_simp_chinese.yml` 的 `je_tutorial_increase_market_access_by_decree_reason`：市场接入概念引用。
- 游戏 `common/game_concepts/00_game_concepts.txt` 与 `localization/simp_chinese/concepts_l_simp_chinese.yml`：行政力、合法性、市场接入度、动乱。官僚余量使用 `Concept` 自定义显示文本，保留项目术语；该调用形式有原生本地化先例。
- 希腊日志仍沿用已登记的本地化覆盖，不新增上游覆盖对象。

没有新增对象作用域、函数、动态数值、图标或条件分支。现有动态引用与调用关系不变。

## 验证

运行 `python3 tests/validate_localization.py`；附加 `--game-root <game>` 和重复的 `--upstream <mod>` 可核对概念定义。检查六份文件的 BOM、语言头、键集合、引号、转义、富文本闭合与本地引用，同时验证 metadata JSON。

本次另以编辑前快照比较全部数值字面量与动态引用，并对运行时脚本、metadata、用户已有 AGENTS/toolkit 修改做哈希比对；它们均保持原状。`git diff --check` 通过。

保存的 `content_load.json` 未包含本次目标 FFPA 加载栈，因此未以它声称完成运行验证。未启动游戏；JE 高度、中文字体、长名称换行及悬浮提示仍需在实际启用目标加载栈后检查。这里的验证是静态验证，不是游戏渲染或运行日志证明。
