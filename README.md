# FFPA — Firefall Flavor Pack

面向 `2050: The Fire Falls` 与 `[1.13] Tech & Res` 固定加载环境的国家与地区风味合集。项目采用“一个物理 Mod、内部按地区模块化”的结构；当前包含东地中海模块，未来可继续加入共享相同依赖的其他国家或地区风味。

本合集继续使用原 Mod ID `com.wyb.2050-firefall-personal-adapter`，现有技术 ID、事件 ID、持久变量和存档状态均保持不变。

统一战争、殖民塑形和全局平衡已经迁移到 `2050 Firefall — Core Balance Adapter`；建筑清理已经迁移到 `FFPA — Low-Workforce Building Pruning` 及其 Tech & Res 兼容包；Tech & Res 自动生产兼容已经迁移到 `FFPA — Tech & Res Auto PM Adapter`。按需启用这些独立 Mod 时，技术 ID、存档接口和最终行为与拆分前保持一致。

完整加载栈的推荐顺序：Tech & Res → Auto-Apply PMs → Auto-Apply Automation PMs → 2050: The Fire Falls → Core Balance Adapter → FFPA Building Pruning → FFPA Building Pruning: Tech & Res Compatibility → FFPA Tech & Res Auto PM Adapter → FFPA Firefall Flavor Pack。

## 当前模块：东地中海成立链与风味

- 保留原版土耳其 `TUR`，不另造等效国家；希腊可沿保留的原版民族主义政治线成立 `BYZ`，成立后的既有宣称全部保留。
- 土耳其和拜占庭分别拥有“行政整合—公民包容—内部稳定”三轴共同体日志。各轴条件单独计算，失败时逐月倒退而非清零；完成后在保留原主流文化的同时加入“奥斯曼”或“罗马人”主流文化。
- 加入有限的一次性工业、税制、选举与帝国制度事件，不使用长期循环事件池。临时修正通常持续 6–8 年，并按 Firefall 与 Tech & Res 的高数值环境加强。
- “两洲之门”和“复兴新罗马”提供建设期加速；完成后分别选择互斥的永久都会专精，避免同一首都叠加全部强力奖励。
- 加入十五项巴尔干、南欧、北非、安纳托利亚、黎凡特与美索不达米亚地区建设日志，完成后只对实际工程覆盖州给予专精化永久修正。
- `BYZ` 获得克制的利益集团名称、帝国/执政官政体称号、动态国名和基于原版四字母十字旗的简约动态旗帜；`TUR` 保留原版 Tag、国旗与政体视觉，并获得按君主制/共和国路径区分的专属政体称号。两国政体说明还会显示可供事件与日志复用的正式政府名称。
- 旧版本存档通过月度国家脉冲迁移三轴进度、补加缺失日志与一次性事件标记，不重复发放已经取得的永久奖励。

## 未来扩展约定

- 新地区默认继续适配 Firefall 与 Tech & Res，不静默扩大整个合集的硬依赖。
- 每个地区使用独立的文件名、事件 namespace、技术 ID、持久变量和本地化键前缀。
- 跨地区联动通过命名明确的 scripted trigger 或 scripted effect，不直接读取另一地区的临时变量。
- 现有东地中海的 `ffpa_flavor.*` 事件、`ffpa_tur_*`、`ffpa_byz_*`、`ffpa_region_*` 及版本化变量属于存档接口，不因内部整理而重编号或改名。
