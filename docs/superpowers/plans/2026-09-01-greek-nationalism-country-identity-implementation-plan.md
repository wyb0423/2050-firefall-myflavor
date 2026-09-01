# “伟大理想”国家身份链修复实施计划

日期：2026-09-01

状态：实施完成，静态验证通过，等待游戏内验证

设计来源：`docs/superpowers/specs/2026-09-01-greek-nationalism-country-identity-design.md`

## 1. 交付目标

修复 FFPA 对 `je_greek_nationalism` 的国家身份限制，确保：

- 只有已经形成的 `GRE` 可以新挂载“伟大理想”日志；
- 选择东罗马雄心路线后，活动日志可随 `GRE -> BYZ` 成立链继续存在；
- 有限希腊与“伟大理想”路线只能由 `GRE` 完成，东罗马路线只能由 `BYZ` 完成；
- 米迪耶林镇等错误持有日志的旧档国家通过 `invalid/on_invalid` 无奖励失效；
- 正常成功与失败均明确弹出原版 `greece.4` / `greece.5`；
- 提案事件、恢复决议、BYZ 成立条件和 `formation.3` 使用相同的严格身份语义。

本修复不改变日志门槛、路线奖励、宣称范围、BYZ 成立州范围、本地化文本、元数据或其他东地中海状态机。仓库其他 `c:TAG ?=` 用法另行逐项审计，不在本任务机械替换。

## 2. 文件边界

### 2.1 修改文件

- `common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt`
- `events/ffpa_eastern_mediterranean_events.txt`：仅 `ffpa_flavor.8`
- `common/decisions/ffpa_eastern_mediterranean_decisions.txt`：仅 `ffpa_request_eastern_roman_title`
- `common/country_formation/ffpa_byzantium.txt`
- `events/ffpa_formation_overrides.txt`：仅 `formation.3` 的身份条件

### 2.2 明确不修改

- `.metadata/metadata.json`、`README.md`、`AGENTS.md`；
- 英文和简体中文本地化；
- 国家、文化、州历史和地理区域定义；
- `greece.1`、`greece.4`、`greece.5` 事件正文与效果；
- `ffpa_grant_byzantine_justinianic_claims_v2` 及任何宣称清理逻辑；
- 其他日志、决议、事件或 `c:GRE ?=` / `c:BYZ ?=` / `c:TUR ?=` 表达式。

## 3. 固定状态机与身份表达

### 3.1 严格身份表达

country scope 中统一使用当前 1.13 已工作的定义比较：

```text
country_definition = cd:GRE
country_definition = cd:BYZ
```

不得以 `c:GRE ?= this` 或 `c:BYZ ?= this` 作为本链的唯一身份门槛。`?=` 仅保留给真正允许目标不存在的可选 scope 操作。

### 3.2 日志有效身份

活动 `je_greek_nationalism` 只允许以下两种状态：

```text
GRE
OR
BYZ AND has_variable = embrace_ambitious_agenda_var
```

含义固定为：BYZ 只能继承 GRE 已选择的东罗马路线，不能自行新挂载日志。

### 3.3 失效清理范围

`on_invalid` 只移除本日志运行时状态：

- `greek_homeland_states_owned_var`
- `byzantium_states_owned_var`
- `no_megali_idea_var`
- `embrace_megali_idea_var`
- `embrace_ambitious_agenda_var`
- `byzantium_event_fired`

不得移除：

- `ionian_islands_requirement_var`：没有来源标记，无法证明由本链创建；
- 任意州宣称：旧实现没有逐州来源标记，不能安全区分 FFPA、Firefall、事件或战争授予；
- `je_greek_nationalism_complete`：已结束旧实例缺少可靠的终局事件投递标记，本任务不猜测、不重开。

`on_invalid` 不调用 `greece.5`。错误持有者没有失败一项希腊国家工程，而是从未符合 FFPA 的挂载资格。

