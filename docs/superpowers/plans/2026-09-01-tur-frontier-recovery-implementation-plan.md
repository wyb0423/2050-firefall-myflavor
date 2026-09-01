# TUR 边疆收复与限时宣称机制实施计划

日期：2026-09-01
依据：`docs/superpowers/specs/2026-09-01-tur-frontier-recovery-design.md`
状态：已实施并完成静态验证，待游戏内验证

## 1. 实施约束

- 目标环境为 Victoria 3 `1.13.*`、Firefall `0.1.1`、Tech & Res `1.6'`。
- 开工和交付均运行 `git status --short --branch`，保留用户已有修改。
- 不执行 `git add`、`git commit`、`git reset`、`git checkout --` 或 `git clean`。
- 所有文件修改使用 `apply_patch`；不把本机绝对路径写入 Mod、README、AGENTS 或报告。
- 不修改 `.metadata/metadata.json`，不新增依赖，不提升发布版本。
- 不修改战争目标、统一战争、恶名公式、Firefall TUR 成立顶层定义或外部 Core Balance 对象。
- 新增的变量、JE、决议和事件 ID 一经写入即按存档 API 对待。
- 本计划默认复用既有 `on_country_formed` 和月度 TUR ensure，不新增第二个 on_action。只有静态调用链证明现有入口无法覆盖某个阶段时，才对现有包装文件做最小接线。

## 2. 固定技术 ID

### 2.1 前线

| 顺序 | slug | JE ID | 成功事件 | 超时事件 | 撤回事件 |
|---:|---|---|---|---|---|
| 1 | `western_pact` | `je_ffpa_tur_front_western_pact` | `ffpa_tur_flavor.61` | `ffpa_tur_flavor.69` | `ffpa_tur_flavor.77` |
| 2 | `mosul` | `je_ffpa_tur_front_mosul` | `ffpa_tur_flavor.62` | `ffpa_tur_flavor.70` | `ffpa_tur_flavor.78` |
| 3 | `rumelia` | `je_ffpa_tur_front_rumelia` | `ffpa_tur_flavor.63` | `ffpa_tur_flavor.71` | `ffpa_tur_flavor.79` |
| 4 | `aegean_cyprus` | `je_ffpa_tur_front_aegean_cyprus` | `ffpa_tur_flavor.64` | `ffpa_tur_flavor.72` | `ffpa_tur_flavor.80` |
| 5 | `levant` | `je_ffpa_tur_front_levant` | `ffpa_tur_flavor.65` | `ffpa_tur_flavor.73` | `ffpa_tur_flavor.81` |
| 6 | `mesopotamia` | `je_ffpa_tur_front_mesopotamia` | `ffpa_tur_flavor.66` | `ffpa_tur_flavor.74` | `ffpa_tur_flavor.82` |
| 7 | `egypt` | `je_ffpa_tur_front_egypt` | `ffpa_tur_flavor.67` | `ffpa_tur_flavor.75` | `ffpa_tur_flavor.83` |
| 8 | `ifriqiya` | `je_ffpa_tur_front_ifriqiya` | `ffpa_tur_flavor.68` | `ffpa_tur_flavor.76` | `ffpa_tur_flavor.84` |

`ffpa_tur_flavor.60` 固定为边疆委员会事件。不得复用 `.61–.84` 处理其他内容。

前线目标州和路线不得在实施中再次自由裁量：

| slug | 目标州 | 路线 | 期限 |
|---|---|---|---:|
| `western_pact` | `STATE_WESTERN_THRACE` | 共和国 | 5475 日 |
| `mosul` | `STATE_MOSUL` | 共和国 | 5475 日 |
| `rumelia` | `STATE_ALBANIA`、`STATE_MACEDONIA`、`STATE_WESTERN_THRACE`、`STATE_BULGARIA`、`STATE_DOBRUDJA`、`STATE_NORTHERN_THRACE` | 高门、重建总署 | 7300 日 |
| `aegean_cyprus` | `STATE_ATTICA`、`STATE_CRETE`、`STATE_EAST_AEGEAN_ISLANDS`、`STATE_WEST_AEGEAN_ISLANDS`、`STATE_IONIAN_ISLANDS`、`STATE_CYPRUS` | 高门 | 7300 日 |
| `levant` | `STATE_ALEPPO`、`STATE_SYRIA`、`STATE_LEBANON`、`STATE_PALESTINE`、`STATE_TRANSJORDAN` | 高门、重建总署 | 7300 日 |
| `mesopotamia` | `STATE_MOSUL`、`STATE_BAGHDAD`、`STATE_DEIR_EZ_ZOR`、`STATE_BASRA` | 高门、重建总署 | 7300 日 |
| `egypt` | `STATE_LOWER_EGYPT`、`STATE_MIDDLE_EGYPT`、`STATE_UPPER_EGYPT`、`STATE_SINAI`、`STATE_MATRUH` | 高门 | 7300 日 |
| `ifriqiya` | `STATE_LIBYA`、`STATE_TRIPOLI`、`STATE_TUNISIA` | 高门 | 7300 日 |

