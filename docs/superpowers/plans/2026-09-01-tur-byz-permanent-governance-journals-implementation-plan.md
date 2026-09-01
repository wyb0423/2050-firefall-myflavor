# TUR / BYZ 常驻治理日志实施计划

日期：2026-09-01
状态：设计已确认，等待实施
设计来源：`docs/superpowers/specs/2026-09-01-tur-byz-permanent-governance-journals-design.md`

## 1. 交付目标

在东地中海风味状态机内实现四项长期日志：

- `je_ffpa_tur_imperial_registers`：《帝国簿册与行省中介》；
- `je_ffpa_tur_bread_and_capital`：《面包与首都》；
- `je_ffpa_byz_roman_commonwealth_governance`：《罗马人的公共体》；
- `je_ffpa_byz_military_households_and_dynatoi`：《军户与权门》。

实现必须保持四套异构机制、完整失败/重试状态、版本化存档接口和轻量月度调度，不接管外部 Core Balance、Building Pruning 或 Auto PM Adapter。

## 2. 文件方案

### 2.1 新增运行时文件

- `common/journal_entry_groups/ffpa_permanent_governance_groups.txt`
- `common/journal_entries/ffpa_permanent_governance_journals.txt`
- `common/scripted_buttons/ffpa_permanent_governance_buttons.txt`
- `common/scripted_triggers/ffpa_permanent_governance_triggers.txt`
- `common/scripted_effects/ffpa_permanent_governance_effects.txt`
- `common/script_values/ffpa_permanent_governance_values.txt`
- `common/scripted_progress_bars/ffpa_permanent_governance_progress_bars.txt`
- `common/static_modifiers/ffpa_permanent_governance_modifiers.txt`
- `events/ffpa_turkish_permanent_governance_events.txt`
- `events/ffpa_byzantine_permanent_governance_events.txt`
- `localization/english/ffpa_permanent_governance_l_english.yml`
- `localization/simp_chinese/ffpa_permanent_governance_l_simp_chinese.yml`

TUR 与 BYZ 事件分文件，是因为它们分别使用既有 `ffpa_tur_flavor` 与 `ffpa_flavor` namespace。不要在一个事件文件中混合两个 namespace。

### 2.2 窄修改既有文件

- `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt`：把唯一 ensure/迁移包装接入 `ffpa_ensure_eastern_mediterranean_v2`，或在其明确的 TUR/BYZ分支调用专用 effect。
- `common/scripted_effects/ffpa_turkish_flavor_effects.txt`：在既有 TUR 形成其他 tag 的清理路径加入一行专用清理调用；不要复制新日志内部逻辑。
- `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt`：在既有 `on_country_formed` 包装中加入一行专用国家成立清理/补发调用；不新增第二个 on_action。
- `README.md`：玩家可见说明、旧存档与诊断入口。
- `AGENTS.md`：文件所有权、事件号、持久变量、验证项目和跨模块边界。

采用专用本地化文件，避免与当前工作树中已有的两份大本地化文件修改重叠。

## 3. 固定技术 ID

### 3.1 事件号

实施前重新搜索；若没有新冲突，固定使用：

| 事件 | ID |
|---|---|
| TUR 行省俘获失败 | `ffpa_tur_flavor.90` |
| TUR 纸面帝国失败 | `ffpa_tur_flavor.91` |
| TUR 首都供给崩溃 | `ffpa_tur_flavor.92` |
| BYZ 公共体失守 | `ffpa_flavor.50` |
| BYZ 军役户籍法律选择 | `ffpa_flavor.51` |
| BYZ 军籍册上的空白 | `ffpa_flavor.52` |

未跟踪的 TUR 边疆计划已预留 `ffpa_tur_flavor.60–.84`，本任务不得复用。

### 3.2 日志组

- `je_group_ffpa_tur_permanent_governance`
- `je_group_ffpa_byz_permanent_governance`

均为 country context。四项日志不塞入重建、复归或帝国地区建设组。

### 3.3 核心变量

#### TUR 簿册

- `ffpa_tur_register_balance_v1`
- `ffpa_tur_register_low_extreme_months_v1`
- `ffpa_tur_register_high_extreme_months_v1`
- `ffpa_tur_register_failure_cooldown_v1`
- `ffpa_tur_register_restart_value_v1`
- `ffpa_tur_register_audit_cooldown_v1`
- `ffpa_tur_register_provincial_roll_cooldown_v1`
- `ffpa_tur_register_dual_ledger_cooldown_v1`
- `ffpa_tur_register_emergency_dual_ledger_used_v1`