## 4. Task 0：冻结基线与最终加载栈

**读取**

- `.metadata/metadata.json`
- 本设计规格与本计划
- 第 2.1 节五个目标文件
- 原版 1.13.11 `common/journal_entries/00_greek_nationalism.txt`
- 原版 1.13.11 `events/greece_events.txt` 中 `greece.1`、`greece.4`、`greece.5`
- 原版 1.13.11 `events/misc_unifications.txt` 中 `formation.3`
- 原版 `common/journal_entries/journal_entries.md`
- 原版已工作的 `country_definition = cd:TAG`、`invalid`、`on_invalid`、`transferable = yes` 先例
- Firefall 0.1.1 与 Tech & Res 1.6 中上述顶层键和事件 ID 的定义/引用

**步骤**

1. 运行 `git status --short --branch` 并登记全部已有修改和未跟踪文件；不得覆盖、暂存或提交它们。
2. 用 `rg --files -uu -g '!/.git/**'` 盘点项目文件。
3. 确认 `.metadata/metadata.json` 仍声明 Victoria 3 `1.13.*`、Firefall `0.1.*` 和 Tech & Res `1.*`。
4. 确认实际安装根目录和加载顺序仍为：原版 → Tech & Res → Firefall → FFPA；若版本或路径变化，重新做最终定义比较，不沿用旧结论。
5. 搜索 `je_greek_nationalism`、`greece.1`、`greece.4`、`greece.5`、`formation.3` 的全部定义和引用，记录最终定义来源。
6. 比较 FFPA 完整替换与原版日志，确认除既有的“仅 GRE + 移除 plausible formables 门槛”差异外，所有计数、条件、变量、结果描述与奖励仍与目标版本一致。
7. 确认 Firefall 的 `ZZZEASTERNTHRACEWOOD` 仍拥有 Greek primary culture、首都仍在 `STATE_EASTERN_THRACE`，并把它保留为错误触发回归样本。

**完成检查**

```zsh
git status --short --branch
rg -n "^(je_greek_nationalism|formation\\.3)[[:space:]]*=|id[[:space:]]*=[[:space:]]*greece\\.(1|4|5)" \
  common events \
  "/path/to/Victoria 3/game/common" "/path/to/Victoria 3/game/events" \
  "/path/to/Firefall" "/path/to/Tech & Res"
```

计划中的 `/path/to/...` 是环境占位，不得写入运行时实现。

## 5. Task 1：修复日志挂载与转移生命周期

**修改文件**

- `common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt`

**步骤**

1. 更新文件头说明：这是对原版 1.13.11 的完整替换，FFPA 的有意差异包括严格 GRE 身份、GRE→BYZ 雄心路线转移、旧错误实例失效与明确终局弹窗。
2. 将 `is_shown_in_lobby`、`is_shown_when_inactive` 和 `possible` 中的 `c:GRE ?= this` 替换为 `country_definition = cd:GRE`。
3. 在日志顶层明确加入 `transferable = yes`，使已活动的日志可随 GRE 成立 BYZ 继续存在。
4. 新增 `invalid`：当前国家不是 GRE，且也不是“拥有 `embrace_ambitious_agenda_var` 的 BYZ”时失效。
5. 新增 `on_invalid`，仅移除第 3.3 节列出的六个临时变量；不触发事件、不添加/移除宣称、不写完成变量。
6. 保留 `immediate`、月度计数、事件调度、阈值和结果描述原样。

**目标结构**

```text
transferable = yes

invalid = {
    NOT = {
        OR = {
            country_definition = cd:GRE
            AND = {
                country_definition = cd:BYZ
                has_variable = embrace_ambitious_agenda_var
            }
        }
    }
}

on_invalid = {
    remove_variable = greek_homeland_states_owned_var
    remove_variable = byzantium_states_owned_var
    remove_variable = no_megali_idea_var
    remove_variable = embrace_megali_idea_var
    remove_variable = embrace_ambitious_agenda_var
    remove_variable = byzantium_event_fired
}
```

