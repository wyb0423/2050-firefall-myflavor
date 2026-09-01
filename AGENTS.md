# FFPA Firefall Flavor Pack — Agent 开发指南

## 1. 适用范围与目标

本文件适用于仓库根目录及全部子目录。统一战争、殖民塑形和全局平衡已经剥离到同级的 `2050-firefall-core-balance`；建筑清理已经剥离到同级的 `ffpa-building-pruning` 与 `ffpa-building-pruning-techres`；自动 PM 兼容已经剥离到同级的 `ffpa-techres-auto-pm-adapter`。本文件约束当前的 Firefall 风味合集，并登记与这些外部模块的边界。

本项目是面向 Firefall 与 Tech & Res 固定加载环境的单一风味内容包。发布、启用和依赖管理以整个合集为单位，运行时代码、持久状态、本地化和覆盖登记按国家或地区明确归属。判断任何定义是否正确时，必须以“当前游戏版本 + 所有上游 Mod + 本项目”按实际加载顺序形成的最终数据库为准，不能只看本仓库中的同名文件。

项目当前目标版本和身份以 `.metadata/metadata.json` 为准：

- 玩家可见名称：`FFPA — Firefall Flavor Pack`
- Mod ID：`com.wyb.2050-firefall-personal-adapter`（保留既有发布与存档连续性）
- Victoria 3：`1.13.*`
- 已声明依赖：`2050: The Fire Falls`、`[1.13] Tech & Res`
- README 约定的运行顺序：Tech & Res → Auto-Apply PMs → Auto-Apply Automation PMs → 2050: The Fire Falls → Core Balance Adapter → FFPA Building Pruning → FFPA Building Pruning: Tech & Res Compatibility → FFPA Tech & Res Auto PM Adapter → FFPA Firefall Flavor Pack
- Auto-Apply PMs 的 Workshop ID：`3353797125`
- Auto-Apply Automation PMs 的 Workshop ID：`3344726320`
- Tech & Res 的 Workshop ID：`3472248460`

后面三个 Workshop ID 已归外部 Auto PM Adapter 的生成器与兼容逻辑所有；本项目只为完整加载栈登记它们。两个 Auto-Apply Mod 的当前 metadata ID 为空，不得在本项目中伪造依赖关系。

## 2. 开工前必须执行

1. 运行 `git status --short --branch`，确认用户已有修改。不得覆盖、回退、暂存或提交不属于当前任务的改动。
2. 用 `rg --files -uu -g '!/.git/**'` 盘点文件，用 `rg -n` 同时搜索定义、引用、本地化键和持久变量。
3. 确认游戏根目录、Workshop 根目录、目标 Mod、依赖版本与真实加载顺序。路径是环境输入，不得把新的机器绝对路径写进可复用实现。
4. 对要改的顶层键，依次检查原版、Tech & Res、Firefall 和本项目的最终定义；只有外部 Auto PM Adapter 的变更才需要额外检查两个 Auto-Apply Mod。
5. 在当前安装版本的相同目录、相同脚本类别、相同 scope 中寻找已工作的语法先例。IDE 提示和旧 Wiki 只能作为线索。
6. 先确定下文中的模块所有者，再改文件。跨模块修改必须说明接口变化和拆分影响。

## 3. 总体依赖方向

允许的依赖方向如下；反向引用或环形引用需要先设计显式桥接接口：

```text
游戏原版
  ├─ Firefall ───────────────┬─ 外部 Core Balance Adapter
  │                          └─ FFPA Firefall Flavor Pack
  ├─ Tech & Res ─────────────┬─ 外部 Core Balance Adapter
  │                          ├─ 外部 Auto PM Adapter
  │                          ├─ 外部建筑清理兼容包
  │                          └─ FFPA Firefall Flavor Pack 的数值环境
  ├─ 外部 Building Pruning（无依赖）
  ├─ Auto-Apply PMs ─────────┐
  └─ Auto-Apply Automation ──┴─ 外部 Auto PM Adapter

FFPA Firefall Flavor Pack
  ├─ 东地中海模块
  │  ├─ TUR / BYZ 身份与成立链
  │  ├─ 日志、迁移与共同体状态机
  │  └─ 帝国地区建设 ──> 西方整合桥接 ──> 东地中海风味事件
  └─ 未来国家或地区模块（共享相同依赖，内部状态相互隔离）
```

`localization/`、`.metadata/metadata.json` 和 on_action 数据库是共享接缝，不是可随意堆放业务逻辑的“公共模块”。共享文件中的每一组键仍归对应功能模块所有。

## 4. 功能模块边界

### 4.1 发布元数据与项目说明

**所有文件**

- `.metadata/metadata.json`
- `README.md`
- `AGENTS.md`
- `.gitignore`

**职责**

