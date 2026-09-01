# TUR 边疆收复与限时宣称机制设计

日期：2026-09-01
状态：设计已确认，尚未实施

## 1. 背景与证据

本项目当前固定运行于 Victoria 3 `1.13.*`、`2050: The Fire Falls` `0.1.1` 与 `[1.13] Tech & Res` `1.6'` 的加载环境。

Firefall 最终数据库中的 TUR 成立定义位于 Workshop `3768192009/common/country_formation/tff_major_formables.txt`。成立要求以下 11 个州中至少 70%，但成立效果只整合已经拥有的州，没有补发宣称：

- `STATE_EASTERN_THRACE`
- `STATE_HUDAVENDIGAR`
- `STATE_AYDIN`
- `STATE_ANKARA`
- `STATE_KONYA`
- `STATE_ADANA`
- `STATE_KASTAMONU`
- `STATE_TRABZON`
- `STATE_ERZURUM`
- `STATE_DIYARBAKIR`
- `STATE_KARS`

本项目的 `je_ffpa_tur_rebuild_anatolia` 后续要求掌握上述 11 州中的 10 州。因成立只要求 70%，玩家可能形成 TUR 后既没有足够领土，也没有历史宣称可用于低恶名的 `Return State` 战争目标，导致重建路线和后续风味链缺少稳定扩张出口。

原版 `Return State` 与 `Conquer State` 仍由最终加载栈拥有。本设计只提供受控宣称，不新增战争目标，也不接管战争、外交博弈或统一战争 AI。

另一个兼容风险来自 Tech & Res 的 `je_ottoman_empire_collapse`。当前顶层定义位于 Workshop `3472248460/common/journal_entries/ztr_je_turkey.txt`：1900 年后，只要 TUR 不是列强、政体不民主且平均生活水平低于 12，日志即可启动；最终完成效果会拆分希腊、保加利亚、亚美尼亚、伊拉克、叙利亚等领土。该历史机制不适合 Firefall 2050 年后重新成立并由本项目管理的 TUR。

## 2. 目标

- 为所有 TUR 路线补齐 Firefall 成立核心区的永久宣称，解除安纳托利亚重建链的领土死锁。
- 在路线终局后提供有限、分阶段、一次只开一条的收复前线。
- 让高门、共和国和重建总署拥有不同的扩张范围与节奏。
- 使用原版 `Return State`，保留战争成本、外交反应、兴趣要求和军事胜负。
- 让前线收复自然衔接现有地区建设和治理会议，而不免费完成建设。
- 对玩家和 AI 使用同一套领土状态机，但给 AI 增加财政、恶名、军力和列强门槛。
- 只对 FFPA 管理的 TUR 排除 Tech & Res 的旧奥斯曼崩溃日志，并为旧存档安全清理活动实例。
- 保持新游戏、旧存档、标签变化、超时、撤回和战争中结算路径均可恢复且幂等。

## 3. 非目标

- 不新增或覆盖战争目标、外交博弈、统一战争、恶名公式或 AI 外交战略。
- 不修改 Firefall 的 TUR 国家定义、成立定义、旗帜或政体视觉。
- 不复制 BYZ 的 45–55 年全面复归战争范围或奖励结构。
- 不向 TUR 提供塞尔维亚—波斯尼亚腹地、阿拉伯半岛、意大利、西地中海、西班牙或马格里布西部的系统宣称。
- 不直接完成 15 项地区建设 JE，不免费生成建筑，也不修改 `ffpa_region_*` 奖励。
- 不禁止沙盒征服。某条路线没有前线宣称，不代表玩家不能通过普通战争取得该地区并使用既有建设内容。
- 不全局关闭 Tech & Res 的历史内容；未被 FFPA 标记的普通 TUR 保留原 `je_ottoman_empire_collapse` 行为。
- 不调用或重新定义外部 Core Balance、Building Pruning、Auto PM Adapter 的对象。

## 4. 采用方案与架构

采用“成立核心宣称 + 路线化边疆委员会 + 独立限时 JE”的方案：

