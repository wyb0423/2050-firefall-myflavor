# CMF 能力索引

核对基线：2026-09-09，本地 CMF 1.65.0 / 声明支持 Victoria 3 1.13.*。这不是游戏内验证，也不是版本兼容保证。路径均相对发现的 CMF_ROOT；接口和资源以当前本地源码为准。

来源：[上游 Wiki](https://github.com/Victoria-3-Modding-Co-op/Community-Mod-Framework/wiki)、本地 `.metadata/metadata.json` 和表中源码。


下列路径相对 CMF 根目录；“入口”表示后续实现时优先读哪里，不代表每个模块已逐行审计或通过实机测试。

| 能力 | 适用需求 | 本地入口与接入要点 |
|---|---|---|
| Mod 检测协议 | 同时兼容多个风味或大修 Mod | `common/scripted_triggers/0_community_mod_triggers.txt` 提供默认假值；所属 Mod 用 `REPLACE_OR_CREATE` 将自己的检测设为真。`zz_com_detection_trigger.txt` 定义 `community_framework_is_active`。不是自动扫描已安装 Mod。 |
| 通用变量操作 | 累加计数、保存日志作用域、更新 map | `common/scripted_effects/com_general_effects.txt`：`com_change_variable`、local/global 变体、clamp 变体、`com_save_journal_to_variable`、`com_update_value_in_variable_map` 等。注意每个 effect 的参数与当前作用域。 |
| 日志 UI 扩展 | 自定义标题、角色、建筑、公司、DLC 标识 | `gui/com_journal_injects/injects.gui` 及同目录分模块 GUI；JE 的 `widget` 必须填写正确的 `gui/name/container` 三项。 |
| 日志分组显隐 | 把全局组织或后台日志移出普通日志页 | `com_journal_entry_effects.txt`：`com_hide_journal_entry_group`、`com_show_journal_entry_group`，使用全局分组列表，影响范围不是单个国家。 |
| 样式进度条 | 显示当前值、趋势、目标线、分段 | `com_progressbar_effects.txt` 与 `common/journal_entries/com_progress_in_style.txt`。支持颜色、drift、target、levels、高亮、显隐；需原生 scripted progress bar + CMF widget + 初始化 + 清理。 |
| 仿立法阶段组件 | 三阶段改革、成功/停滞概率、阶段推进显示 | `com_enactment_journal_effects.txt` 和 `gui/com_journal_injects/enactment.gui`。`com_setup_enactment_journal` 写入 `com_enactment_widget` map；概率与阶段显示不会替作者执行抽签、推进或结算。 |
| 国际局势 | 双方对抗、阶段进度、结局信息 | `com_international_situation_effects.txt`、`common/journal_entries/com_international_situation.txt`、`gui/com_journal_injects/situation_widgets.gui`。新接口有插图、左右角色与标题、阶段、结局、索引进度；文件后半部分明确标记旧接口。 |
| 国际组织 | 组织面板、领袖、主席、总部、成员展示 | `com_international_organization_effects.txt`、同名 JE 示例、`gui/com_gui_international_organizations_panel.gui`。支持分组注册、contextless JE 和侧栏激活；成员条件、投票、会费、奖励仍由业务 Mod 编写。 |
| 自定义侧栏按钮 | 给国家机制提供独立入口 | `gui/com_gui_sidebar.gui`、`common/scripted_guis/example_button_sgui.txt`。当前使用 flag 列表注册，flag 名对应同名 ideology（图标/文案）与 scripted GUI（显隐/可用/点击）。 |
| 事件窗口样式 | 信件、电报、报纸、超事件、多角色事件 | `gui/com_event_windows/` 提供 letter、telegram、superevent、europa、character、widescreen、text 等布局。需核对具体窗口类型和要求的角色/变量上下文。 |
| 角色肖像控制 | 改动作、镜头、环境、背景与粒子 | `com_character_animation_effects.txt`、`com_character_background_effects.txt`，配套 `gui/00_com_character.gui` 等消费者。支持单项和组合设置、全局展示覆盖、移除肖像覆盖；不是新增动画资产的生成工具。 |
| 角色交互阻断 | 保护剧情角色免遭流放或退休 | `com_general_effects.txt` 的 block/unblock 系列及 `common/character_interactions/com_character_interactions.txt`；在 CHARACTER scope 调用，可设置原因文本。 |
| 继承/摄政/成立事件阻断 | 自定义君主或建国流程 | `common/on_actions/cmf_heir_blocker.txt`、`com_formation_event_blocker.txt`、`events/00_com_regency_event_blocker.txt` 中有 `no_heirs`、`com_no_formation_events`、`com_no_regencies`；设置前检查实际读取作用域。不是通用“关闭任何 on_action”。 |
| 法律显隐挂钩 | 按剧情隐藏原版法律 | `common/scripted_triggers/com_law_blocker_triggers.txt` 提供主/替代 trigger，`common/laws/` 中相应法律消费它们。trigger 存在不等于每个法律已接入，必须查引用。 |
| 政治运动兼容 | 多 Mod 的意识形态、支持权重协作 | `common/political_movements/ycom_*.txt`、`com_political_movement_triggers.txt`、`ycom_ideology_trigger_overrides.txt` 和各 Mod 的 script values。是共同维护的覆盖与挂钩体系，不是任意新意识形态自动注册。 |
| 政党名称兼容 | 国家、文化、Mod 特定党名 | `common/parties/` 用 `first_valid`、检测 trigger 和本地化做选择；添加分支时考虑优先次序和其他 Mod 覆盖。 |
| 通用角色名字兼容 | 姓名、头衔显示与 Universal Names 共存 | `common/customizable_localization/00_com_universal_names.txt`：`GetUniversalFullName`、带头衔/无格式变体、`GetUniversalTitle`；历史人物旧接口在注释中标记不支持。 |
| 每周调度 | 指定星期对所有国家触发 on_action | `com_weekly_event.txt`、`com_weekly_on_action.txt`、`com_weekly_event_script_values.txt`。全局月脉冲预排当月各周，星期 0–6；不是 JE 原生周脉冲的必要替代。 |
| Struct 对象容器 | 保存独立结构、给 UI 持久引用对象 | `com_struct.txt`、`common/character_templates/com_struct.txt`、`com_save_void_characters.txt`。实际用特殊角色承载，存在生命周期与月度维护成本，不能当无成本通用对象。 |
| Float Array | 固定长度数值数组、索引访问 | `com_floatarray_effects.txt`、`com_floatarray_utils.txt`、`com_floatarray_triggers.txt`。支持 8/16/32/64/128/256/512；读写使用共享工作变量，需考虑嵌套覆盖。 |
| Dict / scope-value map | 数字键值、scope 到数值映射 | `common/scripted_effects/com_dict.txt` 和 `common/script_values/com_dict.txt`。数值打包实现有范围约束；优先评估游戏已有 variable map，不盲目使用内部工具。 |
| 解散 Power Bloc | 剧情中结束势力集团 | `com_dissolve_power_bloc.txt` 的 `com_disband_power_bloc` 配合 `can_lead_power_bloc` 覆盖；临时切换领袖国家类型触发资格重算，需针对实际政体/大修做运行验证。 |
| 更多 PM 的 UI 容纳 | 大量生产方式/生产方式组 | `gui/MPM_custom_types.gui` 和 `00_MPM_*.gui` 使用滚动区域扩展建筑相关面板。属于展示能力，不是自动选择 PM 的算法。 |
| Mod/DLC 展示兼容 | 在前端呈现 Mod 扩展内容 | `gui/00_MDF_frontend_dlc.gui` 和 `data_binding/MDF_macros.txt` 区分原版与 Mod DLC 项；是显示层能力。 |
| 共用按键与调试 | GUI 快捷键、旗帜和容器检查 | `input_profile/default.profile`、`com_debug_sgui.txt`、`common/console_command_macros/com_macros.txt`；已有保留按键需避让，宏 `com_flag` / `com_container` 打开查看器。 |
| 图形和绑定工具 | 修正图标、UI 粒子、逻辑与取值宏 | `gfx/interface/icons/timed_modifier_icons/`、`gfx/particles/`、`gfx/models/particles/`、`data_binding/com_macros.txt`。已看到粒子与图标资产；不因上游栏目含 Shaders 就推断本地存在独立 shader 源文件。 |

