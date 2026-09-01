# 东地中海玩家可见内容严格国家身份门控设计

## 1. 背景

Firefall 通过 `replace_path` 重建国家定义与开局国家，GRE、TUR、BYZ 等旧世界国家在开局时可能只有 country definition 与 formable，并不存在对应的全局 country 对象。

FFPA 过去大量使用：

```txt
c:TUR ?= this
c:GRE ?= this
c:BYZ ?= this
```

作为“当前国家必须是指定 tag”的条件。`?=` 是可选 scope 操作；目标 country 对象不存在时，条件可能被跳过，而不是返回 false。已经提交的 `f16c1a9 fix(greece): enforce nationalism country identity` 证明这一问题会使 Firefall 继承国家错误获得希腊民族主义 JE，并把希腊链改为：

```txt
country_definition = cd:GRE
country_definition = cd:BYZ
```

横向审查发现，相同模式仍存在于 TUR/BYZ 政府类型、国家集团名称池、决议、JE、country event、on_action 调度和直接添加玩家内容的外层 scripted trigger/effect。若不先修复，后续润色后的奥斯曼、罗马、安纳托利亚与新罗马文本仍可能显示给错误国家。

本设计只审计和修复“玩家可见内容交付边界”，不对整个仓库执行机械替换。

## 2. 已确认决策

1. 优先修复玩家可见边界，不一次性重写全部 `?=`。
2. 沿用已提交希腊修复的直接 `country_definition = cd:TAG` 语法，不新增共享身份 trigger。
3. 政府类型、国家集团候选名、决议、JE、事件 trigger、on_action 调度和直接添加玩家内容的外层 guard 纳入本轮。
4. 外交关系、事件目标、保存 scope、第三国交互等允许对象不存在的 `?=` 保留。
5. BYZ 动态国名中 `exists = scope:actor` 后的 `scope:actor ?= { ... }` 保留。
6. BYZ 党名 scripted GUI 当前使用严格 `this = c:BYZ`，不是可选 `?=`；本轮保留并运行时验证。
7. 本轮先阻止继续错误发放；已经写入旧档的永久奖励、利益集团槽位与历史变量不做全局猜测清理。
8. 身份修复先于三份已批准叙事设计实施。

## 3. 目标

- 在 TUR/GRE/BYZ 尚未形成时，禁止任何其他国家获得其政府类型、决议、JE、事件或国家集团名称候选。
- tag 形成后，让原有玩家内容按当前 country definition 正常出现。
- tag 变化后，让玩家可见入口按新的 current country definition 重新评估。
- 对所有保留的 `?=` 给出“对象允许不存在”的具体理由。
- 不改变事件效果、JE 条件、modifier、数值、技术 ID 或存档状态语义。
- 为后续文本验收提供可靠前置条件：文本错误与内容误投不再混淆。

## 4. 非目标

- 不对整个仓库的 `c:TAG ?=` 做盲目正则替换。
- 不修改 Firefall、Tech & Res 或外部拆分包。
- 不重新设计 TUR/GRE/BYZ 的形成、tag 变化或文化身份。
- 不清理无法证明来源的旧宣称、人口移动、永久奖励或外部 modifier。
- 不自动重命名已经建立的国家集团。
- 不修改任何玩家文本；国家形容词、政体翻译和 README 属于后续文本批次。
- 不在本轮审计所有纯数值 effect 的内部可选 scope。

## 5. 操作符语义与严格身份写法

### 5.1 严格当前国家身份

country scope 中：

```txt
country_definition = cd:TUR
country_definition = cd:GRE
country_definition = cd:BYZ
```

否定条件：

```txt
NOT = { country_definition = cd:TUR }
```

ROOT 或 owner 是待检查国家时，先进入对应 country scope：

```txt
ROOT = { country_definition = cd:TUR }
owner = { country_definition = cd:BYZ }
```

实际实现必须按当前文件和 trigger/effect scope 使用本地同类先例，不把 country trigger 直接放入 state、character 或其他 scope。

### 5.2 正确的可选对象访问

以下语义继续使用 `?=`：

