# 日志和 UI 配方

基线：CMF 1.65.0，2026-09-09 本地源码核对。路径相对 CMF_ROOT；片段需嵌入自有定义，不是完整 Mod，也未实机验证。

## 样式进度条

适用：原生 scripted progress bar 需要颜色、趋势、目标线或分段。最小文件集合：自有 JE、scripted progress bar、本地化；动态目标/趋势再加 script values。直接读取 CMF 的 `common/journal_entries/com_progress_in_style.txt`、`common/scripted_progress_bars/com_progress_in_style_progress_bars.txt`、`common/scripted_effects/com_progressbar_effects.txt` 和 `gui/com_gui_progressbars.gui`。

放在自己的 JE 中，my_progress 是自己已定义的 scripted progress bar：

```text
scripted_progress_bar = my_progress
widget = {
    gui = "gui/com_journal_injects/injects.gui"
    name = "com_journal_entry_progress_bars"
    container = "com_custom_widget_container_scripted_progress_bars"
}
immediate = {
    create_com_progress_bar = {
        progress_bar = my_progress
        index = 0
        color = blue
    }
}
```

immediate 中要有 `scope:journal_entry`；保留外层所属 scope，effect 会在该 scope 创建 com_progress_bar_cache，并在 JE 上挂引用。index 是该 JE 中原生进度条的零起点位置，顺序调整时一起修改。my_progress 的实际数值、weekly_progress 和完成条件由自己的 Mod 定义，CMF 样式不会替代原生进度计算。

`create_com_progress_bar_with_both` 额外参数为 `bar_increase_color`、`bar_decrease_color`、`drift_value`、`target_type`、`target_value`。目标位置使用归一化值；drift 表示有方向的变化，按源码示例的归一化 script value 处理，不直接传原始点数或强制删掉负号。颜色、目标标记类型从接口文件末尾清单核对。

生命周期：在实际可能发生的 on_complete/on_fail/on_timeout/on_invalid 等路径，从拥有缓存的同一 scope 调用 `remove_com_progress_bar = { progress_bar = my_progress }`。如果存在多次终止调用，用 `exists_com_progress_bar` 判断后清理。测试 JE 的空结束块不是可复制的完整清理实现。相同所属 scope 的多个活动 JE 使用相同 progress_bar 标识可能命中同一缓存；设计独立 ID 或先验证重用需求。

验收：进度初值和变化正确，目标线/趋势与数值一致；结束后缓存与 struct 对象得到清理；重新创建、新开局和旧档不会重复对象。静态存在性检查不等于这些运行结果。

## 仿立法阶段组件

最小集合：自己的 JE、阶段/提示本地化、驱动阶段的业务 effect/on_action；配套 `gui/com_journal_injects/enactment.gui` 与 `injects.gui`。入口 `common/scripted_effects/com_enactment_journal_effects.txt`。

在 JE scope（如 `scope:journal_entry = { ... }`）调用：

```text
com_setup_enactment_journal = {
    title = my_reform_title
    stall_chance = 20
    success_chance = 60
    step_progress = 0
    current_phase = my_phase_one
    phase_one = my_phase_one
    phase_two = my_phase_two
    phase_three = my_phase_three
}
```

以上数字仅说明参数形态；实际量纲与显示公式先读 GUI 的 ComEnactmentValue 消费方式。widget 的 name 使用 `com_journal_entry_enactment`，container 必须由目标 JE GUI 的现有挂载位置确定，不猜一个通用位置。current_phase 必须等于 phase_one/phase_two/phase_three 对应的本地化键（本例 my_phase_one），GUI 比较的是这些 flag 的值，不是槽位名 phase_one。

该 effect 写 com_enactment_widget map，抽签、暂停、阶段推进和奖励仍是业务逻辑。`com_set_enactment_journal_progressing` 的当前实现需要 element 参数；不要根据函数名当作无参开关。检验显示与真实规则是否一致，重复进入阶段是否重复奖励；JE 销毁以外持有的自有引用/变量另行清理。

## 侧栏按钮

最小集合：自有 ideology、scripted_gui、本地化、注册入口；若打开独立窗口，还需 scripted widget/GUI。来源 `gui/com_gui_sidebar.gui`、`common/history/global/00_com_global.txt`、`common/scripted_guis/example_button_sgui.txt`、`common/ideologies/example_button.txt`。

当前注册协议（在初始化所需的全局上下文执行，注册前判断目标是否已在列表）：

```text
add_to_global_variable_list = {
    name = custom_button_list_flag
    target = flag:my_button
}
```

flag 名必须同时对应 ideology:my_button（图标/文案）和 scripted_gui my_button（country scope，is_shown/is_valid/effect）。GUI 也读取 country 自己的同名列表；按需求选择一种注册范围，避免两处重复。

不要抄 `enable_example_button.txt` 注释中的 custom_button_list/ideology 旧协议。当前 GUI 用 GetIdeology(Scope.GetFlagName) 和 GetScriptedGui(Scope.GetFlagName) 消费 flag；点击时写 GUI 本地 com_open_window 并执行 SGUI。独立面板可参照 `gui/scripted_widgets/com_scripted_widgets.txt` 和现有组织面板的绑定；按钮本身不自动创建窗口。

新游戏可用 global history，旧档另行幂等注册。暂时不可用用 is_shown/is_valid；永久移除注册时在对应全局/国家列表移除自己的条目。保留业务效果在脚本层，GUI 本地开关不承载同步机制状态。

验收：可见、不可用、点击效果、窗口切换、国家切换、新开局/读档；确认重复初始化没有重复按钮，与其他 UI Mod 最终覆盖一致。

## 其他展示能力按需定位

- 事件：`gui/com_event_windows/`。先读选中 type 的属性与需要的 scope/变量，再在自己的事件中按当前原版/依赖的调用方式引用。不要把 GUI type 名未经核对就当事件 gui 参数；`events/com_debug.txt` 注明不要调用，只可静态参考。大型多角色窗口要验证角色缺失与不同文本长度。
- 角色：`common/scripted_effects/com_character_animation_effects.txt`、`com_character_background_effects.txt` 与 `gui/00_com_character.gui`。在角色 scope 调用 `set_com_character_portrait`，参数 animation/camera/environment；资产 ID 从当前原版/依赖查。`remove_com_character_portrait` 移除肖像覆盖相关变量，不自动删除独立背景和 VFX 列表，检查你实际设置过的字段。
- 其他 JE 小组件：`gui/com_journal_injects/injects.gui` 列入口，旁边 buildings/companies/characters/header/dlc 文件定义消费者。每次核对 gui/name/container 和变量读取的 scope，验证空列表与失效对象。
