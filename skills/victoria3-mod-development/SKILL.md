---
name: victoria3-mod-development
description: 基于本地游戏与 Workshop 数据创建、修改、审查和诊断 Victoria 3 Mod，涵盖 Paradox Script、数据覆盖、兼容性、事件与修正、AI、生产方式、日志和存档迁移。在 macOS/Darwin 上进行 Victoria 3 Mod 开发时必须优先使用本技能，并先执行内置的 macOS 环境发现与命令适配。不用于只讨论玩法而不涉及 Mod 实现的请求。
compatibility: 支持 macOS、Windows 和 Linux；macOS 工作流使用 zsh/POSIX 工具，并对 PowerShell 来源工具进行显式能力检查。
---

# Victoria 3 Mod 开发

以当前安装的游戏数据和实际启用的 Workshop Mod 为权威来源。Wiki、论坛、GitHub 项目适合确认概念和寻找先例，但版本敏感的标识符、作用域、触发器、修正项和数值必须回到本地文件核实。

## 工作方式

1. 先检测宿主系统和可用命令。检测到 `Darwin` 时立即读取 [macos-development.md](references/macos-development.md)，后续命令、路径发现和日志定位均以其中的 macOS 工作流为准。
2. 确认游戏根目录、Workshop 根目录、目标 Mod 目录、依赖 Mod ID、游戏版本与加载顺序。将路径参数化，不把某台机器的绝对路径写进可复用脚本。
3. 先检查目标工作树和现有实现，保存用户已有改动。使用 `rg` 定位定义和引用，并同时搜索原版、全部相关依赖及目标 Mod。
4. 建立“合并后的数据库”视图：原版定义按加载顺序依次受到每个依赖的创建、替换和注入，目标 Mod 应针对最终形态工作，而不是只针对原版。
5. 先从本地相同目录和相同作用域寻找已工作的语法先例。不要凭记忆发明 trigger、effect、modifier 或 scope 写法。
6. 选择最小且稳定的覆盖方式：能注入时避免复制整个上游定义；必须替换时，说明它与上游更新、其他 Mod 和加载顺序的关系。
7. 实现后同时做静态验证、合并覆盖验证和运行时日志验证。不能启动游戏时，明确哪些结论仍需实机确认。

## 按需读取

- 在 macOS/Darwin 上工作，或需要把 Windows 来源命令、路径、脚本转换为本机工作流时，先读 [macos-development.md](references/macos-development.md)。
- 涉及依赖 Mod、加载顺序、覆盖或存档兼容时，读 [research-and-compatibility.md](references/research-and-compatibility.md)。
- 涉及 Paradox Script、作用域、初始化、本地化或解析器时，读 [paradox-script-patterns.md](references/paradox-script-patterns.md)。
- 涉及 modifier、事件链、AI 权重或周期性逻辑时，读 [modifiers-events-and-ai.md](references/modifiers-events-and-ai.md)。
- 涉及建筑、商品、PM、PMG 或自动管理系统时，读 [production-method-management.md](references/production-method-management.md)。
- 涉及“不生效”、错误归因、生成器或交付验证时，读 [diagnostics-and-validation.md](references/diagnostics-and-validation.md)。

## 关键不变量

- 标识符可能包含连字符；解析数据库键时不要只允许字母、数字和下划线。
- 文件名不决定覆盖关系。顶层键、加载顺序、替换/注入语义及 `replace_path` 才决定最终数据库。
- 作用域正确性必须由相同上下文的本地先例和运行结果证明；IDE 提示只能作为线索。
- 持久变量、事件目标、journal 状态和生成 ID 都可能成为存档接口。修改含义时设计迁移，不要静默复用旧键。
- 诊断时区分“定义被解析”“调度器到达”“条件成立”“效果执行”和“最终状态保留”；每一层需要不同证据。
- 宿主系统命令只是开发接口，不是 Mod 行为。跨平台转换不得顺带改变生成顺序、覆盖集合、编码、持久 ID 或报告语义。
