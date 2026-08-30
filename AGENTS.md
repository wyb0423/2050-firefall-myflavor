# 2050 Firefall Personal Adapter — Agent 开发指南

## 1. 适用范围与目标

本文件适用于仓库根目录及全部子目录。它既是当前单体 Mod 的维护约定，也是将来拆成多个 Mod 时的边界说明。

本项目不是独立内容包，而是加载栈末端的个人适配层。判断任何定义是否正确时，必须以“当前游戏版本 + 所有上游 Mod + 本项目”按实际加载顺序形成的最终数据库为准，不能只看本仓库中的同名文件。

项目当前目标版本和身份以 `.metadata/metadata.json` 为准：

- Mod ID：`com.wyb.2050-firefall-personal-adapter`
- Victoria 3：`1.13.*`
- 已声明依赖：`2050: The Fire Falls`、`[1.13] Tech & Res`
- README 约定的运行顺序：Tech & Res → Auto-Apply PMs → Auto-Apply Automation PMs → 2050: The Fire Falls → 本项目
- Auto-Apply PMs 的 Workshop ID：`3353797125`
- Auto-Apply Automation PMs 的 Workshop ID：`3344726320`
- Tech & Res 的 Workshop ID：`3472248460`

后面三个 Workshop ID 是生成器和兼容逻辑的输入接口；它们目前没有全部写入元数据依赖。不要在没有确认可选/必需语义和 Launcher 行为前擅自改动依赖声明。

## 2. 开工前必须执行

1. 运行 `git status --short --branch`，确认用户已有修改。不得覆盖、回退、暂存或提交不属于当前任务的改动。
2. 用 `rg --files -uu -g '!/.git/**'` 盘点文件，用 `rg -n` 同时搜索定义、引用、本地化键和持久变量。
3. 确认游戏根目录、Workshop 根目录、目标 Mod、依赖版本与真实加载顺序。路径是环境输入，不得把新的机器绝对路径写进可复用实现。
4. 对要改的顶层键，依次检查原版、Tech & Res、两个自动 PM Mod、Firefall 和本项目的最终定义。
5. 在当前安装版本的相同目录、相同脚本类别、相同 scope 中寻找已工作的语法先例。IDE 提示和旧 Wiki 只能作为线索。
6. 先确定下文中的模块所有者，再改文件。跨模块修改必须说明接口变化和拆分影响。

推荐用参数而不是固化路径调用生成器：

```powershell
$GameRoot = '<Victoria 3>/game'
$WorkshopRoot = '<Steam>/steamapps/workshop/content/529340'
./tools/generate_ffpa_auto_pm_compat.ps1 `
  -GameRoot $GameRoot `
  -WorkshopRoot $WorkshopRoot `
  -OutputRoot (Get-Location).Path
```

## 3. 总体依赖方向

允许的依赖方向如下；反向引用或环形引用需要先设计显式桥接接口：

```text
游戏原版
  ├─ Firefall ───────────────┬─ 全局平衡
  │                          ├─ 统一战争
  │                          ├─ 殖民 AI / 殖民形状
  │                          └─ 东地中海核心
  ├─ Tech & Res ─────────────┬─ 自动 PM 兼容
  │                          ├─ 建筑清理覆盖扩展
  │                          └─ 东地中海内容的数值环境
  ├─ Auto-Apply PMs ─────────┐
  └─ Auto-Apply Automation ──┴─ 自动 PM 兼容

东地中海核心
  ├─ 东地中海状态机与风味
  └─ 帝国地区建设 ──> 西方整合桥接 ──> 东地中海风味事件
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
- README 只描述当前真实行为；生成覆盖数字来自 `TECHRES_AUTO_PM_COVERAGE.md`，不要手工猜测。

### 4.2 全局平衡与通用生命周期

**所有文件/切片**

- `common/history/global/zzz_ffpa_global.txt`
- `common/static_modifiers/ffpa_modifiers.txt`
- `common/scripted_effects/ffpa_innovation_effects.txt`
- `common/institutions/00_institutions.txt`
- `common/production_methods/ffpa_trade_center.txt`
- `common/on_actions/ffpa_on_actions.txt` 中的创新上限初始化与月度刷新切片
- 两份本地化文件中的相应键

**拥有的行为与接口**

