# 东地中海利益集团风味 Trait 设计

日期：2026-09-01

状态：已实施，待游戏内验证

## 1. 背景

FFPA 已经为 BYZ 和取得奥斯曼共同体身份后的 TUR 设置了五个风味利益集团名称：

- BYZ 神圣宗教会议、罗马军队、新罗马学社；
- TUR 帝国总参谋部、奥斯曼改革派。

现有实现只使用 `set_interest_group_name` 改变显示名。五个利益集团仍使用其原版不满、满意和忠诚 trait，因此显示身份与实际提供的增益、减益之间缺少联系。

本设计在五个已改名利益集团的十五个槽位中选择八个最能表达其身份的槽位进行替换。其余七个槽位继续保留原版行为，以控制平衡面、兼容风险和本地化规模。

## 2. 当前版本与最终数据库

本设计以当前安装栈为准：

- Victoria 3 `1.13.11`；
- `2050: The Fire Falls` `0.1.1`；
- `[1.13] Tech & Res` metadata 版本 `1.6'`；
- FFPA `1.2.0`。

Firefall 与 Tech & Res 当前均未提供 `common/interest_groups/` 或 `common/interest_group_traits/` 文件，也未对这两个目录使用 `replace_path`。因此相关最终顶层定义来自原版 1.13.11。

原版 `interest_group` 定义已经将静态 `traits = {}` 标为弃用，并在 `on_enable` 中通过 IG scope 的 `set_ig_trait` 分配三个槽位。原版日本改宗决议会在游戏过程中一次性重设三项宗教集团 trait；菲律宾事件只调用一次 `set_ig_trait`，替换单个忠诚槽位。这证明运行时按槽位替换是当前版本的既有实现路径。

## 3. 目标

- 为五个已改名利益集团替换八个选定的原版 trait 槽位。
- 继续使用原生 IG trait UI、满意度阈值、激活/停用通知和 `IG_TRAIT_STICKINESS`。
- 不覆盖八个原版 `interest_group` 顶层定义。
- 不修改其他国家使用的原版 trait，也不覆盖原版本地化键。
- 新游戏在身份获得时立即应用；旧存档通过现有轻量月度 ensure 补发一次。
- 使用新的版本化持久变量，保证重复 ensure 不反复写 trait。
- 英文与简体中文保持完全相同的新增键集合。

## 4. 非目标

- 不替换五个利益集团的全部十五个槽位。
- 不为尚未改名的 TUR/BYZ 利益集团增加 trait。
- 不根据建国路线、后续政体、宗教或共同体进度动态切换第二套 trait。
- 不新增图标、美术或 GUI。
- 不更改既有意识形态替换、利益集团名称、满意度、政治力量或事件奖励。
- 不为形成其他 tag 后恢复原版名称或 trait 建立新的清理状态机；本次行为与现有持久风味名称保持一致。
- 不修改 metadata、依赖和加载顺序。

## 5. 方案比较

### 5.1 采用：新增 Trait 并在身份入口一次性换槽

新增八个 `ig_trait_ffpa_*` 顶层定义，在 BYZ 成立 ensure 和 TUR 奥斯曼身份入口中用 `set_ig_trait` 应用。每个国家使用独立的版本变量门控旧档迁移。

优点：

- 使用原生 trait 系统，UI 和启停规则自动工作；
- 只新增自有顶层键，不复制上游 `interest_group`；
- 可以精确替换选定的满意度槽位，保留其余原版平衡；
- 形成国家与旧档补发可以复用现有入口，不增加长期调度。

代价：

- 同一利益集团同一槽位只能保留一个 trait；其他 Mod 后续运行时写同槽位时，最后执行者会覆盖先前结果；
- 新 trait ID 与应用变量成为存档 API，后续不能无迁移删除或改变语义。

### 5.2 未采用：完整覆盖原版 Interest Group

在 FFPA 中重定义 `ig_armed_forces`、`ig_devout` 和 `ig_intelligentsia` 的 `on_enable`，加入 TUR/BYZ 条件分支。

