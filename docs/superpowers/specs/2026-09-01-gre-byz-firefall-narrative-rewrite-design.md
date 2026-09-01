# GRE → BYZ 成立链 Firefall 叙事重写设计

## 1. 背景

FFPA 为 Firefall 最终数据库恢复了 `GRE → BYZ` 成立链，并完整替换 `je_greek_nationalism` 与 `formation.3` 的脚本定义。当前实现保留原版政治效果、完成条件、失败条件、宣称、关系变化与奖励，但仍大量消费 Victoria 3 1.13.11 的原版希腊民族主义本地化。

最终玩家可见链包括：

1. `je_greek_nationalism_reason` 与 lobby 文本；
2. JE 启动事件 `greece.1`；
3. FFPA 自有东罗马提议事件 `ffpa_flavor.8`，但其普通入口仍借用 `greece.2` 文本；
4. JE 成功事件 `greece.4`；
5. JE 失败事件 `greece.5`；
6. BYZ 成立事件 `formation.3`。

这些文本原本面向 1836 年后的希腊国家，包含“刚摆脱数百年奥斯曼统治”、把约安尼斯·科莱蒂斯演说当作当代政治讲话、以“吞并全部希腊土地”作为连续国策，以及不论实际法律都宣称国家政治存续永受宪法保障等表述。`formation.3` 的 flavor 还位于古罗马元老院，以众神、雷电与金鹰构成异教神迹，与君士坦丁堡、正教会和 Firefall 2050 核战后再建国家的背景不符。

此外，部分文本与实际效果不一致：

- `greece.4.c` 显示“遣返人民”，实际只添加提高政府利益集团总势力所贡献合法性的 modifier；
- `greece.5` 只有东罗马路线失败时会把艾登、东色雷斯、许达文迪加尔与特拉布宗的希腊人口迁往 ROOT 首都并移除希腊故土，但当前固定正文没有说明这一严厉后果。

本设计在不改变运行时行为的前提下，重写整条玩家可见叙事，使十九世纪历史只作为旧世界档案存在，其余声音属于大火后的当代社会。

## 2. 已确认决策

1. 采用“历史档案式混合”风格。
2. 科莱蒂斯引文只在 `je_greek_nationalism_reason` 中完整出现一次，明确标注为旧世界幸存档案。
3. `greece.1`、`ffpa_flavor.8`、`greece.4`、`greece.5` 与 `formation.3` 全部使用 2050 年后的当代政治声音。
4. 世界内主要称灾变为“大火”或“烈火落下之日”；“2050 核战”只用于 README 或极少数说明性文本，不在事件中反复出现。
5. 保留“伟大理想”JE 标题与“紫凤凰”成立事件标题。
6. 对外 UI 可以使用玩家熟悉的“拜占庭帝国”；当代人物和成立后的内部叙事主要使用“东罗马”“罗马帝国”与“新罗马”。
7. 不完整复制原版 `greece.1`、`greece.4`、`greece.5` 事件；路线差异通过 customizable localization 表达。
8. 不修改任何现有事件 ID、JE ID、路线变量、完成条件、宣称、关系、恶名、modifier 或人口移动效果。

## 3. 目标

- 让 GRE 的成立背景与 Firefall 的“旧国家毁灭—继承政权重组—形成旧世界国家”结构一致。
- 让真实十九世纪材料成为灾后政治人物重新发现和重新解释的历史档案，而不是跨越两个世纪无缝延续的当代演说。
- 为克制希腊、伟大理想、东罗马三条路线提供不同的成功与失败解释。
- 使 `greece.4.c` 与其真实合法性效果一致。
- 使东罗马路线失败文本准确说明人口迁移与故土移除。
- 让 `formation.3` 发生在重建中的君士坦丁堡，并体现王冠、正教会、军队、法学家与行省代表对罗马国号的共同确认。
- 保留原版工具提示与机制信息，避免为了文学润色降低可读性。

## 4. 非目标