- 50 年战后人口恢复：`ffpa_postwar_population_recovery`。
- 动态镜像并翻倍创新上限：`ffpa_refresh_innovation_cap`、`ffpa_double_innovation_cap`、`ffpa_innovation_cap_mirror_value`。
- 永久翻倍科技传播：`ffpa_double_technology_spread`。
- 制度数值覆盖，包括殖民增长、社会保障、工作场所安全、警察和内务。
- 贸易中心容量和贸易数量 PM 的注入。

**边界与风险**

- 创新上限是动态 modifier 图，读取旧值、移除旧 modifier、重建镜像的顺序是逻辑的一部分；不得简化成无状态的 remove/add。
- `ffpa_innovation_cap_mirror_value` 是存档接口。改变含义必须使用新版本键并迁移。
- `common/institutions/00_institutions.txt` 含多个原版顶层键，是未来最适合按顶层键拆分、但也是上游更新风险最高的文件之一。
- 贸易 PM 使用 `INJECT:`，只能增加指定字段；不要复制完整 PM，也不要让本模块接管自动 PM 的选择逻辑。

**未来拆分单位**

- 可整体拆成 `ffpa-core-balance`；殖民制度的顶层键也可跟随殖民模块，但必须避免两个包同时定义 `institution_colonial_affairs`。

### 4.3 统一战争 10% 恶名适配

**所有文件**

- `common/game_rules/ffpa_union_war_rules.txt`
- `common/script_values/ffpa_union_war_values.txt`
- `common/diplomatic_plays/ffpa_union_war_plays.txt`
- `common/war_goal_types/ffpa_union_war_goal.txt`
- `common/scripted_effects/ffpa_union_war_effects.txt`
- 两份本地化文件中的 `uw_*` / `ffpa_union_*` 对应键

**拥有的行为与接口**

- 新增 `dp_union_war_tenth` 和 `ffpa_union_war_annex_country_tenth`。
- 为 Firefall 的 `uw_infamy_cost` 增加 10% 规则选项。
- 替换 `uw_estimated_union_war_infamy` 与 `uw_start_union_war`，把 10% 分支接入 AI 估值和实际开战流程。

**边界与风险**

- 这是对 Firefall 私有接口的窄适配，不拥有 Firefall 其他 0% / 25% / 50% / 100% 战争目标。
- `REPLACE:uw_infamy_cost` 的选项顺序就是 UI 顺序；禁止无理由重排。
- `REPLACE:uw_start_union_war` 和 `REPLACE:uw_estimated_union_war_infamy` 必须在 Firefall 更新后逐段对比上游，确认只增加 10% 分支而未丢失新逻辑。
- 不得把统一战争逻辑混入普通外交战或东地中海成立链。

**未来拆分单位**

- 可独立为 `ffpa-union-war`，只依赖 Firefall；这是耦合较低的优先拆分候选。

### 4.4 殖民 AI、殖民边界与殖民制度

**所有文件/切片**

- `common/ai_strategies/zzzz_ffpa_colonial_region_stances.txt`
- `common/defines/zzzz_ffpa_colonial_shape_defines.txt`
- `common/institutions/00_institutions.txt` 中的 `institution_colonial_affairs`
- 两份本地化文件中的相关说明键（如有）

**拥有的行为与接口**

- 向 `ai_strategy_default` 注入殖民区域评分。
- 通过 `NDiplomacy` 调整殖民省份自动扩张形状。
- 调整殖民事务制度每级的殖民增长。

**边界与风险**

- AI 区域评分只控制“去哪里”；define 控制殖民地内部“选哪个省”；制度控制增长速度。不得用其中一层顺带改变其他层。
- define 同时影响 AI 和玩家，不能把它描述成纯 AI 行为。
- 本模块不拥有同时发展的殖民地数量上限。
- `INJECT:ai_strategy_default` 和 `NDiplomacy` 都是全局冲突面；必须在完整加载栈中检查后加载者。

**未来拆分单位**

- 可独立为 `ffpa-colonial-shaping`。拆分时要决定 `institution_colonial_affairs` 由它还是全局平衡包唯一拥有。

### 4.5 Tech & Res 自动 PM 兼容

**手写控制面**

