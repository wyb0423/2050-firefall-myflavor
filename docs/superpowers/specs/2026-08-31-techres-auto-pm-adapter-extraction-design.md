# FFPA Tech & Res Auto PM Adapter 独立拆分设计

日期：2026-08-31
状态：拆分已实施；机械搬移与静态验证完成，生成器重跑与游戏内验证延期

## 1. 目标

把当前 `2050-firefall-myadapter` 中完整的 Tech & Res 自动生产方式兼容模块迁移到同级独立 Mod：

- 目录：`ffpa-techres-auto-pm-adapter`
- Mod ID：`com.wyb.ffpa-techres-auto-pm-adapter`
- Victoria 3：`1.13.*`
- 初始版本：`1.0.0`

拆分后，新 Mod 独立拥有自动 PM 的运行时、界面、生命周期、生成器、生成产物、覆盖报告和本地化。原 Personal Adapter 不保留自动 PM 桥接逻辑，成为只包含东地中海内容的 Mod。

本次只改变文件和发布包归属，不改变玩家可见行为、上游覆盖、技术 ID、变量含义、调度频率或存档状态机。

## 2. 非目标

- 不重写自动 PM 状态机、经济阈值或类别划分。
- 不重新生成或重新编号 transition、building、PMG、trial、cooldown、manual lock 或 oscillation lock ID。
- 不改变两个 Auto-Apply Mod 的设置变量、日志、频率和单次调整数量。
- 不修复已记录的上游孤立 PMG。
- 不把生成器与运行时拆到不同仓库。
- 不为缺失的 Auto-Apply Mod 增加软降级逻辑。
- 不在当前无法运行游戏的机器上强求运行时测试。
- 不初始化 Git 仓库、不暂存、不提交现有或新 Mod。

## 3. 依赖架构

### 3.1 新 Mod 的直接关系

新适配器同时消费以下三个彼此独立的上游 Mod：

- `[1.13] Tech & Res`，Workshop ID `3472248460`；
- `Auto-Apply PMs`，Workshop ID `3353797125`；
- `Auto-Apply Automation PMs`，Workshop ID `3344726320`。

Tech & Res 的稳定 Mod ID 是 `tech.res`，因此新 Mod 的 `.metadata/metadata.json` 只声明它为 Launcher 硬依赖。

当前安装版本的两个 Auto-Apply Mod 在 `.metadata/metadata.json` 中使用空 `id`，不能安全写入 Launcher 依赖。新 Mod 的 README 和 AGENTS 必须把它们登记为必要运行前置，并保留 Workshop ID 作为生成器和诊断接口。

这不表示两个 Auto-Apply Mod 依赖 Tech & Res。三项前置彼此独立，只有新适配器同时消费三者。

### 3.2 加载顺序

新适配器必须晚于 Tech & Res 和两个 Auto-Apply Mod，以便：

- 读取 Tech & Res 的最终 building → PMG → PM 图；
- 消费两个 Auto-Apply Mod 的 `zw_var_auto_pm_*` 设置和 trigger；
- 用生成的 `REPLACE:` 定义替换两个 Auto-Apply Mod 的最终管理器。

沿用当前已工作的推荐顺序：

```text
Tech & Res
→ Auto-Apply PMs
→ Auto-Apply Automation PMs
→ FFPA Tech & Res Auto PM Adapter
```

前三项之间不由新适配器声明相互依赖；关键约束是新适配器最后加载。

### 3.3 与其他拆分包的关系

新适配器不依赖、调用或覆盖以下 Mod 的自有接口：

- `2050-firefall-myadapter`；
- `2050-firefall-core-balance`；
- `ffpa-building-pruning`；
- `ffpa-building-pruning-techres`；
- `2050: The Fire Falls`。

原 Personal Adapter 继续保留 Firefall 与 Tech & Res 依赖，因为剩余东地中海内容仍消费它们。原包与新适配器互不声明依赖。

## 4. 文件所有权

### 4.1 完整迁移的手写运行时