```text
形成或加载 TUR
      │
      ├─ 幂等补齐 11 州成立核心宣称
      │
      ▼
完成安纳托利亚重建与路线终局选择
      │
      ▼
召开边疆委员会
      │
      ▼
选择一条当前可用前线
      │
      ├─ 只向未拥有、未宣称州添加临时宣称
      ├─ 记录逐州宣称来源
      └─ 启动 15/20 年独立 JE
      │
      ▼
使用原版 Return State 或其他沙盒手段取得领土
      │
      ├─ 完整拥有：成功并解锁后续前线
      ├─ 部分拥有：保留领土，期限后清除未实现临时宣称
      └─ 战争中到期：等待和平后结算
      │
      ▼
实际领土满足既有地区建设条件
      │
      ▼
施工完成变量 → 既有 TUR 地区治理会议
```

未采用的替代方案：

- **成立时一次性授予全部旧帝国宣称**：实现简单，但 AI 会同时强烈追逐大量宣称，破坏路线区分并造成连续扩张。
- **自定义统一战争或专属战争目标**：可精确控制范围，但会跨入外部 Core Balance 的统一战争所有权，增加战争定义、AI 和兼容维护成本。
- **纯决议即时授予永久宣称**：缺少期限、失败、清理和重试状态，远方宣称会永久积累。

## 5. 成立核心区永久宣称

`ffpa_ensure_tur_formation_core_claims_v1` 在 country scope 工作，只对当前 TUR 执行。

对第 1 节列出的 11 个 Firefall 成立州逐一判断：

1. TUR 已经完整拥有该州：不添加宣称。
2. TUR 没有完整拥有，但已经有宣称：保留原宣称，不记录来源。
3. TUR 没有完整拥有且没有宣称：添加永久宣称。

该 effect 可重复调用。它在国家成立入口和现有月度 TUR ensure 中到达，因此旧存档会补发，未来再次失去核心州后也会重新获得宣称。核心宣称不使用临时来源标记，不随前线超时、撤回或标签变化清理。

此机制不覆盖 Firefall 的成立顶层定义；上游成立州清单变化时，应重新比较并显式更新这里的白名单。

## 6. 路线、前线与州范围

### 6.1 前线定义

| 技术前线 | 目标州 | 可用路线 | 期限 | 下游建设 |
|---|---|---|---:|---|
| 西部国民誓约 | `STATE_WESTERN_THRACE` | 共和国 | 15 年 | 不延伸至希腊本土 |
| 摩苏尔问题 | `STATE_MOSUL` | 共和国 | 15 年 | 只处理摩苏尔，不等同完整美索不达米亚前线 |
| 鲁米利亚 | `STATE_ALBANIA`、`STATE_MACEDONIA`、`STATE_WESTERN_THRACE`、`STATE_BULGARIA`、`STATE_DOBRUDJA`、`STATE_NORTHERN_THRACE` | 高门、重建总署 | 20 年 | Via Egnatia、色雷斯—多瑙河工程 |
| 爱琴海与塞浦路斯 | `STATE_ATTICA`、`STATE_CRETE`、`STATE_EAST_AEGEAN_ISLANDS`、`STATE_WEST_AEGEAN_ISLANDS`、`STATE_IONIAN_ISLANDS`、`STATE_CYPRUS` | 高门 | 20 年 | 爱琴海工程；塞浦路斯只作为历史目标 |
| 黎凡特 | `STATE_ALEPPO`、`STATE_SYRIA`、`STATE_LEBANON`、`STATE_PALESTINE`、`STATE_TRANSJORDAN` | 高门、重建总署 | 20 年 | 黎凡特工程覆盖前四州 |
| 美索不达米亚 | `STATE_MOSUL`、`STATE_BAGHDAD`、`STATE_DEIR_EZ_ZOR`、`STATE_BASRA` | 高门、重建总署 | 20 年 | 美索不达米亚工程 |
| 埃及 | `STATE_LOWER_EGYPT`、`STATE_MIDDLE_EGYPT`、`STATE_UPPER_EGYPT`、`STATE_SINAI`、`STATE_MATRUH` | 仅高门 | 20 年 | 尼罗河、亚历山大—西奈工程 |
| 伊弗里基亚 | `STATE_LIBYA`、`STATE_TRIPOLI`、`STATE_TUNISIA` | 仅高门 | 20 年 | 伊弗里基亚工程 |

