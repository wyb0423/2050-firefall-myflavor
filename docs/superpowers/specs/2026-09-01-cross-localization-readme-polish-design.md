# 东地中海横向本地化与 README 润色设计

## 1. 背景

FFPA 的主体叙事优化已经分别形成设计：

- 动态前所有者叙事；
- GRE → BYZ Firefall 成立链；
- TUR/BYZ 常驻治理与地区建设。

横向审查发现仍有少量跨模块文字问题：

- Firefall 英文本地化把 `TUR_ADJ`、`GRE_ADJ` 分别写成 `Turkey`、`Greece`，导致原版和最终加载栈中的动态句可能显示 `Greece gold reserves` 等错误语法；
- `Roman People's Commonwealth` 所有格语义不自然；
- 简中“土耳其国民议会政府”遗漏“大国民议会”的“Grand”；
- 一处英文选项使用 `an Euphrates–Levant`；
- README 开头先讲物理架构、旧 Mod ID 和拆包，缺少玩家进入“大火后东地中海”的叙事入口；
- metadata 的简介和 `Economy/Balance/Utilities` 标签已经过时，但按仓库约定只在实际发布时修改。

本设计完成纯文本横向收口，不再扩展运行时功能。

## 2. 已确认决策

1. 本轮修改游戏内本地化与 README，不修改 metadata。
2. metadata 简介和标签延后到下次实际发布。
3. 覆盖 Firefall 的英文 `TUR_ADJ/GRE_ADJ` 为 `Turkish/Greek`。
4. 简中同步定义 `TUR_ADJ/GRE_ADJ`，保持语言键集合一致。
5. 动态国名改为 `Commonwealth of the Roman Peoples／罗马诸民共同体`。
6. 政体称谓改为“土耳其大国民议会政府”。
7. 修正 `an Euphrates–Levant` 为 `a Euphrates–Levant`。
8. README 先讲世界观与玩家幻想，再讲依赖、模块、旧档和拆包。
9. 党名、意识形态、trait、文化名称和国家集团候选名除已批准术语修正外不做额外重写。

## 3. 目标

- 修复最终加载栈中的 TUR/GRE 英文形容词。
- 统一动态国名和政府名称的中英语义。
- 消除已经确认的英文冠词错误。
- 让 README 在首屏说明玩家将扮演什么、为什么这些国家会在 Firefall 世界中重新出现。
- 保留全部真实机制、阈值、加载顺序、存档和拆包说明。
- 不提前写入尚未实现的叙事名称或行为。

## 4. 非目标

- 不修改 metadata、version、Mod ID、依赖或标签。
- 不改变任何技术 ID、事件、JE、modifier、变量或脚本逻辑。
- 不重新命名 `Rhomaic`、BYZ 党名、利益集团 trait 或意识形态。
- 不扩大到 Firefall 的其他国家形容词。
- 不把 README 改写成完整玩法 Wiki。
- 不删除旧存档和外部拆分包的必要说明。

## 5. 上游形容词覆盖

### 5.1 最终来源

原版 1.13.11：

- `TUR_ADJ: "Turkish"`；
- `GRE_ADJ: "Greek"`。

Firefall 0.1.1 后加载覆盖：

- `TUR_ADJ: "Turkey"`；
- `GRE_ADJ: "Greece"`。

FFPA 按推荐顺序最后加载后，应恢复正确英文形容词：

```yaml
TUR_ADJ: "Turkish"
GRE_ADJ: "Greek"
```

简中同步定义：

```yaml
TUR_ADJ: "土耳其"
GRE_ADJ: "希腊"
```

中文名词与形容词同形，因此显示不变；重复定义只用于保持最终来源与语言键集合一致。

### 5.2 覆盖登记

`AGENTS.md` 的本地化覆盖表增加 `TUR_ADJ`、`GRE_ADJ`：

- 方式：同名本地化键覆盖；
- 原因：修复 Firefall 英文形容词误写；
- 必查上游：原版、Firefall；
- 后加载风险：任何更晚的国家本地化 Mod 都可能再次覆盖。

不覆盖 `TUR`、`GRE` 国名本身，也不修改 BYZ 基础或动态形容词。

## 6. 确定的小修

### 6.1 动态国名

英文：

```text
Roman People's Commonwealth
→ Commonwealth of the Roman Peoples
```

简中：

```text
罗马人民共同体
→ 罗马诸民共同体
```

技术键 `dyn_c_ffpa_roman_peoples_commonwealth` 与 adjective 键不变。

### 6.2 土耳其议会政府

```text
土耳其国民议会政府
→ 土耳其大国民议会政府
```

英文 `Government of the Turkish Grand National Assembly` 保持不变。

### 6.3 英文冠词

```text
Create an Euphrates–Levant Development Authority.
→ Create a Euphrates–Levant Development Authority.
```

事件 ID、选项键和对应效果不变。

### 6.4 已由其他设计拥有的术语

- 中海 → 内海；
- 易弗里基叶 → 伊弗里基亚；
- 毛里塔尼亚滨海道 → 古毛里塔尼亚滨海道；
- Spania → 西班尼亚；
- Law／法统支柱 → Public Authority／公共权威；
- 军户与权门 → 军役户与权门。

这些修改由常驻治理与地区建设叙事设计负责。本设计只在最终横向检查中验证一致性，不重复创建另一套文本。

