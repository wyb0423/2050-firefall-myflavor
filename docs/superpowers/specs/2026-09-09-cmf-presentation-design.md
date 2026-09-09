# CMF 日志与事件接入（2026-09-09）

用户已确认全面检查、选择性增强，并追加进度条数值与悬浮因素明细。
基线：本地 CMF 1.65.0 / Victoria 3 1.13.*；Tech & Res 1.6、Firefall 0.1.1。

## 实现边界

- CMF 硬前置；保留 Mod ID、版本号、玩法条件、奖励、事件 ID 和存档变量含义。
- 13 条原有进度条、7 项日志接入 CMF 的进度条基础组件；悬浮覆盖条身和文字。
- 直接读取现有 JE/国家状态，不创建 CMF struct/cache。旧档无需注册或迁移新状态，日志移除没有新增对象需要清理。
- 显示从实际脚本值提取带标签的计算明细。粮仓合并档位公式由月度结算和展示共用；共同体及公共体条件拆为共享查询，保持原条件等价。
- 三支柱显示状态、恶化和修复计数；军事改革只复用 CMF 阶段格，不显示不存在的成功率。
- CMF 原生挂载槽替代原进度条容器，避免同时显示两套。GUI 只挂到本项目指定 JE，不覆盖 CMF/原版的全局面板。
- 国家作用域来自 JournalEntry.GetCountry，不使用 GetPlayer 代替所属国家；北美只读取当前工程州。
- 国际组织、侧栏、调度框架、数组/字典不接入：当前内容没有相应需要。

## 本地接口依据

- CMF gui/com_gui_progressbars.gui：com_progressbar_base、GetDesc/GetSecondDesc、进度数值。
- CMF gui/com_gui_journal_entry.gui：com_custom_widget_container_scripted_progress_bars 替代槽。
- CMF gui/com_journal_injects/enactment.gui：com_journal_entry_enactment_phase 及三个状态可见性覆盖块。
- 原版 localization/english/ip4_misc_01_l_english.yml 与 common/script_values/ip4_je_values.txt：Scope.GetScriptValueDesc、带 desc 的算术项。
- CMF gui/com_event_windows：所选窗口包含正文、风味段和选项；不依赖额外剧情人物。

## 日志逐项评估