- 不重做希腊民族主义的玩法、数值或领土范围。
- 不改变 `greece.1` 对 TUR/RUS 的关系效果。
- 不改变 `greece.2` / `ffpa_flavor.8` 的宣称、事件事故、恶名或变量写入。
- 不改变 `greece.4` 的三种奖励选项。
- 不改变 `greece.5` 的人口迁移、故土移除、统治者声望或利益集团惩罚。
- 不恢复或重写 Firefall 最终数据库中通常不存在的 ION 支线。
- 不在每段文本中重复“核战、核尘、辐射”等设定词。
- 不新增事件插图、角色、事件 ID 或长期状态机。

## 5. 最终加载栈与文本来源

### 5.1 FFPA 已拥有的脚本对象

- `je_greek_nationalism`：本项目完整替换原版顶层 JE；
- `ffpa_flavor.8`：本项目替代原版 `greece.2` 的东罗马提议入口；
- `formation.3`：本项目完整替换原版成立事件，只保留原版通知和威望结构并使用自有宣称白名单。

### 5.2 继续由原版提供的事件

- `greece.1`：JE 启动；
- `greece.4`：JE 成功；
- `greece.5`：JE 失败。

本项目的 JE 直接触发上述原版事件，因此这些事件的玩家可见文本属于 FFPA 最终行为的一部分，即使文件本身不在本仓库。

### 5.3 有意不纳入的文本

`greece.3` 与 `greece.6` 是爱奥尼亚群岛保护国移交支线，依赖 `c:ION` 及其宗主。Firefall 使用 `replace_path` 重建国家数据库后，该路径通常不可达；它也不是 FFPA 恢复 BYZ 所必经的链条。本轮不覆盖“伦敦条约”相关键。

## 6. 方案比较

### 6.1 完全保留历史引文

把科莱蒂斯的两段引文都标记为档案引用，仅重写连接段。

优点是历史味最浓。缺点是 JE 与成功事件重复同一政治传统，且成功引文承诺“宪法永久保障”，在专制或非立宪法律下会直接违背最终状态。

### 6.2 完全灾后重写

删除所有真实历史引文，整条链只使用 Firefall 世界中的新政治语言。

优点是时代统一。缺点是削弱“旧世界思想遗产在灾后被重新发现”的历史连续感。

### 6.3 历史档案式混合（采用）

JE 以一份幸存的科莱蒂斯演说作为档案引子；随后所有事件由灾后当代人物重新解释希腊国家、伟大理想与罗马遗产。

该方案同时保留真实历史来源和 Firefall 的时间断裂，也避免把旧引文当成适用于所有法律与政体的当代承诺。

## 7. 覆盖架构

### 7.1 最小脚本改动

不完整替换 `greece.1`、`greece.4`、`greece.5`。这些事件包含大量路线化 modifier、利益集团、人口迁移和故土清理效果，复制整个对象会扩大上游更新风险。

采用以下组合：

- 对原版事件仍直接引用的本地化键做完整文本覆盖；
- 对 `greece.4` 与 `greece.5` 使用项目现有 customizable localization 数据库，根据既有路线变量返回不同正文；
- 对本项目已经拥有的 `ffpa_flavor.8` 和 `formation.3` 改用新的 `ffpa_` 本地化键，避免继续覆盖不需要消费的上游正文。

### 7.2 需要覆盖的上游本地化键

JE 与 lobby：

- `je_greek_nationalism_reason`；
- `je_greek_nationalism_lobby`。

启动事件：

- `greece.1.t`；
- `greece.1.d`；
- `greece.1.f`；
- `greece.1.a`；
- `greece.1.b`。

成功事件：

- `greece.4.t`；
- `greece.4.d1`；
- `greece.4.d2`；
- `greece.4.f`；
- `greece.4.a`；
- `greece.4.b`；
- `greece.4.c`。

失败事件：

- `greece.5.t`；
- `greece.5.d`；
- `greece.5.f`；
- `greece.5.a`；
- `greece.5.b`。