**完成检查**

```zsh
rg -n "is_shown_in_lobby|is_shown_when_inactive|possible =|transferable = yes|invalid =|on_invalid =|country_definition = cd:(GRE|BYZ)" \
  common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt
```

人工确认 BYZ 不在三个新挂载条件中，只在活动实例有效性中出现。

## 6. Task 2：按路线限制完成与失败结算

**修改文件**

- `common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt`

**步骤**

1. 在 `complete` 的 `no_megali_idea_var` 分支加入 `country_definition = cd:GRE`。
2. 在 `embrace_megali_idea_var` 分支加入 `country_definition = cd:GRE`。
3. 在 `embrace_ambitious_agenda_var` 分支加入 `country_definition = cd:BYZ`，并删除 `byz_is_this_tt` 内的可选 `c:BYZ ?= this` 身份判断。
4. 保留 `byz_is_this_tt` 玩家提示时，用严格 `country_definition = cd:BYZ` 作为 tooltip 内条件；不得删除该玩家可见要求。
5. 将原 `fail` 条件放在有效身份门槛之后：只有 GRE，或携带雄心变量的 BYZ，才能因原版的附庸/降级且负储备条件失败。
6. 保证非 GRE/BYZ 的旧错误实例首先走 `invalid`，不会同时满足 `fail` 并弹出希腊失败事件。
7. 将 `on_complete` 调整为 `trigger_event = { id = greece.4 popup = yes }`。
8. 将 `on_fail` 调整为 `trigger_event = { id = greece.5 popup = yes }`。
9. `je_greek_nationalism_complete` 的设置位置保持不变；不复制或覆盖 `greece.4` / `greece.5`。

**目标失败条件语义**

```text
(GRE OR (BYZ AND ambitious route))
AND
(is subject OR (rank below minor power AND gold reserves below zero))
```

Paradox Script 同一 block 的并列条件是 AND；实施时必须保留两个独立 `OR` block，不得误写成一个大 `OR`。

**完成检查**

```zsh
rg -n -C 6 "has_variable = (no_megali_idea_var|embrace_megali_idea_var|embrace_ambitious_agenda_var)|fail =|greece\\.(4|5)|byz_is_this_tt" \
  common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt
```

人工演算以下互斥结果：GRE+有限可完成、GRE+伟大理想可完成、GRE+雄心不可完成、BYZ+雄心可完成、非 GRE/BYZ 均不可完成或失败。

## 7. Task 3：收紧东罗马提案事件与恢复决议

**修改文件**

- `events/ffpa_eastern_mediterranean_events.txt`
- `common/decisions/ffpa_eastern_mediterranean_decisions.txt`

**步骤**

1. 仅在 `ffpa_flavor.8` 的 `trigger` 中把 `c:GRE ?= this` 改为 `country_definition = cd:GRE`。
2. 不改事件内对 TUR、RUS、州所有者等可选对象的 `exists + ?=` 逻辑；它们是允许目标不存在的可选 scope，不是当前国家身份判断。
3. 保留事件选择对 `embrace_megali_idea_var` → `embrace_ambitious_agenda_var` 的转换、宣称、恶名和关系效果原样。
4. 仅在 `ffpa_request_eastern_roman_title.is_shown` 中把 `c:GRE ?= this` 改为 `country_definition = cd:GRE`。
5. 保留决议 `possible`、`when_taken` 和 AI 权重原样。

**完成检查**

```zsh
rg -n -C 8 "ffpa_flavor\\.8|ffpa_request_eastern_roman_title|country_definition = cd:GRE|c:GRE \\?=" \
  events/ffpa_eastern_mediterranean_events.txt \
  common/decisions/ffpa_eastern_mediterranean_decisions.txt
```

