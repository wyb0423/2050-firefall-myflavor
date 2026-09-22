# 全球利益集团立场重塑设计

日期：2026-09-22

状态：讨论基线已接受，并纳入用户最新的实业家修正；仅设计，尚未实施。配套实施计划须在修改游戏脚本前确认。

## 1. 目标与范围

在 Firefall 的国家重建、经济恢复和制度竞争背景下，调整集团的政治立场。保留八大利益集团名称与社会基础，不以核灾难、避难所或拾荒社会作为核心创作概念。

首期四个新理念、四个原有理念的定向变体，影响六个集团。地主、实业家、小市民、乡村民众重点重塑；虔信者、工会各调整一个立场；知识分子、军队保留现有理念。

不改变人口吸引力、领袖生成、集团特质及其数值、法律效果、国家成立条件。不新增事件、日志、政治运动、思想阶段链、UI、资源或依赖。不修改 Core Balance，也不提升发布版本。

集团理念定义长期利益；领袖和国家专属理念仍可形成不同立场。通用设计不保证在所有国家、所有领袖下得到同一政治结果。

## 2. 调研基准与限制

- 当前本地游戏：Victoria 3 1.13.11；Firefall 0.1.1；Tech & Res 1.6'；CMF 1.65.0。
- 目标栈遵循 README 的推荐顺序。本机最近保存的加载清单不是 Firefall 配置，未将其视为目标栈实机证据。
- 原版 `common/interest_groups/00_*.txt` 提供八个基础集团、人口条件及初始化。Tech & Res 与 Firefall 未提供独立的八集团重构。
- 原版 `common/ideologies/00_ig_ideologies.txt` 提供下表的通用基础立场。Firefall 的 `common/ideologies/ztr_ideologies.txt` 与当前 Tech & Res 对应文件相同。
- Firefall 的 `common/scripted_effects/tff_country_techs.txt` 显示低档科技包也包含人权等知识，不把经济发展不足等同于没有现代政治观念。
- Firefall 的 `events/ztr_modern_individualism.txt` 已提供实业家个人主义向现代个人主义的转换；本设计保留该路径。
- Firefall 的 `common/scripted_effects/ztr_main_scripts.txt` 中后期转换按 `ideology_laissez_faire` 查找目标；新增发展主义必须接续该路径。
- 本项目 `common/scripted_effects/ffpa_eastern_mediterranean_effects.txt` 的国家理念转换依赖原理念存在，需要扩大明确的来源清单。

下表比较的是指定理念的基础值，不是引擎汇总领袖、其他理念和优先级后的最终集团态度。未列出的原有法律组、法律值与相关元数据原则上保留；新增法律组的完整立场在表中列明。实施时重新核对目标栈，不能用本文件代替上游差异检查。

## 3. 新理念及替换关系

| 新理念 | 集团 | 替换的通用理念 | 职责 |
|---|---|---|---|
| 地产保守主义 | 地主 | `ideology_paternalistic` | 维护精英权力、土地收益和财产秩序，允许不同政体与经济发展 |
| 发展主义 | 实业家 | `ideology_laissez_faire` | 市场主导的生产恢复，接受有限干预、基础监管与劳动力培养 |
| 共和保守主义 | 小市民 | `ideology_reactionary` | 共和、财产与晋升机会，同时保留文化保守和秩序诉求 |
| 乡村自治主义 | 乡村民众 | `ideology_isolationist` | 受保护的市场与地方代表，降低闭关倾向 |

另外建立地主阶序主义、小市民爱国主义、虔信者道德主义、工会无产阶级主义的定向变体。它们保留原有显示名称并修订相应描述，不另造四个政治标签。定向替换不改变同一原始理念在其他集团中的定义。

使用本模块独有 `ffpa_global_ig_` 前缀登记新增技术对象。具体完整对象清单在实施第一步按数据库查重后固定，首次进入运行时或存档后不静默改名。

## 4. 地主

### 4.1 地产保守主义

基于 `ideology_paternalistic`，仅修改下列值：

