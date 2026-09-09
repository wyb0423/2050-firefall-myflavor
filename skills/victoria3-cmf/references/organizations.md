# 国际组织与局势

基线：CMF 1.65.0，2026-09-09 源码核对；路径相对 CMF_ROOT。这里是接入配方，不是已经实现的投票/外交系统。

## 国际组织

最小文件集合：自有 JE、分组（使用 CMF 已有分组时无需新建）、本地化、初始化入口；业务需要时再加 scripted buttons/effects。读取以下真实链路：

- `common/journal_entries/com_international_organization.txt`
- `common/scripted_effects/com_international_organization_effects.txt`
- `common/history/global/00_com_global.txt`
- `common/scripted_guis/com_international_organizations_sgui.txt`
- `gui/com_journal_injects/interorg_widgets.gui`
- `gui/com_gui_international_organizations_panel.gui`

先确认需求是全局 contextless JE，还是每国实例；不要把普通国家 JE 的 owner 假设套到 contextless 对象。

以超国家组织为起点，JE 挂载：

```text
group = je_group_com_supranational_organizations
widget = {
    gui = "gui/com_journal_injects/interorg_widgets.gui"
    name = "widget_com_supranational_organization"
    container = "custom_widget_container_je_icon"
}
```

在 JE immediate 内进入 `scope:journal_entry`，设置 `com_interorg_leader_var` 为有效国家 scope、`com_interorg_chair_var` 为有效角色 scope。用 `com_set_international_organization_headquaters_effect = { state_region = s:STATE_FLANDERS }` 的参数形态设置总部；替换为需求中的 state region，并保留上游 headquaters 拼写。该函数不是 headquarters，也不是 state scope。

`com_hide_all_journal_elements_for_interorg_effect = yes` 会隐藏普通按钮等内容；若需要保留普通按钮，评估 `com_hide_non_button_journal_elements_for_interorg_effect`。只隐藏需求中不再需要的部分。

全局 `com_activate_interorg_sidebar = yes` 激活组织侧栏并隐藏内置组织分组。新自定义分组用 `com_add_journal_group_to_interorg_list` 注册，或用 `com_add_journal_group_to_interorg_list_and_hide_from_journal` 同时隐藏普通日志展示。全局显隐影响所有国家，不当单国权限控制。注册需幂等；默认组已有注册，不必重复。

添加 contextless 实例可检查 `com_add_interorg_journal_entry = { type = my_organization }` 的实现：它包装 add_contextless_journal_entry 和提示；确认实例尚未存在再调用。实例参与条件、非参与国能否查看，按实际 JE 的 should_be_involved / should_show_when_not_involved 设计。

测试源码中的英国、普鲁士、固定总部和测试按钮仅为例子。成员加入/退出、会费、投票、AI 与奖励需自有逻辑；不要在完成 UI 注册后宣称它们已具备。

生命周期：组织结束时按实际 JE 终止机制销毁/结束实例，清理业务持有的引用与持续效果；更换领袖、主席死亡和总部失效时更新引用。不要因一个组织结束而全局关闭其他组织共用的侧栏或移除共用组。

验收：创建一次、重复初始化、不同参与国家看到的内容、领袖/主席失效、组织结束、读档和已有存档迁移；验证成员与按钮规则真正执行。

## 国际局势

入口 `common/journal_entries/com_international_situation.txt`、`common/scripted_effects/com_international_situation_effects.txt`、`gui/com_journal_injects/situation_widgets.gui`。

新功能先研究当前 JE widget：

```text
widget = {
    gui = "gui/com_journal_injects/situation_widgets.gui"
    name = "widget_com_international_situation"
    container = "custom_widget_container_je_icon"
}
```

在 JE scope 上使用的接口包括：

| 接口 | 参数/含义 |
|---|---|
| com_situation_start_date_today_effect | 无参 yes，按当前日期设置 |
| com_set_situation_start_date_effect | month 为 flag 文案键，year 为数值 |
| com_set_situation_left_character / right_character | character 为角色 scope |
| com_set_situation_left_title / right_title | title 为本地化键 |
| com_set_situation_phase_effect | phase_icon、phase_name，核对 GUI 读取的资源与文本格式 |
| com_set_situation_illustration_background_effect | texture 实际转为 ig_trait:$texture$，不是裸 DDS 路径 |
| com_set_situation_outcome_details_effect | type、name、texture；type 需匹配 GUI 实际消费的结局槽位 |
| com_set_indexed_situation_phase_progress_details_effect | index 1–4；next_phase_name、next_phase_icon、progress_value、max_value、min_value、factors；不能套用进度条的零起点索引 |

局势分组可用 `com_add_journal_group_to_situations_list` 注册到对应列表；该函数当前定义在 international_organization_effects 文件，目录归属不能代替符号搜索。

新旧边界：effect 文件的 Outdated Situation Effects 后保留 `create_com_situation_journal_entry` 等旧 struct 模型，另有 `gui/com_journal_injects/situations_old.gui`。新 JE widget 与旧 ComSituation/左右 struct 宏不是天然可混用的接口。已有旧档先识别持久变量、struct 和 JE 的引用关系，保持旧接口或设计显式迁移，不直接换 widget 冒充迁移完成。

阶段推进、双方加入、结局判定由自己的业务 effect/on_action 驱动；展示字段随状态变更更新。退出/结束清理自有持续效果，旧模型还需销毁实际创建的 struct。验收至少覆盖双方角色缺失、阶段边界、结局、失效和读档。