`STATE_EGYPTIAN_DESERT` 明确排除。路线终局入口固定为高门 `ffpa_tur_porte_charter_choice_v1`、共和国 `ffpa_tur_republic_settlement_choice_v1`、重建总署 `ffpa_tur_directorate_settlement_choice_v1`；路线身份继续由 `ffpa_tur_state_project_v1` 的 1/2/3 表示，不新增同义变量。

每条前线固定使用：

- 完成：`ffpa_tur_front_<slug>_complete_v1`；
- 冷却：`ffpa_tur_front_<slug>_retry_cooldown_v1`；
- 待结算：`ffpa_tur_front_<slug>_resolution_pending_v1`。

### 2.2 入口与迁移

- `ffpa_tur_flavor_initialized_v1`
- `ffpa_tur_frontier_recovery_migrated_v1`
- `ffpa_tur_ztr_collapse_cleanup_pending_v1`
- `ffpa_tur_convene_frontier_council`
- `ffpa_tur_withdraw_frontier_mandate`
- `je_group_ffpa_turkish_frontier_recovery`

### 2.3 宣称来源变量

来源变量放在 country scope。命名规则固定为 `ffpa_tur_temporary_claim_<state-slug>_v1`，其中州 slug 为州 ID 去掉 `STATE_` 后的小写形式。西色雷斯和摩苏尔虽然出现在两种路线前线中，仍只各使用一个州级来源变量；一次一条前线保证不会发生并发所有权冲突。

## 3. Task 0：冻结上游证据与工作树基线

**读取文件**

- `.metadata/metadata.json`
- `common/country_formation` 的 Firefall 最终 TUR 定义
- 原版 `common/war_goal_types/21_return_state.txt`
- 原版 `common/war_goal_types/03_conquer_state.txt`
- Tech & Res `common/journal_entries/ztr_je_turkey.txt`
- Tech & Res `events/ottoman_empire/ottoman_empire_collapse.txt`

**步骤**

1. 运行 `git status --short --branch`，记录设计文档和实施计划之外的已有修改。
2. 运行 `uname -s` 与必要命令能力检查；确认 `git`、`rg`、`zsh`、`python3`、`shasum`、`xxd`、`jq` 可用。
3. 解析本机游戏、Workshop、Firefall `3768192009` 和 Tech & Res `3472248460` 路径，仅作为当前 shell 输入。
4. 重新提取 Firefall TUR 的 11 州与 `required_states_fraction = 0.7`，确认没有上游更新。
5. 对 Tech & Res 的 `ztr_je_turkey.txt` 执行 `shasum -a 256`，把哈希写入新覆盖文件头注释或实施报告，不创建机器路径文件。
6. 搜索 `ffpa_tur_flavor.60` 至 `.84`，确认全部为空闲。
7. 搜索计划中的新变量、JE、决议和组 ID，确认当前仓库没有冲突。

**完成检查**

```zsh
git status --short --branch
rg -n "ffpa_tur_flavor\.(60|6[1-9]|7[0-9]|8[0-4])" events common localization || true
rg -n "ffpa_tur_front_|ffpa_tur_flavor_initialized_v1|je_group_ffpa_turkish_frontier_recovery" common events localization || true
```

预期：事件和新 ID 均无现有定义；若上游版本或哈希变化，先更新设计证据并重新比较，不继续复制旧定义。

## 4. Task 1：实现 country-scope 查询层

**修改文件**

- `common/scripted_triggers/ffpa_turkish_flavor_triggers.txt`

**新增查询**

