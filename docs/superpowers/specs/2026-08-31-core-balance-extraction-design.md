# Core Balance 模块剥离设计

## 1. 目标

把当前 `2050-firefall-myadapter` 中的以下三个既有模块整体剥离为一个同级、可独立启用的新 Victoria 3 Mod，不改变脚本行为、技术 ID、存档接口或最终加载结果：

- 统一战争 10% 恶名适配；
- 殖民 AI、殖民边界与殖民制度；
- 全局平衡与通用生命周期。

新旧 Mod 同时按指定顺序加载时，最终数据库应与拆分前等价。原 Mod 与新 Mod 不互相声明依赖，也不保留重复定义。

## 2. 新 Mod 身份

- 目录：`../2050-firefall-core-balance`
- 显示名：`2050 Firefall — Core Balance Adapter`
- Mod ID：`com.wyb.2050-firefall-core-balance`
- 初始版本：`1.0.0`
- 支持版本：`1.13.*`
- 依赖：
  - `2050: The Fire Falls`：`alter_time_2050_fire_falls`，版本 `0.1.*`
  - `[1.13] Tech & Res`：`tech.res`，版本 `1.*`

新 Mod 不声明对 Auto-Apply PMs、Auto-Apply Automation PMs 或原 Personal Adapter 的依赖。

## 3. 采用方案

采用彻底剥离方案：每个运行时顶层键只有一个所有者。新 Mod 直接拥有三个模块的全部定义；原 Mod 删除这些定义，只保留自动 PM、建筑清理和东地中海功能。

未采用的方案：

- 原 Mod 依赖新 Mod：会削弱两个包的独立性；
- 在原 Mod 保留桥接副本或兼容定义：会产生重复顶层键、加载顺序冲突或二次调度风险。

## 4. 整文件迁移清单

以下 12 个运行时文件原样移动到新 Mod，保留相对路径、编码、换行和内容：

1. `common/ai_strategies/zzzz_ffpa_colonial_region_stances.txt`
2. `common/defines/zzzz_ffpa_colonial_shape_defines.txt`
3. `common/diplomatic_plays/ffpa_union_war_plays.txt`
4. `common/game_rules/ffpa_union_war_rules.txt`
5. `common/history/global/zzz_ffpa_global.txt`
6. `common/institutions/00_institutions.txt`
7. `common/production_methods/ffpa_trade_center.txt`
8. `common/script_values/ffpa_union_war_values.txt`
9. `common/scripted_effects/ffpa_innovation_effects.txt`
10. `common/scripted_effects/ffpa_union_war_effects.txt`
11. `common/static_modifiers/ffpa_modifiers.txt`
12. `common/war_goal_types/ffpa_union_war_goal.txt`

其中 `common/institutions/00_institutions.txt` 整体归新 Mod 所有。`institution_colonial_affairs` 与其余六个制度定义不会在原 Mod 留下副本。

## 5. on_action 接缝拆分

当前 `common/on_actions/ffpa_on_actions.txt` 同时调度创新、自动 PM 日志和建筑清理，不能整文件移动。

### 5.1 新 Mod 所有的入口

新 Mod 新建自己的 on_action 文件，并继续拥有以下既有包装 ID：

- `ffpa_initialize_innovation_cap`
- `ffpa_monthly_refresh_innovation_cap`

行为保持为：

- `on_game_started_after_lobby` 调用 `ffpa_initialize_innovation_cap`；
- 初始化包装对所有国家调用 `ffpa_refresh_innovation_cap`；
- `on_monthly_pulse_country` 调用 `ffpa_monthly_refresh_innovation_cap`；
- 月度包装在当前国家 scope 调用 `ffpa_refresh_innovation_cap`。

两个创新包装不再调用原 Mod 的 `ffpa_ensure_auto_pm_compat_journal`，从而使新 Mod 可以脱离原 Mod 独立运行。

### 5.2 原 Mod 保留的入口

原 Mod 的 `common/on_actions/ffpa_on_actions.txt` 改为只负责：

- 新游戏启动时对所有国家确保自动 PM/建筑清理日志和默认变量；
- 每月对当前国家执行相同的幂等确保 effect；
- 每半年执行原有建筑清理扫描。

为避免与新 Mod 的既有创新包装 ID 冲突，原 Mod 使用新的非持久包装 ID：

- `ffpa_initialize_adapter_journals`
- `ffpa_monthly_ensure_adapter_journals`

底层 `ffpa_ensure_auto_pm_compat_journal`、建筑清理变量、扫描 effect 和调度频率不变。on_action 包装 ID 不进入存档，改名不改变持久状态。

## 6. 本地化拆分

新 Mod 新建英文和简体中文本地化文件，并从原文件迁移以下 10 个键：

- `ffpa_postwar_population_recovery`
- `ffpa_postwar_population_recovery_desc`
- `ffpa_double_innovation_cap`
- `ffpa_double_innovation_cap_desc`
- `ffpa_double_technology_spread`
- `ffpa_double_technology_spread_desc`
- `ffpa_union_war_annex_country_tenth`
- `FFPA_UNION_WAR_INFAMY_SCALE`
- `setting_uw_infamy_tenth`
- `setting_uw_infamy_tenth_desc`