- 描述版本、依赖、加载顺序、玩家可见行为、诊断入口和维护约定。
- 元数据版本只在实际发布或用户明确要求时提升。

**边界**

- 不承载游戏脚本定义。
- README 只描述当前真实行为；外部拆分包的覆盖数字和诊断入口归各自 README 与报告所有。

### 4.2 外部 Core Balance Adapter 接口

以下功能及其运行时定义已经迁移到同级 `2050-firefall-core-balance`，不再由本仓库拥有：

- 50 年战后人口恢复、创新上限动态镜像和科技扩散；
- 七个制度顶层定义与贸易中心 PM 注入；
- 统一战争 10% 恶名；
- 殖民 AI 地区评分与 `NDiplomacy` 殖民形状。

外部 Mod ID 为 `com.wyb.2050-firefall-core-balance`，依赖 Firefall 与 Tech & Res，不依赖本项目。本项目也不声明对它的依赖；玩家同时启用两者时恢复拆分前的完整功能。

本项目不得重新定义、复制或调用该 Mod 的 `ffpa_refresh_innovation_cap`、统一战争对象、制度、贸易 PM、殖民评分或 define。双方只分别向原版启动/月度 on_action 登记唯一的模块包装入口。

### 4.3 外部 Tech & Res Auto PM Adapter 接口

Tech & Res 自动生产兼容已经完整迁移到同级 `ffpa-techres-auto-pm-adapter`：

- Mod ID：`com.wyb.ffpa-techres-auto-pm-adapter`；
- metadata 硬依赖：`tech.res`；
- 必要运行前置：Auto-Apply PMs `3353797125`、Auto-Apply Automation PMs `3344726320`；
- 独立拥有生成器、三份生成运行时、覆盖报告、决议、JE、按钮、阈值、状态机、on_action 和两种语言本地化。

两个 Auto-Apply Mod 是彼此及 Tech & Res 均独立的通用 Mod；只有外部适配器同时消费三者。外部适配器必须最后加载，当前两个 Auto-Apply Mod 的空 metadata ID 通过 README 和 AGENTS 登记，而不是伪造 Launcher dependency。

本仓库不依赖该适配器，也不得重新定义、复制或调用其 `ffpa_auto_pm_*`、`je_ffpa_auto_pm_*`、生成 ID、持久变量、guard 或上游 `REPLACE:` 对象。旧存档需要启用外部适配器才能继续获得原自动 PM 功能；技术 ID 和存档变量由外部包原样保留。

### 4.4 外部 Building Pruning 接口

低人力亏损建筑清理已经完整迁移到两个同级 Mod：

- `ffpa-building-pruning` / `com.wyb.ffpa-building-pruning`：无依赖主包，拥有日志、按钮、判定、通知、半年调度、玩家/AI 初始化和 44 个原版建筑清单。
- `ffpa-building-pruning-techres` / `com.wyb.ffpa-building-pruning-techres`：只依赖主包与 Tech & Res，通过替换两个可选扫描 effect 增加 28 个 Tech & Res 建筑。

主包导出 `ffpa_prune_private_optional_buildings` 与 `ffpa_prune_government_optional_buildings` 两个稳定扩展槽；兼容包是当前唯一替换者。本仓库不依赖上述两个 Mod，也不得重新定义、复制或调用其清理 effect、JE、消息、持久变量和扩展槽。

原有 `ffpa_private_building_pruning_active`、`ffpa_government_building_pruning_active` 等持久 ID 由主包原样保留；自动 PM 的初始化与 on_action 已与建筑清理完全解耦。

### 4.5 东地中海模块：国家身份核心

**所有文件**

- `common/country_definitions/ffpa_byzantium.txt`
- `common/country_formation/ffpa_byzantium.txt`
- `common/cultures/ffpa_imperial_cultures.txt`
- `common/government_types/00_ffpa_byzantine_governments.txt`
- `common/government_types/00_ffpa_turkish_governments.txt`
- `common/dynamic_country_names/ffpa_byzantium_dynamic_names.txt`
- `common/power_bloc_names/ffpa_eastern_mediterranean_power_bloc_names.txt`
- `common/flag_definitions/ffpa_byzantine_flag_definitions.txt`
- `common/coat_of_arms/coat_of_arms/ffpa_byzantine_flags.txt`
- `common/scripted_guis/ffpa_byzantium_party_names.txt`
- `common/modifier_type_definitions/ffpa_cultural_acceptance_modifier_types.txt`
- `common/ideologies/ffpa_eastern_mediterranean_ideologies.txt`
- `common/interest_group_traits/ffpa_eastern_mediterranean_interest_group_traits.txt`
- `common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt`
- `events/ffpa_formation_overrides.txt`
- 两份本地化文件中的国家、文化、政体、党名、旗帜、国家集团候选名称和成立链键

**拥有的行为与接口**