这些键必须加入 `AGENTS.md` 的覆盖与冲突登记。FFPA 按推荐顺序最后加载时，它们应成为最终显示来源。

### 7.3 改为自有键的对象

`ffpa_flavor.8` 改用：

- `ffpa_flavor.8.t`；
- `ffpa_flavor.8.d`；
- `ffpa_flavor.8.recovery.d`；
- `ffpa_flavor.8.f`；
- `ffpa_flavor.8.a`；
- `ffpa_flavor.8.b`。

`formation.3` 改用：

- `ffpa_formation_byzantium.t`；
- `ffpa_formation_byzantium.d`；
- `ffpa_formation_byzantium.f`；
- `ffpa_formation_byzantium.a`。

事件技术 ID 不变，只有其 `title`、`desc`、`flavor` 与 `option name` 指向自有键。

### 7.4 明确保留的上游键

- `je_greek_nationalism` 标题“伟大理想”；
- `greek_nationalism_status_loc`；
- `megali_idea_status_loc`；
- `byzantium_status_loc`；
- `greek_state_possible_tt`；
- `greek_state_complete_tt`、`_2`、`_3`；
- `embrace_megali_idea_tt` 与 `not_embrace_megali_idea_tt`；
- `embrace_ambitious_agenda_tt` 与 `not_embrace_ambitious_agenda_tt`；
- 现有 modifier 名称与效果 tooltip。

这些文本主要说明真实机制，没有不可接受的时代承诺。若以后单独进行 UI 文案统一，可另立设计，不与本轮叙事重写混合。

## 8. Customizable Localization 路由

新增以下稳定查询：

- `ffpa_greek_nationalism_success_desc`；
- `ffpa_greek_nationalism_success_flavor`；
- `ffpa_greek_nationalism_failure_desc`；
- `ffpa_greek_nationalism_failure_flavor`。

选择顺序固定为：

1. `has_variable = embrace_ambitious_agenda_var`：东罗马/BYZ 路线；
2. `has_variable = embrace_megali_idea_var`：伟大理想路线；
3. fallback：克制希腊国家路线。

`greece.4.d1` 调用成功描述选择器，在东罗马与伟大理想之间分流；`greece.4.d2` 直接使用克制路线正文；`greece.4.f` 调用成功 flavor 选择器并覆盖三条路线。`greece.5.d` 与 `greece.5.f` 调用失败选择器。

选择器只读取已经存在的路线变量，不新增持久变量或迁移。

## 9. 叙事用语规则

### 9.1 灾变称呼

- 事件与 JE 正文主要使用“大火”“烈火落下之日”“旧世界毁灭”等世界内称呼；
- 不在每段文本中重复“核战争”；
- README 可继续明确说明 2050 核战后背景。

### 9.2 国家与身份称呼

- 成立前：希腊、希腊国家、希腊共同政治空间；
- 提议阶段：东罗马头衔、罗马遗产、新罗马；
- 玩家操作与 formation UI：允许使用“拜占庭帝国”以维持辨识度；
- 成立后内部声音：罗马帝国、罗马人的国家、新罗马；
- 不把“拜占庭”写成复兴国家唯一或主要自称。

### 9.3 不预设固定前身

GRE 可能由 Firefall 中不同的希腊 successor tag 形成。文本可以说“大火后的继承政权、地区政权、分裂政权重新拼合”，但不得指定一定来自某个港邦、部落或特定开局 tag。

### 9.4 不伪造法律

- 不承诺宪法、议会、普选或政教关系，除非当前脚本真的检查相应法律；
- `formation.3` 可提及王冠，因为 BYZ formation 的 `possible` 明确要求君主制；
- 可提及正教会，因为 BYZ 国家定义与成立效果恢复正教身份；
- 不声称王冠与教会已经决定后续公民权或行政体制，相关选择留给 FFPA 后续 JE 和事件。

## 10. 逐阶段文本职责

