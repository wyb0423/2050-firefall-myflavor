# Victoria 3 Mod Development Skill 的 macOS 能力设计

## 决策

原地增强 `skills/victoria3-mod-development`，不创建第二个 skill。技能继续覆盖现有的 Victoria 3 Mod 调研、实现、兼容、诊断和验证能力，并在检测到 macOS 时自动采用 macOS 工作流。

## 修改范围

- 更新 `SKILL.md`：在描述和工作流中加入主机系统检测；macOS 环境优先读取专用参考文件。
- 新增 `references/macos-development.md`：集中描述 Steam 与 Victoria 3 路径发现、zsh 命令、日志定位、JSON/哈希/编码验证和 Windows 脚本兼容策略。
- 更新 `agents/openai.yaml`：默认提示要求先检测主机系统并选择对应工作流。
- 保留现有五份领域参考文件的功能与触发条件，不削减 Windows 或通用能力。

## macOS 工作流

1. 用 `uname -s` 检测 Darwin，并检查 `zsh`、`rg`、`python3`、`jq`、`shasum` 与任务需要的可选工具。
2. 从 Steam 默认目录和 `libraryfolders.vdf` 发现库目录；把游戏根目录、Workshop 根目录和目标 Mod 根目录作为带引号的变量传递，不把本机绝对路径写进实现。
3. 优先使用 macOS 自带或本机已验证的命令：`rg` 搜索、`jq` 或 `python3 -m json.tool` 校验 JSON、`shasum -a 256` 计算 SHA-256、`xxd` 检查 BOM。
4. 从 `~/Documents/Paradox Interactive/Victoria 3/logs` 按修改时间检查当前和轮转日志，并处理路径中的空格。
5. 遇到 `.ps1` 等 Windows 来源工具时先检测 `pwsh`。可用时以参数化路径运行；不可用或脚本内部仍使用 Windows 路径语义时，明确报告阻塞并请求用户决定安装 PowerShell 7 或另行移植，不能声称已经验证生成结果。
6. 避免依赖 GNU 专属参数、未安装的 `realpath`、Windows 路径分隔符和不带引号的空格路径。文件修改继续保留 BOM、换行符和编码。

## 边界与兼容性

- 不修改 Victoria 3 运行时脚本、生成器、元数据、依赖声明或加载顺序。
- 不改变持久变量、事件 ID、生成 ID、顶层覆盖或跨模块接口。
- 本次仅增强开发技能的环境适配；项目中现有 PowerShell 生成器是否原生兼容 macOS，需要在单独获准的生成器任务中验证或移植。

## 验证

- 检查 skill frontmatter、引用路径和 OpenAI 配置结构。
- 搜索未限定平台的 PowerShell、Windows 路径和 GNU-only 命令。
- 在当前 Darwin 环境验证路径发现与必需命令；把缺失的 `pwsh` 作为受控分支而非静默失败。
- 对照修改前后的领域能力和五份参考文件，确认功能没有减少。
- 运行 `git diff --check` 并报告最终工作树，不提交改动。
