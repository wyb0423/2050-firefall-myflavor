# TUR 共和国与重建总署利益集团身份设计

日期：2026-09-04

状态：已实施并完成静态验证，待游戏内验证

## 1. 背景与判断

FFPA 的 TUR 已有三条互斥建国路线、路线事件链、终局选择、常驻治理日志与边疆收复前线，玩法内容不需要继续横向扩张。当前差距集中在持久政治身份：高门路线取得 `ffpa_ottoman` 后会改名两个利益集团并替换三个 Trait 槽位，而共和国与重建总署路线在终局后仍使用通用利益集团名称和 Trait。

本设计只补齐这两个路线身份包，不增加日志、事件、路线分支、国名、旗帜或党名。

## 2. 当前版本与实现依据

设计以当前安装栈为准：

- Victoria 3 `1.13.11`；
- `2050: The Fire Falls` `0.1.1`；
- `[1.13] Tech & Res` metadata 版本 `1.6'`；
- FFPA 当前主分支。

原版利益集团通过 IG scope 的 `set_ig_trait` 按满意度槽位设置 Trait；FFPA 已用同一方式为 BYZ 与奥斯曼身份一次性换槽。共和国和重建总署继续复用这套模式，不覆盖原版 `interest_group` 顶层定义。

## 3. 范围

### 3.1 共和国路线

- `ig_armed_forces` 显示名改为 `Republican General Staff／共和国总参谋部`；
- `ig_intelligentsia` 显示名改为 `Ankara Civic Society／安卡拉公民学社`；
- 替换军队不满、军队满意、知识分子忠诚三个槽位。

### 3.2 重建总署路线

- `ig_industrialists` 显示名改为 `National Reconstruction Combines／国家重建联合体`；
- `ig_intelligentsia` 显示名改为 `National Technical Service Corps／全国技术服务团`；
- 替换实业家不满、实业家满意、知识分子忠诚三个槽位。

每条路线固定一组身份，不根据终局三个选项继续分支。

## 4. Trait 规格

六个 Trait 均复用原版现有图标和已验证可用于 IG Trait 的 modifier。满意槽使用 `min_approval = happy`，忠诚槽使用 `min_approval = loyal`，不满槽使用 `max_approval = unhappy`。

| 路线与集团 | 技术 ID | 玩家可见名 | 槽位 | Modifier |
|---|---|---|---|---|
| 共和国军队 | `ig_trait_ffpa_tur_guardianship_intervention` | Guardianship Intervention／守护者干政 | 不满 | `country_law_enactment_speed_mult = -0.10` |
| 共和国军队 | `ig_trait_ffpa_tur_civilian_command` | Civilian Chain of Command／文官指挥链 | 满意 | `building_training_rate_mult = 0.10`；`unit_defense_mult = 0.05` |
| 共和国知识分子 | `ig_trait_ffpa_tur_republican_public_instruction` | Republican Public Instruction／共和国公共教育 | 忠诚 | `state_education_access_add = 0.05`；`state_pop_qualifications_mult = 0.05` |
| 重建总署实业家 | `ig_trait_ffpa_tur_contractual_obstruction` | Contractual Obstruction／承包体系掣肘 | 不满 | `state_capitalists_investment_pool_efficiency_mult = -0.05`；`country_bureaucracy_mult = -0.05` |
| 重建总署实业家 | `ig_trait_ffpa_tur_reconstruction_contracts` | Coordinated Reconstruction Contracts／协调重建契约 | 满意 | `state_construction_mult = 0.05`；`state_infrastructure_mult = 0.05` |
| 重建总署知识分子 | `ig_trait_ffpa_tur_national_technical_service` | National Technical Service／全国技术服务 | 忠诚 | `state_pop_qualifications_mult = 0.05`；`country_production_tech_research_speed_mult = 0.05` |

每条路线都是一个负面 Trait 与两个正面 Trait，强度对齐原版常见的单项 `10%` 或 FFPA 现有的双项 `5%` 量级。

## 5. 授予与迁移

新增一个 country-scope、幂等的路线身份 effect。两个分支分别要求：

- Root 严格满足 `country_definition = cd:TUR`；
- 共和国为 `ffpa_tur_state_project_v1 = 2`，且已有 `ffpa_tur_republic_settlement_choice_v1`；
- 重建总署为 `ffpa_tur_state_project_v1 = 3`，且已有 `ffpa_tur_directorate_settlement_choice_v1`；
- 对应版本变量尚未设置。