1. `ffpa_tur_is_ffpa_managed_v1`
   - 当前 tag 为 TUR；
   - 满足初始化标记，或存在既有 TUR 路线变量、路线 JE、终局完成变量等旧档明确证据；
   - 不根据当前政体猜测路线。
2. 八个完整所有权 trigger：`ffpa_tur_front_<slug>_owned_v1`。
3. 八个 availability trigger：`ffpa_tur_front_<slug>_available_v1`。
   - 检查路线、终局选择、前置完成变量、未完成、未冷却、无同名 JE；
   - 至少有一个目标州尚未完整拥有。
4. `ffpa_tur_frontier_slot_available_v1`
   - 直接检查八条 JE 和八个待结算变量；
   - 任一存在即返回 false，不使用计数变量。
5. `ffpa_tur_has_available_front_v1`
   - 八个 availability trigger 的 OR。
6. `ffpa_tur_frontier_council_ready_v1`
   - TUR、存在终局选择、和平、非外交博弈承诺参与者、槽位可用、至少一条前线可用。
7. `ffpa_tur_ai_frontier_council_ready_v1`
   - 包含玩家入口全部条件；
   - `infamy < infamy_threshold:infamous`；
   - `gold_reserves > 0`；
   - `country_rank <= rank_value:minor_power`（国家等级枚举数值越小越强）。

**实现注意**

- 使用项目已工作的 `is_diplomatic_play_committed_participant = no` 先例。
- 高门埃及/伊弗里基亚的 `rank_value:major_power` 门槛写进各自 availability 的 AI 分支或事件 AI 权重 guard，不限制玩家。
- trigger 不设置变量、不添加宣称、不触发事件。
- 每个复杂 AND/OR 块在注释中写出布尔含义，尤其是埃及的 `Levant AND (Rumelia OR Mesopotamia)`。

**完成检查**

```zsh
rg -n "^ffpa_tur_(is_ffpa_managed|front_.*_(owned|available)|frontier_slot_available|has_available_front|frontier_council_ready|ai_frontier_council_ready)_v1[[:space:]]*=" common/scripted_triggers/ffpa_turkish_flavor_triggers.txt
```

人工核对：共和国不能看到鲁米利亚等帝国前线；重建总署不能看到爱琴海、埃及或伊弗里基亚；高门埃及条件准确。

## 5. Task 2：实现宣称、结算、清理与迁移 effect

**修改文件**

- `common/scripted_effects/ffpa_turkish_flavor_effects.txt`

### 5.1 成立核心宣称

新增 `ffpa_ensure_tur_formation_core_claims_v1`：

- country scope，先验证 `c:TUR ?= ROOT`；
- 对 11 个 Firefall 成立州显式执行窄判断；
- 只有 `NOT owns_entire_state_region` 且 country scope `NOT = { has_claim = s:STATE_* }` 时，才在 `s:STATE_*` scope 执行 `add_claim = ROOT`；
- 不设置临时来源变量。

当前 1.13 安装中已验证的形态是 country scope `has_claim = s:STATE_*`，以及 `s:STATE_* = { add_claim = ROOT }` / `remove_claim = ROOT`。

### 5.2 逐州临时宣称原语

对前线使用到的每个唯一州建立清晰、可审查的显式分支。每个分支支持：

- **add**：未拥有且无宣称时添加，并在 ROOT 设置来源变量；
- **ensure**：只有来源变量已经存在时，恢复被移除的活动宣称；
- **cleanup**：来源变量存在时，未拥有且仍有宣称才移除，随后清除来源变量。

不要用全世界 `every_state_region` 扫描。州集合是固定白名单，使用 `s:STATE_*` 显式访问。

### 5.3 前线 effect

为八条前线分别实现：

- `ffpa_start_tur_front_<slug>_v1`
  - 调用目标州 add 分支；
  - 添加对应 JE；
  - 不发 modifier 或奖励。
- `ffpa_complete_tur_front_<slug>_v1`
  - 设置完成变量；
  - 清理目标州来源变量；
  - 移除待结算变量；
  - 触发固定成功事件 `.61–.68`。
- `ffpa_fail_tur_front_<slug>_v1`
  - 清理未实现临时宣称；
  - 设置 5 年冷却；
  - 移除待结算变量；
  - 触发固定超时事件 `.69–.76`。
