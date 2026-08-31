# Building Pruning 模块剥离设计

## 1. 目标

把当前 `2050-firefall-myadapter` 中的低人力亏损建筑清理功能剥离为独立 Mod，同时满足：

- 主 Mod 在纯原版 Victoria 3 1.13 环境中无任何依赖并正常运行；
- 安装 Tech & Res 后，可以通过可选兼容 Mod 清理其新增建筑；
- 不改变玩家开关、AI 默认值、半年调度、立即扫描、清理条件、通知条件和存档 ID；
- 主 Mod、Tech & Res 兼容 Mod 与拆分后的 Personal Adapter 之间不存在重复运行时定义。

Victoria 3 会无条件加载单个 Mod 目录中的全部脚本，且 `remove_building` 必须接收具体建筑类型。项目不采用在无依赖主包中直接引用 Tech & Res 建筑 ID 的做法。

## 2. 发布结构

本功能作为两个同级 Launcher Mod 发布。

### 2.1 无依赖主包

- 目录：`../ffpa-building-pruning`
- 显示名：`FFPA — Low-Workforce Building Pruning`
- Mod ID：`com.wyb.ffpa-building-pruning`
- 初始版本：`1.0.0`
- 支持版本：`1.13.*`
- 依赖：无

### 2.2 Tech & Res 可选兼容包

- 目录：`../ffpa-building-pruning-techres`
- 显示名：`FFPA — Building Pruning: Tech & Res Compatibility`
- Mod ID：`com.wyb.ffpa-building-pruning-techres`
- 初始版本：`1.0.0`
- 支持版本：`1.13.*`
- 依赖：
  - `com.wyb.ffpa-building-pruning`，版本 `1.*`
  - `tech.res`，版本 `1.*`

兼容包必须在主包和 Tech & Res 之后加载。主包不声明对 Tech & Res、Firefall、Auto-Apply Mod 或 Personal Adapter 的依赖。

## 3. 方案选择

采用“主状态机 + 可替换空扩展 effect”方案。

未采用：

- 兼容包复制完整扫描、UI、on_action 或通知：会造成重复调度、重复通知和状态机漂移；
- 在主包中直接保留 Tech & Res 建筑 ID 并用 `if` 包裹：不能保证加载阶段没有无效数据库对象；
- 为两个加载栈生成完整构建变体：发布和维护成本高于本次拆分需要；
- 创建 Tech & Res 占位建筑：会污染纯原版数据库并改变功能；
- 从 building scope 动态传入 `THIS`/`PREV`：当前安装版本没有可工作的 `remove_building` 语法先例。

## 4. 主包文件所有权

以下现有运行时对象迁入主包：

- `common/journal_entries/ffpa_building_pruning_je.txt`
- `common/scripted_buttons/ffpa_building_pruning_buttons.txt`
- `common/scripted_triggers/ffpa_building_pruning_triggers.txt`
- `common/scripted_effects/ffpa_building_pruning_effects.txt`
- `common/messages/ffpa_building_pruning_messages.txt`
- 建筑清理专用 on_action 与初始化 effect
- 英文和简体中文中的 10 个建筑清理键
- `BUILDING_PRUNING_PORT.md`

主包还创建：

- `.metadata/metadata.json`
- `README.md`
- `AGENTS.md`
- `.gitignore`

主包只包含 44 种原版建筑引用。图标、JE 分组、trigger 和 effect 语法必须全部来自原版 1.13 数据库。

## 5. 主状态机与扩展接口

现有以下 ID 和行为保持不变：

- `ffpa_prune_private_building_type`
- `ffpa_prune_government_building_type`
- `ffpa_prune_private_buildings`
- `ffpa_prune_government_buildings`
- `ffpa_is_prunable_private_building`
- `ffpa_is_prunable_government_building`

主包新增两个稳定扩展 effect：

- `ffpa_prune_private_optional_buildings`
- `ffpa_prune_government_optional_buildings`

主包中的两个扩展 effect 默认定义为空。主扫描按以下固定顺序执行：

1. 删除本轮临时通知变量；
2. 扫描 44 种原版建筑；
3. 调用对应 optional effect；
4. 若任一基础或可选扫描实际删除过建筑，发送一次对应通知；
5. 清理本轮临时通知变量。

兼容包使用：

```text
REPLACE:ffpa_prune_private_optional_buildings
REPLACE:ffpa_prune_government_optional_buildings
```

分别加入 28 种 Tech & Res 建筑调用。兼容 effect 复用主包的参数化单建筑扫描，不拥有通知变量的初始化和清理。

兼容包不得定义独立按钮、JE、message、on_action、扫描设置变量或通知收尾逻辑。

## 6. 建筑清单

### 6.1 原版主包：44 种