该方案会复制大量原版 1.13.11 国家、文化、宗教和 DLC 分支，并对后续上游更新形成高维护覆盖。GRE 形成 BYZ 时既有 IG 未必重新执行 `on_enable`，仍需要运行时补发，因此没有采用。

### 5.3 未采用：用国家 Modifier 模拟

根据利益集团满意度在周期 pulse 中添加和移除国家 modifier。

该方案需要复制原生满意度阈值与黏滞规则，效果也不会显示为利益集团 trait，并引入不必要的周期调度，因此没有采用。

## 6. Trait 规格

八个 trait 均复用已存在的原版图标路径。数值选取自原版国家专属 IG trait 的常见量级；目标是改变侧重点，而非在原有效果上叠加额外强化。

| 国家与利益集团 | 技术 ID | 玩家可见名 | 槽位 | 替换的原版 Trait | Modifier | 复用图标 |
|---|---|---|---|---|---|---|
| BYZ 神圣宗教会议 | `ig_trait_ffpa_byz_synodal_deadlock` | Synodal Deadlock／宗教会议掣肘 | 不满 | `ig_trait_pious_fiction`：教育机会 `-10%` | `country_bureaucracy_mult = -0.05`；`state_radicals_from_political_movements_mult = 0.05` | `pious_fiction.dds` |
| BYZ 神圣宗教会议 | `ig_trait_ffpa_byz_synodal_stewardship` | Synodal Stewardship／宗教会议共治 | 满意 | `ig_trait_divine_right`：权威 `+10%` | `country_bureaucracy_mult = 0.05`；`state_education_access_add = 0.05` | `divine_right.dds` |
| BYZ 罗马军队 | `ig_trait_ffpa_byz_strategikon` | Strategikon／《战略论》 | 满意 | `ig_trait_veteran_consultation`：军事科技研究 `+10%` | `building_training_rate_mult = 0.10`；`unit_morale_recovery_mult = 0.05` | `veteran_consultation.dds` |
| BYZ 罗马军队 | `ig_trait_ffpa_byz_restored_eagles` | Restored Eagles／重举鹰旗 | 忠诚 | `ig_trait_patriotic_fervor`：进攻与防御 `+10%` | `unit_offense_mult = 0.10`；`unit_morale_recovery_mult = 0.10` | `patriotic_fervor.dds` |
| BYZ 新罗马学社 | `ig_trait_ffpa_byz_new_rome_academies` | New Rome Academies／新罗马学苑 | 忠诚 | `ig_trait_propagandists`：移民吸引力 `+15%` | `state_pop_qualifications_mult = 0.05`；`state_education_access_add = 0.05` | `avant_garde.dds` |
| TUR 帝国总参谋部 | `ig_trait_ffpa_tur_erkan_i_harbiye` | Erkân-ı Harbiye／帝国总参谋体系 | 满意 | `ig_trait_veteran_consultation`：军事科技研究 `+10%` | `building_training_rate_mult = 0.10`；`country_military_tech_research_speed_mult = 0.05` | `veteran_consultation.dds` |
| TUR 奥斯曼改革派 | `ig_trait_ffpa_tur_reformist_fractures` | Reformist Fractures／改革派裂痕 | 不满 | `ig_trait_crisis_of_identity`：同化速度 `-15%` | `country_law_enactment_speed_mult = -0.10` | `social_criticism.dds` |
| TUR 奥斯曼改革派 | `ig_trait_ffpa_tur_tanzimat_legacy` | Tanzimat Legacy／坦志麦特遗产 | 忠诚 | `ig_trait_propagandists`：移民吸引力 `+15%` | `country_law_enactment_speed_mult = 0.10`；`country_bureaucracy_mult = 0.05` | `propagandists.dds` |

对应阈值固定为：

- 满意槽：`min_approval = happy`；
- 忠诚槽：`min_approval = loyal`；
- 不满槽：`max_approval = unhappy`。

不得在同一个新 trait 中同时写 `min_approval` 与 `max_approval`。不得把新效果叠加为永久国家 modifier。

## 7. 数据与文件所有权

新增运行时定义文件：