- `ffpa_withdraw_tur_front_<slug>_v1`
  - 与 fail 相同清理和冷却；
  - 触发固定撤回事件 `.77–.84`。

上述 effect 均须幂等：重复调用不得重复事件、延长既有冷却或删除无来源宣称。用结果事件的 scheduled/fired guard，或确保 effect 只从唯一 JE 回调进入；选择一种并统一应用。

### 5.4 活动 ensure 与待结算

新增：

- `ffpa_ensure_tur_active_front_claims_v1`：只检查当前实际活动 JE 对应州，并仅恢复带来源标记的宣称。
- `ffpa_resolve_tur_pending_fronts_v1`：仅在和平且非外交博弈承诺参与者时运行；先检查完整所有权，成功优先，否则失败。
- `ffpa_cleanup_tur_frontier_on_tag_change_v1`：关闭活动 JE、清理待结算和临时宣称，不删除完成变量、路线变量或 11 州核心宣称。

BYZ 转换不复制 BYZ 白名单。依赖现有 `ffpa_on_eastern_mediterranean_country_formed` 顺序：先调用 `ffpa_handle_tur_flavor_country_formed_v1` 清理 TUR 临时宣称，再调用 `ffpa_ensure_byzantine_formation_effects` 重建 BYZ 永久宣称。验证最终状态而不是要求中间帧不发生 remove/add。

### 5.5 迁移与接线

新增 `ffpa_ensure_tur_frontier_recovery_v1`，顺序固定：

1. 设置 `ffpa_tur_flavor_initialized_v1`；
2. 确保 11 州核心宣称；
3. 确保活动前线来源宣称；
4. 和平时结算 pending；
5. 只有终局选择变量存在且尚未迁移时，根据路线和完整所有权依顺序推断完成变量，然后设置 `ffpa_tur_frontier_recovery_migrated_v1`；
6. 若 `ffpa_tur_ztr_collapse_cleanup_pending_v1` 存在，清除已登记 T&R 国家级临时变量，但不刷新该一年期限。

把该 ensure 放在 `ffpa_ensure_tur_flavor_v1` 的 TUR 分支顶部，使初始化标记和核心宣称早于路线事件链维护。扩展 `ffpa_handle_tur_flavor_country_formed_v1` 的非 TUR 分支识别条件，使仅残留活动 JE、pending 或临时宣称的损坏存档也进入清理。

**完成检查**

```zsh
rg -n "^ffpa_(ensure_tur_formation_core_claims|ensure_tur_frontier_recovery|ensure_tur_active_front_claims|resolve_tur_pending_fronts|cleanup_tur_frontier_on_tag_change)_v1[[:space:]]*=" common/scripted_effects/ffpa_turkish_flavor_effects.txt
rg -n "^ffpa_(start|complete|fail|withdraw)_tur_front_.*_v1[[:space:]]*=" common/scripted_effects/ffpa_turkish_flavor_effects.txt
```

人工核对所有 remove_claim 分支均同时要求对应来源变量。

## 6. Task 3：新增日志组与八条前线 JE

**修改文件**

- `common/journal_entry_groups/ffpa_turkish_reconstruction_group.txt`

**新增文件**

- `common/journal_entries/ffpa_turkish_frontier_recovery.txt`

### 6.1 日志组

新增 `je_group_ffpa_turkish_frontier_recovery`：

- `context = country`；
- 与 TUR 重建组分离，便于 UI 和所有权审查；
- 不承担调度逻辑。

### 6.2 JE 通用结构

每条 JE：

- 使用地图/军事类现有图标；
- 进入新日志组；
- `complete` 调用对应完整所有权条件；
- 共和国小前线 `timeout = 5475`；其余 `timeout = 7300`；
- `on_complete` 调用对应 complete effect；
- `on_timeout` 再检查完整所有权，成功优先；否则战争或外交博弈中写 pending，和平时调用 fail effect；
- `invalid = { NOT = { c:TUR ?= this } }`；
- `on_invalid` 调用不设置冷却、不触发结果事件的 tag-cleanup 分支；
- `progressbar = no`；
- `status_desc` 显示目标州和期限；
- 默认 pin，确保玩家能看到期限。

不要在 JE `immediate` 中再次授予宣称；宣称只由 start effect 写入，避免旧档重建 JE 时重置来源。

### 6.3 回调竞态

