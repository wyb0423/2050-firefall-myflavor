# BYZ 西罗马公民权宪章地区整合加速设计

日期：2026-08-31

状态：已实施，待游戏内验证

## 1. 背景与现有设计关系

`ffpa_flavor.32`“西罗马公民权宪章”已经通过文化接受度、政治反应和路线专属 modifier 表达西方人口进入罗马政治共同体的结果，但没有直接改善州整合速度。实际游戏中，意大利和伊比利亚州通常仍需较长时间整合，埃及与马格里布州尤其明显，因此事件的叙事承诺与行政结果之间存在落差。

本设计是 `2026-08-31-byz-western-integration-permanent-choices-design.md` 的专项增补。既有设计中的以下接口继续有效：

- 事件 ID `ffpa_flavor.32`；
- 西方整合完整州白名单 trigger `ffpa_is_byzantine_western_integration_state`；
- 选择变量 `ffpa_byz_western_citizenship_choice_v2`；
- 选择值 `1–3` 以及对应的国家和历史快照州 modifier；
- `ffpa_byz_western_civic_extension_fired_v1` 等现有调度和存档标记。

本设计不改变其他三个西方整合事件，也不改变既有永久奖励的“选择时州快照”语义。新增的整合速度是公民权政策在行政整合期间发挥作用的动态奖励，因此使用独立状态机。

## 2. 调研结论

### 2.1 Victoria 3 1.13.11 机制

当前安装版本提供以下州级 modifier 类型：

- `state_incorporation_speed_mult`；
- `state_contiguous_incorporation_speed_mult`；
- `state_non_contiguous_incorporation_speed_mult`。

本设计使用不区分陆路连续性的 `state_incorporation_speed_mult`。白名单同时覆盖隔海的意大利、伊比利亚、马格里布和埃及，改用连续或非连续专用 modifier 会让同一公民权制度因地理连接方式产生不必要的数值差异。

原版 1.13.11 的基础整合时间大致为：

- 同文化：2 年；
- 同传承且同语言：5 年；
- 同传承或同语言：10 年；
- 同文化特质组：15 年；
- 无匹配：25 年。

`ffpa_rhomaic` 使用希腊传承与语言。意大利和伊比利亚文化通常落在约 15 年档，埃及和北非文化通常落在约 25 年档。原版社会科技合计还可提供约 `+25%` 整合速度；Firefall 与 Tech & Res 当前未重定义本设计使用的三个 modifier 类型。

以已取得约 `+25%` 科技加成为例，三条路线的近似结果为：

| 基础整合时间 | 普遍公民权 `+75%` | 行省公民契约 `+50%` | 服役即公民权 `+25%` |
|---|---:|---:|---:|
| 15 年 | 约 7.5 年 | 约 8.6 年 | 约 10 年 |
| 25 年 | 约 12.5 年 | 约 14.3 年 | 约 16.7 年 |

这些数值显著缩短西方重建期，但不会把北非或西欧新领土瞬间变成整合州。

### 2.2 历史与风味依据

罗马公民权扩张可以合理地代表法律身份、征税资格、司法渠道和公共义务进入统一制度，从而缩短新领土转化为正式行政区所需的时间。与此同时，公民权并不会自动消除地方语言、宗教、城市制度和精英网络，因此效果应是“加速整合”而不是直接整合。

拜占庭行省治理也长期依赖中央规范与地方官员、城市和地方精英之间的合作。由此形成三档风味：

- 普遍公民权以统一法权直接覆盖行省，速度最高、政治冲击最大；
- 行省公民契约借助地方共同体落实公民身份，速度居中；
- 服役即公民权通过军役、工程军团与退伍军人网络建立有限联系，仍有帮助但不能替代完整民政体系。

白名单限制使这项制度表现为对查士丁尼传统疆域和既有西方建设范围的“再接纳”，而不是 BYZ 征服任意地区时都可使用的全球同化能力。

## 3. 目标