#### TUR 供给

- `ffpa_tur_capital_reserve_v1`
- `ffpa_tur_capital_supply_unlock_delay_v1`
- `ffpa_tur_capital_supply_crisis_months_v1`
- `ffpa_tur_capital_supply_famine_months_v1`
- `ffpa_tur_capital_supply_failure_cooldown_v1`
- `ffpa_tur_capital_purchase_cooldown_v1`
- `ffpa_tur_capital_granary_cooldown_v1`
- `ffpa_tur_capital_rationing_cooldown_v1`
- `ffpa_tur_capital_rationing_emergency_used_v1`

首次正常初始化储备固定为 50；失败重试固定为 10。

#### BYZ 公共体

每根支柱使用状态和恶化计时，状态值固定为：0 完好、1 预警、2 破裂、3 修复中。

- `ffpa_byz_polity_law_state_v1`
- `ffpa_byz_polity_welfare_state_v1`
- `ffpa_byz_polity_recognition_state_v1`
- 每柱的 `two_bad_months_v1`、`three_bad_months_v1`、`repair_months_v1`；
- `ffpa_byz_polity_total_failure_months_v1`
- `ffpa_byz_polity_failure_cooldown_v1`
- 三个按钮冷却和三个按危机强制使用标记；
- `ffpa_byz_polity_sol_baseline_v1`
- `ffpa_byz_polity_sol_baseline_review_v1`
- 全国州统计缓存：已整合州总数、市场接入合格数、饥荒数、高动乱数。

#### BYZ 军户

- `ffpa_byz_dynatoi_pressure_v1`
- `ffpa_byz_dynatoi_danger_months_v1`
- `ffpa_byz_dynatoi_collapse_months_v1`
- 三个可重复按钮冷却和紧急共负税标记；
- `ffpa_byz_military_households_reform_stage_v1`：0–3；
- `ffpa_byz_military_register_choice_v1`：1 职业军队、2 大规模征兵；
- `ffpa_byz_military_households_active_reform_v1`：1/2/3；
- `ffpa_byz_military_households_reform_months_v1`
- `ffpa_byz_military_households_reform_fatigue_v1`
- `ffpa_byz_military_households_crisis_reform_used_v1`
- `ffpa_byz_dynatoi_failure_cooldown_v1`
- `ffpa_byz_dynatoi_restart_value_v1`

### 3.4 迁移标记

- `ffpa_permanent_governance_migrated_v1`
- 每项日志一个初始化标记，避免用数值变量是否存在猜测状态。

## 4. Task 0：冻结基线与兼容证据

**读取**

- `.metadata/metadata.json`
- 当前设计规格与本计划
- 本任务计划修改的全部既有文件
- 原版 `common/journal_entries/journal_entries.md`
- 原版 `common/scripted_buttons/scripted_buttons.md`
- 原版已工作的 `modifiers_while_active`、`fail/on_fail`、scripted button、progress bar 先例
- Tech & Res `events/ztr_superpower.txt` 的 `activate_law` 先例
- 最终数据库中的 `law_professional_army`、`law_mass_conscription`

**步骤**

1. 运行 `git status --short --branch`，把当前 TUR 边疆、权力集团名称、README、AGENTS 和本地化改动登记为用户/其他任务现有修改。
2. 用 `rg --files -uu -g '!/.git/**'` 重新盘点文件；不得覆盖、暂存或提交现有改动。
3. 确认 Victoria 3 1.13.11、Firefall 0.1.1、Tech & Res 1.6 与实际加载顺序没有变化。
4. 搜索本计划全部 JE、group、event、modifier、button 和变量 ID；任何冲突先改计划，不边写边改名。
5. 确认 `ffpa_tur_flavor.90–.92`、`ffpa_flavor.50–.52` 未被当前工作树或其他未跟踪规格预留。
6. 对法律定义建立最终来源表：原版定义、Firefall/Tech & Res 是否同名替换、科技前置、互斥法律和直接激活副作用。
7. 从本地先例冻结本任务实际使用的 modifier 字段。若设计中的同名概念没有合法字段，只允许使用同方向、同层级的近似字段，并在实施报告登记。