检查结果允许文件其他对象仍有可选 tag scope，但 `ffpa_flavor.8` 与恢复决议不得再用可选 GRE 比较。

## 8. Task 4：收紧 BYZ 成立入口与成立事件

**修改文件**

- `common/country_formation/ffpa_byzantium.txt`
- `events/ffpa_formation_overrides.txt`

**步骤**

1. 将 BYZ formation 的 `potential` 改为 `country_definition = cd:GRE`。
2. 将 `possible` 中 `ffpa_byzantium_only_greece_tt` 的判断改为 `country_definition = cd:GRE`。
3. 保留 monarchy、`embrace_ambitious_agenda_var`、12 州和 `required_states_fraction = 1.0` 原样。
4. 将 `formation.3.trigger` 的 `c:BYZ ?= THIS` 改为 `country_definition = cd:BYZ`；统一小写 `this` 不是本任务目标，避免无意义格式修改。
5. 保留全局一次性标记、通知、威望与 `ffpa_grant_byzantine_justinianic_claims_v2` 原样。

**完成检查**

```zsh
rg -n -C 5 "potential =|ffpa_byzantium_only_greece_tt|country_definition = cd:(GRE|BYZ)|formation\\.3" \
  common/country_formation/ffpa_byzantium.txt events/ffpa_formation_overrides.txt
```

人工确认非 GRE 即使满足全部州、君主制和变量条件也看不到/不能成立 BYZ；成立后的 `formation.3` 只对当前 BYZ 执行一次。

## 9. Task 5：静态验证与差异审查

**结构与引用检查**

1. 重新搜索五个目标对象，确认本链所有排他身份门槛已经使用 `country_definition = cd:GRE/BYZ`。
2. 确认 `je_greek_nationalism` 在 FFPA 中只有一个顶层定义，`formation.3` 只有预期的完整覆盖。
3. 比较修改后 JE 与原版 1.13.11：差异必须限于原有 FFPA 差异和本计划明确列出的生命周期修复。
4. 检查 `greece.4` / `greece.5` 在最终加载栈中仍存在、没有 country trigger 阻断，并且 FFPA 没有复制其定义。
5. 检查六个失效清理变量均有既有定义/引用，拼写完全一致。
6. 检查花括号、引号、注释和顶层键；若没有专用 parser，使用项目/原版语法先例与最小结构检查，不把简单计数当成完整运行时证明。
7. 确认本任务没有新增本地化键，英中键集合无需改变。

**建议命令**

```zsh
rg -n "c:(GRE|BYZ) \\?= (this|THIS)" \
  common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt \
  common/country_formation/ffpa_byzantium.txt \
  common/decisions/ffpa_eastern_mediterranean_decisions.txt \
  events/ffpa_eastern_mediterranean_events.txt \
  events/ffpa_formation_overrides.txt

rg -n "country_definition = cd:(GRE|BYZ)|popup = yes|on_invalid =|remove_variable =" \
  common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt \
  common/country_formation/ffpa_byzantium.txt \
  common/decisions/ffpa_eastern_mediterranean_decisions.txt \
  events/ffpa_eastern_mediterranean_events.txt \
  events/ffpa_formation_overrides.txt

jq empty .metadata/metadata.json
git diff --check
git diff -- \
  common/journal_entries/zzzz_ffpa_greek_nationalism_override.txt \
  common/country_formation/ffpa_byzantium.txt \
  common/decisions/ffpa_eastern_mediterranean_decisions.txt \
  events/ffpa_eastern_mediterranean_events.txt \
  events/ffpa_formation_overrides.txt
git status --short --branch
```

第一条 `rg` 会命中目标文件中不属于本链的其他对象，例如 BYZ 复归事件；评审时按对象边界分类，不能把“文件仍有命中”误判为本修复未完成。

## 10. Task 6：运行时验证矩阵