### 10.1 `je_greek_nationalism_reason`

- 以幸存的科莱蒂斯演说副本作为唯一历史引文；
- 明确区分引文所处的旧王国时代与大火后的新希腊；
- 提出核心问题：新国家是否把旧地图当作历史档案、文化共同体，还是现实国策；
- 保留 geographic region 动态名称及现有东罗马 reason custom loc 接缝。

### 10.2 Lobby 文本

- 不再次完整引用科莱蒂斯；
- 用一至两句说明旧世界纲领正在被新国家重新审议；
- 不扩大 lobby 所承诺的机制范围。

### 10.3 `greece.1`

- 标题表达“大火后重新形成的希腊国家”；
- 正文说明国家由地区继承政权重新拼合，但不指定具体前身；
- flavor 是当代政治争论，不再声称刚刚摆脱奥斯曼统治；
- 选项 A 把历史文化空间转化为现实宣称；
- 选项 B 优先巩固已经重新统一的国家。

### 10.4 `ffpa_flavor.8`

- 由王室、正教会、法学家、军官和政治集团重新解释幸存的东罗马档案；
- 目标是是否接受东罗马国号与罗马国家工程，而不是简单复制中世纪制度；
- 普通入口与 JE 已结束后的恢复入口使用同一世界观；
- 接受选项继续写入 `embrace_ambitious_agenda_var` 并产生现有效果；拒绝选项保持原行为。

### 10.5 `formation.3`

- 标题保留“紫凤凰”；
- 场景设在重建中的君士坦丁堡；
- 王冠、正教会、军队、法学家与行省代表共同确认罗马国号；
- 删除古罗马元老院、异教众神与雷电金鹰神迹；
- flavor 强调旧名号只是开始，新国家仍需证明自己能够治理活着的人；
- 不提前承诺后续共同体、首都专精或常驻治理日志的具体选择。

### 10.6 `greece.4` 成功

克制路线：

- 希腊国家完成最低限度的领土统一与制度稳固；
- 奖励解释为行政、权威或合法性成果。

伟大理想路线：

- 爱琴海—马其顿希腊空间完成政治整合；
- 不宣称所有居民只属于一种民族，也不虚构特定前所有者。

东罗马路线：

- 希腊民族纲领已经转化为新的罗马国家工程；
- 成功不等于完成 FFPA 后续“新罗马再加冕”或“罗马人的共同体”，必须保留后续发展空间。

`greece.4.c` 改写为把统一事业转化为政府授权、政府联盟势力或合法性，不再写没有执行的人口遣返。

### 10.7 `greece.5` 失败

克制路线：

- 国家资源与行政能力无法支撑统一计划；
- 失败表现为政府与反对派争夺责任归属。

伟大理想路线：

- 领土纲领失去政治支持，国家威望与官僚信誉受损；
- 不提人口撤离，因为该路线没有对应效果。

东罗马路线：

- 东部罗马事业破产；
- 未控制的艾登、东色雷斯、许达文迪加尔和特拉布宗中的希腊人口被迫迁往 ROOT 首都；
- 这些地区失去希腊故土地位；
- 文本必须把撤离写成失败后果，而不是奖励、自愿移民或正常同化；
- 两个选项仍分别表示政府共同承担失败或追究统治者责任。

## 11. 文件范围

预计修改：

- `common/customizable_localization/ffpa_eastern_mediterranean_custom_loc.txt`：成功/失败路线选择器；
- `events/ffpa_eastern_mediterranean_events.txt`：`ffpa_flavor.8` 改用自有键；
- `events/ffpa_formation_overrides.txt`：`formation.3` 改用自有键；
- `localization/english/ffpa_l_english.yml`：英文覆盖键与自有键；
- `localization/simp_chinese/ffpa_l_simp_chinese.yml`：简中对应键；
- `AGENTS.md`：本地化覆盖登记与上游检查范围。

不修改：