- `common/interest_group_traits/ffpa_eastern_mediterranean_interest_group_traits.txt`。

八个 trait 的静态定义属于“东地中海模块：国家身份核心”，因为它们描述 BYZ/TUR 的稳定政治身份。应用与旧档补发位于：

- `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt`。

这些 effect 属于“东地中海模块：日志、迁移与风味状态机”。该分工保持“静态身份对象 → 状态机应用”的单向依赖，不向地区建设或外部拆分包增加接口。

`AGENTS.md` 必须登记新增 trait 文件、八个 trait 的所有者以及版本变量属于存档 API。README 只需在现有利益集团风味说明中补充“名称与有限专属 trait”；不修改 metadata 版本。

## 8. BYZ 应用与迁移

新增 country scope effect：

- `ffpa_ensure_byzantine_interest_group_traits_v1`。

前置条件：

1. Root 是 `c:BYZ`；
2. Root 不具有 `ffpa_byzantine_interest_group_traits_v1`。

效果：

1. `ig:ig_devout ?=` 设置 `ig_trait_ffpa_byz_synodal_deadlock` 与 `ig_trait_ffpa_byz_synodal_stewardship`；
2. `ig:ig_armed_forces ?=` 设置 `ig_trait_ffpa_byz_strategikon` 与 `ig_trait_ffpa_byz_restored_eagles`；
3. `ig:ig_intelligentsia ?=` 设置 `ig_trait_ffpa_byz_new_rome_academies`；
4. 设置国家变量 `ffpa_byzantine_interest_group_traits_v1`。

调用位置放在现有 `ffpa_ensure_byzantine_formation_effects` 中，与三项利益集团名称相邻但使用独立的 `if` 分支。该 ensure 已由 `on_country_formed` 和月度旧档入口调用，因此：

- 新形成 BYZ 当次立即应用；
- 已存在 BYZ 的旧档在更新后的首次月度 ensure 应用一次；
- 已有 `ffpa_byzantine_flavor_names_v2` 的旧档不会漏掉 trait；
- 之后的月度 ensure 只检查变量，不重复调用 `set_ig_trait`。

不得复用或改义 `ffpa_byzantine_flavor_names_v2`。

## 9. TUR 应用与迁移

新增 country scope effect：

- `ffpa_apply_ottoman_interest_group_traits_v1`。

前置条件：

1. Root 是 `c:TUR`；
2. Root 拥有主流文化 `cu:ffpa_ottoman`；
3. Root 不具有 `ffpa_ottoman_interest_group_traits_v1`。

效果：

1. `ig:ig_armed_forces ?=` 设置 `ig_trait_ffpa_tur_erkan_i_harbiye`；
2. `ig:ig_intelligentsia ?=` 设置 `ig_trait_ffpa_tur_reformist_fractures` 与 `ig_trait_ffpa_tur_tanzimat_legacy`；
3. 设置国家变量 `ffpa_ottoman_interest_group_traits_v1`。

现有 `ffpa_apply_ottoman_interest_group_names` 保留技术 ID 和既有名称分支。在该 wrapper 末尾无条件调用新 effect；新 effect 自行检查国家、文化和版本变量。这样现有两个调用者继续覆盖：

- 奥斯曼共同体完成事件：身份取得当次立即改名并换 trait；
- 月度 `ffpa_ensure_eastern_mediterranean_v2`：为旧档补发一次。

不得把 trait 写入受 `ffpa_ottoman_flavor_names_v2` 门控的既有 `if` 内，否则已经改过名的旧档无法迁移。不得改义既有名称变量。

## 10. 本地化

在以下两个现有共享文件中各新增相同的十六个键：

- `localization/english/ffpa_l_english.yml`；
- `localization/simp_chinese/ffpa_l_simp_chinese.yml`。

每个 trait 提供：

- `<trait_id>`：名称；
- `<trait_id>_desc`：风味说明。

数值由游戏根据 trait modifier 自动显示，描述不重复承诺具体百分比，以便后续平衡调整。保持两份文件的 UTF-8 BOM、语言头、换行和缩进，不重写无关内容。