- 为 `.32` 的三条路线分别提供 `+75% / +50% / +25%` 州整合速度。
- 只作用于 `ffpa_is_byzantine_western_integration_state` 白名单中的州。
- 同时覆盖事件发生时已经拥有的州，以及事件后新取得或新生成的白名单州。
- 只在州未整合且由 BYZ 拥有时生效；领土失去、整合完成或国家身份改变后清理。
- 复用既有 v2 选择状态，不建立第二套路线变量。
- 使用事件驱动的幂等刷新，不增加月度或季度全量州扫描。
- 为旧存档提供可证明、只执行一次的迁移。

## 4. 非目标

- 不直接把白名单州设为已整合。
- 不改变州整合的官僚机构成本、开始条件或取消规则。
- 不把整合速度写入全国 modifier；非白名单领土永远不应获得本奖励。
- 不改变三个选项现有的文化接受度、政治代价、军事效果、移民或资格奖励。
- 不把第三项既有的退伍军人定居快照范围从“外西方边疆州”扩大到完整白名单；只有新增的整合速度使用完整白名单。
- 不修改 15 项地区建设 JE、完成变量、工程 modifier 或外部拆分 Mod 接口。

## 5. 方案比较与采用方案

### 5.1 采用：事件驱动的动态州 modifier

事件选择写入既有路线变量并立即刷新当前州。以后由州所有权变化、新州创建和州整合 on_action 调用同一个州级幂等 effect。

优点：

- 精确遵守白名单；
- 能覆盖以后取得的州；
- 领土丢失时可以即时清理；
- 不需要周期性遍历所有国家或所有州；
- 路线状态、地区范围和实际 modifier 相互分离，便于迁移和诊断。

### 5.2 未采用：周期性刷新

每季度或每年扫描 BYZ 所有州也能补齐未来领土，但奖励出现存在延迟，并把本可由明确状态变化驱动的功能放入长期 pulse。旧存档的一次性迁移仍可使用现有月度 ensure，但迁移完成后不保留周期扫描。

### 5.3 未采用：全国整合速度 modifier

把 `state_incorporation_speed_mult` 放入国家 modifier 实现最简单，但会影响 BYZ 在白名单外取得的所有领土，违反用户确认的地区边界，也会削弱西方整合建设链的独特性。

## 6. 持久状态与 modifier

### 6.1 权威路线状态

继续以 `ffpa_byz_western_citizenship_choice_v2` 为唯一权威路线状态：

| 值 | 路线 | 动态整合速度 |
|---:|---|---:|
| `1` | 罗马人不分行省／普遍公民权 | `+75%` |
| `2` | 城市与行省共同体／行省公民契约 | `+50%` |
| `3` | 服役即公民权 | `+25%` |

不得另建三个布尔路线标记。数值变量与现有西方整合永久选择设计一致，避免出现两套可能互相矛盾的存档状态。

### 6.2 新州 modifier

新增三项只含整合速度的州 modifier：

- `ffpa_byz_western_universal_incorporation_state_v1`：`state_incorporation_speed_mult = 0.75`；
- `ffpa_byz_western_provincial_incorporation_state_v1`：`state_incorporation_speed_mult = 0.50`；
- `ffpa_byz_western_service_incorporation_state_v1`：`state_incorporation_speed_mult = 0.25`。

必须使用独立 modifier，不能把数值并入以下既有对象：

- `ffpa_byz_western_universal_citizenship_v2`；
- `ffpa_byz_western_provincial_civic_compact_state_v2`；
- `ffpa_byz_western_veteran_settlement_state_v2`。

原因是既有对象属于永久国家奖励或选择时州快照；新增对象则要随所有权和整合状态动态挂载、移除。合并会导致非白名单泄漏、未来领土遗漏，或在清理整合速度时误删其他永久奖励。

### 6.3 新迁移标记

新增国家变量：

- `ffpa_byz_western_citizenship_incorporation_migrated_v1`。