- `common/decisions/ffpa_auto_pm_decisions.txt`
- `common/journal_entries/ffpa_auto_pm_compat_je.txt`
- `common/scripted_buttons/ffpa_auto_pm_buttons.txt`
- `common/script_values/ffpa_auto_pm_values.txt`
- `common/scripted_effects/ffpa_auto_pm_settings_effects.txt`
- `common/scripted_effects/ffpa_auto_pm_journal_effects.txt`
- `common/on_actions/ffpa_on_actions.txt` 中确保日志存在的调用
- 两份本地化文件中的 `ffpa_auto_pm_*` 键

**生成器与生成产物**

- 唯一源：`tools/generate_ffpa_auto_pm_compat.ps1`
- 生成：`common/scripted_effects/ffpa_generated_auto_pm_effects.txt`
- 生成：`common/scripted_effects/ffpa_generated_auto_pm_trials.txt`
- 生成：`common/scripted_triggers/ffpa_generated_auto_pm_triggers.txt`
- 报告：`TECHRES_AUTO_PM_COVERAGE.md`

**拥有的行为与接口**

- 读取原版、Tech & Res、Auto-Apply PMs、Auto-Apply Automation PMs 的最终 building → PMG → PM 图。
- 为普通生产、自动化、运输和数据优化生成相邻双向切换边。
- 管理候选、试运行、经济验收、回滚、冷却、手动保护和震荡锁。
- 读取上游 `zw_var_auto_pm_*` 设置；这些变量属于上游，本模块只消费，不得改名或改变含义。
- 对已完整覆盖的实例生成 guard，使上游管理器委托给本模块；未覆盖实例仍归上游。

**边界与风险**

- 禁止直接编辑三个 `ffpa_generated_*` 文件和覆盖报告。改变分类、阈值模板、guard 或状态机后运行生成器。
- 四个生成结果必须与生成器同次提交，且生成器连续运行两次应产生相同哈希。
- 生成 ID、州变量、建筑/PMG 隔离键和试运行状态都是存档接口；不得因排序或重构重新编号。
- 普通生产、自动化和运输分类以“上游实际引用 + 最终建筑挂载”为准，不能仅按 PM/PMG 名称猜测。
- 两个报告中的孤立 PMG 是有意排除项；上游未修复挂载前不得静默纳入。
- 本模块不拥有生产方式定义本身，也不拥有上游日志、频率变量和未覆盖建筑。

**未来拆分单位**

- 应整体拆为 `ffpa-techres-auto-pm-adapter`，并同时携带生成器、三份运行时产物、覆盖报告和 UI 控制面。
- 不要把生成器和运行时文件拆到不同仓库，除非建立版本锁定和可重复发布流程。

### 4.6 低人力亏损建筑清理

**所有文件/切片**

- `common/journal_entries/ffpa_building_pruning_je.txt`
- `common/scripted_buttons/ffpa_building_pruning_buttons.txt`
- `common/scripted_triggers/ffpa_building_pruning_triggers.txt`
- `common/scripted_effects/ffpa_building_pruning_effects.txt`
- `common/messages/ffpa_building_pruning_messages.txt`
- `common/on_actions/ffpa_on_actions.txt` 中的半年调度切片
- `common/scripted_effects/ffpa_auto_pm_journal_effects.txt` 中的初始化接缝
- `BUILDING_PRUNING_PORT.md`
- 两份本地化文件中的 `ffpa_*building_pruning*` / 清理通知键

**拥有的行为与接口**

- 玩家私有/公有两个开关和 AI 默认启用状态。
- 和平时期半年扫描，以及玩家开启时立即扫描。
- 低于 20% 雇佣、周利润不高于 0、未补贴和多数所有权分类。
- 显式建筑白名单、保护性排除和实际删除通知。

**边界与风险**

- `remove_building` 删除具体州中该类型建筑的全部等级；不得把它描述成降一级。
- `ffpa_private_building_pruning_active`、`ffpa_government_building_pruning_active` 是持久设置接口。
- 私有与公有扫描必须覆盖同一建筑集合，只允许所有权判断不同。
- 自动 PM 模块只负责在其日志确保 effect 中初始化/挂载界面；清理判定与删除权完全属于本模块。
- 扩充 Tech & Res 建筑时同步更新 `BUILDING_PRUNING_PORT.md`，基础设施和本地商品建筑必须单独评估死循环风险。

**未来拆分单位**