- 恢复 Firefall 最终数据库中缺失的 `BYZ` 身份和 GRE → BYZ 成立链。
- 保持原版 `TUR`，不创建第二个等价土耳其 tag。
- 定义 `ffpa_ottoman`、`ffpa_rhomaic`、TUR/BYZ 专属政体与政府称谓，以及 BYZ 动态国名、旗帜和党名适配。
- 为 TUR 提供两个通用及三条建国路线各两个国家集团候选名称，为 BYZ 提供两个通用及五类政体各一个候选名称；这些条目只扩展随机名称池，不自动改名。
- 定义五个已改名利益集团使用的八个 `ig_trait_ffpa_*` 风味 trait；每个集团仍保留至少一个原版槽位。
- 提供东地中海状态机使用的意识形态与文化接受 modifier 类型。

**边界与风险**

- 本模块拥有“身份和静态定义”，不拥有日志进度、事件调度或地区建设奖励。
- `BYZ`、`je_greek_nationalism`、`formation.3`、十三个通用党名本地化键、党名数据库适配和旗帜定义都可能覆盖上游对象；更新 Firefall/原版后必须做最终数据库比较。
- 形成 BYZ 后保留已有宣称的约定不可在身份重构时丢失。
- 八个 trait 技术 ID 是存档对象；不得通过覆盖原版 `interest_group` 的 `on_enable` 重新实现其分配。
- 十五个 `ffpa_tur_*` / `ffpa_byz_*` 国家集团名称是普通新增顶层键，不得覆盖原版名称、绑定集团效果或通过周期逻辑强制改名。
- 不要为了 TUR 风味复制或替换原版 TUR 国家定义、旗帜或政体视觉。

**内部所有权**

- 这是东地中海内部的静态身份职责，不再拆成独立物理 Mod。
- 状态机和地区建设可以消费这些稳定对象，但不得复制其顶层定义。

### 4.6 东地中海模块：日志、迁移与风味状态机

**所有文件/切片**

- `common/journal_entries/ffpa_eastern_mediterranean_journal_entries.txt`
- `common/journal_entries/ffpa_byzantine_restoration_campaigns.txt`
- `common/journal_entries/ffpa_turkish_reconstruction_programs.txt`
- `common/journal_entries/ffpa_turkish_frontier_recovery.txt`
- `common/journal_entries/ffpa_permanent_governance_journals.txt`
- `common/journal_entries/zzzz_ffpa_techres_ottoman_collapse_override.txt`
- `common/journal_entry_groups/ffpa_turkish_reconstruction_group.txt`
- `common/journal_entry_groups/ffpa_permanent_governance_groups.txt`
- `common/customizable_localization/ffpa_eastern_mediterranean_custom_loc.txt`
- `common/decisions/ffpa_eastern_mediterranean_decisions.txt`
- `common/decisions/ffpa_turkish_flavor_decisions.txt`
- `common/script_values/ffpa_eastern_mediterranean_values.txt`
- `common/script_values/ffpa_permanent_governance_values.txt`
- `common/scripted_buttons/ffpa_permanent_governance_buttons.txt`
- `common/scripted_progress_bars/ffpa_eastern_mediterranean_progress_bars.txt`
- `common/scripted_progress_bars/ffpa_permanent_governance_progress_bars.txt`
- `common/scripted_triggers/ffpa_eastern_mediterranean_triggers.txt` 中共同体、成立和风味条件
- `common/scripted_triggers/ffpa_turkish_flavor_triggers.txt`
- `common/scripted_triggers/ffpa_permanent_governance_triggers.txt`
- `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt` 中身份、共同体、迁移和风味 effect
- `common/scripted_effects/ffpa_turkish_flavor_effects.txt`
- `common/scripted_effects/ffpa_permanent_governance_effects.txt`
- `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt`
- `common/static_modifiers/ffpa_eastern_mediterranean_modifiers.txt` 中非 `ffpa_region_*` 定义
- `common/static_modifiers/ffpa_turkish_flavor_modifiers.txt`
- `common/static_modifiers/ffpa_permanent_governance_modifiers.txt`
- `events/ffpa_eastern_mediterranean_events.txt` 中非西方整合事件
- `events/ffpa_turkish_flavor_events.txt`
- `events/ffpa_turkish_permanent_governance_events.txt`
- `events/ffpa_byzantine_permanent_governance_events.txt`
- 两份本地化文件中的 `ffpa_flavor.*`、TUR/BYZ 日志与修正键
- `localization/english/ffpa_turkish_flavor_l_english.yml`
- `localization/simp_chinese/ffpa_turkish_flavor_l_simp_chinese.yml`
- `localization/english/ffpa_permanent_governance_l_english.yml`
- `localization/simp_chinese/ffpa_permanent_governance_l_simp_chinese.yml`

**拥有的行为与接口**