**完成检查**

```zsh
rg -n "je_ffpa_(tur_imperial_registers|tur_bread_and_capital|byz_roman_commonwealth_governance|byz_military_households_and_dynatoi)" common events localization docs || true
rg -n "ffpa_tur_flavor\.(90|91|92)|ffpa_flavor\.(50|51|52)" common events localization docs || true
```

除设计和计划中的预留外，运行时不得已有定义。

## 5. Task 1：创建文件骨架、日志组与显示进度条

**新增文件**

- `common/journal_entry_groups/ffpa_permanent_governance_groups.txt`
- `common/scripted_progress_bars/ffpa_permanent_governance_progress_bars.txt`
- 其余第 2.1 节文件的带说明空骨架

**步骤**

1. 用 `apply_patch` 创建文件；不要用 shell 重定向或 `cat`。
2. 创建两个日志组。
3. 创建三根变量镜像进度条：
   - TUR 簿册：0–100；
   - TUR 储备：0–100；
   - BYZ 权门侵蚀：0–100。
4. BYZ 公共体不用数值进度条，通过 status desc 和三个状态变量显示支柱状态。
5. progress bar 只做显示镜像，country 变量是权威存档状态；同步 effect 必须显式调用现有日志进度条写值先例。
6. 为三根进度条提供 second desc，显示本月变化来源、危险计时或当前档位。

**完成检查**

```zsh
rg -n "^je_group_ffpa_(tur|byz)_permanent_governance[[:space:]]*=" common/journal_entry_groups/ffpa_permanent_governance_groups.txt
rg -n "^ffpa_(tur_register|tur_capital_reserve|byz_dynatoi)_bar[[:space:]]*=" common/scripted_progress_bars/ffpa_permanent_governance_progress_bars.txt
```

## 6. Task 2：实现查询层、script value 与通用状态原语

**修改文件**

- `common/scripted_triggers/ffpa_permanent_governance_triggers.txt`
- `common/script_values/ffpa_permanent_governance_values.txt`
- `common/scripted_effects/ffpa_permanent_governance_effects.txt`

**步骤**

1. 创建四项解锁 trigger：
   - TUR 核心要求 `c:TUR ?= ROOT` 且三条路线任一终局选择存在；
   - TUR 副日志要求核心日志首次挂载已满一年；
   - BYZ 两日志要求 `ffpa_byz_new_rome_complete` 与 `ffpa_byz_rhomaic_commonwealth_complete`，兼容旧 v2 JE 的稳定完成变量；
   - 失败冷却存在时阻止重新挂载。
2. 创建四项 `active_or_should_exist` trigger，用于 ensure 和 tag 清理。
3. 创建变量 clamp、档位同步、按钮冷却清理和危机标记清理 effect；每个 effect 明确 country scope。
4. 财政按钮费用使用国家 GDP 或收入 accessor 的受限 script value，并设最小/最大值；不得按月扫描建筑计算国家规模。
5. 所有 trigger 只判断，不写变量；所有数值变化集中到 effect。
6. 对 `0–100` 数值统一在每次变化后 clamp，禁止只依赖 UI bar 上限。

**完成检查**

```zsh
rg -n "^ffpa_(tur_register|tur_capital_supply|byz_polity|byz_dynatoi).*=" common/scripted_triggers/ffpa_permanent_governance_triggers.txt common/scripted_effects/ffpa_permanent_governance_effects.txt common/script_values/ffpa_permanent_governance_values.txt
```

人工核对 trigger 中没有 `set_variable`、`change_variable` 或 `add_modifier`。

## 7. Task 3：定义全部 modifier 并冻结未定数值

**修改文件**

- `common/static_modifiers/ffpa_permanent_governance_modifiers.txt`

**步骤**

1. 按日志前缀分四段定义档位、按钮代价、工程代价、永久结果和失败结果。
2. BYZ 权门五档严格使用设计规格中的数值；本地字段映射以最终数据库为准：全国税收能力使用国家可传播的 `state_tax_capacity_mult`，征兵使用 `state_conscription_rate_mult`，训练使用 `building_training_rate_mult`。
3. `ffpa_byz_veteran_settlement_system_v1` 固定 `state_welfare_payments_add = 0.10`，不附加生活水平修正。
4. TUR 首都失败州 modifier 与国家 modifier 分开定义；添加时分别使用 state/country scope，均通过 `is_decaying = yes` 添加，持续 8 年与 6 年。
5. TUR 核心未冻结的小档位收益控制在以下边界：
   - 税收、官僚或吞吐类绝对幅度不超过 10%；
   - 权威不超过 ±100；
   - 合法性不超过 +5；
   - 极端档位自身不提供净收益。