- 如果某国存在则调整关系；
- 对可能不存在的保存 scope 执行效果；
- 访问可空的 `scope:actor`、战争对象、事件目标或前所有者；
- 对可能不存在的外部 country object 查询或写入，而当前 ROOT 的身份由其他严格条件保证。

判断标准不是“是否写了 TUR/BYZ/GRE”，而是“目标对象不存在时，本段逻辑应该失败，还是应该安静跳过”。

## 6. 方案比较

### 6.1 每个入口直接使用 country definition（采用）

优点：

- 与已经提交的希腊修复一致；
- 没有新顶层接口；
- 代码审查时可直接看到目标身份；
- 不依赖全局 country 对象存在。

缺点是重复少量语句，但身份门控本身足够简单，不值得增加间接层。

### 6.2 新增共享身份 scripted trigger

例如 `ffpa_is_tur_country_v1`。写法更短，但会新增跨文件接口和额外顶层定义，也可能诱使后续开发者在非 country scope 直接调用。未采用。

### 6.3 全仓批量替换

会破坏正确的可空 scope 和第三国交互，无法区分身份断言与可选访问。禁止采用。

## 7. 玩家可见边界分类

### 7.1 政府类型

文件：

- `common/government_types/00_ffpa_turkish_governments.txt`；
- `common/government_types/00_ffpa_byzantine_governments.txt`。

对象：TUR 七个、BYZ 七个政府类型。

`possible` 当前 country 必须使用严格 country definition。否则 TUR/BYZ 尚未形成时，其他满足君主制、总统制或议会制法律的国家可能进入奥斯曼或罗马政府类型并显示错误名称与统治者称号。

本轮不改变 transfer of power、ruler title、heir、regency 或法律条件。

### 7.2 国家集团候选名称

文件：

- `common/power_bloc_names/ffpa_eastern_mediterranean_power_bloc_names.txt`；
- `common/scripted_triggers/ffpa_turkish_flavor_triggers.txt` 中三条建国路线查询。

两个 TUR 通用名称、两个 TUR 高门名称、两个 TUR 共和国名称、两个 TUR 总署名称及七个 BYZ 名称都必须以严格身份为入口。

路线变量仍决定 TUR 专属子池，政体法律仍决定 BYZ 专属子池。只收紧国家身份，不改变名称权重或随机池顺序。

### 7.3 决议

文件：

- `common/decisions/ffpa_eastern_mediterranean_decisions.txt`；
- `common/decisions/ffpa_turkish_flavor_decisions.txt`。

所有 `is_shown` 与承担身份资格的 `possible` 使用 strict country definition。已经提交的 GRE 东罗马恢复决议保持现状。

按钮效果内对可空对象的操作不在本轮替换。

### 7.4 Journal Entry

纳入本项目东地中海 JE 的：

- `is_shown_in_lobby`；
- `is_shown_when_inactive`；
- `possible`；
- route-specific completion identity branch；
- `invalid`。

重点文件：

- `ffpa_eastern_mediterranean_journal_entries.txt`；
- `ffpa_turkish_reconstruction_programs.txt`；
- `ffpa_turkish_frontier_recovery.txt`；
- `ffpa_permanent_governance_journals.txt`；
- `ffpa_byzantine_restoration_campaigns.txt`；
- `ffpa_imperial_regional_development.txt`；
- 已提交修复的 `zzzz_ffpa_greek_nationalism_override.txt`。

JE 内部访问目标 state、owner 或外部 country 的可选 scope 保留。

### 7.5 Country Event

纳入：

- country event 根 trigger 中的当前国家身份；
- cancellation/continuation 中必须维持的当前国家身份；
- 由事件自身直接决定是否向 TUR/GRE/BYZ 显示的入口。

重点文件：

- `events/ffpa_eastern_mediterranean_events.txt`；
- `events/ffpa_turkish_flavor_events.txt`；
- `events/ffpa_turkish_permanent_governance_events.txt`；
- `events/ffpa_byzantine_permanent_governance_events.txt`；
- 已提交修复的 `events/ffpa_formation_overrides.txt`。

事件 effect 中对 `thrace_owner`、`aydin_owner`、TUR、RUS 或其他外部对象的交互不因本轮身份审计改变。

### 7.6 On-action 调度

文件：

- `common/on_actions/ffpa_eastern_mediterranean_on_actions.txt`。

