# 东地中海国家集团核心名称池设计

## 1. 背景与证据

当前安装版本为 Victoria 3 `1.13.11 (Matcha)`。原版通过
`common/power_bloc_names/` 数据库向国家集团创建与自定义界面提供候选名称：

- 顶层键同时作为本地化键；
- `trigger` 在集团领袖的 country scope 中求值；
- 创建界面另提供 `scope:selected_identity`，但本设计不依赖它；
- 符合条件的名称进入随机候选池，玩家仍可在创建时及创建后手工改名；
- 原版界面的名称编辑框限制为 30 个字符，因此新增英文显示名也不超过 30 个字符。

原版已经为 TUR 提供 `sublime_alliance`，并为 TUR 参与特定联盟时提供
`central_powers`；原版也已经为 GRE/BYZ 提供 `hellenic_league`，并在特定
罗马国家结盟条件下提供 `league_of_romans`。这些条目继续保留。

Tech & Res `1.6'` 和 Firefall `0.1.1` 均未提供或替换
`common/power_bloc_names/`。Firefall 虽然替换
`common/history/power_blocs/`，但那只移除或重建开局历史集团，不影响候选名称数据库。

## 2. 目标

- 为 FFPA 当前拥有内容的 `TUR` 与 `BYZ` 增加有限的国家集团风味名称。
- 使用“历史制度连续性 × 2050 灾后重建”的混合风格。
- 减少原版常见的 `Alliance`、`League`、`Pact` 拼词感，优先使用
  `System`、`Framework`、`Council`、`Conference`、`Directorate`、
  `Senate`、`Synod` 等具体制度称谓。
- 采用核心名称池：TUR 名称只按 Tag 或既有三条建国路线开放；BYZ 名称只按
  Tag 或当前政体家族开放，不再与所选国家集团身份交叉。
- 只增加名称候选，不增加集团效果、AI 权重、自动改名或持久状态。

## 3. 非目标

- 不替换或删除任何原版国家集团名称。
- 不覆盖 `common/history/power_blocs/`、国家集团身份、原则、徽章或 GUI。
- 不恢复原版开局奥斯曼国家集团，也不为现有集团强制改名。
- 不根据集团身份建立完整命名矩阵。
- 不新增事件、on_action、变量、迁移或存档 API。

## 4. TUR 核心名称池

| 技术 ID | 英文 | 简体中文 | 条件 |
|---|---|---|---|
| `ffpa_tur_anatolian_recovery_community` | Anatolian Recovery Community | 安纳托利亚重建共同体 | `c:TUR ?= this` |
| `ffpa_tur_council_of_the_straits` | Council of the Straits | 海峡理事会 | `c:TUR ?= this` |
| `ffpa_tur_porte_charter_system` | Porte Charter System | 高门宪章体系 | `ffpa_tur_has_ottoman_state_project_v1 = yes` |
| `ffpa_tur_conference_of_vilayets` | Conference of Vilayets | 行省会议 | `ffpa_tur_has_ottoman_state_project_v1 = yes` |
| `ffpa_tur_ankara_recovery_framework` | Ankara Recovery Framework | 安卡拉重建框架 | `ffpa_tur_has_republican_state_project_v1 = yes` |
| `ffpa_tur_council_of_anatolian_corridors` | Council of Anatolian Corridors | 安纳托利亚走廊理事会 | `ffpa_tur_has_republican_state_project_v1 = yes` |
| `ffpa_tur_anatolian_recovery_directorate` | Anatolian Recovery Directorate | 安纳托利亚重建总署 | `ffpa_tur_has_directorate_state_project_v1 = yes` |
| `ffpa_tur_anatolian_development_board` | Anatolian Development Board | 安纳托利亚发展理事会 | `ffpa_tur_has_directorate_state_project_v1 = yes` |

两个 Tag 通用名称保证刚形成、尚未完成建国路线选择的 TUR 仍有 FFPA 候选。
六个路线名称复用既有稳定查询 trigger，不直接读取
`ffpa_tur_state_project_v1`，也不改变路线含义。

## 5. BYZ 核心名称池