有意排除 `STATE_EGYPTIAN_DESERT`。埃及前线只覆盖现有尼罗河与亚历山大—西奈建设所需地区。

八条前线的技术 slug 固定为：

| 前线 | slug | JE ID |
|---|---|---|
| 西部国民誓约 | `western_pact` | `je_ffpa_tur_front_western_pact` |
| 摩苏尔问题 | `mosul` | `je_ffpa_tur_front_mosul` |
| 鲁米利亚 | `rumelia` | `je_ffpa_tur_front_rumelia` |
| 爱琴海与塞浦路斯 | `aegean_cyprus` | `je_ffpa_tur_front_aegean_cyprus` |
| 黎凡特 | `levant` | `je_ffpa_tur_front_levant` |
| 美索不达米亚 | `mesopotamia` | `je_ffpa_tur_front_mesopotamia` |
| 埃及 | `egypt` | `je_ffpa_tur_front_egypt` |
| 伊弗里基亚 | `ifriqiya` | `je_ffpa_tur_front_ifriqiya` |

后文 `<front>` 一律替换为本表 slug。`<state>` 一律使用州 ID 去掉 `STATE_` 后的小写形式，例如 `STATE_WESTERN_THRACE` 对应 `ffpa_tur_temporary_claim_western_thrace_v1`。实现不得另建第二套同义 slug。

### 6.2 路线解锁顺序

边疆委员会直到路线终局选择变量存在后才开放：

- 高门：`ffpa_tur_porte_charter_choice_v1`；
- 共和国：`ffpa_tur_republic_settlement_choice_v1`；
- 重建总署：`ffpa_tur_directorate_settlement_choice_v1`。

具体顺序：

- **共和国**：西部国民誓约与摩苏尔问题同时进入候选，但一次只能启动一条；两者均完成后结束系统支持的扩张。
- **重建总署**：先开放鲁米利亚和黎凡特；黎凡特完成后开放美索不达米亚；不开放爱琴海、埃及或非洲前线。
- **高门**：先开放鲁米利亚和黎凡特；鲁米利亚完成后开放爱琴海；黎凡特完成后开放美索不达米亚；完成黎凡特并再完成鲁米利亚或美索不达米亚之一后开放埃及；埃及完成后开放伊弗里基亚。

路线由既有 `ffpa_tur_state_project_v1` 固定。后续政体变化只影响既有路线事件的暂停条件，不改写路线，也不转换已完成前线。

## 7. 前线状态机

每条前线使用独立 JE，生命周期为：

```text
不可用 → 可用 → 运行中 → 成功
                    ├────→ 超时失败 → 五年冷却 → 可重试
                    ├────→ 主动撤回 → 五年冷却 → 可重试
                    ├────→ 到期但处于战争/外交博弈 → 待结算 → 成功或失败
                    └────→ 不再是 TUR → 标签清理
```

### 7.1 启动

`ffpa_tur_convene_frontier_council` 决议只有在以下条件均成立时可用：

- 当前国家是 TUR；
- 对应路线终局选择已完成；
- 和平且不是外交博弈的承诺参与者；
- 没有任何活动前线 JE；
- 没有任何待结算前线；
- 至少有一条满足解锁、未完成、未冷却且仍有未拥有目标州的前线。

会议事件只显示实际可用选项。选择前线时，对每个目标州执行：

- 已完整拥有：不处理；
- 已有 TUR 宣称：保留，不设置 FFPA 来源标记；
- 未拥有且无宣称：添加宣称，并设置 `ffpa_tur_temporary_claim_<state>_v1` 来源标记。

随后添加对应 JE，期限从玩家确认前线的当天开始。

### 7.2 一次一条前线

并发限制不使用持久计数器。`ffpa_tur_frontier_slot_available_v1` 直接检查八条实际 JE 和八个待结算变量；只要任意一个存在，就禁止启动下一条前线。这样超时、标签变化、旧档迁移或异常清理不会造成计数漂移。