纳入会：

- 添加 JE；
- 排程事件；
- 运行 GRE/TUR/BYZ 迁移；
- 分配风味意识形态、文化、trait 或国家修正；
- 同步 BYZ 州级奖励。

的最外层 country identity limit。

州级 on_action 在进入 `owner` scope 后检查 strict country definition。仅用来访问可空 owner 时的 `owner ?= { ... }` 结构可以保留，但内部身份必须严格。

### 7.7 直接调度玩家内容的 scripted trigger/effect

纳入：

- `ffpa_tur_has_ottoman_state_project_v1`；
- `ffpa_tur_has_republican_state_project_v1`；
- `ffpa_tur_has_directorate_state_project_v1`；
- 常驻治理 ready trigger；
- 边疆委员会 ready trigger；
- 西方整合与地区治理事件调度最外层 guard；
- formation/old-save ensure 中决定是否进入 GRE/TUR/BYZ 业务逻辑的 guard。

不深入替换已经由 strict outer guard 保护、且只执行数值或对象操作的内层可选 scope，除非该内层本身会向错误 country 添加玩家内容。

### 7.8 党名与动态国名

BYZ 党名 scripted GUI 使用：

```txt
this = c:BYZ
```

它不是可选操作符。本轮保留，测试 BYZ 不存在、形成和 tag 变化三种状态。若当前 1.13.11 运行日志证明严格等式在 country object 不存在时有错误，才另行改为 country definition；不得仅为统一风格扩大改动。

BYZ 动态国名位于 `BYZ = { ... }` 顶层，且各分支先检查 `exists = scope:actor` 再用 `scope:actor ?= { law checks }`。该写法表达 actor 可空，不是国家身份门控，原样保留。

## 8. 明确保留的可选交互示例

- `c:TUR ?= { owns_entire_state_region = ... }`：只在 TUR 存在时读取其领土；
- `scope:thrace_owner ?= { ... }`：前所有者可能不存在；
- `scope:actor ?= { ... }`：动态国名 actor 可能为空；
- `c:RUS ?= { ... }`：外部国家可能尚未形成；
- 保存战争、外交、事件或州 owner scope 后的可选效果；
- `exists = c:TUR` 与随后可选进入 country object 的配对。

分类清单必须记录保留原因，避免后续维护再次把正确的可选语义当作 bug。

## 9. 旧存档行为

### 9.1 活动 JE

错误国家上的活动 JE 通过修正后的 `invalid` 路径失效，并只执行该 JE 已登记的运行时清理。不能把无资格实例当作正常成功或失败。

### 9.2 已排程事件

事件弹出时重新评估 strict trigger；不符合身份时不得显示或执行。若某个事件由 `trigger_event` 绕过普通 trigger 语义，必须在调度包装和事件 trigger 两端同时有 strict guard，并在运行时验证。

### 9.3 政府类型与名称池

- 政府类型在重新评估后退出错误的奥斯曼/罗马名称；
- 候选名称池只影响以后创建或重新随机命名的国家集团；
- 已存在国家集团若恰好使用错误候选名，不自动改名，因为没有可靠来源标记且玩家可能已手工接受该名称。

### 9.4 已写入的永久状态

本轮不全局清理：

- 已发放永久 modifier；
- 已替换利益集团 trait 槽位；
- 已添加宣称；
- 已设置路线终局或完成变量；
- 已发生人口迁移。

虽然许多对象使用 `ffpa_` 前缀，恢复原状仍可能需要知道被替换槽位、其他来源宣称和具体旧档历史。若实际存档发现污染，使用独立、玩家确认的修复设计，不在身份入口修复中猜测。

## 10. 文件与所有权边界

预计涉及：

- 两份 country-specific government type 文件；
- `ffpa_eastern_mediterranean_power_bloc_names.txt`；
- 两份 decisions；
- 东地中海各 JE 文件；
- 四份东地中海 event 文件及 formation override；
- `ffpa_eastern_mediterranean_on_actions.txt`；
- 与上述入口直接相连的 scripted trigger/effect 文件；
- `AGENTS.md`：登记严格身份规则和保留 `?=` 的分类标准；
- 实施交付说明中的逐项分类表：列出每个替换与保留的 `?=` 位置、所在 scope 和判断理由；不另建审计报告文件。