| 法律键 | 原值 | 新值 |
|---|---|---|
| `law_monarchy` | strongly_approve | approve |
| `law_presidential_republic` | neutral | approve |
| `law_theocracy` | approve | neutral |
| `law_oligarchy` | approve | strongly_approve |
| `law_autocracy` | strongly_approve | approve |
| `law_wealth_voting` | neutral | approve |
| `law_census_voting` | disapprove | neutral |
| `law_hereditary_bureaucrats` | approve | neutral |
| `law_appointed_bureaucrats` | neutral | approve |
| `law_traditionalism` | strongly_approve | neutral |
| `law_interventionism` | neutral | approve |
| `law_laissez_faire` | disapprove | neutral |
| `law_isolationism` | approve | neutral |
| `law_protectionism` | neutral | approve |

仍支持地产投票，反对普选和削弱精英控制的制度。君主制与总统共和制同为支持，不由该理念单独推动两者相互切换；议会共和制保持中立。

### 4.2 地主阶序主义变体

基于 `ideology_hierarchic`：

| 法律键 | 原值 | 新值 |
|---|---|---|
| `law_serfdom` | strongly_approve | neutral |
| `law_tenant_farmers` | approve | strongly_approve |
| `law_commercialized_agriculture` | neutral | approve |

税收、福利、其他土地及身份立场保持原值。地产保守主义与该变体分工，国家专属政治理念可以取代前者而不顺带抹掉土地立场。

## 5. 实业家

发展主义基于 `ideology_laissez_faire`。以下是纳入用户最终修正后的完整关注项；表中保留两项不变值，防止误用上一轮提案。

| 法律键 | 原值 | 新值 |
|---|---|---|
| `law_laissez_faire` | strongly_approve | strongly_approve |
| `law_interventionism` | approve | approve |
| `law_free_trade` | approve | strongly_approve |
| `law_protectionism` | disapprove | neutral |
| `law_child_labor_allowed` | approve | disapprove |
| `law_restricted_child_labor` | neutral | approve |
| `law_compulsory_primary_school` | disapprove | neutral |
| `law_regulatory_bodies` | disapprove | approve |
| `law_worker_protections` | strongly_disapprove | disapprove |

实业家优先自由放任和自由贸易，接受干预主义，对保护主义及义务初等教育保持中立。有限童工与基础监管获得支持，但更强的劳动保障仍受反对。合作所有制、计划经济继续强烈反对。

“义务教育”在本轮修改中指此前讨论的 `law_compulsory_primary_school`，不扩大到 Tech & Res 的强制中等教育或公立大学。学校所有制、财阀主义、个人主义、现代个人主义不在此处改写。

上游原有后期新自由主义转换继续适用于发展主义。已经持有 `ideology_neoliberism` 的旧档不降级成发展主义；上游个人主义向现代个人主义的转换不受影响。

## 6. 小市民

### 6.1 共和保守主义

基于 `ideology_reactionary`：

| 法律键 | 原值 | 新值 |
|---|---|---|
| `law_presidential_republic` | neutral | approve |
| `law_parliamentary_republic` | neutral | approve |
| `law_monarchy` | approve | neutral |
| `law_social_monarchy` | approve | neutral |
| `law_theocracy` | approve | disapprove |

公民权、劳工组织、移民态度保持原值。保留精英主义及其资格性选举、晋升和反世袭取向；支持共和不等于支持普选或文化平等。

### 6.2 小市民爱国主义变体

基于 `ideology_patriotic`，只用于小市民：

| 法律键 | 原值 | 新值 |
|---|---|---|
| `law_dedicated_police` | approve | strongly_approve |
| `law_militarized_police` | strongly_approve | approve |

军队保留原爱国主义。其他内务、言论和海军立场不变。

## 7. 乡村民众

乡村自治主义基于 `ideology_isolationist`：

| 法律键 | 原值 | 新值 |
|---|---|---|
| `law_isolationism` | approve | disapprove |
| `law_protectionism` | approve | strongly_approve |
| `law_closed_borders` | strongly_approve | neutral |
| `law_elected_bureaucrats` | 未表态 | approve |
| `law_appointed_bureaucrats` | 未表态 | neutral |
| `law_hereditary_bureaucrats` | 未表态 | disapprove |