它只表示“本次动态整合奖励已经按当前可证明路线完成首次刷新”，不替代 `ffpa_western_integration_rewards_migrated_v2`。两项迁移必须保持先后顺序：先建立或确认 v2 公民权选择，再迁移动态州奖励。

## 7. 刷新 effect 设计

### 7.1 单州刷新

新增州 scope 的幂等 effect，例如：

- `ffpa_refresh_byz_western_citizenship_incorporation_state_v1`。

每次调用时先移除三项动态整合 modifier，再按以下条件至多添加一项：

1. 当前州满足 `ffpa_is_byzantine_western_integration_state = yes`；
2. 当前州 `is_incorporated = no`；
3. 当前 owner 是 `c:BYZ`；
4. owner 拥有合法的 `ffpa_byz_western_citizenship_choice_v2` 值；
5. 按选择值添加 `+75%`、`+50%` 或 `+25%` 对应 modifier。

“先清理、后至多添加一项”保证 effect 可重复执行，也能修复控制台操作、旧测试版本或异常状态造成的重复 modifier。

### 7.2 BYZ 全州刷新

新增 country scope effect，例如：

- `ffpa_refresh_byz_western_citizenship_incorporation_states_v1`。

它只在 Root 是 BYZ 且选择值合法时遍历 Root 当前拥有的 scope states，并调用单州刷新。事件选择和旧存档迁移使用该入口；所有权变化等单州事件不调用全州遍历。

为了清理身份变化后的遗留 modifier，可增加一个只遍历 Root 当前州并调用单州刷新的通用清理包装。它在低频的国家成立事件中使用，不加入月度 pulse。

## 8. 调度入口

### 8.1 `ffpa_flavor.32`

三个选项保持现有永久奖励和政治反应，按以下顺序增加新行为：

1. 清理需要迁移的旧公民权奖励；
2. 写入 `ffpa_byz_western_citizenship_choice_v2 = 1/2/3`；
3. 发放现有 v2 国家和历史快照州奖励；
4. 调用 BYZ 全州动态整合刷新；
5. 设置 `ffpa_byz_western_citizenship_incorporation_migrated_v1`；
6. 结算非 review 模式的一次性利益集团反应。

所有三条路线的动态整合奖励都使用完整 `ffpa_is_byzantine_western_integration_state` 白名单。第三项的既有 `ffpa_byz_western_veteran_settlement_state_v2` 仍只授予 `ffpa_is_byzantine_outer_western_integration_state` 快照州，二者不得混用。

### 8.2 州级 on_action

在共享 on_action 数据库中只追加 FFPA 自有包装入口，不复制或替换原版 effect：

- `on_state_owner_change`：Root 为所有权发生变化的州，调用单州刷新。州转入 BYZ 时补发；转出 BYZ 时清理。
- `on_state_created`：Root 为新州，调用单州刷新，覆盖拆分州和运行时新建州。
- `on_state_incorporation`：Root 为相关州，调用单州刷新，用于整合状态变化时同步或清理。

当前 1.13.11 的 `00_code_on_actions.txt` 明确记录这三个入口的 Root 为州；原版没有注明 `on_state_incorporation` 在开始还是完成阶段触发。因此实现不能仅凭静态文件宣称完成后清理已经验证，必须进行游戏内日志验证。无论该入口在开始还是完成时触发，单州 effect 都保持幂等；整合速度是否生效不依赖清理后的 UI 状态。

### 8.3 国家身份变化

复用本模块已有 `on_country_formed` 包装入口：

- Root 成为 BYZ 时，在选择和迁移状态有效的情况下刷新当前白名单州；
- 原 BYZ 国家形成其他 tag 时，对其当前州执行清理包装，移除三项动态整合 modifier。

革命、割让和归还主要由 `on_state_owner_change` 处理。不得为这些低频状态变化另建全局月度扫描。

## 9. 旧存档迁移

### 9.1 推断顺序

月度 `ffpa_ensure_eastern_mediterranean_v2` 只在新迁移标记缺失时执行以下轻量检查：