对“完整所有权与 timeout 同日成立”使用以下优先级：

1. `on_timeout` 首先重检完整所有权；
2. 完整则调用 complete effect；
3. 否则才 pending 或 fail。

运行时仍需验证引擎先判断 `complete` 还是 `timeout`，但两条路径最终都必须把完整所有权解释为成功。

**完成检查**

```zsh
rg -n "^je_ffpa_tur_front_.*[[:space:]]*=" common/journal_entries/ffpa_turkish_frontier_recovery.txt
rg -n "timeout = (5475|7300)|on_complete|on_timeout|on_invalid" common/journal_entries/ffpa_turkish_frontier_recovery.txt
```

预期：恰好八个顶层 JE；两个 5475 日、六个 7300 日。

## 7. Task 4：实现决议、会议事件、结果事件与 AI 权重

**修改文件**

- `common/decisions/ffpa_turkish_flavor_decisions.txt`
- `events/ffpa_turkish_flavor_events.txt`

### 7.1 决议

新增 `ffpa_tur_convene_frontier_council`：

- `is_shown`：TUR、至少一个终局选择存在、仍有未完成前线；
- `possible`：`ffpa_tur_frontier_council_ready_v1 = yes`；
- `when_taken`：触发 `ffpa_tur_flavor.60`；
- `ai_chance`：只有 `ffpa_tur_ai_frontier_council_ready_v1` 才为正，否则为 0。

新增 `ffpa_tur_withdraw_frontier_mandate`：

- 只在存在活动前线 JE 时显示；
- 和平且非外交博弈承诺参与者时可用；
- `when_taken` 通过互斥 if/else-if 找到实际 JE，先调用对应 withdraw effect，再移除对应 JE；
- AI chance 固定为 0，AI 依靠超时而不主动撤回。

当前 1.13 安装中没有可用的 `remove_journal_entry` effect。撤回决议因此设置一次性 `ffpa_tur_frontier_withdraw_requested_v1`；唯一活动 JE 随后由 `invalid` 自行结束，并在 `on_invalid` 中执行来源安全清理、五年冷却和撤回事件。

### 7.2 边疆委员会 `.60`

- trigger 再次检查 TUR、和平、无外交博弈和槽位可用，防止决议到事件之间状态变化；
- 八个选项分别由 availability trigger 控制；
- 每个选项调用对应 start effect；
- 提供默认“暂不授权”选项，不产生状态；
- 选项 tooltip 显示州范围、期限和下游建设。

### 7.3 AI 选项权重

- 基础优先级按规格设置；
- 部分拥有目标州和前置地域连续性增加权重；
- 主要目标持有者军力投射高于 TUR 时降低权重，不写绝对禁止；
- 埃及、伊弗里基亚在 AI 不是主要列强时 option `ai_chance = 0`；
- 不遍历全世界，只检查固定目标州当前 owner；
- 不从事件直接发动战争。

### 7.4 结果事件 `.61–.84`

- 每条前线一个成功、一个超时、一个撤回事件；
- 事件只确认结果，不发 modifier、免费军队、恶名或建设；
- trigger 至少要求当前国家仍为 TUR；
- 每个事件只有一个默认确认选项；
- 成功事件说明后续前线/建设解锁；失败和撤回说明五年冷却与未实现宣称清理。

**完成检查**

```zsh
rg -n "^ffpa_tur_(convene_frontier_council|withdraw_frontier_mandate)[[:space:]]*=" common/decisions/ffpa_turkish_flavor_decisions.txt
rg -n "^ffpa_tur_flavor\.(60|6[1-9]|7[0-9]|8[0-4])[[:space:]]*=" events/ffpa_turkish_flavor_events.txt
```

预期：`.60–.84` 共 25 个事件且无重复。

## 8. Task 5：覆盖 Tech & Res 奥斯曼崩溃 JE

**新增文件**

- `common/journal_entries/zzzz_ffpa_techres_ottoman_collapse_override.txt`

**步骤**

