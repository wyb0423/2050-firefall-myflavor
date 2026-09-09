---
name: victoria3-cmf
description: 在 Victoria 3 Mod 中选用、接入和排查 Community Mod Framework（CMF）的日志/UI、国际组织、局势及脚本工具。用户提到 CMF，或已有 CMF 依赖项目需要这些扩展时使用；不用于普通玩法讨论或无关的原生脚本修改。
---

# Victoria 3 Community Mod Framework

将需求对应到已有 CMF 能力，用当前安装源码确认接口，再完成最小接入。原生 JE、变量或按钮已经足够时直接使用；不要因本技能存在就给每个 Mod 增加 CMF 依赖。

## 定位与工作方式

1. 确认宿主、目标 Mod、游戏版本和实际加载栈；通用开发可配合已安装的 `victoria3-mod-development`，macOS 路径发现按其工作流执行。
2. 从实际 Steam 库找到 `steamapps/workshop/content/529340/3385002128`；本地 checkout 可由用户提供。将位置作为本次 `CMF_ROOT`，用 `.metadata/metadata.json` 核对 ID `com.github.Victoria-3-Modding-Co-op.Community-Mod-Framework` 与版本。不要把某台机器路径写入产物。未找到源码时说明缺口，不猜测当前 API。
3. 按下表只读所需 reference；查当前 effect/trigger 定义、调用示例及 GUI 消费者，核对参数大小写、scope、资源和初始化方式。参考材料基于 1.65.0，版本变化时重新核对使用的接口。
4. 把依赖、注册/初始化、业务逻辑、展示、本地化及必要清理/迁移一起接通。修改写入用户的目标 Mod，不直接改 Workshop 依赖，除非任务就是修改该框架。
5. 验证新开局/旧存档和实际结束路径。分别报告静态检查、游戏内显示、按钮效果和 AI/调度证据；未运行游戏就明确说明。

## 按需读取

- 不清楚框架能做什么或需要选型：读 [能力索引](references/capabilities.md)。
- 日志进度条、阶段组件、侧栏、事件窗口、肖像：读 [日志和 UI 配方](references/journal-and-ui.md)。
- 国际组织、跨国局势或旧模型迁移：读 [组织和局势](references/organizations.md)。
- 变量、每周调度、数组、结构体、字典：读 [脚本工具](references/scripting.md)。
- 新增依赖、检测、法律/政治挂钩、公共覆盖或兼容排查：读 [兼容接入](references/compatibility.md)。

## 容易误用的边界

- CMF 的组织、局势和阶段 UI 不替作者实现投票、概率抽签、奖励或 AI 决策。
- 旧示例不等于现行协议：尤其侧栏 flag 注册、局势 Outdated 区域、测试 JE 的空清理块。以定义与实际消费者交叉验证。
- struct 用特殊角色承载；样式进度条也有缓存与对象生命周期。创建后覆盖实际终止路径，保持所属 scope 一致。
- global history 只初始化新游戏；已有存档需要幂等注册和迁移。GUI 本地开关不是同步的机制状态。
- `INJECT` / `REPLACE` / `REPLACE_OR_CREATE` 是需要核对的数据库加载语义，不是 CMF 提供的代码生成接口。