## 11. 兼容与存档规则

- 八个新 trait 顶层键均使用 `ig_trait_ffpa_` 前缀，不覆盖原版、Firefall 或 Tech & Res。
- `set_ig_trait` 按满意度槽位替换当前对象，因此不会把原版 trait 继续叠加在同一槽位。
- FFPA 在首次身份 ensure 时有意接管这八个槽位。若其他 Mod 随后通过事件重写同槽位，后执行者获胜；本设计不增加周期性争夺写入。
- 两个新国家变量与八个新 trait ID 都是存档 API。后续语义变化必须增加新版本变量或迁移，不能静默复用 `_v1`。
- 更新前已经处于对应满意度阈值的旧档可能在首次换槽时看到一次 trait 激活或停用通知；是否出现以及通知顺序需要游戏内验证。
- 本设计不尝试恢复另一个 Mod 已写入的未知 trait，因为当前 1.13.11 数据中没有找到可验证的通用 `has_ig_trait` 兼容先例。

## 12. 预计实施文件

- 新增 `common/interest_group_traits/ffpa_eastern_mediterranean_interest_group_traits.txt`；
- 修改 `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt`；
- 修改 `localization/english/ffpa_l_english.yml`；
- 修改 `localization/simp_chinese/ffpa_l_simp_chinese.yml`；
- 修改 `AGENTS.md`；
- 修改 `README.md` 现有 BYZ/TUR 身份说明，将“利益集团名称”窄改为“利益集团名称与有限专属 trait”，不得扩大为版本发布说明；
- 不修改 `.metadata/metadata.json`、on_action、事件 ID、JE 或外部拆分包。

## 13. 验证标准

### 13.1 静态与最终数据库

- 八个新 trait 的花括号、阈值、图标和 modifier 字段可解析。
- 所有 modifier 类型都能在当前原版或 Tech & Res 数据中找到工作先例。
- 八个技术 ID 在原版、Firefall、Tech & Res 和 FFPA 中不存在冲突。
- 两种语言各新增十六个键，键集合完全一致，且保留 UTF-8 BOM。
- 两个 scripted effect 的调用方、Root scope 和 IG scope 与当前原版/FFPA 先例一致。
- `jq empty .metadata/metadata.json`、`git diff --check` 与项目括号检查通过。
- 不新增 `interest_group` 顶层覆盖，不新增 on_action，不改变既有变量含义。

### 13.2 新游戏

- GRE 形成 BYZ 后，三个风味名称和五个新 trait 同次到达。
- BYZ 四个未替换槽位仍保持原版结果。
- TUR 在没有 `ffpa_ottoman` 主流文化时不获得三个新 trait。
- TUR 取得 `ffpa_ottoman` 主流文化后，同次获得两个风味名称与三个新 trait。
- TUR 两个已改名集团的其余三个原版槽位继续保留；未改名虔诚集团的 Mecelle 等原版专属 trait 也不受影响。

### 13.3 旧存档与幂等性

- 已经拥有 `ffpa_byzantine_flavor_names_v2` 的 BYZ 在首次月度 ensure 后仍能获得五个新 trait。
- 已经拥有 `ffpa_ottoman_flavor_names_v2` 与 `ffpa_ottoman` 的 TUR 在首次月度 ensure 后仍能获得三个新 trait。
- 两个新版本变量设置后，后续月度 pulse 不再次写 trait或重复通知。
- 缺少 `ffpa_ottoman` 的 TUR 旧档不设置奥斯曼 trait 变量，以便将来身份达成时正常应用。
- 保存并重载后，trait 分配和版本变量继续存在。

### 13.4 运行时证据

- 最新 `error*.log` 不出现八个 trait、两项 effect、两个变量或 modifier 类型的解析错误。
- IG 面板分别检查不满、满意和忠诚阈值下的实际启停与 modifier 数值。
- 确认旧档首次迁移时的系统通知是否可接受。
- 确认形成 BYZ 后原 GRE trait 的相应槽位确实被替换，而不是并存。

无法启动游戏时，交付必须把静态确认与上述待游戏内验证项分开报告。