新增官僚制法律组包含以上三项。保留农本主义和特殊主义，不重复新增自耕、民兵和反征发理念。自由贸易、无移民控制仍反对，移民控制仍支持。其他殖民、公民权、海军立场不变。

“自治”只通过现有法律表达，不实现联邦制、地方财政或新的地方政府系统。

## 8. 其他集团

- 虔信者道德主义变体：基于 `ideology_moralist`，仅将 `law_monarchy` 从 strongly_approve 改为 neutral。神权制、其他政体和政教关系原值保留。
- 工会无产阶级主义变体：基于 `ideology_proletarian`，仅将 `law_command_economy` 从 approve 改为 neutral。合作所有制、公共福利、劳动保障、税收与组织权原值保留。
- 知识分子、军队的基础理念不改。上述变体只替换指定集团中的通用原型，不覆盖宗教、文化或国家已有专属变体。

## 9. 分配、国家接续与迁移

1. 本项目新增“全球政治风味”内部模块，独立持有定义、本地化和轻量调度，不把全球业务写进东地中海调度器，不拆出新的物理 Mod。
2. 八项替换均为明确的“指定集团＋已知源理念”映射。只删除相应源对象，添加单个对应对象；不清空理念集合，不批量恢复所谓默认值。
3. 缺失目标集团、源理念已被专属理念替代、目标理念已存在时安全跳过。来源与目标意外共存时，只清理该映射的源对象，不清理其他理念。
4. 新档、旧档补挂、新国家或身份变化共用有界的原生 effect。重复执行不改变法律、领袖、名称、特质，不发放资源或奖励，不重新覆盖已经生效的国家特色。
5. TUR/BYZ 原有实业家与小市民理念转换、TUR 地主行省契约、BYZ 虔信者帝国共治的来源判断要纳入对应通用新对象。形成国家与通用分配的先后顺序都应得到相同结果。
6. 国家专属政治理念只接管自己原先替换的部分。例如 TUR 行省契约取代地产保守主义；地主阶序主义变体可继续存在。小市民的国家理念取代共和保守主义，治安变体保留。其余专属定义、奖励、选择和旧 `_v1`/`_v2` 变量语义不变。
7. 原有国家门控已处理的旧档，不通过清除旧门控重放事件。若发现历史上应获专属理念却缺失的情况，仅在现有身份和路线能够证明时执行独立、有版本的修复，不凭通用初始化猜测路线。
8. 发展主义接续原生后期转换：与原自由放任来源相同的科技/阶段入口、相同目标新自由主义，不另建月度思想演变。保留上游其他集团、BPM 条件分支和全部非相关行为。
9. 保留同一原型在其他集团和领袖中的使用。不能提高优先级到足以压制领袖和既有专属理念来掩盖叠加问题。

## 10. 验收与已知限制

- 八项定义以实机目标栈中的源理念为基准，逐项证明只有本文批准的值变化；完整保留未改法律组和元数据。
- 执行实际分配脚本子集，验证普通国家、源缺失、重复执行、源目标共存、已有国家变体、国家形成两种顺序、旧档与后期转换。
- 实业家固定断言：自由放任 strongly_approve、干预主义 approve、自由贸易 strongly_approve、保护主义 neutral、义务初等教育 neutral。
- 不新增集团或改变人口吸引力、领袖生成、法律本身效果、集团名称及特质数值。
- 检查中英本地化、BOM、图标存在性、顶层键唯一性及引用。理念文本要与实际态度一致，不暗示未实现的地方自治或制度。
- 静态/脚本子集验证不能证明原生理念优先级、领袖覆盖、立法支持、AI、初始化时序或存读档；这些属于后续实机验收，本轮没有启动游戏。

对应实施计划：[`../plans/2026-09-22-global-interest-group-positions-implementation-plan.md`](../plans/2026-09-22-global-interest-group-positions-implementation-plan.md)。