- TUR 与 BYZ 的重建、共同体、首都工程和有限政治经济事件。
- TUR 的三条互斥建国路线、高门/共和国/重建总署事件链、三项安纳托利亚工程、计划大会、新海峡公约与三场地区治理会议。
- TUR 的 11 州成立核心永久宣称，以及按建国路线分层、一次一条、15–20 年限期的八条边疆收复前线；临时宣称使用逐州来源标记，超时或撤回后只清理未实现的自有宣称。
- TUR 路线终局后的“帝国簿册与行省中介”“面包与首都”，以及 BYZ 双重重建终局后的“罗马人的公共体”“军户与权门”四项常驻治理日志；四者分别使用平衡、消耗性储备、三支柱修复和单向结构压力，不共享统一模板。
- BYZ 军户日志导出的三阶段改革状态：军役户籍立即落实职业军队或大规模征兵，田产清丈逐步切断土地压力，军需与退伍安置院完成后永久提供全国福利金修正。
- 通过完整替换 Tech & Res `je_ottoman_empire_collapse`，只对 FFPA 管理的 TUR 排除旧奥斯曼崩溃并迁移活动实例；未标记 TUR 保留上游行为。
- BYZ 分区复归战争的御前会议入口、45–55 年日志、成功/失败/重试状态与战后和议选择。
- `namespace = ffpa_flavor` 的既有东地中海事件 ID 空间，以及新增 TUR 内容专用的 `namespace = ffpa_tur_flavor`。
- `on_country_formed`、月度迁移检查、首次选举和 BYZ 公民权白名单州动态整合入口。
- BYZ 成立时与 TUR 取得奥斯曼共同体身份时的一次性 trait 分配，以及 `ffpa_byzantine_interest_group_traits_v1`、`ffpa_ottoman_interest_group_traits_v1` 旧档补发门控。
- 版本化迁移、一次性事件标记、共同体三轴进退和清理路径。

**边界与风险**

- 变量名带 `_v1` / `_v2` 的键都是存档 API，不是可清理的命名噪音。
- `ffpa_tur_state_project_v1` 的值 1/2/3 分别固定表示高门、共和国、重建总署；路线终局、工程、海峡和地区治理选择变量同样属于存档 API。后续政体变化不得自动重写建国路线。
- `ffpa_tur_front_<front>_complete_v1`、`ffpa_tur_front_<front>_retry_cooldown_v1`、`ffpa_tur_front_<front>_resolution_pending_v1`、`ffpa_tur_temporary_claim_<state>_v1`、八条前线 JE 与 `ffpa_tur_flavor.60–84` 都是存档 API；州范围或状态语义变化时必须版本化迁移。
- TUR 八条前线与 BYZ 七条复归战争的 `*_owner_tracking_v1`、`*_owner_snapshot_v1`、`*_completion_predecessor_v1`、`*_completion_predecessor_ready_v1`，以及 `ffpa_tur_restoration_predecessor_tracking_migrated_v1`、`ffpa_byz_restoration_predecessor_tracking_migrated_v1` 都是叙事用存档 API；其含义固定为当前活动前线中最后转入本国的目标 state 实例之直接前所有者，不得改作主要敌国或开战对象。
- 四项常驻日志的 `ffpa_tur_register_*_v1`、`ffpa_tur_capital_*_v1`、`ffpa_byz_public_*_v1`、`ffpa_byz_dynatoi_*_v1`、`ffpa_byz_military_reform_*_v1`、改革完成与福利变量、四项 JE 和六条进度条镜像，以及 `ffpa_tur_flavor.90–92`、`ffpa_flavor.50–52` 均为存档 API；失败只清理运行时冷却与未完成工程，不得删除已完成改革或已落实法律。
- ensure/migration effect 必须幂等；月度入口不得反复发奖励、重置有限期限或遍历全世界建筑。
- 事件链应保持“未初始化 → 可用 → 运行中 → 完成/失败/取消”的显式状态；每条异常路径都要清理临时状态。
- 本模块可消费地区建设模块导出的完成变量和查询 trigger，但不得直接重写地区日志内部状态。
- TUR 的地区治理只在既有地区建设实际完成后触发，不自动授予历史宣称，也不得复制 BYZ 的分区复归战争结构。
- TUR 历史宣称只由边疆收复状态机授予；地区治理会议仍不得添加宣称或直接读取前线 JE 内部状态。

**内部所有权**

- 这是东地中海内部的状态机职责，不再拆成独立物理 Mod。
- 西方整合事件继续消费地区建设导出的稳定查询，不直接读取 15 个日志的内部字段。

### 4.7 东地中海模块：帝国地区建设与西方整合桥接

**所有文件/切片**

