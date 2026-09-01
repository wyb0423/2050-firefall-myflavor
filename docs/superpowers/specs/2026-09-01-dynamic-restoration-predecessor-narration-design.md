# TUR / BYZ 复归成功事件动态前所有者叙事设计

## 1. 背景

FFPA 当前以两套长期领土状态机表达东地中海国家的有限历史复归：

- TUR 的八条路线限定边疆前线；
- BYZ 的七条分区复归战争。

两套状态机都只在 country scope 检查是否完整拥有目标 state region。成功时直接设置既有完成变量并触发结果事件，没有保存战争对象、目标州前所有者或领土转移来源。因此，现有成功文本只能按固定地理范围叙述，无法可靠点名实际失去最后一处目标领土的国家。

Firefall 开局中的许多地区最初由部落、城邦或州级残存政权占据，但复归战争可能在数十年后才完成。届时目标领土通常已经属于发展成熟的国家，不能继续假定复归对象仍是开局时的港邦、部落议会或松散政权。地区建设也发生在领土已经纳入 TUR/BYZ 国家机器之后，不应被描述为首次创造可治理的政治秩序。

本设计增加一个只服务于叙事的所有者快照接口，使成功事件能够点名“使日志达成的最后一个关键州的直接前所有者”，同时重新规定地区建设与治理会议的叙事边界。

## 2. 已确认决策

1. 成功事件点名使 JE 达成的最后一个目标 state 实例的直接前所有者。
2. 动态国名只用于成功事件；到期与主动撤回仍按地区整体叙述。
3. 领土取得方式统一使用中性表述，不声称一定经过战争、征服或击败。
4. 动态国名只进入事件正文，不进入标题、引语或选项。
5. 前所有者无效或无法可靠恢复时使用无国名降级文本。
6. 地区建设与治理会议以“领土已经处于本国统治下”为固定前提，不把当地描述为仍待组织的独立港邦、部落或松散政权。
7. 不改现有 JE、事件 ID、完成变量、宣称来源或前线解锁顺序。

## 3. 目标

- 在 TUR `.61–68` 与 BYZ `.40–46` 共十五个成功事件中，可靠引用最后一个关键州的直接前所有者。
- 正确处理一条前线由多个国家分割、目标州在第三国之间转手、同一 state region 存在多个 state 实例等情况。
- 允许 TUR 与 BYZ 同时追踪相同或重叠地理范围，且 BYZ 的两条并行复归战争互不覆盖状态。
- 为无主地、和平转让、吞并、殖民完成、旧存档与前所有者消失提供不伪造事实的降级文本。
- 把地区建设和后续治理文本从“首次使地区可治理”调整为“接管后统一行政、交通、产业标准与区域分工”。
- 保持 on_action 轻量，不为叙事功能增加月度世界扫描。

## 4. 非目标

- 不识别领土转移究竟来自战争目标、外交让步、吞并、殖民或其他 Mod 效果。
- 不保存或显示一条前线涉及的全部失地国家列表。
- 不点名到期或撤回时仍控制未完成目标的国家。
- 不改变战争目标、宣称、恶名、外交 AI、JE 完成条件、奖励或失败惩罚。
- 不把 Firefall 开局政治形态静态投射到几十年后的复归结果。
- 不创建通用的全球领土历史数据库。

## 5. 方案比较

### 5.1 纯通用本地化

只把十五个成功事件改写为彼此不同的固定地区文本。

优点是零运行时状态、零迁移风险。缺点是无法满足动态点名实际失地国家的目标。

### 5.2 前线启动时保存主要占有国

在 JE 启动时选择拥有最多目标地区的国家，并在最终成功事件中引用。

实现较简单，能形成连续的“宣战对象”叙事。但 TUR 前线为 15–20 年，BYZ 复归战争为 45–55 年，期间可能发生标签形成、吞并、州转让和第三国战争。启动时的主要占有国可能与最终失去领土的国家无关。

### 5.3 持续追踪 state 直接前所有者（采用）

JE 启动后为每个实际 state 实例保存 owner 快照。state 每次易手时先读取旧快照，再更新为当前 owner；当当前 owner 成为对应 TUR/BYZ 时，把旧快照写入该前线的国家级叙事变量。

最近一次写入必然来自最后转入 TUR/BYZ 的目标 state。若该转移使 JE 完成，该国家就是“最后一个关键州的直接前所有者”。该语义不依赖转移方式，也不要求一个国家曾控制整条前线。

## 6. State 实例与 State Region

现有 JE 使用 `owns_entire_state_region` 判断完整所有权，但 `on_state_owner_change` 的 ROOT 是实际 state 实例。同一 state region 可能被多个国家分割，因此追踪必须以 state 实例为单位：