1. 使用 `apply_patch` 创建完整上游副本，不用 shell 重定向或 `cat` 写文件。
2. 文件头记录：T&R 名称、metadata ID `tech.res`、版本 `1.6'`、Workshop ID、原始相对路径、SHA-256、覆盖原因和预期差异。
3. 在 `is_shown_when_inactive` 中要求当前 TUR 不是 `ffpa_tur_is_ffpa_managed_v1`。
4. 在 `possible` 的 `c:TUR` 块中加入同一排除条件。
5. 在 `complete` 中加入同一排除条件，防止旧档完成与失效竞态。
6. 把 `invalid` 改为：TUR 不存在，或当前 TUR 由 FFPA 管理。
7. 完整保留上游 `on_invalid`，之后追加：
   - 清除 `ottoman_empire_collapse_var`；
   - 清除 `ottoman_empire_collapse_arab_var`；
   - 清除 `ottoman_empire_collapse_army_var`；
   - 清除 `ottoman_empire_collapse_foreign_var`；
   - 清除三个 aid-taken 变量；
   - 清除从 T&R 事件文件盘点出的国家级 `ottoman_collapse_*` 临时变量；
   - 设置 `ffpa_tur_ztr_collapse_cleanup_pending_v1`，期限一年。
8. 不移除 `ztr_ottoman_collapse_happened` 等全局变量，不改事件文件，不覆盖 scripted button。

**上游临时变量盘点**

在落笔前运行：

```zsh
# `v3_techres_root` 使用 Task 0 已解析的当前安装路径；不要把其值写入仓库。
rg -n "(set|change|remove)_variable" \
  "$v3_techres_root/events/ottoman_empire/ottoman_empire_collapse.txt" \
  "$v3_techres_root/common/journal_entries/ztr_je_turkey.txt"
```

按 country/global/其他国家 scope 分类，只清除 FFPA TUR 自身的崩溃状态和上游已在 `on_invalid` 清理的赞助标记。

**差异验证**

- 用括号深度提取两个 `je_ottoman_empire_collapse` 顶层块；
- 对比前先删除文件头注释；
- 人工确认差异只包含四处 guard 与扩展 `on_invalid`；
- 记录这是唯一新增的有意上游顶层替换。

若 T&R 源文件在 Task 0 后变化，停止并重新比较，不能继续套旧补丁。

## 9. Task 6：本地化、README 与 AGENTS 登记

**修改文件**

- `localization/english/ffpa_turkish_flavor_l_english.yml`
- `localization/simp_chinese/ffpa_turkish_flavor_l_simp_chinese.yml`
- `README.md`
- `AGENTS.md`

### 9.1 本地化

为以下对象提供完全对应的英文和简体中文键：

- 新日志组；
- 八条 JE 的名称、描述、状态和目标提示；
- 两个决议及其描述、可用条件和效果提示；
- `.60–.84` 事件标题、描述、flavor 和确认选项；
- 八个委员会选项和默认取消选项；
- 15/20 年期限、五年冷却、临时宣称清理、战争中待结算的通用 tooltip。

保持两份文件 UTF-8 BOM，不重排已有键，不把 T&R 上游本地化复制进本项目。

### 9.2 README

新增玩家可见说明：

- 11 州成立核心宣称；
- 三条路线的前线范围；
- 一次一条、15/20 年、五年重试；
- 前线不自动完成地区建设；
- FFPA TUR 排除 T&R 旧崩溃日志；
- 旧存档迁移和已排程 T&R 弹窗限制。

### 9.3 AGENTS

在东地中海状态机所有者中登记：

- 新 JE 文件和 T&R 覆盖文件；
- 新决议、事件、trigger/effect 切片和本地化键；
- `je_ottoman_empire_collapse` 加入覆盖表，注明 T&R 版本敏感完整替换；
- 新持久变量、来源标记和事件 ID 为存档 API；
- 新增 TUR 前线专项验收项目；
- 不改变“地区治理不直接授予宣称”的既有边界：治理会议仍不授予宣称，宣称属于此前线状态机。

**本地化检查**

```zsh
xxd -l 3 localization/english/ffpa_turkish_flavor_l_english.yml
xxd -l 3 localization/simp_chinese/ffpa_turkish_flavor_l_simp_chinese.yml
```

两者必须输出 `efbbbf`。提取冒号前键名并排序比较，新增键集合必须完全一致。

## 10. Task 7：静态与最终数据库验证

### 10.1 结构检查