不涉及本地化、metadata、README、外部拆分包或全局游戏数据库。

## 11. 与已批准文本设计的实施顺序

1. 保留已提交的 GRE 身份修复；
2. 实施本设计；
3. 在 Firefall 开局无 TUR/GRE/BYZ 的场景验证无内容泄漏；
4. 实施动态前所有者叙事；
5. 实施 GRE → BYZ Firefall 文本重写；
6. 实施常驻治理与地区建设文本重写；
7. 最后处理国家形容词、动态国名语法、政体翻译、metadata 与 README。

身份门控变化不应与叙事文本变化混在同一审查提交中。

## 12. 静态验证

- 每个替换项都位于 country identity assertion；
- 每个保留项都有对象可空的明确理由；
- 玩家可见入口中不存在仅依赖 `c:TUR/GRE/BYZ ?= this` 的 exclusive guard；
- strict country trigger 位于合法 country scope；
- government type 的其他法律和 transfer-of-power 条件不变；
- JE 条件、事件效果、数值、ID 和持久变量不变；
- 动态国名 actor 可选逻辑与党名 strict equality 原样保留；
- `.metadata/metadata.json` 不变且可解析；
- `git diff --check` 无新增空白错误。

## 13. 新游戏运行时矩阵

### 13.1 无旧世界 tag 的 Firefall 开局

抽查不同国家、不同政体和不同地区：

- 不显示奥斯曼或罗马政府类型；
- 不出现 GRE/TUR/BYZ 决议、JE 或事件；
- 国家集团名称候选不出现 FFPA TUR/BYZ 名称；
- 月度和成立 on_action 不写入 FFPA 东地中海身份、迁移或完成变量；
- 非 BYZ 党名继续使用原版 fallback；
- 无相关 scope/parser 错误。

### 13.2 形成 GRE

- 希腊民族主义链按已提交修复运行；
- TUR/BYZ 内容仍不可用；
- 非 GRE 国家不获得 GRE 内容。

### 13.3 形成 TUR

- TUR 政体名称、决议、JE、事件、国家集团名称与路线查询正常；
- 其他国家不获得相同内容；
- TUR 后续形成其他 tag 时入口按 current country definition 退出。

### 13.4 形成 BYZ

- BYZ 政体、党名、动态国名、JE、事件和国家集团名称正常；
- 党名在 BYZ 不存在时显示 fallback，形成后显示专属名；
- BYZ 形成其他 tag 后专属入口退出，已登记持久历史按原设计保留。

## 14. 正确可选交互回归

- TUR 不存在时，与 TUR 相关的关系/领土可选读取安静跳过；
- TUR 存在时，同一交互正常执行；
- `thrace_owner`、`aydin_owner` 缺失时事件不报错；
- 动态国名 actor 为空时不报错，存在时按法律显示；
- 外部 RUS、ION 或其他可选国家不存在时不产生 parser/runtime 错误；
- 保存 scope 失效时走既有 fallback 或跳过路径。

## 15. 日志证据

调试版本按最低必要频率记录：

- `IDENTITY_GATE_REJECTED`：对象、当前 country definition、入口；
- `IDENTITY_GATE_ACCEPTED`：形成后的 GRE/TUR/BYZ 与入口；
- `OPTIONAL_SCOPE_SKIPPED`：仅在验证关键外部对象时临时记录；
- `VISIBLE_CONTENT_SCHEDULED`：JE/事件/决议调度；
- `VISIBLE_CONTENT_BLOCKED`：错误国家被阻止。

验证后移除或关闭高频日志。交付时区分静态确认、日志确认和仍需游戏内目测的政府/名称池/党名表现。

## 16. 成功标准

实现完成后，Firefall 开局中不存在的 GRE/TUR/BYZ 不再让 optional country scope 跳过 exclusive identity guard。任何其他国家都不会获得奥斯曼或罗马政府名、东地中海决议、JE、事件或国家集团候选；对应 tag 形成后，原有内容完整恢复。所有保留的 `?=` 都继续表达真正允许对象不存在的关系，身份修复不会破坏外交、事件目标或动态国名逻辑。