- 可独立为 `ffpa-building-pruning`。若要降低依赖，可再拆“原版建筑核心清单”和“Tech & Res 覆盖扩展”，但两者必须共享同一个扫描接口，不能复制状态机。

### 4.7 东地中海国家身份核心

**所有文件**

- `common/country_definitions/ffpa_byzantium.txt`
- `common/country_formation/ffpa_byzantium.txt`
- `common/cultures/ffpa_imperial_cultures.txt`
- `common/government_types/00_ffpa_byzantine_governments.txt`
- `common/government_types/00_ffpa_turkish_governments.txt`
- `common/dynamic_country_names/ffpa_byzantium_dynamic_names.txt`
- `common/flag_definitions/ffpa_byzantine_flag_definitions.txt`
- `common/coat_of_arms/coat_of_arms/ffpa_byzantine_flags.txt`
- `common/scripted_guis/ffpa_byzantium_party_names.txt`
- `common/modifier_type_definitions/ffpa_cultural_acceptance_modifier_types.txt`
- `common/ideologies/ffpa_eastern_mediterranean_ideologies.txt`
- `common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt`
- 两份本地化文件中的国家、文化、政体、党名、旗帜和成立链键

**拥有的行为与接口**

- 恢复 Firefall 最终数据库中缺失的 `BYZ` 身份和 GRE → BYZ 成立链。
- 保持原版 `TUR`，不创建第二个等价土耳其 tag。
- 定义 `ffpa_ottoman`、`ffpa_rhomaic`、TUR/BYZ 专属政体与政府称谓，以及 BYZ 动态国名、旗帜和党名适配。
- 提供东地中海状态机使用的意识形态与文化接受 modifier 类型。

**边界与风险**

- 本模块拥有“身份和静态定义”，不拥有日志进度、事件调度或地区建设奖励。
- `BYZ`、`je_greek_nationalism`、党名数据库适配和旗帜定义都可能覆盖上游顶层键；更新 Firefall/原版后必须做最终数据库比较。
- 形成 BYZ 后保留已有宣称的约定不可在身份重构时丢失。
- 不要为了 TUR 风味复制或替换原版 TUR 国家定义、旗帜或政体视觉。

**未来拆分单位**

- 拆成 `ffpa-eastern-mediterranean-core`，供状态机和地区建设包依赖。

### 4.8 东地中海日志、迁移与风味状态机

**所有文件/切片**

- `common/journal_entries/ffpa_eastern_mediterranean_journal_entries.txt`
- `common/scripted_triggers/ffpa_eastern_mediterranean_triggers.txt` 中共同体、成立和风味条件
- `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt`
- `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt`
- `common/static_modifiers/ffpa_eastern_mediterranean_modifiers.txt` 中非 `ffpa_region_*` 定义
- `events/ffpa_eastern_mediterranean_events.txt`
- 两份本地化文件中的 `ffpa_flavor.*`、TUR/BYZ 日志与修正键

**拥有的行为与接口**

- TUR 与 BYZ 的重建、共同体、首都工程和有限政治经济事件。
- `namespace = ffpa_flavor` 的事件 ID 空间。
- `on_country_formed`、月度迁移检查和首次选举入口。
- 版本化迁移、一次性事件标记、共同体三轴进退和清理路径。

**边界与风险**

- 变量名带 `_v1` / `_v2` 的键都是存档 API，不是可清理的命名噪音。
- ensure/migration effect 必须幂等；月度入口不得反复发奖励、重置有限期限或遍历全世界建筑。
- 事件链应保持“未初始化 → 可用 → 运行中 → 完成/失败/取消”的显式状态；每条异常路径都要清理临时状态。
- 本模块可消费地区建设模块导出的完成变量和查询 trigger，但不得直接重写地区日志内部状态。

**未来拆分单位**

- 可拆为 `ffpa-eastern-mediterranean-flavor`，依赖身份核心。
- 当前西方整合事件会消费地区建设完成状态；若地区建设另包，风味包必须显式依赖它，或把这部分调用移入单独 bridge 包。

### 4.9 帝国地区建设与西方整合桥接

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
- 向风味模块导出完成状态查询：`ffpa_has_two_western_development_projects`、`ffpa_has_italian_development_project`、`ffpa_has_outer_western_development_project`、`ffpa_western_*_ready`。
- 完成日志后调用 `ffpa_check_western_integration_events`，但事件具体奖励归风味模块。