- `common/decisions/ffpa_auto_pm_decisions.txt`
- `common/journal_entries/ffpa_auto_pm_compat_je.txt`
- `common/scripted_buttons/ffpa_auto_pm_buttons.txt`
- `common/script_values/ffpa_auto_pm_values.txt`
- `common/scripted_effects/ffpa_auto_pm_settings_effects.txt`
- `common/scripted_effects/ffpa_auto_pm_journal_effects.txt`
- `common/on_actions/ffpa_on_actions.txt`

`ffpa_on_actions.txt` 当前只负责自动 PM 日志的启动初始化和月度补发，因此整文件迁移，不保留共享包装或桥接 effect。

### 4.2 完整迁移的生成接口与产物

- `tools/generate_ffpa_auto_pm_compat.ps1`
- `common/scripted_effects/ffpa_generated_auto_pm_effects.txt`
- `common/scripted_effects/ffpa_generated_auto_pm_trials.txt`
- `common/scripted_triggers/ffpa_generated_auto_pm_triggers.txt`
- `TECHRES_AUTO_PM_COVERAGE.md`

生成器、三份运行时产物和覆盖报告必须始终作为同一版本单元维护。生成器继续通过 `GameRoot`、`WorkshopRoot` 和 `OutputRoot` 参数接收环境路径，不写入新的机器绝对路径。

### 4.3 按键迁移的共享文件

从以下文件迁移英文和简体中文各 26 个自动 PM 键：

- `localization/english/ffpa_l_english.yml`
- `localization/simp_chinese/ffpa_l_simp_chinese.yml`

迁移范围是 `je_ffpa_auto_pm_*`、`ffpa_auto_pm_*` 及对应决议/按钮说明。新本地化文件保留正确语言头、原文本、原技术 ID、UTF-8 BOM 和现有换行格式。

### 4.4 新建的发布文件

新 Mod 新建：

- `.metadata/metadata.json`
- `.gitignore`
- `README.md`
- `AGENTS.md`

原 Personal Adapter 更新自身 metadata 简介、README、AGENTS 和加载顺序说明，使文档只描述当前仍拥有的东地中海功能，并登记外部自动 PM 适配器边界。

## 5. 运行数据流

拆分后调用链不变：

1. `on_game_started_after_lobby` 遍历国家，调用 `ffpa_ensure_auto_pm_compat_journal`。
2. `on_monthly_pulse_country` 为旧存档或缺失界面的玩家补发 `je_ffpa_auto_pm_compat`。
3. JE 月度脉冲读取上游 `zw_var_auto_pm_*` 频率、类别和一/三建筑预算。
4. `ffpa_update_auto_pm_trials` 先推进候选、试运行、验收、保留、回滚和冷却状态。
5. `ffpa_process_new_techres_buildings` 扫描 Tech & Res 新建筑和扩展普通生产链。
6. 自动化与运输入口按上游设置和劳动力条件扫描州级实例。
7. 生成 guard 继续把已完整覆盖的实例从旧管理器委托给本适配器，未覆盖实例仍由上游处理。

生成 effects 当前包含 40 个上游 `REPLACE:`：38 个建筑管理器，以及自动化和运输两个州级管理器。迁移不得改变这些覆盖对象的顺序或内容。

## 6. 跨包接口与存档兼容

以下对象保持原名、原含义和原作用域：

- `je_ffpa_auto_pm_compat`；
- 11 个类别按钮及其设置变量；
- `ffpa_auto_pm_*` 阈值、effect、trigger 和调度入口；
- 上游 `zw_var_auto_pm_*` 消费接口；
- `ffpa_ap_b*` building/PMG 隔离变量；
- `ffpa_pending_*`、`ffpa_trial_*`、基线、计数器、cooldown、manual lock 和 oscillation lock；
- 生成 transition ID、debug log 标记及 40 个上游覆盖键。

物理迁移不需要新增迁移 effect。旧存档启用新适配器后继续读取原 JE、开关、候选、trial 和冷却状态。

原 Personal Adapter 不再提供这些定义。玩家如果只启用原包，将只获得东地中海内容；同时启用新适配器后恢复拆分前的自动 PM 功能。

## 7. 缺失前置与错误边界