- 制造业 17：`building_food_industry`、`building_textile_mill`、`building_furniture_manufactory`、`building_glassworks`、`building_tooling_workshop`、`building_paper_mill`、`building_chemical_plant`、`building_explosives_factory`、`building_synthetics_plant`、`building_steel_mill`、`building_motor_industry`、`building_shipyard`、`building_automotive_industry`、`building_electrics_industry`、`building_arms_industry`、`building_artillery_foundry`、`building_munition_plant`。
- 农业与种植园 16：`building_rye_farm`、`building_wheat_farm`、`building_rice_farm`、`building_maize_farm`、`building_millet_farm`、`building_livestock_ranch`、`building_vineyard`、`building_coffee_plantation`、`building_cotton_plantation`、`building_dye_plantation`、`building_opium_plantation`、`building_tea_plantation`、`building_tobacco_plantation`、`building_sugar_plantation`、`building_banana_plantation`、`building_silk_plantation`。
- 采掘与其他 11：`building_coal_mine`、`building_iron_mine`、`building_lead_mine`、`building_sulfur_mine`、`building_gold_mine`、`building_logging_camp`、`building_rubber_plantation`、`building_fishing_wharf`、`building_whaling_station`、`building_oil_rig`、`building_art_academy`。

### 6.2 Tech & Res 兼容包：28 种

- 数字与工业 14：`building_office`、`building_software_industry`、`building_interactive_media_industry`、`building_datacenter_industry`、`building_ecommerce_logistics`、`building_alloys_plant`、`building_electronics_industry`、`building_battery_plant`、`building_processors_foundry`、`building_computer_assembly_plant`、`building_robotics_industry`、`building_aircraft_industry`、`building_pharmaceuticals_industry`、`building_consumer_electronics_industry`。
- 资源与农业 8：`building_water_plant`、`building_bauxite_mine`、`building_copper_mine`、`building_commonores_mine`、`building_advancedores_mine`、`building_natural_gas_rig`、`building_rare_earths_mine`、`building_hydroponic`。
- Tech & Res 的 Morgenroete 兼容定义 6：`building_uranium_mine`、`building_elgar_opera`、`building_manzoni_publishing_industry`、`building_instrument_workshops`、`building_mendelejew_hydrogenation_plants`、`building_mendelejew_synthetic_rubber_factory`。

每个包内的私有和公有列表必须包含完全相同的建筑集合，且每个建筑恰好出现一次。

## 7. 生命周期与初始化解耦

主包新增幂等 effect：

- `ffpa_ensure_building_pruning`

其职责仅为：

- 玩家国家缺少 `je_ffpa_building_pruning` 时补加 JE；
- AI 国家尚未初始化时设置两个启用变量和 `ffpa_ai_building_pruning_initialized`。

主包独立登记：

- `on_game_started_after_lobby`：包装 effect 对所有国家调用 ensure；
- `on_monthly_pulse_country`：当前国家调用 ensure，修复旧存档；
- `on_half_yearly_pulse_country`：和平且对应开关启用时执行清理。

保留 `ffpa_half_yearly_building_pruning` ID。新增启动/月度包装 ID 使用清晰的 `ffpa_*building_pruning*` 命名，不与 Personal Adapter 的自动 PM 包装重名。

Personal Adapter 中：

- `ffpa_ensure_auto_pm_compat_journal` 删除 AI 清理变量初始化和玩家清理 JE 挂载；
- `common/on_actions/ffpa_on_actions.txt` 删除半年清理 on_action 与 `ffpa_half_yearly_building_pruning`；
- 自动 PM 的启动和月度 ensure 保持原频率不变。

## 8. 玩家行为

以下行为不变：

- 玩家两个开关默认关闭；
- AI 两个开关默认启用；
- 玩家启用开关时立即扫描；
- 此后仅在和平时期每半年扫描；
- 建筑必须同时满足：等级大于 0、occupancy 严格低于 20%、weekly profit 不高于 0、未补贴；
- 私有扫描要求 private ownership fraction 大于 50%，公有扫描要求不高于 50%；
- `remove_building` 删除州中该类型建筑的全部等级；
- 只有本轮实际删除过建筑才发通知；
- 保护性排除清单不变。

## 9. 本地化

主包迁入以下 10 个英文和简体中文键：

- `je_ffpa_building_pruning`
- `je_ffpa_building_pruning_reason`
- `ffpa_toggle_private_building_pruning_button`
- `ffpa_toggle_private_building_pruning_button_desc`
- `ffpa_toggle_government_building_pruning_button`
- `ffpa_toggle_government_building_pruning_button_desc`
- `notification_ffpa_private_buildings_pruned_notification_name`
- `notification_ffpa_private_buildings_pruned_notification_desc`
- `notification_ffpa_government_buildings_pruned_notification_name`
- `notification_ffpa_government_buildings_pruned_notification_desc`

兼容包不新增玩家可见对象，默认不需要本地化文件。主包两种语言键集合必须一致并保留 UTF-8 BOM。