### 7.3 成功

成功要求 TUR 完整拥有该前线列出的全部州。成功时：

- 设置 `ffpa_tur_front_<front>_complete_v1`；
- 清除该前线的临时宣称来源标记；
- 触发路线化叙事结果事件；
- 立即刷新可用前线查询；
- 不发永久国家 modifier，不直接完成地区建设。

已经完成的前线是永久历史状态。以后再次失去该地区不会重开同一前线；正常的近期失地或其他游戏机制负责后续宣称。

### 7.4 超时、撤回与战争中结算

期限届满且 TUR 处于和平、未参与外交博弈时：

- 保留已经取得的州；
- 只移除仍未拥有、当前仍有 TUR 宣称、且存在 FFPA 来源标记的宣称；
- 清除来源标记；
- 设置该前线 5 年重试冷却；
- 发送失败结果事件。

`ffpa_tur_withdraw_frontier_mandate` 决议只在和平且存在活动前线时可用，执行同样的清理和 5 年冷却。

若期限届满时 TUR 正在战争或作为承诺参与者进入外交博弈，JE 结束但写入对应 `ffpa_tur_front_<front>_resolution_pending_v1`。待结算状态继续占用唯一前线槽，并保留临时宣称。现有月度 TUR ensure 只做一次轻量和平检查；恢复和平后，完整拥有则成功，否则按超时失败清理。

### 7.5 宣称来源限制

Victoria 3 的宣称对象不保存“由哪个 Mod 或哪个事件授予”的来源。逐州变量只能证明 FFPA 曾在该州没有 TUR 宣称时添加过宣称，无法识别活动期间另一系统对同一州再次授予的同质宣称。

因此清理遵守最小破坏原则：

- 没有 FFPA 来源标记的宣称永不移除；
- 有来源标记但州已拥有时只清标记；
- 有来源标记且州未拥有时才移除宣称；
- 前线活动期间，若带来源标记的宣称被移除，ensure 可以恢复；启动前已有的无标记宣称消失时不恢复。

这是当前引擎接口下风险最低的可实现语义。

### 7.6 标签变化

TUR 形成其他 tag 时，现有 `ffpa_handle_tur_flavor_country_formed_v1` 扩展调用前线清理 effect：

- 当前 1.13 没有 `remove_journal_entry` effect；活动 JE 通过“不再是 TUR”的 `invalid` 条件自行结束，标签形成入口同时清理待结算状态；
- 对未拥有州清除 FFPA 临时宣称；
- 保留前线完成变量、路线变量和历史选择变量；
- 不清除 11 州成立核心宣称。

若新 tag 是 BYZ，属于 BYZ 永久复归宣称白名单的州保留宣称，只移除 TUR 临时来源标记；白名单外的未实现 TUR 临时宣称清除。这样不会让 TUR 清理覆盖 BYZ 成立链应保留的宣称。

## 8. 玩家体验与奖励

- 边疆委员会选项显示州范围、15/20 年期限和对应地区建设。
- 活动 JE 显示目标州所有权清单和剩余期限，不增加数值进度条。
- 成功、失败和主动撤回均有明确结果文本。
- 前线启动不发免费军队、军队增益、恶名减免或永久国家修正。
- 成功的奖励是领土、完成状态、后续前线和已有建设内容；避免与 `ffpa_region_*` 物理工程奖励及三场治理会议重复堆叠。

前线与建设保持单向松耦合：前线不读取地区 JE 内部状态，地区 JE 也不依赖前线变量。实际取得领土后，现有 `possible` 所有权条件自然允许施工。地区建设仍通过既有完成变量被以下稳定查询消费：

- `ffpa_tur_rumelian_settlement_ready_v1`：Via Egnatia、多瑙河、爱琴海三项中的两项；
- `ffpa_tur_eastern_settlement_ready_v1`：黎凡特、美索不达米亚、亚历山大—西奈、尼罗河四项中的两项；
- `ffpa_tur_african_settlement_ready_v1`：伊弗里基亚、毛里塔尼亚、尼罗河三项中的两项。