- `common/journal_entry_groups/ffpa_imperial_development_group.txt`
- `common/journal_entries/ffpa_imperial_regional_development.txt`
- `common/static_modifiers/ffpa_eastern_mediterranean_modifiers.txt` 中的 `ffpa_region_*` 定义
- `common/scripted_triggers/ffpa_eastern_mediterranean_triggers.txt` 中地区解锁、完成集合和西方整合查询 trigger
- `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt` 中 `ffpa_check_western_integration_events` 接缝
- `events/ffpa_eastern_mediterranean_events.txt` 中由地区完成度触发的西方整合事件
- 两份本地化文件中的地区建设键

**拥有的行为与接口**

- 15 项地区建设 JE、完成变量和仅作用于实际工程州的 `ffpa_region_*` 永久 modifier。
- 向风味模块导出完成状态查询：`ffpa_has_two_western_development_projects`、`ffpa_has_italian_development_project`、`ffpa_has_outer_western_development_project`、`ffpa_western_*_ready`；导出地区奖励地理查询：`ffpa_is_byzantine_western_integration_state`、`ffpa_is_byzantine_outer_western_integration_state`。
- 向 TUR 风味导出既有完成变量，并由 `ffpa_tur_rumelian_settlement_ready_v1`、`ffpa_tur_eastern_settlement_ready_v1`、`ffpa_tur_african_settlement_ready_v1` 聚合为稳定查询；风味侧只调用 `ffpa_check_tur_post_reconstruction_events_v1`，不读取地区 JE 内部状态。
- 完成日志后调用 `ffpa_check_western_integration_events`，但事件具体奖励归风味模块。

**边界与风险**

- 地区 modifier 是物理工程结果，不能在国家身份或共同体完成时全局发放。
- 完成变量和 modifier 名称是旧存档接口；地区更名时保留技术 ID。
- 这是东地中海内部唯一允许的“建设 → 风味”桥；不要让事件直接检查 15 个日志的内部字段。

**内部所有权**

- 地区建设、西方整合 bridge 与风味事件继续随东地中海模块一同发布，不再拆成独立物理 Mod。
- 内部仍通过完成变量和查询 trigger 维持单向“建设 → 风味”数据流，避免形成隐式循环。

### 4.8 开发技能与调研文档

**所有文件**

- `skills/`
- `docs/`

**职责与边界**

- `skills/` 是开发代理说明，不会被 Victoria 3 加载；修改它不等于修改 Mod 行为。
- `docs/` 中的调研和拆分设计必须注明上游、版本、差异、有意排除项和验证限制。
- 自动 PM 生成器、生成产物与覆盖报告归外部 Auto PM Adapter，不得复制回本仓库。
- 这些文件应纳入版本控制，不要因为不是运行时脚本就加入 `.gitignore`。

## 5. 共享接缝与唯一所有者规则

| 共享接缝 | 当前使用者 | 规则 |
|---|---|---|
| `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt` | 东地中海成立、TUR/BYZ 迁移、选举、公民权州同步、复归前所有者快照 | 仅调度 TUR/BYZ；州所有权变化先以十五组 tracking 标记过滤，新州按活动 JE 与地区白名单补建快照，其他州所有权、新州和整合入口仍须先用白名单、owner 或既有 modifier 轻量过滤，不得吸收全局经济功能。 |
| `common/static_modifiers/ffpa_eastern_mediterranean_modifiers.txt` | 风味、共同体、地区建设 | 技术 ID 前缀决定内部所有者；整理文件时按定义完整移动，不复制。 |
| `common/scripted_triggers/ffpa_eastern_mediterranean_triggers.txt` | 风味与地区建设 | 地区模块导出查询 trigger，风味模块消费；禁止反向读取风味内部变量。 |
| `events/ffpa_eastern_mediterranean_events.txt` | TUR/BYZ 风味与西方整合 | 共享 `ffpa_flavor` namespace；新增 ID 先搜索冲突，不重编号旧事件。 |
| `events/ffpa_turkish_flavor_events.txt` | TUR 三路线、工程与地区治理 | 独占 `ffpa_tur_flavor` namespace；不向未来地区模块开放，也不覆盖上游事件。 |
| `localization/english/ffpa_l_english.yml` | 东地中海与未来地区模块 | 每组键归明确地区所有；改玩家可见技术对象时同步更新。 |
| `localization/simp_chinese/ffpa_l_simp_chinese.yml` | 东地中海与未来地区模块 | 与英文保持键集合一致，不得只补一种语言。 |
| 两份 `ffpa_turkish_flavor_l_*.yml` | TUR 三路线、工程与治理会议 | 两种语言保持完全相同的键集合与 UTF-8 BOM；不得把 TUR 新键回填为上游覆盖。 |
| `.metadata/metadata.json` | 风味合集发布外壳 | 只有发布身份或依赖变化才改；不得因内部模块增加而更换既有 Mod ID。 |

跨地区调用优先使用命名清晰的 scripted effect、scripted trigger 或稳定顶层对象。除明确登记的存档接口外，禁止直接读取另一个地区模块的临时变量。