1. 若 `ffpa_byz_western_citizenship_choice_v2` 已为合法值 `1–3`，直接以它为准；
2. 若选择值缺失，而旧版永久“普遍公民权”modifier 是唯一存在的旧公民权 modifier，则由既有 v2 迁移映射为值 `1`；
3. 若选择值缺失，而旧版永久“行省公民契约”modifier 是唯一存在的旧公民权 modifier，则映射为值 `2`；
4. 若两个旧 modifier 同时存在或都不存在，不猜测路线，也不发放整合速度；继续使用既有 v2 review 流程让玩家重新确认；
5. 路线得到确认后执行一次 BYZ 全州刷新并设置新迁移标记。

既有 v2 迁移判断必须确保“恰好一个旧 modifier”才能自动推断，不能因 `if/else_if` 顺序在两个旧 modifier 同时存在时默认选择普遍公民权。

### 9.2 幂等性

- 新标记存在时，月度 ensure 不遍历州；
- 选择事件设置标记后，下个月不得重复发放；
- 已存在正确 modifier 的州重复刷新后仍只保留一项；
- 没有可证明路线的旧存档不设置新标记，待 review 选择完成后由事件直接刷新；
- 白名单以后发生技术 ID 或范围变化时必须增加新的迁移版本，不能重用 `_v1` 标记静默改变旧存档。

## 10. 玩家可见文本

英文和简体中文必须同步增加：

- 三项动态州 modifier 的名称和描述；
- 三条选项各自的精确 tooltip；
- 必要时补充事件描述中关于行政整合的句子。

建议中文 tooltip 语义：

- 普遍公民权：当前以及以后取得的未整合西方整合白名单州获得 `+75%` 地区整合速度，直至完成整合或失去该州。
- 行省公民契约：同范围获得 `+50%`。
- 服役即公民权：同范围获得 `+25%`。

tooltip 必须明确“当前及以后取得”“未整合”“西方整合白名单州”三个边界。由于动态奖励通过 scripted effect 和 on_action 发放，不能只依赖 `add_modifier` 自动 tooltip。

## 11. 预计实施文件

东地中海风味与地区建设模块内部修改：

- `events/ffpa_eastern_mediterranean_events.txt`：三项选择接入动态刷新和 tooltip；
- `common/static_modifiers/ffpa_eastern_mediterranean_modifiers.txt`：新增三项动态州 modifier；
- `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt`：新增单州刷新、全州刷新和一次性迁移，并收紧旧路线推断；
- `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt`：追加州所有权、新州、州整合和身份变化包装入口；
- `localization/english/ffpa_l_english.yml`：新增英文 modifier 与 tooltip；
- `localization/simp_chinese/ffpa_l_simp_chinese.yml`：与英文保持相同键集合；
- `docs/superpowers/specs/2026-08-31-byz-western-integration-permanent-choices-design.md`：在 `.32` 和验证章节中交叉引用本专项设计，避免旧文档继续暗示公民权没有动态整合效果。

不修改 metadata、国家定义、成立链、地区建设 JE、白名单内容或任何外部拆分包。

## 12. 验证标准

### 12.1 静态验证

- 当前游戏、Firefall、Tech & Res 与本项目最终加载栈中可以解析 `state_incorporation_speed_mult`。
- 三项新 modifier 顶层键唯一，且只含对应整合速度。
- 单州 effect 的 whitelist、owner、`is_incorporated` 和路线判断都在正确 scope。
- on_action 通过唯一 FFPA 包装追加，不替换原版同名 effect。
- `.32` 的事件 ID、trigger、fired/scheduled/review 变量和既有奖励未被删除。
- 第三项整合速度使用完整白名单；退伍军人定居快照仍使用外西方子集。
- 两份本地化键集合一致并保持 UTF-8 BOM。
- 修改文件花括号、字符串、注释和顶层键结构正常。
- `.metadata/metadata.json` 仍可解析，`git diff --check` 无新增空白错误。

### 12.2 新游戏路径