1. `jq empty .metadata/metadata.json`。
2. 对所有修改 `.txt` 做忽略注释与字符串后的花括号平衡检查。
3. 搜索八条 JE、两项决议、25 个事件、trigger/effect、组和本地化引用。
4. 检查 `ffpa_tur_flavor.60–.84` 恰好各定义一次。
5. 检查本项目顶层键重复；只允许已登记覆盖。
6. `git diff --check`。

### 10.2 宣称安全检查

```zsh
rg -n "remove_claim" common events
```

逐处确认：

- TUR 临时清理均由对应 `ffpa_tur_temporary_claim_*_v1` guard 保护；
- 核心宣称没有 cleanup 调用；
- T&R 覆盖没有新增 TUR 之外的 claim 删除；
- BYZ 形成后现有 ensure 会恢复其永久白名单宣称。

### 10.3 调度与性能检查

- `on_country_formed` 仍只有既有东地中海包装 ID；
- 月度 on_action 列表没有新增第二个 TUR 包装；
- 月度 ensure 只访问固定州和活动/pending 前线；
- AI 评分只访问固定前线州 owner，不出现 `every_country`、`every_state_region` 或建筑遍历；
- T&R 覆盖保留上游已有遍历，但本项目没有把它复制到新高频入口。

### 10.4 上游覆盖检查

- Firefall TUR 成立顶层定义未被本项目覆盖；
- `Return State` 和 `Conquer State` 未被本项目定义；
- `je_ottoman_empire_collapse` 与 T&R 源块完成预期差异检查；
- 本项目没有出现外部 Core Balance 的统一战争技术 ID。

### 10.5 工作树检查

```zsh
git diff --check
git status --short --branch
git diff --stat
```

交付时逐项列出本任务新增/修改文件，不把进入任务前的设计文档或用户其他改动冒充为运行时代码改动。

## 11. Task 8：游戏内验证清单

本任务无法从命令行启动游戏时，以下项目明确标记为待实机验证；不得以静态通过代替：

### 11.1 新游戏与成立核心

- 形成只拥有 8/11 核心州的 TUR；
- 检查缺失州获得宣称、已有宣称不重复、Return State 可选；
- 次月 ensure 不重复奖励或制造错误；
- 取得后再次失去核心州，永久宣称重新出现。

### 11.2 三路线

- 分别完成高门、共和国、重建总署终局；
- 核对委员会候选和解锁顺序；
- 确认禁止范围不出现；
- 一条活动或 pending 时无法开启第二条。

### 11.3 生命周期

- 完整收复成功；
- 部分收复后超时；
- 和平主动撤回；
- 到期时处于战争；
- 到期时处于外交博弈；
- 五年冷却到期后重试；
- 来源标记存在时宣称被移除后的恢复；
- 无来源标记的宣称不被清理。

### 11.4 标签和旧档

- TUR→BYZ：最终 BYZ 永久宣称完整，TUR 临时来源标记消失；
- TUR→其他 tag：未实现临时宣称清除，完成变量保留；
- 旧 TUR 完整拥有已解锁前线：只补完成变量，不弹成功事件；
- 旧 TUR 部分拥有：不误判完成、不自动授予远方临时宣称。

### 11.5 T&R

- 新 FFPA TUR 不显示或启动崩溃 JE；
- 旧活动崩溃 JE 在加载后 invalid，不执行领土拆分；
- 一年清理窗口不被月度 ensure 延长；
- 已排程 `.1–.4` 即使残留弹出，也不能恢复 JE 或触发完成；
- 未标记 T&R TUR 的原始日志路径仍可工作。

### 11.6 AI 与地区建设

- AI 在高恶名、负储备、低等级、战争中或已有前线时不启动；
- 高门 AI 不是主要列强时不选择埃及/伊弗里基亚；
- AI 获得宣称后由外交 AI 自主判断战争；
- 前线成功不自动完成地区建设；
- 真实完成对应工程后，鲁米利亚、东方和非洲治理会议仍各最多触发一次。

## 12. 交付格式

完成实施后报告：

- 修改了 TUR 状态机、T&R 覆盖、文档和本地化中的哪些文件；
- 新增的跨模块接口仅限现有 TUR ensure 与 T&R 顶层覆盖，没有调用外部拆分包；
- 新增了哪些存档 API，是否存在迁移；
- 执行了哪些静态、最终数据库和日志验证；
- 哪些结论仍需游戏内验证；
- 当前分支和工作树状态；
- 未经用户明确要求不提交 Git。