该映射使重建总署通过黎凡特和美索不达米亚触发东方治理，高门通过尼罗河和伊弗里基亚触发非洲治理。共和国没有系统支持的帝国地区前线，但通过沙盒战争取得完整地区后仍可使用现有建设与治理内容。

## 9. AI 行为

本系统不直接命令 AI 宣战。AI 只决定是否召开边疆委员会以及选择哪条前线；宣称产生后继续由最终数据库中的原版/Firefall 外交 AI 评估 `Return State`。

AI 召开会议必须满足玩家的全部启动条件，并额外满足：

- 恶名低于 `infamy_threshold:infamous`；
- `gold_reserves > 0`；
- 国家等级至少为 `rank_value:minor_power`；
- 不在前线重试冷却中。

选项使用权重而不是绝对脚本化宣战：

- 已经拥有部分目标州：提高权重；
- 目标与 TUR 现有领土接壤，或顺接上一条已完成前线：提高权重；
- 主要目标持有者的军力投射明显高于 TUR：降低权重，但不形成永久禁令；
- 共和国优先西色雷斯，其次摩苏尔；
- 重建总署优先黎凡特或鲁米利亚，之后才是美索不达米亚；
- 高门优先鲁米利亚、黎凡特，再考虑爱琴海和美索不达米亚；
- 高门的埃及与伊弗里基亚额外要求至少为 `rank_value:major_power`。

AI 评分只在低频决议评估和会议事件中运行，不加入全世界州或建筑的月度遍历。

## 10. Tech & Res 奥斯曼崩溃兼容

### 10.1 标记和识别

新增 `ffpa_tur_flavor_initialized_v1` 作为稳定存档标记，由以下入口幂等设置：

- 新 TUR 的 `on_country_formed` 包装 effect；
- 现有 `ffpa_ensure_tur_flavor_v1`；
- 旧存档月度迁移入口。

为避免旧档第一次 ensure 之前出现一帧竞态，`ffpa_tur_is_ffpa_managed_v1` 还把既有路线变量、TUR 重建/路线 JE 和明确的 TUR 风味完成变量作为辅助证据。辅助证据只用于识别已有 FFPA 状态，不改写路线。

### 10.2 覆盖方式

新增一个完整同名覆盖 `je_ottoman_empire_collapse`，来源固定记录为：

- Mod：`[1.13] Tech & Res`；
- metadata ID：`tech.res`；
- 本地版本：`1.6'`；
- 原始文件：`common/journal_entries/ztr_je_turkey.txt`。

覆盖保留当前 T&R 的图标、日志组、涉事国家、按钮、月度/年度效果、完成、失败、进度条和非 FFPA 路径，只做以下差异：

- `is_shown_when_inactive` 和 `possible` 排除 `ffpa_tur_is_ffpa_managed_v1`；
- `complete` 也排除 FFPA TUR，防止完成与失效在同一帧竞争；
- `invalid` 在原“没有 TUR”之外，增加“当前 TUR 由 FFPA 管理”；
- `on_invalid` 保留上游清理，并额外清除 TUR 的主崩溃计数、三个分项计数、援助接受状态和已经建立的事件临时状态；
- 旧活动日志失效时设置一年期 `ffpa_tur_ztr_collapse_cleanup_pending_v1`；现有月度 TUR ensure 在该窗口内重复清除上述国家级临时状态，吸收已经排程事件可能产生的一次性回写；
- 不删除 T&R 的全局历史变量，也不改写未标记 TUR 的行为。

这属于版本敏感的完整顶层替换。文件名前缀只用于项目内排序，真正生效依赖 T&R 在本项目之前加载。每次 T&R 更新必须重新比较整个顶层对象，而不能只确认新增 guard 仍存在。

### 10.3 旧活动日志

旧存档中已经活动的 T&R 日志在识别 FFPA TUR 后走 `on_invalid`：

- 不进入 `on_complete`，因此不拆分领土；
- 清理日志计数、TUR 援助状态和其他国家的赞助标记；
- 在一年清理窗口内移除残留事件重新写入的国家级崩溃临时变量；
- 不授予 T&R 成功或失败奖励。