## 10. 存档兼容

保留以下持久或玩家可见 ID：

- `je_ffpa_building_pruning`
- 两个 scripted button ID；
- 两个 notification ID；
- `ffpa_private_building_pruning_active`；
- `ffpa_government_building_pruning_active`；
- `ffpa_ai_building_pruning_initialized`；
- 两个本轮临时通知变量；
- 现有扫描和判定 effect/trigger ID。

旧存档启用主包后继续读取原设置变量和 JE 状态。月度 ensure 只补缺失内容，不重置玩家开关、不重复初始化 AI，也不重复发送奖励或通知。

两个 optional effect 是新扩展接口，不承载持久状态。以后增加其他建筑 Mod 兼容时，应新建独立兼容包并替换或聚合稳定 hook，不能让多个兼容包无序互相覆盖；在增加第二个兼容包前必须先把单槽 hook 升级为明确的多扩展调度接口。

## 11. 文档与原 Mod 更新

主包创建 README、AGENTS、metadata 和 `.gitignore`，并拥有更新后的 `BUILDING_PRUNING_PORT.md`。文档明确区分 44 种原版建筑和 28 种 Tech & Res 建筑。

兼容包创建独立 README、AGENTS、metadata 和 `.gitignore`，说明它只拥有两个 `REPLACE:` 扩展 effect。

Personal Adapter 更新：

- README 删除建筑清理功能说明，并在完整加载顺序中加入主包和可选兼容包；
- AGENTS 把建筑清理登记为外部模块，更新 on_action 和自动 PM ensure 的所有权；
- metadata 名称、ID、版本、依赖保持不变，只修改 short description，不再声称拥有 building cleanup；
- 不提升版本，不执行 Git 提交。

## 12. 推荐加载顺序

纯原版栈：

```text
Victoria 3 → FFPA Building Pruning
```

Tech & Res 兼容栈：

```text
Victoria 3 → Tech & Res → FFPA Building Pruning → FFPA Building Pruning: Tech & Res Compatibility
```

完整个人 Mod 栈：

```text
Tech & Res
→ Auto-Apply PMs
→ Auto-Apply Automation PMs
→ Firefall
→ Core Balance Adapter
→ FFPA Building Pruning
→ FFPA Building Pruning: Tech & Res Compatibility
→ FFPA Firefall Flavor Pack
```

## 13. 验证方案

### 13.1 纯原版静态验证

- 主包 metadata 的 relationships 为空；
- 主包所有建筑 ID 均存在于原版 1.13 最终建筑数据库；
- 主包不包含 `building_office` 等 28 个 Tech & Res ID、`tech.res` 或其他上游运行时引用；
- 主包在不加载兼容包时两个 optional effect 均为空且可调用。

### 13.2 Tech & Res 静态验证

- 兼容包 metadata 只依赖主包和 `tech.res`；
- 28 个建筑 ID 均存在于当前安装的 Tech & Res 建筑数据库，包括 `REPLACE_OR_CREATE` 定义；
- 两个兼容列表各 28 个、集合相同、无重复；
- 兼容包只定义两个 `REPLACE:` effect，不复制主状态机。

### 13.3 联合结构验证

- 主包私有/公有原版清单各 44 个且集合一致；
- 原版清单与 Tech & Res 清单无交集；
- 主包和兼容包的自有顶层键只有有意的 `REPLACE:` 关系；
- Personal Adapter 不再包含清理文件、清理本地化或清理调用；
- 英文与简体中文键集合一致，原 Mod 与主包键集合互斥，合并后等于拆分前；
- 两份或三份 metadata 均可解析；
- 修改脚本的括号、字符串和顶层结构正常；
- `git diff --check` 无本次新增空白错误。

### 13.4 运行时矩阵

纯原版 + 主包：

- 新游戏玩家获得 JE，开关默认关闭；
- AI 默认启用；
- 立即扫描和半年扫描可清理原版建筑；
- error/debug 日志无 Tech & Res 缺失引用。

Tech & Res + 主包 + 兼容包：

- 同一次立即或半年扫描覆盖 44 + 28 种建筑；
- 删除 Tech & Res 建筑会设置主包的本轮变量并只发一次通知；
- 未加载兼容包时 Tech & Res 建筑不由主包处理，但主包其余功能正常。

两个加载栈都要验证战争、补贴、正利润、高就业和保护建筑分别阻止删除，并分别测试私有和公有所有权路径。

## 14. 成功标准

- 主包在纯原版环境中没有依赖和缺失数据库引用；
- 兼容包加载后扩展为 72 种建筑，不改变主状态机；
- 新旧存档中的开关、JE 和 AI 初始化状态保持；
- Personal Adapter 完全停止拥有和调度建筑清理；
- 两个新 Mod 物理独立存在于当前目录的上层目录；
- 没有重复通知、重复半年扫描、重复本地化或新的机器绝对路径。
