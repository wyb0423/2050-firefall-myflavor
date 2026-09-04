# TUR 共和国与重建总署利益集团身份实施计划

日期：2026-09-04

依据：`docs/superpowers/specs/2026-09-04-tur-republic-directorate-interest-group-identity-design.md`

状态：已实施并完成静态验证，待游戏内验证

## 1. 实施约束

- 保留工作区已有修改，不回退、不重写、不顺带格式化。
- 目标环境固定为 Victoria 3 `1.13.11`、Firefall `0.1.1`、Tech & Res `1.6'`。
- 只新增自有 `ffpa_` 顶层键，不覆盖原版 `interest_group`。
- 复用现有 TUR 月度 ensure，不新增 on_action、事件 ID、日志或运行时文件。
- 不修改高门/BYZ 身份包、路线 `1/2/3` 语义、终局三个选项或 metadata。
- 所有修改使用窄补丁；本地化保持 UTF-8 BOM。

## 2. 固定技术对象

### 2.1 共和国

| 对象 | 技术 ID |
|---|---|
| 军队名称 | `ffpa_ig_tur_republican_general_staff` |
| 知识分子名称 | `ffpa_ig_tur_ankara_civic_society` |
| 军队不满 Trait | `ig_trait_ffpa_tur_guardianship_intervention` |
| 军队满意 Trait | `ig_trait_ffpa_tur_civilian_command` |
| 知识分子忠诚 Trait | `ig_trait_ffpa_tur_republican_public_instruction` |
| 迁移门控 | `ffpa_tur_republic_interest_group_identity_v1` |

### 2.2 重建总署

| 对象 | 技术 ID |
|---|---|
| 实业家名称 | `ffpa_ig_tur_national_reconstruction_combines` |
| 知识分子名称 | `ffpa_ig_tur_national_technical_service_corps` |
| 实业家不满 Trait | `ig_trait_ffpa_tur_contractual_obstruction` |
| 实业家满意 Trait | `ig_trait_ffpa_tur_reconstruction_contracts` |
| 知识分子忠诚 Trait | `ig_trait_ffpa_tur_national_technical_service` |
| 迁移门控 | `ffpa_tur_directorate_interest_group_identity_v1` |

共享 effect：`ffpa_apply_tur_route_interest_group_identity_v1`。

## 3. Task 1：新增六个 Trait

**修改文件**

- `common/interest_group_traits/ffpa_eastern_mediterranean_interest_group_traits.txt`

**步骤**

1. 在现有 TUR Trait 后新增共和国三个定义，依次使用不满、满意、忠诚阈值。
2. 新增重建总署三个定义，依次使用不满、满意、忠诚阈值。
3. 复用原版已存在的 `social_criticism.dds`、`veteran_consultation.dds`、`propagandists.dds`、`tax_avoidance.dds`、`engines_of_progress.dds` 图标；不增加美术文件。
4. modifier 与已批准设计逐项一致，不扩充数值。

**完成检查**

```zsh
rg -n '^ig_trait_ffpa_tur_(guardianship_intervention|civilian_command|republican_public_instruction|contractual_obstruction|reconstruction_contracts|national_technical_service)[[:space:]]*=' common/interest_group_traits/ffpa_eastern_mediterranean_interest_group_traits.txt
```

预期恰好六个唯一顶层键；每个 Trait 只有一个满意度阈值。

## 4. Task 2：实现一次性授予和终局接线

**修改文件**

- `common/scripted_effects/ffpa_turkish_flavor_effects.txt`
- `events/ffpa_turkish_flavor_events.txt`

**步骤**

1. 新增 country-scope `ffpa_apply_tur_route_interest_group_identity_v1`。
2. 共和国分支同时检查：严格 TUR、路线值 `2`、存在 `ffpa_tur_republic_settlement_choice_v1`、缺少共和国门控变量。
3. 在 `ig_armed_forces ?=` 中改名并设置不满、满意 Trait；在 `ig_intelligentsia ?=` 中改名并设置忠诚 Trait；最后设置共和国门控变量。
4. 重建总署分支按路线值 `3`、对应终局变量和门控变量执行同样结构，目标集团为实业家与知识分子。
5. 在 `ffpa_ensure_tur_permanent_flavor_rewards_v1` 末尾调用共享 effect，为旧档提供现有月度补发入口。
6. 在 `ffpa_tur_flavor.23` 与 `.33` 各增加一个 `after` 调用，使任一终局选项结算后立即授予。

**完成检查**

```zsh
rg -n 'ffpa_apply_tur_route_interest_group_identity_v1|ffpa_tur_(republic|directorate)_interest_group_identity_v1' common events
```

人工核对：终局前条件不成立；每条路线三个终局选项共用同一身份；高门路线不进入任一分支；版本变量设置后重复 ensure 不写槽位。

## 5. Task 3：补齐双语本地化与项目登记

**修改文件**

- `localization/english/ffpa_turkish_flavor_l_english.yml`
- `localization/simp_chinese/ffpa_turkish_flavor_l_simp_chinese.yml`
- `README.md`
- `AGENTS.md`

**步骤**

1. 两种语言各新增四个利益集团名称键。
2. 两种语言各新增六个 Trait 名称和六个 `_desc` 键，共 16 个新增键。
3. 描述只表达制度风味，不重复百分比。
4. README 仅在既有 TUR 路线说明中登记两个终局身份包。
5. AGENTS 在国家身份核心中登记六个 Trait，在 TUR 状态机中登记四个名称、授予 effect 和两个存档变量，并扩展对应验收项。

**完成检查**

```zsh
xxd -l 3 localization/english/ffpa_turkish_flavor_l_english.yml
xxd -l 3 localization/simp_chinese/ffpa_turkish_flavor_l_simp_chinese.yml
rg -n 'ffpa_ig_tur_(republican_general_staff|ankara_civic_society|national_reconstruction_combines|national_technical_service_corps)|ig_trait_ffpa_tur_(guardianship_intervention|civilian_command|republican_public_instruction|contractual_obstruction|reconstruction_contracts|national_technical_service)' localization
```

预期两份文件头均为 `efbbbf`，且新增键集合完全一致。

## 6. Task 4：静态、最终数据库与运行时验证

1. 新增并运行无依赖的 `tests/test_tur_route_interest_group_identity.py`，检查固定 ID、分支条件、事件接线、花括号和双语键集合。
2. 在原版、Firefall、Tech & Res 和本项目中搜索六个 Trait ID、四个名称键与共享 effect，确认没有上游冲突或本项目重复定义。
3. 验证所有图标和 modifier 能在当前原版同类数据中找到先例。
4. 解析 `.metadata/metadata.json`，运行 `git diff --check`。
5. 搜索当前及轮转 `error*.log` 中的新增技术 ID；若未启动包含本次改动的游戏，只将其作为历史日志检查。
6. 游戏内分别验证：终局前无身份、共和国三个终局选项、重建总署三个终局选项、旧档月度补发、重复 ensure、高门路线隔离、保存重载。

## 7. 交付边界

实现完成后报告静态确认、已有日志证据和待游戏内验证项。不为测试方便新增调试事件、决议、日志或长期诊断状态；需要实机触发时直接使用现有路线终局与旧档入口。