## 6. 覆盖与冲突登记

以下对象不是普通新增定义，修改前必须对最终数据库做差异检查：

| 顶层键/数据库 | 方式 | 原因 | 必查上游 |
|---|---|---|---|
| `BYZ` 国家/成立/动态名/旗帜 | 新建或替换 | Firefall 最终库缺少/改变 BYZ | 原版、Firefall |
| `je_greek_nationalism` | 同名顶层替换 | 接回 GRE → BYZ 路线 | 原版、Firefall |
| `formation.3` | 同名事件完整替换 | 保留原版通知与威望流程，以自有查士丁尼宣称白名单替换原版巴尔干/近东广域宣称 | 原版、Firefall |
| `je_ottoman_empire_collapse` | 同名日志完整替换 | 排除 FFPA 管理的 2050 TUR，并在旧活动实例失效时清理 T&R 崩溃运行状态；其余上游语义保持不变 | Tech & Res |
| `je_greek_nationalism_reason`、`je_greek_nationalism_lobby`、`greece.1.t/d/f/a/b`、`greece.4.t/d1/d2/f/a/b/c`、`greece.5.t/d/f/a/b` | 同名本地化键替换 | 将原版十九世纪希腊叙事改写为大火后重新拼合国家对旧世界档案的再解释，并按克制、伟大理想与东罗马路线显示不同结局 | 原版及任何后加载的希腊事件/本地化 Mod |
| `TUR_ADJ`、`GRE_ADJ` | 同名本地化键替换 | 将 Firefall 英文中误作国名的 `Turkey`、`Greece` 恢复为形容词 `Turkish`、`Greek`；简中同步登记同形词 | 原版、Firefall 及任何后加载的国家本地化 Mod |
| `party_agrarian`、`party_anarchist`、`party_communist`、`party_conservative`、`party_fascist`、`party_free_trade`、`party_liberal`、`party_military`、`party_radicals`、`party_religious`、`party_christian`、`revolutionary_party_name`、`party_social_democrats` | 同名本地化键替换 | 通过 scripted GUI 为 BYZ 返回专属党名，并为其他国家返回原版通用名称 | 原版及任何后加载的党名/本地化 Mod |

文件名前缀 `00_`、`zzz_`、`zzzz_` 只是加载排序工具，不等于安全覆盖。不得仅通过改文件名解决冲突；必须记录目标顶层键、操作语义和后加载者。

统一战争、殖民、制度和贸易中心覆盖登记归外部 Core Balance Adapter；自动 PM 的 40 个上游 replacement 归外部 Auto PM Adapter。若本项目需要消费外部结果，只能通过稳定的最终数据库对象，不得复制覆盖。

## 7. 命名、作用域与存档兼容

- 新增自有技术 ID 使用 `ffpa_` 前缀，并继续细分为地区或国家前缀。现有东地中海沿用 `ffpa_tur_`、`ffpa_byz_`、`ffpa_region_`；新地区不得复用这些空间。
- 新事件使用独立的地区 namespace；`ffpa_flavor` 保留给既有东地中海事件，`ffpa_tur_flavor` 保留给 TUR 新状态机，两者均不供未来地区模块复用。
- 覆盖上游 ID 时保留上游名字，并在文件头注释来源、目标版本、覆盖原因和预期差异。
- trigger 不产生副作用，effect 改状态，script value 算数值，modifier 描述叠加量；不能跨类别照搬语法。
- 每次跨 country/state/building/market/strategic region scope 时，在复杂实现旁写明进入和返回的 scope。
- Firefall 的可成立国家在开局可能没有全局 country 对象。凡“当前国家必须是 TUR/GRE/BYZ”的排他身份门控，必须在 country scope 使用 `country_definition = cd:TUR`、`cd:GRE` 或 `cd:BYZ`；不得把 `c:TAG ?= this` / `c:TAG ?= ROOT` 作为唯一身份断言。
- `?=` 只用于目标对象允许不存在的可选 scope，例如外部国家关系、战争对象、保存 scope、事件目标或已经先用 `exists` 保护的 actor。审查时必须按 scope 与意图区分，禁止对 `c:TAG ?=` 做全仓盲目替换。
- 标识符可能包含连字符；工具和正则不得只接受字母、数字和下划线。
- 持久变量、event target、JE 状态、动态 modifier、事件 ID 和生成 ID 都是存档 API。
- 旧键含义变化时创建新版本键并在幂等 ensure effect 中迁移；不要静默复用，也不要仅为“整洁”删除 `_v1` / `_v2` 键。
- 新游戏初始化、旧存档补发和周期刷新是三个入口，必须分别验证。
- 高频 AI 评分和月度 pulse 保持轻量；全世界、全州、全建筑遍历使用最低必要频率。

## 8. 本地化与文件格式