6. TUR 两种核心失败惩罚持续 5 年：低端侧重 `state_tax_capacity_mult`、权威和地主支持；高端侧重 `country_bureaucracy_mult`、合法性或动乱影响。两者不得复制首都供应惩罚。
7. BYZ 公共体失败持续 5 年，集中于合法性、权威、激进派与利益集团冲突；不使用农业、军需或首都市场字段。
8. 确认所有 modifier 字段在原版/依赖最终数据库有定义和同 scope 先例。

**完成检查**

```zsh
rg -n "state_welfare_payments_add = 0\.10|is_decaying" common/static_modifiers/ffpa_permanent_governance_modifiers.txt common/scripted_effects/ffpa_permanent_governance_effects.txt
```

`is_decaying` 应出现在添加 modifier 的 effect 参数中，而不是静态 modifier 定义内部。

## 8. Task 4：实现 TUR《帝国簿册与行省中介》

**修改文件**

- `common/journal_entries/ffpa_permanent_governance_journals.txt`
- `common/scripted_buttons/ffpa_permanent_governance_buttons.txt`
- `common/scripted_triggers/ffpa_permanent_governance_triggers.txt`
- `common/scripted_effects/ffpa_permanent_governance_effects.txt`
- `events/ffpa_turkish_permanent_governance_events.txt`

**步骤**

1. 初始化 effect 按既有 `ffpa_tur_state_project_v1` 的 1/2/3 与终局变量写入 45/55/65；未知或损坏路线不猜测，暂不挂载并保留诊断日志入口。
2. 月度 effect 只读取已核实的国家级行政、官僚、市场和动乱聚合条件，计算一个有符号变化值并 clamp。
3. 同步七个互斥数值区间：35–65、25–34、66–74、10–24、75–89、0–9、90–100。两个外侧协商区可复用数值 modifier，两个极端可复用“无净收益”基础，但状态描述和失败计时必须分别维护。
4. 低端或高端每月分别累计对应计时；离开该极端时以每月 -3 回退，直至 0。另一端计时不得继续残留。
5. 计时达到 24 后让 JE `fail` 成立；`on_fail` 根据当前端触发 `.90` 或 `.91`。
6. 实现三枚按钮：
   - 稽核使团 +10，12个月；
   - 行省名册 -10，12个月；
   - 双重账簿向 50 移动最多15，24个月，不得越过 50。
7. 极端危机允许双倍代价提前用双重账簿一次；使用后设置本危机标记，离开极端时清除。
8. 两种失败事件添加不同 5 年惩罚、3 年失败冷却和 25/75 重启值；事件只能确认结果，不提供无惩罚选项。
9. 重启清理全部按钮冷却与极端计时，再从存储的重启值挂载。

**完成检查**

```zsh
rg -n "^je_ffpa_tur_imperial_registers[[:space:]]*=|ffpa_tur_flavor\.(90|91)" common/journal_entries/ffpa_permanent_governance_journals.txt events/ffpa_turkish_permanent_governance_events.txt
```

人工演算从 0/100、9/90、24/25、34/35、65/66、74/75、89/90 跨界的档位和计时。

## 9. Task 5：实现 TUR《面包与首都》

**修改文件**

与 Task 4 相同的 TUR 文件切片。

**步骤**

1. 正常初始储备写 50；失败重启写 10。
2. 建立四个明确 trigger：粮食市场价 `+25%`、首都州运输本地价 `+25%`、电力本地价 `+25%`、市场接入 `<85%`。
3. 建立四个严重危机分支：饥荒、接入 `<60%`、粮食 `+50%` 且运输/电力任一 `+50%`、四项普通异常全有。
4. 用互斥 `if/else_if` 按异常数量结算 `+3/+1/-2/-5/-8`，饥荒再额外 -10，最后 clamp。
5. 实现储备档位 70–100、30–69、1–29、0；主动开仓的两年收益用有限期限 modifier，不由 ensure 续期。
6. 实现三枚按钮：采购 +15/6月、开仓 -15/6月、紧急配给 +25/12月；采购费用读取调用当月价格和国家规模。
7. 严重危机下允许双倍代价提前配给一次；补入储备后同时清除严重危机和饥荒失败计时。
8. 空仓且严重危机累计6月；空仓且首都饥荒累计3月；任一达到阈值让 JE 失败并触发 `.92`。
9. 失败事件先保存危机首都 scope，再给该州添加 8 年衰减修正，给国家添加 6 年衰减修正，并对首都中下层人口一次性增加激进派。
10. 失败设置 4 年冷却；迁都不移除旧危机州修正，月度读取自动转向新首都。

