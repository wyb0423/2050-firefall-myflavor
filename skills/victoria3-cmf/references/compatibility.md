# 兼容接入

基线：CMF 1.65.0 / 1.13.*，2026-09-09 源码核对；以下路径相对 CMF_ROOT。


上游 Wiki 的 metadata 依赖格式如下；应合并进自己的 `relationships`，保留已有依赖：

```json
{
  "rel_type": "dependency",
  "id": "com.github.Victoria-3-Modding-Co-op.Community-Mod-Framework",
  "display_name": "Community Mod Framework",
  "resource_type": "mod",
  "version": "1.*"
}
```

元数据声明之外，核实启动器实际启用和加载顺序；发布 Workshop 时按上游要求设置 required item。依赖格式来源：[上游 Getting Started](https://github.com/Victoria-3-Modding-Co-op/Community-Mod-Framework/wiki#setting-dependency)。

每次接入至少检查：

1. 当前 CMF 版本、游戏版本、目标 Mod 与相关 GUI/大修 Mod 的最终覆盖。
2. effect 定义、参数宏大小写、调用者、GUI 消费者、资源和本地化键是否对应。
3. scope 是否正确，是否重复注册；完成、失败、退出、死亡、灭国等实际适用路径是否清理。
4. 新开局与旧存档分别验证；UI 目测、按钮执行、AI 调度与错误日志分别记录结果。

尤其应搜索 `Outdated`、`deprecated`、`example`、`Test Journal`、`DO NOT`。`events/com_debug.txt` 明确禁止直接调用其事件；`com_add_rise_of_communism.txt` 的启动注册被注释，不能把示例的存在视为自动启用。

`INJECT`、`REPLACE`、`REPLACE_OR_CREATE` 应按游戏数据库加载语义核对；CMF 源码使用这些语法，不意味着 CMF 是它们的实现者。


## 检测与公共挂钩

检测入口：`common/scripted_triggers/0_community_mod_triggers.txt` 与 `zz_com_detection_trigger.txt`。前者包含第三方默认假值，后者将 CMF 检测设为真。只为自己所属 Mod 覆盖对应检测，不复制整个检测文件，也不伪造其他 Mod 激活。文件排序还要与实际 Mod 加载顺序共同检查。

法律：同时搜索 `common/scripted_triggers/com_law_blocker_triggers.txt` 与 `common/laws/`；只有法律定义实际消费的挂钩才有效。政治运动：从 `common/political_movements/ycom_*.txt` 追到对应 scripted triggers / script values；党名从 `common/parties/` 的 first_valid 分支检查优先级。这些是共享覆盖，不能假定会自动注册任意新 Mod 内容。

原版流程阻断：`common/on_actions/cmf_heir_blocker.txt`、`com_formation_event_blocker.txt`、`events/00_com_regency_event_blocker.txt`。读取 no_heirs / com_no_formation_events / com_no_regencies 时的 scope 才决定变量放哪里，不能根据文件首行 Root 注释推断所有嵌套读取。剧情结束时恢复需要恢复的开关。

解散集团：`common/scripted_effects/com_dissolve_power_bloc.txt` 接受 `power_bloc` 参数，配合 `common/scripted_rules/com_dissolve_power_bloc_scripted_rules.txt`。实现暂时切换国家类型触发资格刷新，须检查目标类型分支及其他 Mod 是否覆盖 can_lead_power_bloc，运行中检查集团解散与领袖国家类型恢复。

验证最低结果：新游戏及已有存档的初始化次数正确；框架接口在最终栈中仍存在；受影响的原版法律/运动/GUI 行为没有被目标覆盖意外丢失。以上结果需要实际证据，不能由 metadata 推断。