- 新增任何玩家可见对象时，同步添加英文和简体中文键，并检查两份文件的键集合。
- 保留现有文件的 BOM、换行符、缩进和编码；不要因小改动重写整份脚本或本地化文件。
- 技术 ID 用于脚本和日志，显示文本使用本地化键。
- 本地化文件首行语言头必须保持正确；Victoria 3 本地化通常要求 UTF-8 BOM。
- 不在本地化中承诺脚本没有实现的精确阈值、持续时间或覆盖数量。

## 9. 验证标准

### 9.1 每次修改的最低静态验证

- `.metadata/metadata.json` 能被 `ConvertFrom-Json` 解析。
- 修改文件的花括号、字符串、注释和顶层键结构正常。
- 新增引用能在“最终加载栈”中找到，而不只是本仓库。
- 新增玩家可见对象同时有英文和简体中文本地化。
- 同一 Mod 内没有意外重复顶层键；有意重复/注入要说明操作语义。
- 玩家可见入口、调度包装与其 readiness trigger 中的 TUR/GRE/BYZ 排他身份门控使用 strict `country_definition`；保留的 `c:TAG ?=` 必须能说明对象为何允许不存在。
- `git diff --check` 没有新增空白错误；但不要为通过检查而格式化用户无关文件。

### 9.2 Auto PM Adapter 拆分集成验证

- 本仓库不得再包含自动 PM 运行时、生成器、生成产物、覆盖报告、本地化键、持久变量引用或调度调用。
- 外部适配器必须独立携带全部 517 个顶层键、两种语言各 26 个键和 40 个上游 replacement。
- 迁移前后生成器、三个生成脚本和覆盖报告的 SHA-256 必须一致。
- 外部包与本项目不得互相依赖、调用或重复定义自有顶层键。
- 旧存档需启用外部适配器才能继续获得原自动 PM 状态机和界面。

### 9.3 建筑清理修改的额外验证

- 本仓库不得再包含建筑清理运行时文件、本地化键、持久变量引用或调度调用。
- 外部主包的私有/公有原版清单必须一致；外部兼容包的私有/公有 Tech & Res 清单也必须一致，且两包清单不得交叉。
- 主包单独启用时不得解析 Tech & Res 建筑 ID；兼容包只能替换两个已登记的可选扫描 effect。
- 同时启用两包时，战争、补贴、保护建筑、正利润和高雇佣率仍能分别阻止删除，且只在实际删除后发送通知。
- 新旧存档分别验证默认变量、日志挂载和原持久设置的继承。

### 9.4 东地中海模块修改的额外验证

- Firefall 开局尚无 TUR/GRE/BYZ country 对象时，其他国家不得获得其政府类型、决议、JE、事件、迁移变量或国家集团候选名称；对应 tag 形成后这些内容只对正确 country definition 开放。
- GRE → BYZ 成立、TUR 不被替换、BYZ 形成后宣称保留。
- 共同体三轴分别前进/倒退，完成奖励不重复。
- TUR 三条建国路线在新档中分别可达且互斥；旧档可从奥斯曼共同体/文化和安纳托利亚公民权可靠迁移，无法识别的重建总署旧档只出现一次人工确认入口。
- TUR 三条路线各自的三场里程碑事件、终局选择和临时状态只能触发一次；政体变化只暂停不符合条件的完成检查，不改写建国路线。
- 黑海、高原和丘库罗瓦—幼发拉底工程只奖励实际工程州，连同安纳托利亚干线满足四选三后计划大会只触发一次；海峡三种制度互斥并只作用于 TUR 拥有的东色雷斯。
- 鲁米利亚、东方水利贸易和非洲港口治理会议只消费既有地区完成查询，不授予宣称、不重复触发，也不读取地区 JE 内部字段。
- TUR 新旧档均补齐 Firefall 成立清单中的 11 州核心宣称；已有领土或其他来源宣称不被重写，核心宣称不因前线结束或标签变化清理。
- 共和国、重建总署和高门只显示各自前线及正确解锁顺序；活动或待结算前线占用唯一槽位，成功、部分超时、主动撤回、战争中延迟结算和五年重试均能幂等收尾。
- 临时宣称只在边疆委员会授权时添加；清理必须同时要求逐州来源标记，保留已取得州和启动前已有的宣称，前线成功不得自动完成地区建设。
- FFPA 管理的 TUR 不显示或完成 Tech & Res 奥斯曼崩溃日志；旧活动实例失效时不拆分领土，并在一年清理窗口吸收已排程事件对 TUR 崩溃变量的回写；未标记 TUR 保持上游行为。
- TUR 常驻簿册日志的两个极端计时分别推进且离开极端会倒退；首都供应异常严格对应谷物、首都运输、首都电力和首都市场接入四项，失败后的首都地区与国家修正均随时间衰减，并固定留在失败时的首都州。
- BYZ 公共体的法统、全国福祉和公共认同条件不交叉复用，全国州判定每月只扫描一次已整合州；警告、破裂、强制修复、五年失败冷却和重试初态分别可达。
- BYZ 权门压力按法律、地主力量、税收路线和三个改革阶段正确累加；重编军役户籍事件立即落实所选军制法，违约暂停工程，改革疲劳与高压强制入口互斥，失败保留已完成阶段、军制法和永久福利修正。
- 所有失败、取消、政体变化、标签形成和旧存档路径都能清理或迁移状态。
- 地区建设只奖励实际覆盖州；完成状态可稳定触发一次西方整合事件。
- 公民权整合速度只作用于 BYZ 拥有的未整合西方白名单州，未来取得、失去、完成整合和身份变化路径能补发或清理。
- BYZ 新旧档分别获得五个专属 trait，且四个未替换槽位保持原版；TUR 只在取得 `ffpa_ottoman` 后获得三个专属 trait，两个已改名集团的其余三个槽位及未改名虔诚集团的 Mecelle 等原版 trait 不受影响。
- 两个 trait 迁移变量设置后不得在月度 pulse 重复写槽位；旧档已有名称变量时仍必须补发 trait。
- 动态国名、政府称号、党名、旗帜、国家集团候选名称和两种语言在主要政体路径下显示正确。