无法由静态检查替代的场景按以下顺序在包含完整实际加载栈的新档/旧档中验证，并查看最新 `debug*.log`、`error*.log`、`game*.log` 及轮转文件。

### 10.1 新档：错误触发回归

1. 以 `ZZZEASTERNTHRACEWOOD`（米迪耶林镇）开局：不显示、不挂载 `je_greek_nationalism`，不显示恢复决议。
2. 选取另一个位于 Megali 地区、含 Greek primary culture 的 Firefall 后继政权：结果同上。
3. 检查无效国家不能触发 `ffpa_flavor.8`，也不能通过本链成立 BYZ。

### 10.2 新档：GRE 正常路线

1. 形成 GRE：日志可用，挂载后 `greece.1` 正常出现一次。
2. 有限希腊路线成功：仅 GRE 可完成，`greece.4` 明确弹出一次。
3. 伟大理想路线成功：仅 GRE 可完成，`greece.4` 明确弹出一次。
4. 两条 GRE 路线分别触发失败条件：`greece.5` 明确弹出一次。
5. 确认成功/失败后 `je_greek_nationalism_complete` 仍按原链设置，事件不重复。

### 10.3 新档：GRE → BYZ 雄心路线

1. GRE 选择伟大理想后满足条件，`ffpa_flavor.8` 或恢复决议只对 GRE 出现。
2. 接受东罗马雄心，确认变量转换为 `embrace_ambitious_agenda_var`。
3. 形成 BYZ：活动日志因 `transferable = yes` 保留，计数和路线变量不重置。
4. BYZ 成功：只有雄心分支可完成，`greece.4` 弹出一次。
5. BYZ 失败：`greece.5` 弹出一次。
6. `formation.3` 仅对 BYZ 运行一次，现有查士丁尼宣称白名单和已持有宣称保持不变。

### 10.4 旧档迁移

1. 载入米迪耶林镇或其他非 GRE/BYZ 正在持有日志的旧档：日志走 `invalid` 消失，不触发 `greece.4` / `greece.5`，六个临时变量被清理。
2. 验证该国更新前已有宣称仍然存在，`ionian_islands_requirement_var` 不被删除。
3. 载入 GRE 的活动实例：日志和进度保留。
4. 载入带 `embrace_ambitious_agenda_var` 的 BYZ 活动实例：日志和进度保留。
5. 载入非 GRE 已经结束日志的旧档：不追发希腊奖励、不重开日志，提案、决议和 BYZ 成立入口均不可用。

### 10.5 运行时证据分层

交付报告分别记录：

1. 五个目标文件已被加载且没有被后加载内容覆盖；
2. 顶层定义成功解析；
3. 日志/决议/事件/成立入口实际到达；
4. trigger 在正确 country scope 得到预期真假值；
5. 日志失效、转移、终局事件和宣称最终状态未被其他模块回写。

若本轮不能启动游戏，只能把前四项中的静态可证部分标为“已静态确认”，其余明确列为“待游戏内验证”，不得把定义存在等同于功能生效。

## 11. 交付与工作树保护

1. 实施结束再次运行 `git status --short --branch` 和 `git diff --check`。
2. 只汇报第 2.1 节五个运行时文件的修改；设计/计划文档作为辅助交付单列。
3. 不执行 `git add`、`git commit`、`git reset`、`git checkout --` 或 `git clean`。
4. 保留当前工作树中所有既有未跟踪规格文件，不格式化或重写无关文件。
5. 交付时分别列出：已静态确认、已由日志确认、仍需游戏内验证。

## 12. 后续独立审计

本任务完成后另开一次分类审计：逐个判断仓库内剩余 `c:GRE ?=`、`c:BYZ ?=`、`c:TUR ?=` 是严格当前国家身份门槛、可选全局对象 scope，还是其他 scope 比较。只有第一类在确认调用 scope 与存档影响后改为 `country_definition = cd:TAG`；不得做全仓库正则替换。
