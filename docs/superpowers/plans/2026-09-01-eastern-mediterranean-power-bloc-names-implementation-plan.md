# 东地中海国家集团核心名称池实施计划

## 目标

按已批准设计为 TUR 新增 8 个、BYZ 新增 7 个国家集团随机候选名称，并补齐双语本地化、项目说明和模块所有权登记。实现只扩展 `common/power_bloc_names/`，不覆盖原版对象，不修改集团身份、效果、AI、调度或存档状态。

## 实施步骤

1. 新建 `common/power_bloc_names/ffpa_eastern_mediterranean_power_bloc_names.txt`。
   - TUR 两个 Tag 通用条目直接检查 `c:TUR ?= this`。
   - TUR 六个路线条目调用既有 `ffpa_tur_has_*_state_project_v1` 查询。
   - BYZ 两个 Tag 通用条目直接检查 `c:BYZ ?= this`。
   - BYZ 五个政体条目复用当前动态国名已工作的法律条件。
2. 在 `localization/english/ffpa_l_english.yml` 与 `localization/simp_chinese/ffpa_l_simp_chinese.yml` 的国家身份切片加入相同的 15 个本地化键，保持 UTF-8 BOM。
3. 窄改 README 的现有 TUR/BYZ 身份说明，登记国家集团候选名称。
4. 更新 AGENTS 的国家身份核心文件清单、行为与验证清单，不改变外部模块接口。

## 验证步骤

1. 比较原版、Tech & Res、Firefall 与本项目的 15 个技术 ID，确认无重复。
2. 验证运行时文件恰有 15 个唯一顶层键，所有 trigger 为 country scope 且无状态写入。
3. 检查三个 TUR 查询 trigger 和 BYZ 法律 ID 可解析。
4. 对比英中新增键集合、UTF-8 BOM 与英文名称长度（不超过 30 字符）。
5. 检查花括号、字符串、注释、JSON、`git diff --check` 和最终工作树。
6. 搜索现有轮转日志中的新增 ID；未启动含本次改动的游戏时，把解析、候选池和界面行为列为待游戏内验证。

## 工作树保护

当前工作树另有 TUR 边疆收复相关的 scripted effect、scripted trigger、规格和实施计划改动。本任务不编辑、格式化、暂存或提交这些文件，也不把它们计入本任务成果。