1. JE 启动时，仅对其目标 state region 中当前存在的全部 state 实例建立追踪。
2. 每个 state 实例保存自己的前线专属 owner 快照。
3. `on_state_created` 在目标 state region 新产生 state 实例时补建追踪。
4. JE 仍继续使用原有 state-region 完成条件；叙事接口不参与完成判断。

这样，最后一个分割部分转入 TUR/BYZ 时也能获得正确的直接前所有者。

## 7. 持久状态

### 7.1 州级变量

每条前线在相关 state 实例上使用两类前线专属变量：

- `ffpa_<country>_<front>_owner_tracking_v1`：证明该 state 正由指定前线追踪；
- `ffpa_<country>_<front>_owner_snapshot_v1`：保存最近一次已知 country owner scope。

追踪标记与 owner 快照分开，原因是 state 可能暂时无 owner。无主 state 仍需保留追踪标记，但不得伪造前所有者。

变量必须按前线隔离。不得让 TUR、BYZ 或两条 BYZ 并行复归战争共享同一个可被清理的州级 owner 快照。

### 7.2 国家级变量

每条前线在对应 TUR/BYZ country scope 保存：

- `ffpa_<country>_<front>_completion_predecessor_v1`：最近一个转入本国的目标 state 的直接前所有者 country scope；
- `ffpa_<country>_<front>_completion_predecessor_ready_v1`：证明变量由当前前线运行期内的有效 state 转移写入。

十五条成功事件各读自己的变量，不使用“最近战争对手”或全局共享变量。

这些变量都是新增存档接口，含义固定为“当前版本前线运行期间，最近一个转入对应国家的目标 state 的直接前所有者”，不得以后静默改为主要敌国或开战对象。

## 8. 调度与数据流

### 8.1 前线启动

TUR 的八个 `ffpa_start_tur_front_*_v1` effect 与 BYZ 七个 JE 的 `immediate` 入口调用各自的追踪初始化 effect：

1. 清理该前线可能遗留的旧国家级 predecessor 变量；
2. 遍历目标 state region 中当前存在的 state 实例；
3. 设置前线专属 tracking 标记；
4. state 当前有 owner 时，把 owner 保存为 snapshot；无 owner 时保持 snapshot 为空。

初始化只在前线启动或旧档迁移时执行，不挂入普通月度路径。

### 8.2 州所有权变化

在现有共享接缝 `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt` 的 `on_state_owner_change` 列表中增加唯一包装入口。ROOT 仍为发生变化的 state。

包装入口只处理带至少一个 FFPA owner-tracking 标记的 state：

1. 对每个活动追踪标记分别读取该前线 snapshot；
2. 若当前 owner 是该前线对应的 TUR/BYZ、旧 snapshot 是另一有效国家，则把旧 snapshot 写入对应国家级 predecessor；
3. 若旧 snapshot 无效、为空或等于当前 owner，不写 predecessor；
4. 清除旧 snapshot；
5. 当前 state 有 owner 时，把当前 owner 写为新 snapshot。

state 在两个第三国之间易手时只执行第 4–5 步。以后若 TUR/BYZ 从新的占有国手中取得该 state，保存的是直接前所有者而不是前线启动时的国家。

### 8.3 新 state 实例

复用现有 `on_state_created` 接缝。只有新 state 所属 state region 位于活动 TUR/BYZ 前线中时，才添加对应 tracking 标记和当前 owner snapshot。

检查只直接访问唯一的 `c:TUR`、`c:BYZ` 和相关活动 JE，不遍历世界国家。

### 8.4 JE 完成与成功事件

原有完成变量和永久奖励顺序不变。成功结果事件从同帧立即弹出改为固定延迟 1 天：

1. state 转移；
2. `on_state_owner_change` 保存 predecessor；
3. JE 完成并设置既有完成变量；
4. 延迟结果事件读取 predecessor。

延迟用于避免 owner-change on_action 与 JE 完成在同一帧的未知执行顺序。实际时序仍需游戏内日志证明。

## 9. 本地化规则

### 9.1 动态国名版本

仅当以下条件同时成立时显示：

- 对应 `completion_predecessor_ready_v1` 存在；
- predecessor 变量持有有效 country scope；
- predecessor 不是当前 ROOT country。

推荐基础句式：

> 随着最后一处目标领土从 `[前所有者]` 手中转入 `[ROOT 国家]` 统治，……

英文对应使用中性 `passed from [predecessor] into [ROOT] rule`、`was transferred from` 或 `came under`，不使用 `conquered`、`defeated`、`wrested in war` 等未经脚本证明的词。

动态国名使用 country scope 的当前玩家可见名称。系统不尝试保存一段历史字符串；若对方在弹窗前形成新 tag，显示 scope 当前名称属于允许的表现。