共和国分支改名两个集团、写入三个 Trait，并设置 `ffpa_tur_republic_interest_group_identity_v1`。重建总署分支执行对应操作，并设置 `ffpa_tur_directorate_interest_group_identity_v1`。

调用方式：

1. 共和国与重建总署终局事件结算后调用一次，使新游戏立即获得身份；
2. 现有 `ffpa_ensure_tur_permanent_flavor_rewards_v1` 调用同一 effect，使已完成终局的旧档在首次月度 ensure 补发；
3. 版本变量设置后不再重复调用 `set_interest_group_name` 或 `set_ig_trait`，避免与后续事件或其他 Mod 周期争夺槽位。

路线缺失、损坏、尚未完成终局或不是 TUR 时不推断、不授予。后续政体变化不撤销；形成其他 tag 时不建立反向恢复逻辑，因为原槽位可能受 DLC 和其他 Mod 影响，硬编码恢复值会破坏最终数据库兼容。该持久语义与现有奥斯曼/BYZ一次性身份包一致。

## 6. 文件与所有权

预计修改：

- `common/interest_group_traits/ffpa_eastern_mediterranean_interest_group_traits.txt`：新增六个静态 Trait；
- `common/scripted_effects/ffpa_turkish_flavor_effects.txt`：新增路线身份 effect，并接入现有永久奖励 ensure；
- `events/ffpa_turkish_flavor_events.txt`：两个既有终局事件各增加一次结算后调用；
- `localization/english/ffpa_turkish_flavor_l_english.yml`；
- `localization/simp_chinese/ffpa_turkish_flavor_l_simp_chinese.yml`；
- `README.md` 与 `AGENTS.md`：窄幅登记真实行为、所有权和存档 API。
- `tests/test_tur_route_interest_group_identity.py`：无依赖静态回归检查。

静态 Trait 属于东地中海国家身份核心；路线判定、授予和迁移属于 TUR 风味状态机。两个模块只通过六个稳定 Trait 顶层对象连接。不修改 `.metadata/metadata.json`，不新增 on_action 或运行时文件。

## 7. 本地化

四个利益集团名称各需要一个本地化键；六个 Trait 各需要名称和描述两个键。英文与简体中文必须保持相同的 16 个新增键，并保留现有 UTF-8 BOM、语言头和文件格式。

Trait 描述只写制度风味，不重复百分比；具体效果由原生 Trait UI 显示。

## 8. 兼容与存档规则

- 六个 Trait ID、四个名称键和两个版本变量均使用 `ffpa_` 前缀，不覆盖上游对象；
- 六个 Trait ID 与两个版本变量成为存档 API，后续改变语义时必须版本化迁移；
- `set_ig_trait` 只替换相同满意度槽位，每条路线仍保留未指定的原版槽位；
- 高门路线、既有奥斯曼身份包和 BYZ 身份包不改动；
- 若其他 Mod 在身份包执行后改写同一槽位，后执行者生效；FFPA 不用月度逻辑抢写；
- 路线历史继续以既有 `ffpa_tur_state_project_v1` 的 `1/2/3` 语义为准，不新增同义路线变量。

## 9. 验证标准

### 9.1 静态与最终数据库

- 六个 Trait 的阈值、图标、modifier 和花括号可解析；
- 所有 modifier 均能在 Victoria 3 `1.13.11` 的 IG Trait 中找到有效先例；
- 原版、Firefall、Tech & Res 与 FFPA 不存在同名顶层键；
- 两种语言新增键集合一致并保留 UTF-8 BOM；
- effect 和事件调用使用严格 TUR 身份门控与正确 country/IG scope；
- `git diff --check`、metadata JSON、重复键和括号检查通过。

### 9.2 行为

- 两条路线在终局选择前均不改名、不换 Trait；
- 任一终局选项结算后，同一路线获得相同身份包；
- 已完成终局的旧档在首次月度 ensure 补发一次；
- 版本变量设置后重复 ensure 不再次写名称或 Trait；
- 共和国保留军队忠诚、知识分子不满和满意等未指定原版槽位；
- 重建总署保留实业家忠诚、知识分子不满和满意等未指定原版槽位；
- 高门路线以及尚未选择、无法识别或损坏的路线不获得新身份包；
- 最新 `error*.log` 不出现新增 ID、scope 或 modifier 的解析错误。

无法启动游戏时，交付必须把静态验证与待游戏内验证项分开报告。