**完成检查**

```zsh
rg -n "0\.25|0\.50|0\.85|0\.60|ffpa_tur_flavor\.92|is_decaying = yes" common/scripted_triggers/ffpa_permanent_governance_triggers.txt common/scripted_effects/ffpa_permanent_governance_effects.txt events/ffpa_turkish_permanent_governance_events.txt
```

人工核对“单独粮价 +50%”不满足严重危机。

## 10. Task 6：实现 BYZ 全国统计与动态生活水平基准

**修改文件**

- `common/scripted_effects/ffpa_permanent_governance_effects.txt`
- `common/scripted_triggers/ffpa_permanent_governance_triggers.txt`
- `common/script_values/ffpa_permanent_governance_values.txt`

**步骤**

1. 日志首次挂载时保存全国平均生活水平为基准。
2. 每五年比较当前平均生活水平与基准：只在当前值更高时上调，不下调；更新下一次审查期限时不得被月度 ensure 刷新。
3. 在一个 country-scope effect 中清零四个缓存计数，然后只执行一次 `every_scope_state`：
   - 只统计 owner 为 ROOT 且 `is_incorporated = yes` 的州；
   - 总数 +1；
   - 市场接入至少 85% 时合格数 +1；
   - 饥荒州 +1；
   - 动乱至少 25% 时高动乱数 +1。
4. 使用交叉相乘比较比例，避免除零和浮点误差：
   - 市场合格数 ×100 ≥ 总数 ×80；
   - 饥荒数 ×100 ≤ 总数 ×5；
   - 高动乱数 ×100 ≤ 总数 ×15。
5. 若没有已整合州，三项全国州条件视为不合格并记录诊断状态，不能除以零或自动通过。
6. 统计只在 BYZ 公共体 JE 活动时按月执行一次；其他三项日志不得调用该州遍历。

**完成检查**

```zsh
rg -n "every_scope_state|ffpa_byz_polity_(incorporated|accessible|famine|high_turmoil)" common/scripted_effects/ffpa_permanent_governance_effects.txt
```

人工确认文件中只有一个属于本功能的已整合州月度循环。

## 11. Task 7：实现 BYZ《罗马人的公共体》

**修改文件**

- `common/journal_entries/ffpa_permanent_governance_journals.txt`
- `common/scripted_buttons/ffpa_permanent_governance_buttons.txt`
- `common/scripted_triggers/ffpa_permanent_governance_triggers.txt`
- `common/scripted_effects/ffpa_permanent_governance_effects.txt`
- `events/ffpa_byzantine_permanent_governance_events.txt`

**步骤**

1. 为三柱分别创建三个原子条件 trigger，不能让合法性、违约、动乱等条件跨柱复用。
2. 每月计算每柱坏条件数：
   - 0：清除预警与恶化计时；
   - 1：状态为预警，但不累计破裂；
   - 2：`two_bad_months` +1，12月破裂；
   - 3：`three_bad_months` +1，6月破裂。
3. 破裂时只移除该柱收益并应用轻微对应负担，不写另一柱状态。
4. 实现三枚6个月按钮；完好/预警时清理对应恶化计时并设置保护，破裂时允许一次双倍成本强制使用。
5. 破裂柱只有在三项条件全部健康、已经使用修复按钮并连续6个月后转回完好。
6. 总失败计时：三柱破裂累计6月；两柱破裂且剩余一柱预警累计12月。组合解除立即清零。
7. `.50` 添加公共体失败惩罚和5年冷却；重启时法律柱为完好，另两柱为破裂，按钮均可用。
8. status desc 显示每柱状态、坏条件数、破裂/修复剩余月份；不用统一数值 progress bar。

**完成检查**