### 9.2 无国名降级版本

以下情况使用无国名文本：

- 前所有者在领土转移中被彻底吞并，scope 已无效；
- state 此前无主；
- 旧存档迁移时已经拥有最后目标州，无法恢复转移历史；
- 其他 Mod 以未触发可靠快照的路径直接完成领土变化；
- snapshot 异常等于当前 TUR/BYZ。

推荐基础句式：

> 随着最后一处目标领土纳入 `[ROOT 国家]` 统治，……

降级文本必须是完整、自然的结果叙事，不能出现空括号、缺失旗帜或技术 ID。

### 9.3 不点名的位置

- 事件标题；
- flavor 引语；
- 成功选项；
- 前线 JE 名称、原因与状态；
- 到期与撤回事件；
- 地区建设 JE 与治理会议。

这样可避免把单一前所有者误写成整条疆界的唯一敌人。

## 10. 地区建设与治理会议文本边界

地区建设 JE 与 TUR 的鲁米利亚、东方、非洲治理会议发生时，目标州已经处于本国统治下。文本遵守以下规则：

- 不写“使该地变得可以治理”；
- 不默认当地仍有独立港邦、部落议会、州级残存政权或其他开局实体；
- 可描写地方官署、企业、市政机构、军政机关、社会集团和既有行政传统，但它们是本国统治下的利益相关者；
- 建设行为定位为统一标准、修复或扩充既有网络、提高国家机器的日常覆盖能力，以及确定地区在全国财政、代表、交通与产业体系中的位置；
- 不在建设完成时重新叙述领土征服，不重复动态前所有者逻辑。

示例：

旧方向：

> 新铁路和港口已经使安纳托利亚能够治理鲁米利亚。

采用方向：

> 鲁米利亚已经处于土耳其行政之下；新铁路和港口如今把它的城市、税务机关与生产网络更紧密地接入安纳托利亚。接下来的问题不再是谁拥有这片土地，而是谁任命官员、谁代表各省，以及哪一种法律协调这些走廊。

## 11. 并发与重叠疆界

### 11.1 BYZ 双前线

BYZ 最多同时推进两条复归战争。每条使用自己的 state tracking、snapshot 与 country predecessor。完成或失败一条前线时，只清理该前线变量，不影响另一条。

### 11.2 TUR 与 BYZ 同时存在

TUR 与 BYZ 可能同时追踪同一个实际 state。state 上可以同时存在一组 TUR 和一组 BYZ 前线变量。所有权变化包装入口依次更新两组快照：

- state 转入 BYZ 时，只写 BYZ predecessor；TUR 快照更新为 BYZ；
- state 以后转入 TUR 时，TUR predecessor 因而正确保存 BYZ；
- 任一前线结束只清理自己的变量。

### 11.3 同日多州转移

一次和平协议可能同日转移多个目标 state。最后一次由引擎处理、并使 JE 成立的目标 state 所保存的前所有者成为结果事件对象。设计不保证同日多个 state 的内部处理顺序，但无论顺序如何，文本都只声称该国是“最后一处目标领土”的直接前所有者，不声称其为整场战争的唯一对手。

## 12. 清理路径

每条前线提供单一幂等清理 effect，移除：

- 目标 state 上该前线的 tracking 标记；
- 目标 state 上该前线的 owner snapshot；
- country scope 上该前线的临时 predecessor 与 ready 标记。

调用入口：

- 成功结果事件关闭后；
- 到期结算后；
- TUR 主动撤回后；
- JE invalid；
- TUR/BYZ 形成其他 tag 或对应国家不再存在；
- 旧存档迁移发现 predecessor 状态存在但对应 JE、待结算状态和结果事件均不存在。

成功完成变量、路线变量、重试冷却、永久 modifier 和已落实领土不属于本清理 effect。

## 13. 旧存档迁移

活动 JE 没有 tracking 标记时，版本化 ensure 只执行一次：

1. 按目标 state region 找出当前 state 实例；
2. 为其设置 tracking；
3. 当前有 owner 时保存当前 owner snapshot；
4. 不推断迁移前已经发生的州转移或战争对象；
5. 设置本功能专属迁移完成变量。

若旧档在加载时已经满足 JE 完成条件，现有 JE 可能在快照初始化前完成。该路径允许使用无国名降级文本，不通过当前外交关系或最近战争变量猜测历史。

新档初始化、旧档补发和普通 state owner change 必须分别验证。

## 14. 文件与模块所有权

预计只修改东地中海“日志、迁移与风味状态机”及其共享接缝：