**边界与风险**

- 地区 modifier 是物理工程结果，不能在国家身份或共同体完成时全局发放。
- 完成变量和 modifier 名称是旧存档接口；地区更名时保留技术 ID。
- 这是东地中海内部唯一允许的“建设 → 风味”桥；不要让事件直接检查 15 个日志的内部字段。

**未来拆分单位**

- 可拆为 `ffpa-imperial-regional-development`，依赖身份核心。
- 初次拆分建议把西方整合 bridge 暂时与风味包同放，等接口稳定后再独立，避免形成循环依赖。

### 4.10 开发工具、技能与报告

**所有文件**

- `tools/`
- `skills/`
- `TECHRES_AUTO_PM_COVERAGE.md`
- `BUILDING_PRUNING_PORT.md`

**职责与边界**

- `tools/` 只生成或验证游戏数据，不应成为游戏运行时依赖。
- `skills/` 是开发代理说明，不会被 Victoria 3 加载；修改它不等于修改 Mod 行为。
- 生成报告必须由工具生成；调研文档可以手写，但必须注明上游、版本、差异和有意排除项。
- 这些文件应纳入版本控制，不要因为不是运行时脚本就加入 `.gitignore`。

## 5. 共享接缝与唯一所有者规则

| 共享接缝 | 当前使用者 | 规则 |
|---|---|---|
| `common/on_actions/ffpa_on_actions.txt` | 创新上限、自动 PM 日志、建筑清理 | 只负责调度到模块 effect；新增功能尽量使用自己的命名 on_action 包装，不把复杂逻辑内联。 |
| `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt` | 东地中海成立、迁移、选举 | 仅调度 TUR/BYZ；不得吸收全局经济功能。 |
| `common/static_modifiers/ffpa_eastern_mediterranean_modifiers.txt` | 风味、共同体、地区建设 | 技术 ID 前缀决定所有者；拆分时按定义完整移动，不复制。 |
| `common/scripted_triggers/ffpa_eastern_mediterranean_triggers.txt` | 风味与地区建设 | 地区模块导出查询 trigger，风味模块消费；禁止反向读取风味内部变量。 |
| `common/scripted_effects/ffpa_auto_pm_journal_effects.txt` | 自动 PM、建筑清理初始化 | 只允许做“确保存在/初始化默认值”；删除逻辑归各自模块。 |
| `events/ffpa_eastern_mediterranean_events.txt` | TUR/BYZ 风味与西方整合 | 共享 `ffpa_flavor` namespace；新增 ID 先搜索冲突，不重编号旧事件。 |
| `localization/english/ffpa_l_english.yml` | 全部玩家可见模块 | 每个模块拥有自己的键切片；改技术对象时同步更新。 |
| `localization/simp_chinese/ffpa_l_simp_chinese.yml` | 全部玩家可见模块 | 与英文保持键集合一致，不得只补一种语言。 |
| `.metadata/metadata.json` | 所有发布模块 | 只有发布/依赖变化才改；未来拆包时每个包使用新且稳定的 ID。 |

跨模块调用优先使用命名清晰的 scripted effect、scripted trigger 或稳定顶层对象。除本表明确列出的存档接口外，禁止直接读取另一个模块的临时变量。

## 6. 覆盖与冲突登记

以下对象不是普通新增定义，修改前必须对最终数据库做差异检查：

| 顶层键/数据库 | 方式 | 原因 | 必查上游 |
|---|---|---|---|
| `uw_infamy_cost` | `REPLACE:` | 插入有序 UI 选项 | Firefall |
| `uw_estimated_union_war_infamy` | `REPLACE:` | AI 恶名估值增加 10% 分支 | Firefall |
| `uw_start_union_war` | `REPLACE:` | 开战流程增加 10% 分支 | Firefall |
| `ai_strategy_default` | `INJECT:` | 殖民区域评分 | 原版、Tech & Res、Firefall |
| `NDiplomacy` | define 覆盖 | 殖民边界形状 | 原版及所有改 define 的 Mod |
| `institution_*` | 同名顶层定义 | 全局制度平衡 | 原版、Firefall |
| `BYZ` 国家/成立/动态名/旗帜 | 新建或替换 | Firefall 最终库缺少/改变 BYZ | 原版、Firefall |
| `je_greek_nationalism` | 同名顶层替换 | 接回 GRE → BYZ 路线 | 原版、Firefall |
| `pm_trade_center*` | `INJECT:` | 容量与运输投入增量 | 原版、Tech & Res、Firefall |
| 自动 PM 上游选择器 | 生成 guard 注入/替换 | 委托已覆盖实例 | 两个 Auto-Apply Mod |

