# Cold War Era 建筑清理功能调研与迁移

## 上游实现

来源：Steam Workshop `Cold War Era (1950)`（`2988303719`）。其调用链为：

1. `common/scripted_buttons/cwe_prune_excess_buildings.txt` 设置私有或公有清理变量，并在启用时立即调用清理效果。
2. `events/AI_incompetence_management/system_AI_Incompetence_Management.txt` 的隐藏年度事件在和平时期再次调用清理效果。
3. `common/scripted_triggers/cwe_scripted_triggers.txt` 用雇佣率、招聘失败、利润、补贴和多数所有权判断建筑是否应被清理。
4. `common/scripted_effects/cwe_prune_excess_buildings.txt` 逐建筑类型扫描所有州，并使用 `remove_building` 删除该州该类型的全部等级。

该实现可以迁移，因为使用的 `occupancy`、`has_failed_hires`、`weekly_profit`、`is_subsidized`、`private_ownership_fraction` 和 `remove_building` 在 Victoria 3 1.13 仍然有效。由于 `remove_building` 是需要具体建筑类型的州效果，不能只遍历建筑作用域后做一次通用删除，所以兼容其他 mod 时仍需维护显式建筑清单。

## 已修正的上游问题

- 上游本地化宣称阈值为 10%，实际触发器写成 `occupancy <= 0.01`（1%）。本适配器现按项目规则使用严格低于 20% 的阈值。
- 上游年度事件检查了不存在/错误的 `effect_prune_government_buildings` 变量，而按钮设置的是 `government_building_pruning_active`。本迁移统一使用 `ffpa_government_building_pruning_active`。
- 上游无论是否实际删除建筑都会发通知。本迁移只在本轮至少删除一栋建筑后发通知。
- 上游私有和公有清单各复制一份完整州扫描。本迁移把单建筑扫描参数化，保留显式清单但减少单行逻辑漂移。

## 本迁移的运行规则

- 两个玩家开关默认关闭，分别管理多数私有（`private_ownership_fraction > 0.5`）和多数公有（`<= 0.5`）建筑；AI 国家在日志加入时默认同时开启。
- 玩家开启时立即扫描；之后每半年扫描一次。战争期间不能切换，也不执行半年扫描。
- 必须同时满足：建筑存在、雇佣率严格低于 20%、周利润不高于 0、没有补贴。招聘失败与施工状态均不参与判定。
- 命中后使用 `remove_building`，即删除该州该类型建筑的全部等级，并非只降低一级。
- 玩家日志和 AI 默认变量都会通过现有月度存档修复机制初始化，因此兼容旧存档；旧存档中的 AI 会在首次初始化时自动获得两个启用变量，但不会额外挂载玩家界面日志。

## 覆盖范围

### 原版（44）

- 制造业 17：食品、纺织、家具、玻璃、工具、造纸、化工、炸药、合成、钢铁、发动机、造船、汽车、电气、武器、火炮、弹药。
- 农业与种植园 16：黑麦、小麦、水稻、玉米、小米、畜牧、葡萄园，以及咖啡、棉花、染料、鸦片、茶叶、烟草、糖、香蕉、丝绸种植园。
- 采掘与其他 11：煤、铁、铅、硫、金矿，伐木、橡胶、渔业、捕鲸、油井、艺术学院。

### Tech & Res（28）

- 数字与工业 14：办公楼、软件、互动媒体、数据中心、电商物流、合金、电子、电池、处理器、电脑组装、机器人、飞机、制药、消费电子。
- 资源与农业 8：水处理、铝土、铜、普通矿物、高级矿物、天然气、稀土、水培。
- Tech & Res 内置的 Morgenroete 兼容建筑 6：铀矿、歌剧院、出版、乐器、炼油、合成橡胶。

## 保护性排除

不处理不可常规缩减或容易形成自动重建/本地商品死循环的建筑：铁路、港口、机场、城市中心、贸易中心、庄园、金融区、公司总部、建造部门、政府与军事建筑、纪念碑、生计建筑、金矿区、原版及 Tech & Res 电力建筑、电网、通信产业、现代州基线、核武器发射井、研究中心。

后续若要扩大范围，只需在 `common/scripted_effects/ffpa_building_pruning_effects.txt` 的私有与公有调用清单中同步加入建筑类型；建议对基础设施或本地商品建筑单独增加更严格条件，而不是直接并入当前规则。