两种语言必须保持相同键集合并保留 UTF-8 BOM。原 Mod 删除这 10 个键，不留重复本地化。

殖民模块没有自有玩家可见本地化键，继续使用原版或上游键。

## 7. 文档与元数据

新 Mod 创建：

- `.metadata/metadata.json`
- `README.md`
- `AGENTS.md`
- `.gitignore`

新 README 只描述三个迁入模块、依赖、加载顺序、覆盖风险、存档接口和验证方式。

原 Mod 更新：

- README 删除已迁出功能的归属描述，并把完整推荐顺序改为：Tech & Res → Auto-Apply PMs → Auto-Apply Automation PMs → Firefall → Core Balance Adapter → Personal Adapter；
- AGENTS 更新模块所有权、总体依赖图、共享接缝、覆盖登记和未来拆分说明；
- `.metadata/metadata.json` 的名称、ID、版本、支持版本和依赖保持不变，只修改 `short_description`，不再声称拥有 personal balance。

本次不提升原 Mod 的 `1.2.0` 版本，也不执行 Git 提交。

## 8. 加载顺序与运行关系

推荐完整顺序：

1. `[1.13] Tech & Res`
2. `Auto-Apply PMs`
3. `Auto-Apply Automation PMs`
4. `2050: The Fire Falls`
5. `2050 Firefall — Core Balance Adapter`
6. `FFPA — Firefall Flavor Pack`

新 Mod 必须在 Firefall 与 Tech & Res 之后加载，以确保 `REPLACE:`、`INJECT:`、`NDiplomacy` 和同名制度定义针对最终上游数据库生效。

新旧 Mod 之间不再直接调用 scripted effect、读取临时变量或共享自有顶层键。两者只各自向原版 on_action 数据库登记模块包装入口；`on_game_started_after_lobby` 和 `on_monthly_pulse_country` 是有意共享的原版扩展接缝，模块包装 ID 本身保持唯一。

## 9. 存档兼容

以下技术接口原样保留：

- `ffpa_innovation_cap_mirror_value`
- `ffpa_refresh_innovation_cap`
- `ffpa_double_innovation_cap`
- `ffpa_double_technology_spread`
- 统一战争 game rule、script value、外交战、战争目标和 effect ID
- 人口恢复与贸易 PM 注入 ID

物理路径和 Mod ID 变化不改变这些脚本键的含义。旧存档需要同时启用新 Mod 与拆分后的原 Mod，才能继续获得拆分前的完整功能。

原单体版本与拆分后的两个版本不得同时以副本形式加载；同名顶层键只能由新文件集合提供一次。

## 10. 验证方案

### 10.1 文件与顶层键

- 记录拆分前三个模块的顶层键清单和文件 SHA-256；
- 验证新 Mod 对应 12 个整文件哈希不变；
- 验证“新 Mod + 原 Mod”的自有顶层键并集等于拆分前，并且交集为空；有意共同登记的原版 on_action 接缝按其模块包装列表比较，不作为重复自有键；
- 搜索原 Mod，确认不再含三个迁出模块的自有定义和本地化键；
- 搜索新 Mod，确认不含自动 PM、建筑清理或东地中海运行时定义。

### 10.2 静态结构

- 两份 metadata 均可解析；
- 全部修改脚本的括号、字符串、注释和顶层结构正常；
- 英文与简体中文键集合分别一致且无重复；
- 本地化保留 UTF-8 BOM；
- 两个工作树分别执行 `git diff --check`；若新 Mod 尚未初始化 Git，则执行等价空白检查并明确报告。

### 10.3 功能回归

- 新游戏只初始化一次 50 年人口恢复；读档不重置持续时间；
- 创新上限启动刷新、月度刷新和旧存档修复均正常；
- 科技扩散 modifier 不重复叠加；
- 统一战争 UI 顺序、AI 估值和四种开战分支保持不变；
- 殖民地区评分、殖民边界和殖民事务增长保持不变；
- 贸易中心容量及所有贸易数量 PM 注入保持不变；
- 原 Mod 的自动 PM 日志、建筑清理日志、AI 默认变量和半年扫描仍在原频率到达；
- 东地中海 on_action 与事件不受影响。

无法启动游戏时，交付分别报告静态确认、上游比较、日志证据和仍需游戏内验证的项目。

## 11. 成功标准

- 新 Mod 能在不加载原 Personal Adapter 时独立提供三个迁入模块；
- 原 Personal Adapter 能在不加载新 Mod 时独立提供剩余功能，且不存在缺失 effect 调用；
- 同时加载两者时，玩家可见行为、调度频率、数值、技术 ID 和存档状态与拆分前一致；
- 除有意共同登记的原版 on_action 接缝外，没有重复自有顶层键、重复本地化、反向依赖或新的机器绝对路径。