文件名前缀 `00_`、`zzz_`、`zzzz_` 只是加载排序工具，不等于安全覆盖。不得仅通过改文件名解决冲突；必须记录目标顶层键、操作语义和后加载者。

## 7. 命名、作用域与存档兼容

- 新增自有技术 ID 使用 `ffpa_` 前缀；建议继续细分为 `ffpa_auto_pm_`、`ffpa_tur_`、`ffpa_byz_`、`ffpa_region_`、`ffpa_union_` 等。
- 覆盖上游 ID 时保留上游名字，并在文件头注释来源、目标版本、覆盖原因和预期差异。
- trigger 不产生副作用，effect 改状态，script value 算数值，modifier 描述叠加量；不能跨类别照搬语法。
- 每次跨 country/state/building/market/strategic region scope 时，在复杂实现旁写明进入和返回的 scope。
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
- `git diff --check` 没有新增空白错误；但不要为通过检查而格式化用户无关文件。

### 9.2 自动 PM 修改的额外验证

1. 运行生成器，确认所有内置断言通过。
2. 再运行一次，比较三个生成脚本和覆盖报告的 SHA-256；两次必须一致。
3. 确认报告仍覆盖全部上游 automation building/PM 对、完整炸药厂双向链，并只保留已记录的有意孤立项。
4. 复核升级边有反向降级边、设置 gate 正确、未覆盖实例仍由上游管理。
5. 游戏中搜索 `FFPA_PM|`，至少区分调度到达、候选、试运行、验收、保留/回滚和外部取消。

### 9.3 建筑清理修改的额外验证

- 私有和公有清单一致。
- 正向场景同时满足雇佣、利润、补贴和所有权条件后才删除。
- 战争、补贴、保护建筑、正利润和高雇佣率分别能阻止删除。
- 只在实际删除后发送对应通知。
- 新旧存档分别验证默认变量和日志挂载。

### 9.4 东地中海修改的额外验证

- GRE → BYZ 成立、TUR 不被替换、BYZ 形成后宣称保留。
- 共同体三轴分别前进/倒退，完成奖励不重复。
- 所有失败、取消、政体变化、标签形成和旧存档路径都能清理或迁移状态。
- 地区建设只奖励实际覆盖州；完成状态可稳定触发一次西方整合事件。
- 动态国名、政府称号、党名、旗帜和两种语言在主要政体路径下显示正确。

### 9.5 运行时证据

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

## 11. 推荐拆分顺序

1. **统一战争**：边界窄、只依赖 Firefall，最容易独立验证。
2. **殖民形状**：三个全局对象边界清楚，但先决定殖民制度键的唯一所有者。
3. **建筑清理**：状态机独立；可选择保留 Tech & Res 硬依赖，或拆基础清单/扩展清单。
4. **全局平衡**：把创新、人口恢复、制度和贸易作为一个小包，再按需求细分。
5. **自动 PM 兼容**：整体搬迁生成器、产物、UI、报告和上游 guard，不做半拆。
6. **东地中海身份核心**：先抽出 BYZ/TUR 静态身份接口。
7. **地区建设与风味**：在身份核心稳定后拆；先保留西方整合 bridge 的单一所有者，避免循环依赖。

每次拆分都要建立“旧包与新包的顶层键集合差异”：旧包移除的每个自有键必须恰好由一个新包提供；共享覆盖键不能被两个新包同时定义；持久 ID 不因物理移动而改变。

## 12. 交付格式

完成任务时简要报告：

- 修改了哪个模块及其文件。
- 是否改变跨模块接口、上游覆盖或存档 API。
- 执行了哪些静态、生成器和运行时验证。
- 哪些结论仍需游戏内确认。
- 当前 Git 分支与工作树状态；不得把用户原有修改冒充为本次改动。