```zsh
rg -n "^je_ffpa_byz_roman_commonwealth_governance[[:space:]]*=|ffpa_flavor\.50" common/journal_entries/ffpa_permanent_governance_journals.txt events/ffpa_byzantine_permanent_governance_events.txt
```

建立 0/1/2/3 坏条件与三种总失败组合的真值表，逐行核对。

## 12. Task 8：实现 BYZ 权门侵蚀、档位与可重复按钮

**修改文件**

BYZ 专用 trigger/effect/button/JE/modifier 切片。

**步骤**

1. 初始侵蚀写 20；每月按设计来源相加：第一阶段前 +0.25、强大地主 +0.50、佃农 +0.50、农奴 +1.00、农民征召 +0.50、税收特权 +0.25、统一地籍抵消 0.25，最低0。
2. 根据阶段永久削弱来源：
   - 阶段1：取消基础 +0.25，农民征召降至 +0.25；
   - 阶段2：佃农 +0.25、农奴 +0.50；
   - 阶段3：强大地主 +0.25、税收特权来源归零。
3. 每月变化后 clamp 0–100，并同步五档互斥 modifier。
4. 实现三枚可重复按钮和18/12/24个月冷却；资金赎回在违约时不可用，共负税只在侵蚀至少70时可用。
5. 侵蚀至少90时，每场危机允许双倍代价提前使用共负税一次；降到90以下清理危机标记。
6. 危险计时：100 连续6月；90以上连续18月且强大地主、农奴/佃农、农民征召任一存在。离开阈值立即清理对应计时。
7. JE `fail` 只读取已维护计时，不在 fail trigger 中重新执行复杂月度逻辑。

**完成检查**

```zsh
rg -n "0\.25|0\.50|1\.00|ffpa_byz_dynatoi_pressure_v1" common/scripted_effects/ffpa_permanent_governance_effects.txt common/scripted_triggers/ffpa_permanent_governance_triggers.txt
```

人工演算阶段0–3在所有风险组合下的月度净增长。

## 13. Task 9：实现三阶段改革与军制选择事件

**修改文件**

- `common/scripted_buttons/ffpa_permanent_governance_buttons.txt`
- `common/scripted_effects/ffpa_permanent_governance_effects.txt`
- `common/scripted_triggers/ffpa_permanent_governance_triggers.txt`
- `events/ffpa_byzantine_permanent_governance_events.txt`

**步骤**

1. 创建三枚按阶段互斥显示的改革按钮；第三阶段完成后全部隐藏。
2. 通用启动 guard：无革命/内战、未违约、官僚非负、无运行中改革；正常还要求无改革疲劳。
3. 侵蚀至少80时允许每场危机提前越过疲劳一次；即时 IG 代价和临时 modifier 时长翻倍，工程月数不变。
4. 第一阶段按钮额外要求 `military_drill`、`enlistment_offices` 与当前没有正在推进的其他法律，并调度 `.51`。
5. `.51` 三个选项：
   - 立即 `activate_law = law_type:law_professional_army`，添加对应5年代价；
   - 立即 `activate_law = law_type:law_mass_conscription`，添加对应5年代价；
   - 放弃，清理调度并设置3个月按钮冷却。
6. 已经采用所选法律时保留改组成本、IG 激进派减半。保存选择值1/2，但不锁定后续立法。
7. 选择法律后启动12个月工程；违约暂停月份。完成才 -15、阶段1和永久增长削弱。
8. 第二阶段启动5年诉讼代价、18个月工程；完成 -20、阶段2和土地风险削弱。
9. 第三阶段要求正黄金储备，启动5年军需基金、24个月工程；完成 -25、阶段3、增长削弱和永久福利 modifier。
10. 每项完成后设置3年疲劳；完成 effect 先检查 active reform 和目标阶段，保证重复调用不会重复发一次性 IG 变化或侵蚀降低。

**完成检查**

```zsh
rg -n "activate_law = law_type:law_(professional_army|mass_conscription)|state_welfare_payments_add = 0\.10|ffpa_flavor\.51" common events
```

验证直接激活法律时没有正在推进的法律；实机确认该 effect 不留下损坏 enactment 状态。

## 14. Task 10：实现 BYZ 军户失败选择、重试和清理

**修改文件**

BYZ 专用 JE/effect/event 切片。

**步骤**