由于两个 Auto-Apply Mod 没有可用 metadata ID，Launcher 不能自动保证它们存在。新包通过以下方式降低误用风险：

- README 首段列出两个必要前置、Workshop ID 和加载要求；
- AGENTS 把两个 Workshop 目录登记为生成器输入和覆盖验证对象；
- 交付报告明确说明 metadata 只能硬依赖 Tech & Res。

不增加不存在上游时的脚本探测或软降级。此类逻辑会改变当前定义解析、guard 和管理权语义，超出“仅物理拆分”的范围。

## 8. 实施方法

1. 记录工作树和自动 PM 文件、生成器、生成产物、报告、本地化切片的基线哈希与顶层键集合。
2. 在当前仓库的临时目录中组装新 Mod，避免在验证前写入上层目录。
3. 机械搬移完整文件；对两份本地化仅移动已登记的 26 键切片。
4. 创建新 metadata、README、AGENTS 和 `.gitignore`。
5. 从原 Personal Adapter 移除自动 PM 文件、键、说明与调度入口。
6. 对原包、新包和全部上游执行静态与最终数据库验证。
7. 验证通过后，将新 Mod 移到当前目录的上层 `ffpa-techres-auto-pm-adapter`。

目标目录存在时不得覆盖，必须停止并确认其所有权。

## 9. 验证标准

### 9.1 静态迁移等价性

- 新包 metadata 可解析，ID 唯一，只声明 `tech.res` 依赖。
- 完整迁移文件与拆分前逐字节一致。
- 英文和简体中文各 26 个键，键集合与文本保持一致，且均保留 BOM。
- 旧包移除的每个自动 PM 顶层键恰好由新包提供一次。
- 原 Personal Adapter 的运行时与本地化不再引用自动 PM 自有键或生成 guard。
- 原包与新包之间没有意外重复的自有顶层键。
- 40 个 `REPLACE:` 目标都存在于当前两个 Auto-Apply Mod 的最终数据库。
- 生成运行时引用的 building、PMG、PM、goods 和上游 trigger/effect 能在原版、Tech & Res 与两个 Auto-Apply Mod 中解析。
- 脚本花括号、字符串、注释和顶层结构正常。
- `git diff --check` 无新增空白错误。

### 9.2 生成器与报告

迁移前后比较以下文件 SHA-256：

- `ffpa_generated_auto_pm_effects.txt`
- `ffpa_generated_auto_pm_trials.txt`
- `ffpa_generated_auto_pm_triggers.txt`
- `TECHRES_AUTO_PM_COVERAGE.md`
- `generate_ffpa_auto_pm_compat.ps1`

当前机器未发现 `pwsh`，且不得未经授权安装系统软件。因此本次机械搬移以哈希一致证明生成逻辑和产物未改变，并在交付中记录“生成器未重新执行”。未来在具备 PowerShell 的环境中仍需连续运行两次，确认三个生成脚本和覆盖报告哈希稳定。

### 9.3 运行时验证延期

当前机器不能运行 Victoria 3。以下项目延期到可运行游戏的环境：

- 新游戏 JE 初始化；
- 旧存档设置、候选、trial 和 cooldown 继承；
- 普通生产、自动化与运输的相邻双向切换；
- 候选、试运行、收益验收、保留、回滚、外部取消和震荡锁；
- guard 委托与未覆盖实例的上游管理；
- `FFPA_PM|` 调度和状态日志链；
- 最终状态没有被后加载内容回写。

不得把静态定义存在或哈希相同描述成运行时已经生效。

## 10. 完成条件

- `ffpa-techres-auto-pm-adapter` 能在不启用 Personal Adapter 或 Firefall 的加载栈中独立提供原自动 PM 适配功能。
- 原 Personal Adapter 只保留东地中海运行时内容。
- 两包没有相互依赖或隐藏调用。
- 自动 PM 玩家行为、上游管理权、持久 ID 和生成结果均未因拆分改变。
- 所有静态和最终数据库验证通过；无法执行的生成器与游戏测试明确列为待办。
- 不覆盖、暂存、提交或冒充用户已有修改。