T&R 已经排程的 `.1`–`.4` 个别事件使用空或独立 trigger，可能在迁移后最多 90 天内再显示一次。已失效的 JE 不再执行年度推进或领土拆分。为消除这些无害残留弹窗而完整覆盖 T&R 事件文件，会显著扩大覆盖面，因此有意不做。

## 11. 存档接口

以下新增对象一经实施即视为存档 API：

- `ffpa_tur_flavor_initialized_v1`；
- `ffpa_tur_frontier_recovery_migrated_v1`；
- 一年期 `ffpa_tur_ztr_collapse_cleanup_pending_v1`；
- 八个 `ffpa_tur_front_<front>_complete_v1`；
- 八个 `ffpa_tur_front_<front>_retry_cooldown_v1`；
- 八个 `ffpa_tur_front_<front>_resolution_pending_v1`；
- 所有 `ffpa_tur_temporary_claim_<state>_v1` 来源标记；
- 八条 `je_ffpa_tur_front_*`；
- 新增决议和 `ffpa_tur_flavor` 事件 ID。

前线名称或本地化以后可以调整，但不得静默改变上述技术对象含义。若州范围或状态语义需要变化，应创建新版本键并在 ensure 中迁移。

## 12. 旧存档迁移

`ffpa_ensure_tur_frontier_recovery_v1` 挂入现有 `ffpa_ensure_tur_flavor_v1`，不增加第二个全局调度器。执行顺序固定为：

1. 设置 FFPA TUR 初始化标记。
2. 补齐 11 个成立核心州宣称。
3. 若尚无 `ffpa_tur_frontier_recovery_migrated_v1`，根据既有路线、终局选择、前置顺序和完整领土所有权推断已经完成的前线。
4. 推断完成状态时不触发成功事件、不发奖励、不设置冷却。
5. 若存在待结算前线且已经和平，执行一次成功/失败结算。
6. 清理不可能同时存在的重复 JE 或过期临时标记，并设置迁移完成变量。

迁移不会：

- 启动新前线；
- 为远方前线自动添加临时宣称；
- 将部分控制误判为完整成功；
- 根据当前政体重写 `ffpa_tur_state_project_v1`；
- 删除没有 FFPA 来源标记的既有宣称。

## 13. 文件与模块边界

预计新增运行时文件：

- `common/journal_entries/ffpa_turkish_frontier_recovery.txt`：八条 TUR 前线 JE；
- `common/journal_entries/zzzz_ffpa_techres_ottoman_collapse_override.txt`：T&R 顶层覆盖。

预计修改：

- `common/journal_entry_groups/ffpa_turkish_reconstruction_group.txt`：增加 TUR 边疆日志组；
- `common/decisions/ffpa_turkish_flavor_decisions.txt`：委员会和撤回决议；
- `common/scripted_triggers/ffpa_turkish_flavor_triggers.txt`：路线、前线、槽位、AI 与 FFPA 管理识别；
- `common/scripted_effects/ffpa_turkish_flavor_effects.txt`：核心宣称、临时宣称、启动、结算、清理和迁移；
- `events/ffpa_turkish_flavor_events.txt`：会议与结果事件，使用现有 `ffpa_tur_flavor` namespace 的已验证空闲 ID，不重编号旧事件；
- `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt`：仅在现有 TUR 包装入口确实无法到达所需阶段时做最小接线；默认复用现有 country formed 和月度 ensure；
- 两份 `ffpa_turkish_flavor_l_*.yml`：完整的英文与简体中文本地化；
- `README.md`、`AGENTS.md`：行为、覆盖、存档 API 和验收登记。

不修改 `.metadata/metadata.json`：本项目已硬依赖 Tech & Res，功能没有增加新的发布依赖，也不需要提升版本号。

## 14. 验证计划

### 14.1 静态验证