1. `on_fail` 先捕获已完成阶段，取消运行中改革，移除其临时 modifier，清除工程月数、疲劳、按钮冷却、危机标记、危险计时和档位修正。
2. 已经即时激活的军队法律不回滚；未完成第一阶段时不写阶段1和永久增长削弱。
3. 触发 `.52`，只提供两个坏结局：
   - 权门乡约：8年修正、4年冷却、重启70；
   - 紧急没收：地主激进派、农村忠诚派、5年修正、3年冷却、重启55。
4. default/AI fallback 固定权门乡约；AI 根据地主力量、财政和军事需求调整选择权重，但不能选择空选项。
5. 重试按保存值挂载，重新同步已完成阶段和福利 modifier，不重复发 -15/-20/-25。
6. tag 失效移除福利和运行中状态，但保留阶段与历史选择；恢复 BYZ 后根据阶段3幂等补回福利。

**完成检查**

```zsh
rg -n "ffpa_flavor\.52|ffpa_byz_military_households_reform_stage_v1|ffpa_byz_veteran_settlement_system_v1" common events
```

人工核对失败发生在第一阶段法律已切换但工程未完成的特殊路径。

## 15. Task 11：接入 ensure、迁移与 tag 清理

**修改文件**

- `common/scripted_effects/ffpa_permanent_governance_effects.txt`
- `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt`
- `common/scripted_effects/ffpa_turkish_flavor_effects.txt`

**步骤**

1. 创建唯一包装 `ffpa_ensure_permanent_governance_journals_v1`，只在当前国家为 TUR/BYZ 或仍有本系统临时状态时执行。
2. 把包装接入现有 `ffpa_ensure_eastern_mediterranean_v2`；不新增第二个 `on_monthly_pulse_country`。
3. 固定 ensure 顺序：
   - 旧档迁移；
   - tag 失效清理；
   - 永久阶段 modifier 幂等同步；
   - 失败冷却到期后的重试；
   - 解锁日志挂载；
   - 不处理实际活动 JE 的月度数值。
4. TUR 形成其他 tag 时清理两个 JE、动态档位、冷却和失败计时，不删除 `ffpa_tur_state_project_v1` 或既有路线历史。
5. BYZ tag 变化清理两个 JE、运行中改革、档位和福利 modifier，保留阶段与历史军制选择。
6. `ffpa_permanent_governance_migrated_v1` 只在迁移完成后写入；迁移不发事件、IG 变化、侵蚀降低或失败惩罚。
7. 对损坏旧档使用保守恢复：数值缺失才初始化；已有数值 clamp；阶段非法值清理活动工程并停止自动奖励。

**完成检查**

```zsh
rg -n "ffpa_ensure_permanent_governance_journals_v1" common/on_actions common/scripted_effects
```

预期只有一个定义和一个稳定调用链；on_action 文件不包含业务逻辑。

## 16. Task 12：本地化、README 与 AGENTS 登记

**新增文件**

- 两份专用本地化文件

**修改文件**

- `README.md`
- `AGENTS.md`

**步骤**

1. 为四项 JE、两组、三根 bar、十五枚常规/改革按钮、六个事件、全部 modifier、status desc、失败条件和 tooltip 添加双语键。
2. TUR 供应 status 必须逐项显示四项普通异常与严重危机，不使用模糊“供应异常”。
3. BYZ 公共体 status 必须显示三柱各自条件、当前坏条件数和剩余月数。
4. BYZ 军户 status 必须显示月度侵蚀来源、改革阶段、工程进度和紧急使用状态。
5. 英文和简体中文键集合完全一致，均保持 UTF-8 BOM。
6. README 说明日志解锁、长期效果、失败可重试、衰减惩罚和第三阶段全国福利成本。
7. AGENTS 登记新文件、事件号、变量为存档 API；把该功能归东地中海日志/迁移/风味状态机所有。
8. AGENTS 专项验收增加四日志的新档、旧档、失败、重试、tag 变化与性能检查。
9. 合并 README/AGENTS 时只做窄补丁，保留当前工作树中 TUR 边疆和权力集团命名的并行改动。

**完成检查**

```zsh
xxd -l 3 localization/english/ffpa_permanent_governance_l_english.yml
xxd -l 3 localization/simp_chinese/ffpa_permanent_governance_l_simp_chinese.yml
```

两者必须为 `efbbbf`。