| 技术 ID | 处理 |
|---|---|
| `je_ffpa_byz_restore_balkans` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_byz_restore_anatolia` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_byz_restore_oriens` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_byz_restore_aegyptus` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_byz_restore_africa` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_byz_restore_italia` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_byz_restore_spania` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_rebuild_anatolia` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_ottoman_commonwealth` | CMF 数值／悬浮进度条：progress |
| `je_ffpa_tur_gate_of_two_continents` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_gre_islands_and_mainland` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_byz_new_rome` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_byz_rhomaic_commonwealth` | 保留上游覆盖／旧档兼容职责 |
| `je_ffpa_byz_rhomaic_commonwealth_v2` | CMF 数值／悬浮进度条：progress |
| `je_ffpa_byz_restore_new_rome` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_via_egnatia` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_danube_thrace_corridor` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_aegean_maritime_network` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_southern_italian_harbors` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_nile_works` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_ifriqiya_coastal_network` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_anatolian_trunk_lines` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_levant_trade_corridor` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_mesopotamian_waterworks` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_italian_urban_axis` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_adriatic_arsenals` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_western_mediterranean_sea_lanes` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_spanian_littoral` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_mauretanian_coastal_road` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_alexandria_sinai_axis` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_na_local_recovery_v1` | CMF 数值／悬浮进度条：progress |
| `je_ffpa_tur_imperial_registers_v1` | CMF 数值／悬浮进度条：register |
| `je_ffpa_tur_bread_and_capital_v1` | CMF 数值／悬浮进度条：reserve |
| `je_ffpa_byz_public_polity_v1` | CMF 数值／悬浮进度条：pillars |
| `je_ffpa_byz_military_households_v1` | CMF 数值／悬浮进度条：pressure；改革阶段格 |
| `je_ffpa_tur_front_western_pact` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_front_mosul` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_front_rumelia` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_front_aegean_cyprus` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_front_levant` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_front_mesopotamia` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_front_egypt` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_front_ifriqiya` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_charter_of_the_porte` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_second_foundation_of_ankara` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_reconstruction_directorate` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_black_sea_lifeline` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_eastern_highlands_survey` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_cukurova_euphrates_works` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_ffpa_tur_new_straits_convention` | 保留原生条件布局；无适合替换的连续量或阶段 |
| `je_greek_nationalism` | 保留上游覆盖／旧档兼容职责 |
| `je_ottoman_empire_collapse` | 保留上游覆盖／旧档兼容职责 |

## 事件逐项评估

| 技术 ID | 窗口 |
|---|---|
| `ffpa_flavor.10` | event_window_widescreen_classic |
| `ffpa_flavor.100` | com_event_window_letter_paper |
| `ffpa_flavor.101` | com_event_window_letter_paper |
| `ffpa_flavor.102` | com_event_window_letter_paper |
| `ffpa_flavor.103` | com_event_window_letter_paper |
| `ffpa_flavor.104` | com_event_window_letter_paper |
| `ffpa_flavor.105` | com_event_window_letter_paper |
| `ffpa_flavor.106` | com_event_window_letter_paper |
| `ffpa_flavor.11` | com_event_window_letter_paper |
| `ffpa_flavor.12` | event_window_widescreen_classic |
| `ffpa_flavor.13` | com_event_window_letter_paper |
| `ffpa_flavor.14` | com_event_window_letter_paper |
| `ffpa_flavor.15` | 原生：通用成立通知或普通叙事／多选菜单 |
| `ffpa_flavor.2` | 原生：通用成立通知或普通叙事／多选菜单 |
| `ffpa_flavor.20` | event_window_widescreen_classic |
| `ffpa_flavor.21` | com_event_window_letter_paper |
| `ffpa_flavor.22` | event_window_widescreen_classic |
| `ffpa_flavor.23` | com_event_window_letter_paper |
| `ffpa_flavor.24` | com_event_window_letter_paper |
| `ffpa_flavor.25` | 原生：通用成立通知或普通叙事／多选菜单 |
| `ffpa_flavor.3` | event_window_superevent_modern |
| `ffpa_flavor.30` | event_window_widescreen_classic |
| `ffpa_flavor.31` | com_event_window_letter_paper |
| `ffpa_flavor.32` | com_event_window_letter_paper |
| `ffpa_flavor.33` | com_event_window_letter_paper |
| `ffpa_flavor.39` | 原生：通用成立通知或普通叙事／多选菜单 |
| `ffpa_flavor.4` | 原生：通用成立通知或普通叙事／多选菜单 |
| `ffpa_flavor.40` | event_window_widescreen_classic |
| `ffpa_flavor.41` | event_window_widescreen_classic |
| `ffpa_flavor.42` | event_window_widescreen_classic |
| `ffpa_flavor.43` | event_window_widescreen_classic |
| `ffpa_flavor.44` | event_window_widescreen_classic |
| `ffpa_flavor.45` | event_window_widescreen_classic |
| `ffpa_flavor.46` | event_window_widescreen_classic |
| `ffpa_flavor.47` | com_event_window_telegram |
| `ffpa_flavor.5` | 原生：通用成立通知或普通叙事／多选菜单 |
| `ffpa_flavor.50` | com_event_window_telegram |
| `ffpa_flavor.51` | com_event_window_letter_paper |
| `ffpa_flavor.52` | com_event_window_letter_paper |
| `ffpa_flavor.6` | event_window_superevent_modern |
| `ffpa_flavor.7` | event_window_superevent_modern |
| `ffpa_flavor.8` | 原生：通用成立通知或普通叙事／多选菜单 |
| `ffpa_na_flavor.1` | com_event_window_letter_image |
| `ffpa_na_flavor.2` | com_event_window_letter_image |
| `ffpa_tur_flavor.1` | com_event_window_letter_paper |
| `ffpa_tur_flavor.10` | com_event_window_letter_paper |
| `ffpa_tur_flavor.11` | com_event_window_letter_paper |
| `ffpa_tur_flavor.12` | com_event_window_letter_paper |
| `ffpa_tur_flavor.13` | event_window_superevent_modern |
| `ffpa_tur_flavor.20` | com_event_window_letter_paper |
| `ffpa_tur_flavor.21` | com_event_window_letter_paper |
| `ffpa_tur_flavor.22` | com_event_window_letter_paper |
| `ffpa_tur_flavor.23` | event_window_superevent_modern |
| `ffpa_tur_flavor.30` | com_event_window_letter_paper |
| `ffpa_tur_flavor.31` | com_event_window_letter_paper |
| `ffpa_tur_flavor.32` | com_event_window_letter_paper |
| `ffpa_tur_flavor.33` | event_window_superevent_modern |
| `ffpa_tur_flavor.40` | event_window_widescreen_classic |
| `ffpa_tur_flavor.41` | event_window_widescreen_classic |
| `ffpa_tur_flavor.50` | event_window_widescreen_classic |
| `ffpa_tur_flavor.51` | event_window_widescreen_classic |
| `ffpa_tur_flavor.52` | event_window_widescreen_classic |
| `ffpa_tur_flavor.60` | 原生：通用成立通知或普通叙事／多选菜单 |
| `ffpa_tur_flavor.61` | event_window_widescreen_classic |
| `ffpa_tur_flavor.62` | event_window_widescreen_classic |
| `ffpa_tur_flavor.63` | event_window_widescreen_classic |
| `ffpa_tur_flavor.64` | event_window_widescreen_classic |
| `ffpa_tur_flavor.65` | event_window_widescreen_classic |
| `ffpa_tur_flavor.66` | event_window_widescreen_classic |
| `ffpa_tur_flavor.67` | event_window_widescreen_classic |
| `ffpa_tur_flavor.68` | event_window_widescreen_classic |
| `ffpa_tur_flavor.69` | com_event_window_telegram |
| `ffpa_tur_flavor.70` | com_event_window_telegram |
| `ffpa_tur_flavor.71` | com_event_window_telegram |
| `ffpa_tur_flavor.72` | com_event_window_telegram |
| `ffpa_tur_flavor.73` | com_event_window_telegram |
| `ffpa_tur_flavor.74` | com_event_window_telegram |
| `ffpa_tur_flavor.75` | com_event_window_telegram |
| `ffpa_tur_flavor.76` | com_event_window_telegram |
| `ffpa_tur_flavor.77` | com_event_window_telegram |
| `ffpa_tur_flavor.78` | com_event_window_telegram |
| `ffpa_tur_flavor.79` | com_event_window_telegram |
| `ffpa_tur_flavor.80` | com_event_window_telegram |
| `ffpa_tur_flavor.81` | com_event_window_telegram |
| `ffpa_tur_flavor.82` | com_event_window_telegram |
| `ffpa_tur_flavor.83` | com_event_window_telegram |
| `ffpa_tur_flavor.84` | com_event_window_telegram |
| `ffpa_tur_flavor.90` | com_event_window_letter_paper |
| `ffpa_tur_flavor.91` | com_event_window_letter_paper |
| `ffpa_tur_flavor.92` | com_event_window_telegram |
| `formation.3` | 原生：通用成立通知或普通叙事／多选菜单 |

## 验证与限制

静态检查涵盖依赖/GUI 类型/资源/本地化、共享条件等价、粮仓计算等价、原事件效果和 JE 玩法结构保留。
本机禁止启动游戏。GUI 布局、中文字体、悬浮作用域、选项滚动、读档即时呈现、AI 与月度时序均须游戏内验收。
启动器当前活动播放集未启用完整 Firefall/Tech & Res/FFPA 栈；源码栈检查不代表该播放集运行验证。

实施顺序：接口核对 → 日志数值/悬浮 → 改革阶段 → 事件分类 → 最终栈静态检查。

### 本轮静态结果

- 352组算术场景通过：簿册边界合法性、权门三阶段与法律／地主／税籍组合、粮仓全部16种异常组合与饥荒开关。
- 52个日志与91个事件对基线 `2904f934d4a82694521f7f2e1af31cd4c7241acf` 的结构对比通过：除 `widget` / `gui_window` 外的字段完全一致。
- 共同体、公共体拆出的查询因素递归展开后与基线条件完全相同。
- 双语158个新增键；所有本地化共1397键／语言，BOM、格式、引用与概念检查通过。
- 北美两项检查、TUR路线身份检查、CMF引用／GUI挂载／资源检查与 `git diff --check` 通过。
- 目标栈中 CMF 的 `eventwindow.gui`、`com_gui_journal_entry.gui`、`com_gui_progressbars.gui` 没有被本地 Tech & Res 或 Firefall 同路径覆盖。完整活动播放集仍不等于此目标栈。
- 改革可选项目变量在读取前受保护；尚未建立的修复计数通过只读脚本值显示0。三支柱修复状态使用蓝色，避免作为最高风险显示。

复验命令（各根目录由本机发现提供）：

```sh
python3 tests/check_cmf_presentation.py --game-root "$GAME_ROOT" --cmf-root "$CMF_ROOT" --upstream "$TECHRES_ROOT" --upstream "$FIREFALL_ROOT"
python3 tests/validate_localization.py --game-root "$GAME_ROOT" --upstream "$CMF_ROOT" --upstream "$TECHRES_ROOT" --upstream "$FIREFALL_ROOT"
python3 tests/check_north_america_local_recovery.py
python3 tests/check_north_america_preflight.py --game-root "$GAME_ROOT" --firefall-root "$FIREFALL_ROOT" --techres-root "$TECHRES_ROOT"
python3 tests/test_tur_route_interest_group_identity.py
git diff --check
```


## 第二批：危机与工程明细

适用上游仍为 Victoria 3 1.13、CMF 1.65.0、本地 Tech & Res 与 Firefall；不改变原有判定、奖励、持久变量或周期入口。

- 四项常驻治理显示8个危机计数、失败阈值与清零／衰减规则。公共体修复中仍计作破裂；解除权门结构性问题不会清空高压计数。
- 15项地区工程从原 JE 生成56组逐州条件，显示市场接入、动乱、建筑等级及逐项达标状态，提供原生州定位。开工领土单列；例如埃格纳提亚的东色雷斯只属开工领土。分裂州按实际 state 单独判断，不合并建筑。
- 北美按既有三条路线列出16类建筑，显示已建成等级、就业率、合格贡献；缺失或就业不足的建筑贡献为0。目标州与建筑采用原生定位／详情入口，保留原有目标有效性门控。

运行 `python3 tools/generate_cmf_project_widgets.py` 更新生成物；`--check` 只核对。生成仅发生在开发阶段，不增加游戏周期扫描。

新增 `python3 tests/check_cmf_project_views.py` 验证展示与实际条件的一致性及表达式结构。对比上一提交确认三份 JE 除 widget 外全部定义保持一致，原有 script values 保持一致。静态检查不能证明引擎渲染、列表高度、按钮行为或悬浮 scope；遵守不启动本机游戏的约束，以上仍待游戏内验收。