- `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt`：登记唯一的州 owner-change / state-created 包装入口；
- `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt`：BYZ 七条复归的追踪、记录与清理 effect；
- `common/scripted_effects/ffpa_turkish_flavor_effects.txt`：TUR 八条前线的追踪、记录与清理 effect；
- `common/journal_entries/ffpa_byzantine_restoration_campaigns.txt`：BYZ 初始化、完成延迟与 invalid 清理；
- `common/journal_entries/ffpa_turkish_frontier_recovery.txt`：TUR 完成/失败接缝保持现有状态语义；
- `events/ffpa_eastern_mediterranean_events.txt`：BYZ 七个成功事件的条件描述与结果后清理；
- `events/ffpa_turkish_flavor_events.txt`：TUR 八个成功事件的条件描述与结果后清理；
- `localization/english/ffpa_l_english.yml` 与 `localization/simp_chinese/ffpa_l_simp_chinese.yml`：BYZ named/fallback 正文、地区建设及共享治理文本；
- `localization/english/ffpa_turkish_flavor_l_english.yml` 与 `localization/simp_chinese/ffpa_turkish_flavor_l_simp_chinese.yml`：TUR named/fallback 正文与三场地区治理会议文本；
- `AGENTS.md`：登记新增变量、on_action 接缝使用和存档接口；
- `README.md`：不修改；动态引用前所有者属于事件表现细节，不改变玩家可操作规则。

不修改 metadata、国家定义、战争目标、宣称范围、地区奖励或外部拆分包。

## 15. 性能

- `on_state_owner_change` 入口首先检查前线专属 tracking 标记，没有标记的世界州不进入深层逻辑。
- JE 启动时的 state 遍历只执行一次，且限定在该前线目标 state region。
- `on_state_created` 只直接检查 TUR/BYZ 唯一 tag 的相关活动 JE。
- 不增加月度全世界州、建筑、人口或国家遍历。
- 旧档迁移只运行到本功能版本变量设置完成。

## 16. 验证标准

### 16.1 静态验证

- 新变量均使用唯一 `ffpa_` 前缀与 `_v1` 版本后缀；
- 十五条前线的 state tracking、snapshot、country predecessor 和清理对象一一对应；
- 英文和简体中文键集合一致，文件保持 UTF-8 BOM；
- named 文本仅在 predecessor country scope 有效且不是 ROOT 时显示；
- fallback 文本不包含未解析 scope；
- 现有事件 ID、JE ID、完成变量、重试变量和宣称变量不变；
- `git diff --check` 无新增空白错误。

### 16.2 单国与多国

- 单一国家拥有全部目标：最后一块转移后点名该国；
- 多个国家分割目标：点名最后一块的直接前所有者，不声称其拥有整条疆界；
- 目标 state 在两个第三国间易手后被 TUR/BYZ 取得：点名第二个第三国；
- 同日从多个国家取得多个 state：显示引擎最后处理且使 JE 完成的 state 前所有者，文本语义仍成立。

### 16.3 转移方式

- 战争割让、外交让步、吞并和附庸整合均使用中性“转入统治”文本；
- state 此前无 owner 时使用 fallback；
- 前所有者被彻底吞并且 scope 无效时使用 fallback；
- 不显示“击败”“征服”等未经证明的动词。

### 16.4 并发

- 两条 BYZ 前线同时运行，完成其中一条不改变另一条快照；
- TUR 与 BYZ 同时追踪同一 state，双方先后取得时分别记录正确直接前所有者；
- 一条前线到期或撤回只清理自己的 state 变量。

### 16.5 旧存档与异常路径

- 活动旧 JE 只补建当前 owner 快照，不猜测历史；
- 加载即完成的旧 JE 可以安全显示 fallback；
- 标签变化、JE invalid、主动撤回与超时均无残留 tracking；
- 结果事件被延迟期间保存/重载后仍能显示正确 named 或 fallback 文本；
- predecessor 变量异常等于 ROOT 时强制 fallback。

### 16.6 运行时证据

为调试版本记录：

- `TRACKING_INITIALIZED`：前线、state、当前 owner；
- `OWNER_SNAPSHOT_UPDATED`：前线、state、新 owner；
- `COMPLETION_PREDECESSOR_CAPTURED`：前线、state、前 owner、当前 owner；
- `SUCCESS_TEXT_NAMED` / `SUCCESS_TEXT_FALLBACK`；
- `TRACKING_CLEANED`：前线与清理原因。

日志验证后应移除或降频，避免长期轮转噪音。

## 17. 成功标准

实现完成后，TUR/BYZ 复归成功事件能够在事实允许时点名使日志达成的最后一个关键州的直接前所有者；无法可靠取得对象时自然降级。文本不把一个国家误写为整条疆界的唯一敌人，不把所有权变化误写为必然的战争征服，也不把已经纳入本国统治的地区继续描述为待组织的开局港邦或部落政权。