- `common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt` 的逻辑；
- 原版 `greece_events.txt`；
- README；
- metadata；
- 静态 modifier；
- 国家定义、国家形成条件、旗帜或政府类型。

## 12. 覆盖与兼容性

新增覆盖对象是原版本地化键，不是新脚本顶层定义。由于 Victoria 3 本地化按最终加载顺序解析，FFPA 必须继续在原版、Firefall、Tech & Res 和其他相关本地化之后加载。

上游更新后必须重新比较：

- 原版 `ip3_greece_l_english.yml` / `l_simp_chinese.yml`；
- 原版 `JE_lobby_text_l_*`；
- 原版 `greece_events.txt` 中 `greece.1`、`.4`、`.5` 的 title/desc/flavor/option 引用；
- FFPA `je_greek_nationalism` 是否仍触发相同事件；
- FFPA `formation.3` 是否仍为 BYZ 专用。

若另一后加载本地化 Mod 再定义这些键，FFPA 文本可能被覆盖；不能通过文件名前缀假定安全。

## 13. 存档兼容

本设计不新增或修改持久变量、事件 target、JE 状态、动态 modifier 或事件 ID，因此不需要存档迁移。

活动旧 JE 在加载后将显示新的 reason、启动、成功与失败文本，但其路线和进度保持不变。已经排程但尚未弹出的 `greece.1`、`.4`、`.5` 与 `formation.3` 会使用最终加载的新版文本。

## 14. 验证标准

### 14.1 静态验证

- 英文与简中新增键集合完全一致；
- 两份文件保持 UTF-8 BOM；
- customizable localization 的三路线顺序与变量语义正确；
- `ffpa_flavor.8` 和 `formation.3` 不再引用原版叙事正文；
- 机制 tooltip 和 modifier ID 不变；
- `AGENTS.md` 登记全部有意覆盖键；
- `git diff --check` 无新增空白错误。

### 14.2 路线显示

- 克制路线：`greece.4` 与 `.5` 只显示希腊国家巩固/失败文本；
- 伟大理想路线：成功与失败只讨论扩大的希腊政治空间；
- 东罗马路线：成功显示希腊纲领向罗马国家工程转化，失败显示撤离与故土消失；
- `greece.4.c` 显示政府授权语义，不出现“遣返”；
- 三路线均不重复完整科莱蒂斯引文。

### 14.3 成立链

- GRE 启动 JE 时显示旧世界档案框架；
- 正常东罗马提议与 JE 完成后的恢复提议保持同一语气；
- BYZ formation 只显示新的“紫凤凰”正文；
- 成立正文位于君士坦丁堡，不再出现古罗马元老院异教神迹；
- 成立后内部称呼以罗马/新罗马为主。

### 14.4 行为回归

- `greece.1` 两选项的宣称、关系、恶名与路线变量不变；
- `ffpa_flavor.8` 接受/拒绝效果不变；
- `greece.4` 三选项 modifier 不变；
- `greece.5` 两选项惩罚、人口移动与故土移除不变；
- `formation.3` 的威望与查士丁尼宣称白名单不变；
- 新旧存档不需要迁移。

### 14.5 运行时证据

游戏内分别触发六种关键结果：

1. 克制路线成功；
2. 克制路线失败；
3. 伟大理想成功；
4. 伟大理想失败；
5. 东罗马路线成功并形成 BYZ；
6. 东罗马路线失败并执行人口迁移/故土移除。

检查事件标题、正文、flavor、选项、tooltip、效果与最终 modifier。错误归因仍需结合 script location、最终本地化来源和触发路线。

## 15. 成功标准

实现完成后，GRE → BYZ 成立链不再把 1836 年希腊民族主义当作 2050 核战后的无缝当代政治。真实历史通过一份幸存档案保留，其余事件由大火后重新形成的希腊与新罗马社会发声。所有路线文本与实际效果一致，尤其不再出现虚假的人口遣返奖励、无条件宪法承诺和东罗马失败后未被叙述的强制人口撤离。
