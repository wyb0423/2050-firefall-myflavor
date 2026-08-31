# macOS 开发工作流

本文件只负责宿主环境适配。Victoria 3 数据语义、加载顺序、作用域、存档接口和验证标准仍由主技能及其他领域参考文件决定。

## 进入条件与工具检查

先确认当前系统，不能仅根据路径外观猜测：

```zsh
uname -s
```

输出为 `Darwin` 时使用本流程。开工前检查任务会用到的命令：

```zsh
for v3_cmd in git rg zsh python3 shasum xxd; do
  command -v "$v3_cmd" || printf 'missing command: %s\n' "$v3_cmd"
done
command -v jq || true
command -v pwsh || true
```

`jq` 可由 Python 的 JSON 模块替代；`pwsh` 只在运行 PowerShell 来源工具时需要。缺少工具时先说明影响，不自动安装软件或修改系统配置。

## 发现本机路径

把路径视作当前环境输入。以下变量只用于当前 shell，不应写入生成器、Mod 数据、报告或版本控制：

```zsh
v3_repo_root="$(git rev-parse --show-toplevel)"
v3_steam_root="${HOME}/Library/Application Support/Steam"
v3_library_file="${v3_steam_root}/steamapps/libraryfolders.vdf"
v3_user_root="${HOME}/Documents/Paradox Interactive/Victoria 3"
```

先检查 Steam 默认库候选：

```zsh
v3_game_root="${v3_steam_root}/steamapps/common/Victoria 3/game"
v3_workshop_root="${v3_steam_root}/steamapps/workshop/content/529340"
test -d "$v3_game_root" && printf '%s\n' "$v3_game_root"
test -d "$v3_workshop_root" && printf '%s\n' "$v3_workshop_root"
```

若默认库不存在或依赖不完整，读取而不是猜测外置 Steam 库：

```zsh
test -f "$v3_library_file" && rg -n '"path"[[:space:]]+' "$v3_library_file"
```

对 `libraryfolders.vdf` 中每个实际库根目录分别验证：

```text
<library>/steamapps/common/Victoria 3/game
<library>/steamapps/workshop/content/529340
```

游戏和 Workshop 可能位于不同 Steam 库。分别验证目录、目标 Workshop ID 与版本，不能假定两者共享同一根目录。路径含空格时始终使用双引号；可复用实现使用参数，不嵌入 `/Users/<name>/...`。

## zsh 与 BSD 用户空间规则

- 优先使用 `rg --files` 和 `rg -n`，不要用宽泛的 `find /` 扫描整机。
- 给每个路径变量加双引号。处理多文件结果时使用 `-print0`、`-0` 或工具原生的多路径参数，不能用未加引号的命令替换拆词。
- 使用 `/` 作为文件系统路径分隔符。Paradox Script 中的技术 ID 和字符串只按游戏语义修改，不能因宿主平台转换。
- macOS 默认是 BSD 用户空间。不要无条件使用 GNU 专属的 `sed -i`、`stat -c`、`date -d`、`readlink -f` 或 `sha256sum`。
- 需要规范化现有目录时可在目录内使用 `pwd -P`。不要假定系统安装了 `realpath`。
- 文件修改优先使用代理提供的补丁工具。确需命令行改写时先保留编码和换行特征，并写入临时文件后再做窄替换。
- 默认文件系统常为大小写不敏感，但游戏数据库键、Git 路径和发布包仍应保持精确大小写。

常用验证的 macOS 等价命令：

```zsh
jq empty -- .metadata/metadata.json
python3 -m json.tool .metadata/metadata.json >/dev/null
shasum -a 256 path/to/generated-file.txt
file path/to/file
xxd -l 3 path/to/localization.yml
git diff --check
```

优先使用 `jq` 校验 JSON；只有 `jq` 不可用时才使用 Python 备用命令。Victoria 3 本地化通常需要 UTF-8 BOM，`xxd -l 3` 应显示 `efbbbf`；不要为了统一格式重写无关文件。

## 运行 Windows 来源工具

`.ps1` 文件不等于可在 macOS 上直接运行。开始前检查三件事：

1. `pwsh`（PowerShell 7）是否存在；
2. 脚本是否使用盘符、反斜杠子路径、Windows-only cmdlet 或注册表等平台语义；
3. 输出路径、排序、编码和换行是否会因平台变化而改变。

可以先做窄搜索：

```zsh
command -v pwsh || true
rg -n "[A-Za-z]:\\\\|Join-Path.*['\"][^'\"]*\\\\|ConvertFrom-Json|Get-FileHash" tools --glob '*.ps1'
```

只有工具和脚本都通过检查后才参数化运行：

```zsh
pwsh -NoProfile -File "$v3_repo_root/tools/<generator>.ps1" \
  -GameRoot "$v3_game_root" \
  -WorkshopRoot "$v3_workshop_root" \
  -OutputRoot "$v3_repo_root"
```

若缺少 `pwsh`，或脚本仍依赖 Windows 路径语义，应停止对应生成步骤并说明：哪些静态检查仍可完成、哪些生成器断言尚未运行、是否需要用户批准安装 PowerShell 7 或另开任务移植脚本。不能用手工编辑生成产物冒充成功生成。

生成器需要确定性验证时连续运行两次，对生成脚本和报告分别执行 `shasum -a 256`，并比较同一路径的两组结果。哈希一致只证明输出稳定，不证明游戏语义正确。

## 日志和运行时证据

macOS 的默认日志目录候选为：

```zsh
v3_log_root="${v3_user_root}/logs"
```

按修改时间列出当前和轮转日志：

```zsh
find "$v3_log_root" -maxdepth 1 -type f \
  \( -name 'debug*.log' -o -name 'error*.log' -o -name 'game*.log' \) \
  -exec ls -lt {} +
```

跨轮转日志搜索稳定标识：

```zsh
rg -n 'TARGET_PREFIX|technical_id' "$v3_log_root" \
  --glob 'debug*.log' --glob 'error*.log' --glob 'game*.log'
```

启动游戏、打开 GUI 或安装工具会改变外部状态，只在用户请求或批准后执行。无法启动时，交付中分别报告静态证据、生成器证据、已有日志证据和待游戏内验证项。

## macOS 交付检查

- 实际使用的游戏、Workshop、用户数据和目标 Mod 根目录均已解析，但没有写入可复用文件。
- 所有含空格路径均被引用；没有把 PowerShell 语法直接交给 zsh，也没有把 zsh 语法交给 PowerShell。
- Windows 来源工具已完成能力检查；未运行的生成器和原因被明确记录。
- JSON、哈希、BOM、换行和 `git diff --check` 使用了当前 macOS 可用工具。
- 最终数据库、存档 API、模块所有权和运行时证据仍按主技能标准验证，没有因平台适配降低要求。