## 7. 有意保留的名称

- `Rhomaic／罗马人`；
- BYZ 十二个党名；
- TUR/BYZ 十五个国家集团候选名称；
- `Strategikon／《战略论》`；
- `Tanzimat Legacy／坦志麦特遗产`；
- `Imperial Symphonia／皇权—教会协和论`；
- `Erkân-ı Harbiye／帝国总参谋体系`；
- 玩家可读的 `Emperor／皇帝`、`Empress／女皇`、`Consul／执政官`。

这些名称的现有说明已经表达旧世界历史材料在复兴国家中的现代用途。无需为了提高 Firefall 关键词密度而逐项加入“大火、核尘、废墟”。

## 8. README 玩家入口

README 开头采用两段玩家导向文字：

> 2050年的核战——幸存者后来所称的“大火”——摧毁了东地中海的旧国家，却没有抹去它们的档案、道路、宗教机构与政治记忆。Firefall 让城邦、州级政权与地区继承者重新拼合旧世界国家；FFPA 的故事从这些名字重新出现在地图上之后开始。
>
> 重建后的土耳其必须在高门共同体、安卡拉共和国与重建总署之间确定国家遗产；重新形成的希腊则可以把旧档案中的“伟大理想”推向东罗马头衔。成立新罗马并不是终点——复归领土、公共权威、全国福祉、军役户、地方中介和地中海交通网络都将继续检验这些国家能否真正统治大火后的世界。

这两段只描述已批准并将在同一文本批次实际实现的内容。若主体叙事尚未落地，README 必须最后修改。

## 9. README 章节结构

1. 世界观与玩家幻想；
2. 固定依赖与推荐加载顺序；
3. 希腊—东罗马成立链；
4. TUR 三条路线、工程、前线与治理；
5. BYZ 复归战争、共同体与常驻治理；
6. 地区建设与西方整合；
7. 旧存档与 Tech & Res 兼容；
8. 外部拆分包；
9. 未来扩展约定。

当前 README 中的机制、阈值、互斥关系、加载顺序、旧档迁移和拆包边界全部保留。重组目标是减少一段十八条长列表和开头的维护者视角，不删除必要信息。

原 Mod ID、发布连续性和外部模块归属移动到兼容性/拆包部分，不占用第一屏。

## 10. Metadata 延后项

下次实际发布时再审议：

- `short_description` 是否加入 post-nuclear Eastern Mediterranean 定位；
- tags 从 `Gameplay/Economy/Balance/Utilities` 调整为更符合风味包的集合，例如 `Gameplay/Alternative History/Cultures and Religions/New Nations`；
- 是否随发布提升版本号。

本设计不授权当前实现修改 `.metadata/metadata.json`。

## 11. 文件范围

预计修改：

- `localization/english/ffpa_l_english.yml`；
- `localization/simp_chinese/ffpa_l_simp_chinese.yml`；
- `localization/english/ffpa_turkish_flavor_l_english.yml`；
- `README.md`；
- `AGENTS.md`。

简中 Turkish flavor 文件没有对应文字变化，不为制造机械 diff 而重写；两种语言的技术键集合仍保持一致，因为修正的是既有键值。

不修改 common、events、metadata、依赖或版本。

## 12. 实施顺序

1. 玩家可见身份门控技术支线；
2. 动态前所有者叙事；
3. GRE → BYZ Firefall 成立链重写；
4. 常驻治理与地区建设重写；
5. 本横向小修；
6. README 最后重组。

这样可以保证 README 和横向术语只描述已经存在的最终行为。

## 13. 验证标准

### 13.1 最终本地化来源

- 英文 `TUR_ADJ` 为 `Turkish`；
- 英文 `GRE_ADJ` 为 `Greek`；
- 简中对应值为“土耳其”“希腊”；
- 原版希腊 tooltip 不再显示 `Greece gold reserves`；
- FFPA 最后加载时这些键来自本项目。

### 13.2 文本

- 动态国名显示 `Commonwealth of the Roman Peoples／罗马诸民共同体`；
- 土耳其议会政府显示“大国民议会”；
- 英文不存在 `an Euphrates`；
- 横向术语与三份主体叙事设计一致；
- 党名、trait、国家集团名称和 ruler title 未发生无关变化。

### 13.3 README

- 首屏说明大火、Firefall formable 与 FFPA 开始介入的时间点；
- 章节顺序符合玩家阅读，而非维护者拆包顺序；
- 所有阈值、互斥路线、加载顺序和旧档说明仍准确；
- README 不承诺未实现的动态国名、治理名称或文本行为；
- Mod ID 与外部模块边界仍清晰可查。

### 13.4 格式与兼容

- 英文和简中键集合一致；
- 修改的本地化文件保持 UTF-8 BOM；
- 不重编码无关文件；
- `AGENTS.md` 登记有意覆盖；
- `.metadata/metadata.json` 不变且可解析；
- `git diff --check` 无新增空白错误；
- 不需要存档迁移。

## 14. 成功标准

实现完成后，FFPA 的游戏内横向名称没有明显英文语法或中英语义错误，Firefall 的错误国家形容词在最终加载栈中得到修复；README 第一屏直接说明玩家将在大火后的东地中海做什么，而依赖、拆包和旧档信息仍完整保留。metadata 的发布定位调整被明确延后，不与普通文本润色混在一起。