| 技术 ID | 英文 | 简体中文 | 条件 |
|---|---|---|---|
| `ffpa_byz_oikoumene_of_new_rome` | Oikoumene of New Rome | 新罗马普世共同体 | `c:BYZ ?= this` |
| `ffpa_byz_mediterranean_recovery_council` | Mediterranean Recovery Council | 地中海复兴理事会 | `c:BYZ ?= this` |
| `ffpa_byz_council_of_imperial_provinces` | Council of Imperial Provinces | 帝国行省理事会 | BYZ 且实行君主制 |
| `ffpa_byz_senate_of_cities_and_provinces` | Senate of Cities and Provinces | 城市与行省元老院 | BYZ 且实行总统制或议会制共和国 |
| `ffpa_byz_restored_oikoumene_synod` | Restored Oikoumene Synod | 复兴普世宗教会议 | BYZ 且实行神权制 |
| `ffpa_byz_congress_of_roman_communes` | Congress of Roman Communes | 罗马公社大会 | BYZ 且同时实行委员会共和国与无政府制 |
| `ffpa_byz_mediterranean_recovery_system` | Mediterranean Recovery System | 地中海重建体系 | BYZ 且实行企业国制 |

政体条件沿用现有 BYZ 动态国名已经验证的法律组合。无政府名称要求同时满足
`law_council_republic` 与 `law_anarchy`，避免普通委员会共和国过早使用“公社大会”。
未匹配上述五类政体时，两个 Tag 通用名称仍然可用。

## 6. 文件与所有权

新增文件：

- `common/power_bloc_names/ffpa_eastern_mediterranean_power_bloc_names.txt`

修改文件：

- `localization/english/ffpa_l_english.yml`
- `localization/simp_chinese/ffpa_l_simp_chinese.yml`
- `README.md`
- `AGENTS.md`

名称定义与本地化属于“东地中海模块：国家身份核心”，因为它们描述 TUR/BYZ
稳定的对外身份。TUR 路线名称只消费状态机已经导出的三个稳定 scripted trigger，
不复制或反向修改状态机。

`AGENTS.md` 需要把新数据库和本地化键加入身份核心所有权，并把这些新增顶层键登记为
普通新增对象而非上游覆盖。README 只在现有 TUR/BYZ 身份说明中窄增“国家集团候选名称”。

## 7. 数据流与兼容性

```text
国家集团创建/自定义界面
        │
        ├─ 当前领袖是 TUR
        │    ├─ Tag 通用名称
        │    └─ 既有建国路线 scripted trigger → 对应路线名称
        │
        └─ 当前领袖是 BYZ
             ├─ Tag 通用名称
             └─ 当前治理原则法律 → 对应政体名称

符合条件的本地化键 → 随机名称候选池 → 玩家可接受、随机或手工改名
```

条目只在界面请求候选名称时计算，不需要周期调度。旧存档中的既有国家集团名称不会
变化；玩家打开自定义界面并主动随机名称时，才可能选中新候选。

本设计不改变跨物理 Mod 接口、上游覆盖或存档 API。其他后加载 Mod 若定义相同的
`ffpa_` 顶层键或本地化键才会冲突；实施前后均需搜索最终加载栈确认不存在重复。

## 8. 验证

### 静态验证

- 新文件包含 15 个唯一的 `ffpa_` 顶层键：TUR 8 个、BYZ 7 个。
- 每个条目只有 country-scope `trigger`，不包含 effect 或状态写入。
- 所有英文显示名不超过 GUI 的 30 字符限制。
- 英文和简体中文各新增同一组 15 个键，现有 UTF-8 BOM 保持不变。
- 三个 TUR 路线 trigger 与 BYZ 使用的法律 ID 均能在最终加载栈中解析。
- 原版、Tech & Res、Firefall 与本项目不存在同名顶层键或本地化键。
- 元数据 JSON 仍可解析；花括号、字符串、注释与顶层结构正常。
- `git diff --check` 无新增空白错误。

### 游戏内验证

- 未选择路线的 TUR 随机名称只出现两个 TUR 通用候选及仍符合条件的原版候选。
- 三条 TUR 路线分别增加且只增加各自两个路线候选。
- BYZ 的通用候选始终可用；君主、共和国、神权、公社和企业国路径分别增加对应候选。
- GRE 和其他国家不获得任何 `ffpa_tur_*` 或 `ffpa_byz_*` 候选。
- 切换国家集团身份不改变核心候选池；玩家仍可输入自定义名称。
- 已存在的国家集团不会因加载 Mod、变更路线或变更政体而自动改名。

无法启动游戏时，交付必须将上述界面与随机池行为列为待游戏内确认，不能用静态定义
存在代替运行时到达证据。