## 17. Task 13：静态和最终数据库验证

### 17.1 结构

1. `jq empty .metadata/metadata.json`。
2. 对修改/新增 `.txt` 做忽略注释和字符串后的花括号平衡检查。
3. 检查四个 JE、两个 group、三根 bar、按钮、六事件、modifier、trigger/effect/value 和本地化引用。
4. 检查本项目意外重复顶层键；本任务不应新增任何上游覆盖。
5. 检查所有 `ffpa_tur_flavor.90–.92`、`ffpa_flavor.50–.52` 恰好定义一次。
6. `git diff --check`；不要为通过检查格式化并行任务文件。

### 17.2 存档与清理

1. 搜索所有新期限变量，确认 fail、invalid、retry、tag change 至少各有相应清理路径。
2. 搜索所有有限期限 modifier，确认月度 ensure 不会续期。
3. 搜索所有阶段奖励，确认只能从完成 effect 发放一次。
4. 搜索 `activate_law`，确认事件 trigger 明确阻止当前立法被无提示打断。
5. 搜索 `every_scope_state`，确认本功能月度只有 BYZ 公共体的一次已整合州扫描。

### 17.3 最终数据库

1. 重新比较两项军队法律在原版、Firefall、Tech & Res、本项目中的最终来源。
2. 确认所有 modifier 类型在 1.13.11 最终库存在。
3. 确认食品、运输、电力、市场接入、饥荒、政治运动激进度和违约 trigger 均有同 scope 本地先例。
4. 确认新文件没有 `replace_path`，也不重定义外部拆分包对象。

## 18. Task 14：游戏内验证矩阵

### 18.1 TUR 核心

- 三条路线各建一档，确认 45/55/65。
- 强制设置边界值 0、9、10、24、25、34、35、65、66、74、75、89、90、100，检查档位和 UI。
- 模拟两端24个月、短暂越界、按钮提前使用、失败和3年重试。

### 18.2 TUR 供给

- 单独制造四种异常与全部组合，核对每月变化。
- 验证粮价+50%单独不构成严重危机。
- 验证空仓普通危机不失败、严重危机6月失败、饥荒3月失败。
- 迁都后新首都成为读取对象，旧危机州的8年衰减修正保留。
- 观察8年/6年衰减修正随时间实际变弱。

### 18.3 BYZ 公共体

- 分别破坏每柱0/1/2/3项条件，核对6/12月逻辑。
- 用新征服未整合州验证其不进入全国比例；整合后下一月纳入。
- 验证无已整合州不会除零或自动通过。
- 验证三柱全破和两破一预警两种总失败。
- 验证破柱强制按钮双倍成本、健康6月后修复。

### 18.4 BYZ 军户

- 阶段0–3逐一验证所有增长来源和五档 modifier。
- 三项重复按钮冷却、违约限制与90以上紧急共负税。
- 两个军制选项立即激活法律；放弃只产生3个月短冷却。
- 12/18/24月工程、违约暂停、80以上提前推进、失败取消未完成工程。
- 第三阶段福利支付+10%产生真实财政效果；tag 变化移除、返回 BYZ 补回。
- 两种失败选项、3/4年冷却和55/70重启。

### 18.5 运行时日志

检查最新和轮转的 `debug*.log`、`error*.log`、`game*.log`：

1. 文件被加载且没有后加载覆盖；
2. 顶层定义解析成功；
3. ensure、JE、按钮和事件入口到达；
4. trigger scope 正确，effect 实际写入；
5. 最终状态没有被既有 ensure 或另一个模块回写。

无法启动游戏时，交付必须分别列出静态确认、最终数据库确认、已有日志证据和仍需游戏内验证项。

## 19. Task 15：交付与 Git 边界

1. 再次运行 `git status --short --branch`，按“本任务新增/修改”和“开工前已有/并行任务改动”分别列出。
2. 不执行 `git add`、`git commit`、`git reset`、`git checkout --`、`git clean` 或 rebase，除非用户另行明确要求。
3. 不提升 `.metadata/metadata.json` 版本，除非用户要求发布。
4. 交付说明包括：
   - 东地中海日志状态机模块及文件；
   - 是否改变跨模块接口、上游覆盖或存档 API；
   - 静态、最终数据库和运行时验证；
   - 未验证项目；
   - 当前分支与工作树状态。