分别选择三条路线并验证：

1. 当前拥有的未整合白名单州只获得对应 `+75% / +50% / +25%` modifier；
2. 当前拥有的已整合白名单州不获得；
3. 当前拥有的非白名单州不获得；
4. 以后取得的未整合白名单州在所有权变化后立即获得；
5. 以后取得的非白名单州仍不获得；
6. 州失去后 modifier 被移除，重新取得后按原路线恢复；
7. 州开始整合时预计时间反映对应加速；
8. 州完成整合后 modifier 被移除且不再显示；
9. 第三路线在完整白名单获得 `+25%`，但退伍军人定居快照仍只出现在外西方子集。

### 12.3 旧存档与异常路径

- 已有合法 v2 选择但缺少新迁移标记：补发一次当前动态州奖励。
- 仅有旧普遍公民权 modifier：迁移为路线 `1` 并补发一次。
- 仅有旧行省公民契约 modifier：迁移为路线 `2` 并补发一次。
- 两个旧 modifier 同时存在：不猜测、不发奖，进入既有 review 流程。
- 两个旧 modifier 都不存在但 fired 标记存在：不猜测、不发奖，进入既有 review 流程。
- review 选择完成后立即获得正确动态奖励，不重复发放一次性忠诚派或激进派。
- 已迁移存档反复加载和经过多个月度 pulse 后不重复遍历或叠加 modifier。
- 革命转手、州拆分、领土割让与归还分别触发清理或补发。
- BYZ 形成其他 tag 后清理；新形成 BYZ 且存在合法路线状态时恢复。

### 12.4 运行时证据

测试时用日志分别确认：

1. `on_state_owner_change` 和 `on_state_created` 到达单州刷新；
2. `on_state_incorporation` 的实际触发时点以及完成后的清理结果；
3. 事件选择和旧存档 ensure 到达全州刷新；
4. modifier 实际改变整合预计时间，而非只成功解析；
5. 最终状态没有被上游或其他模块回写。

如 `on_state_incorporation` 在 1.13.11 中不能完成整合后的清理，应先记录日志证据并重新评审清理入口，不得直接引入未确认的高频全州扫描。交付时必须把“已静态确认”和“仍需游戏内确认”分开报告。

## 13. 接口与兼容性结论

- 跨模块接口：不变；继续只消费地区建设导出的稳定白名单 trigger。
- 上游覆盖：不新增原版、Firefall 或 Tech & Res 顶层覆盖。
- 存档 API：新增三项州 modifier ID 和一个迁移标记；复用既有 v2 选择变量。
- 调度接口：在本模块共享 on_action 文件中追加唯一包装入口。
- 性能：事件选择和旧存档迁移允许一次性遍历 BYZ 当前州；日常所有权与整合变化只刷新单州。

## 14. 参考资料

- Victoria 3 1.13.11：`game/common/defines/00_defines.txt`。
- Victoria 3 1.13.11：`game/common/modifier_type_definitions/00_modifier_types.txt`。
- Victoria 3 1.13.11：`game/common/on_actions/00_code_on_actions.txt` 与 `game/common/on_actions/_on_actions.md`。
- Metropolitan Museum of Art, *The World between Empires: Art and Identity in the Ancient Middle East*: https://resources.metmuseum.org/resources/metpublications/pdf/The_World_between_Empires_Art_and_Identity_in_the_Ancient_Middle_East.pdf
- Oxford Academic, *Byzantine Provincial Administration*: https://academic.oup.com/edited-volume/29470/chapter-abstract/247164258

## 15. 已确认决策

- 采用事件驱动方案 A；
- 奖励只作用于现有西方整合完整白名单；
- 事件后新取得的白名单领土自动获得奖励；
- 三条路线分别为 `+75% / +50% / +25%`；
- 不增加周期性全州扫描；
- 三条路线共用现有 `ffpa_byz_western_citizenship_choice_v2`；
- 旧存档只在路线可证明时自动迁移，歧义状态由既有 review 流程解决。