- `jq empty .metadata/metadata.json`；
- 修改脚本的花括号、字符串、注释和顶层结构检查；
- 八条 JE、决议、trigger、effect、事件和本地化引用闭合；
- 本设计列出的全部州 ID 能在最终加载栈解析；
- 英文与简体中文新增键集合一致，文件保持 UTF-8 BOM；
- 同一 Mod 内无意外重复顶层键；`je_ottoman_empire_collapse` 是唯一新增的有意上游替换；
- `git diff --check` 无新增空白错误；
- 最终 `git status --short --branch` 区分本任务改动与用户已有改动。

### 14.2 最终数据库验证

- 比较原版、Firefall、Tech & Res 和本项目最终 TUR 成立定义；确认 Firefall 的 11 州与 70% 门槛未被覆盖；
- 比较原版 `Return State`、`Conquer State` 与所有后加载定义；确认本项目没有替换战争目标；
- 对 T&R `je_ottoman_empire_collapse` 做完整顶层差异，除 FFPA guard 和失效清理外保持上游语义；
- 检查本项目没有引用外部 Core Balance 的统一战争对象。

### 14.3 玩家状态机验证

- 形成只拥有 8/11 核心州的 TUR：缺失核心州获得永久宣称，安纳托利亚重建不再因无宣称失去扩张出口；
- 已拥有或已有其他来源宣称的核心州不重复处理；
- 三条路线的候选前线、解锁顺序和禁止范围正确；
- 一条前线活动或待结算时不能启动第二条；
- 启动只标记本机制实际添加的宣称；
- 完整成功、部分超时、主动撤回、五年重试分别正确；
- 到期时处于战争/外交博弈会等待和平，且不会提前开放下一槽位；
- TUR→BYZ 保留 BYZ 白名单宣称，TUR→其他 tag 清理未实现临时宣称；
- 前线成功不会自动完成建设；完成真实工程后，既有治理会议只触发一次。

### 14.4 AI 验证

- AI 自动获得缺失成立核心宣称；
- 高恶名、负储备、战争中、低于次要列强、已有前线或处于冷却时不启动；
- 普通前线按路线和邻接权重选择；
- 高门不是主要列强时不启动埃及或伊弗里基亚；
- 宣称出现后由原外交 AI 决定是否发动 Return State，不出现 FFPA 直接宣战调用；
- 长期观察中无并发前线和月度全世界遍历性能问题。

### 14.5 Tech & Res 兼容验证

- 新 FFPA TUR 不显示、不启动 `je_ottoman_empire_collapse`；
- 人工构造的未标记普通 T&R TUR 保留原日志行为；
- 旧档活动日志在加载后失效并清理计数，不执行领土拆分；
- 已经排程的残留事件即使出现，也不能重新激活日志或触发 `on_complete`；
- T&R 的按钮、其他国家涉事逻辑和非 FFPA 历史内容不受影响。

### 14.6 运行时证据

无法仅凭静态文件证明以下内容，必须在游戏中确认：

1. 覆盖文件被最终加载且顶层对象成功解析；
2. country formed、月度 ensure、决议、JE 和事件调度实际到达；
3. `has_claim_by`、`add_claim`、`remove_claim` 在实际 state-region/country scope 生效；
4. 超时与 `invalid` 的回调顺序符合待结算和 T&R 竞争保护设计；
5. 宣称确实启用最终数据库中的 Return State，且没有被后加载内容移除；
6. AI 决议评估和目标偏好在长期运行中符合限制。

运行时检查 Victoria 3 用户目录下最新与轮转的 `debug*.log`、`error*.log`、`game*.log`，按稳定技术 ID 关联脚本位置、触发时间和调用链。交付时分别报告已静态确认、最终数据库确认、已有日志确认和仍需游戏内验证的结论。

## 15. 成功标准

实现完成后，玩家形成 TUR 即使只控制成立所需的 70% 核心州，也拥有明确而有限的收复路径；三条路线都能扩张，但不会共享同一套旧帝国全图宣称。前线宣称具有期限、来源保护、并发上限和重试规则，成功领土能够自然接入已有地区建设。FFPA 管理的 2050 TUR 不再被 Tech & Res 的旧奥斯曼崩溃日志拆分，而非 FFPA 的 T&R 历史内容保持原状。
