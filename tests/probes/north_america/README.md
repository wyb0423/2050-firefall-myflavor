# 北美分裂州验证包（开发专用）

此目录是独立测试 Mod，放在 `tests/` 下不会被主风味包当作运行时加载。未安装或启用；不得发布为正式内容。

只在 Firefall 0.1.1 的一次性新游戏中使用，选择芝加哥城邦 `ZZZILLINOISCITY` 并暂停。测试会把罗克福德林镇开局的五个省份分两次移交芝加哥，永久改变当前测试档；不得用于用户正常存档，也没有自动回滚。没有启动或月度自动转移。

## 要回答的问题

1. 一省割让后，原 state 引用是否仍有效？
2. 最后四省并入既有芝加哥 state 后，原 state 是否消失？
3. 原 state 的 modifier、变量是保留、复制、丢失还是合并？
4. 所有权变化与新州回调的时序如何？立即、过一天、存读档后是否一致？

原版 `common/scripted_effects/00_chris_scripted_effects.txt` 的 `transfer_province` 提供 `p:ID.state` 与 `set_owner_of_provinces` 先例；原版 `00_code_on_actions.txt` 提供两个回调。静态先例不能证明结果，输出如实记录 PRESENT/ABSENT。

## 测试步骤

1. 用独立测试 playset 挂载此目录，位于 Firefall 和本项目之后；保持用户原 playset 和存档不变。控制台需要 debug mode。
2. 选择芝加哥，暂停，依次在控制台执行下列命令。每次记录 `FFPA_NA_PROBE` 日志，并检查同期 `error.log`。

```text
effect ffpa_na_probe_setup_v1 = yes
effect ffpa_na_probe_partial_v1 = yes
effect ffpa_na_probe_report_v1 = yes
effect ffpa_na_probe_merge_v1 = yes
effect ffpa_na_probe_report_v1 = yes
```

3. 推进一天后再次 report；另存测试档，重新加载后再次 report。只有 `ALL_FIVE_OWNED` 证明所有原目标省份已转入，原 state 存在与否不能单独证明完成。
4. 检查芝加哥伊利诺伊州的 1% 测试税收能力 modifier 实际份数/数值；日志只报告存在性，不能证明没有叠层。
5. 错误国家、重复 setup、跳过 partial 的 merge 都必须输出 REJECTED 且不转移领土。
6. 把日志与原始错误保存到实施记录；测试后禁用本包，不把测试存档继续当作正常游戏。

## 当前验证状态

测试包仅已做静态结构、引用和开局省份核对；未启动游戏，以上运行结果均未知。AI 目标选择属于后续独立验证，此包不证明 AI 改善。