### 9.5 Core Balance 拆分集成验证

- 本项目不得再包含统一战争、殖民塑形、通用平衡或对应本地化键。
- 新旧 Mod 的自有顶层键不得重复；原版 on_action 接缝只比较各自唯一的包装列表。
- 同时启用 Core Balance 与本项目时，创新刷新与东地中海迁移分别到达，且互不调用对方的 effect；建筑清理与自动 PM 分别由各自外部包独立调度。
- 旧存档需同时启用两个 Mod 才能保持拆分前的完整功能。

### 9.6 运行时证据

依次区分以下五层，不要把“定义存在”当成“功能生效”：

1. 文件被加载且没有被后加载内容覆盖。
2. 顶层定义成功解析。
3. on_action / JE / decision / event 调度入口实际到达。
4. trigger 在正确 scope 成立，effect 确实执行。
5. 最终状态未被上游或另一模块回写、回滚或覆盖。

检查 Victoria 3 用户目录下 `logs/debug*.log`、`error*.log`、`game*.log` 的最新文件和轮转文件。错误归因必须同时依据 script location、最终定义来源、触发时间和调用链。

无法启动游戏时，交付说明必须分别列出：已静态确认、已由生成器断言、已由日志确认、仍需游戏内验证。

## 10. Git 工作约定

- 本仓库可能长期有用户未提交工作；开工和交付都运行 `git status --short --branch`。
- 未经明确要求，不执行 `git add`、`git commit`、`git reset`、`git checkout --`、`git clean`、rebase 或 force push。
- 新分支默认使用 `codex/` 前缀。
- 不把 `.metadata/`、`localization/`、生成脚本、生成产物、覆盖报告、迁移文档或 `skills/` 加入 `.gitignore`。
- 大型生成文件是运行时产物，允许体积大；评审时重点看生成器差异、覆盖数字和哈希，而不是逐行阅读数十万行生成代码。
- 不把本机游戏路径、Workshop 路径、日志、存档、崩溃转储、编辑器状态或发布压缩包提交进仓库。

## 11. 风味合集扩展约定

统一战争、殖民塑形和全局平衡已经整体迁移到 `2050-firefall-core-balance`，建筑清理已经迁移到无依赖主包与可选 Tech & Res 兼容包，自动 PM 兼容已经迁移到 `ffpa-techres-auto-pm-adapter`。东地中海身份、状态机、地区建设和风味作为合集的第一个内部模块保留，不再进行物理拆分。

新增国家或地区风味时依次执行：

1. 确认它继续以 Firefall 与 Tech & Res 为固定依赖；如需新的硬依赖或独立启停，先重新判断物理发布边界。
2. 登记地区所有者、文件前缀、事件 namespace、持久变量、本地化键和上游覆盖对象。
3. 分别设计新游戏初始化、旧存档补发和周期刷新入口，并使用唯一的轻量 on_action 包装 ID。
4. 仅在真实联动出现时导出 scripted trigger/effect；不得预建通用框架或直接读取另一地区的临时变量。
5. 建立新增前后的顶层键与本地化键清单，确认没有与东地中海或外部拆分包产生意外重复。

## 12. 交付格式

完成任务时简要报告：

- 修改了哪个模块及其文件。
- 是否改变跨模块接口、上游覆盖或存档 API。
- 执行了哪些静态、生成器和运行时验证。
- 哪些结论仍需游戏内确认。
- 当前 Git 分支与工作树状态；不得把用户原有修改冒充为本次改动。
