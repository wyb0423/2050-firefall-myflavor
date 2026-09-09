# 脚本工具

基线：CMF 1.65.0，2026-09-09 源码核对；路径相对 CMF_ROOT。片段为接入示意，尚未游戏内验证。

## 变量：简单机制优先

来源 `common/scripted_effects/com_general_effects.txt`。`com_change_variable = { name = my_counter value = 1 }` 在当前支持变量的 scope 上累加，缺失时按零起步；local/global 变体操作不同存储区。`com_save_journal_to_variable = { name = my_journal }` 需要已有 `scope:journal_entry`，保存到当前 scope。

只需现有变量加一时原生 change_variable 即可。使用 clamp / map helper 前读函数体和每个参数，不根据名称推断 min/max 的脚本运算语义。机制结束时按存档接口约定保留或移除变量；检查首次初始化、重复调用和边界值。

## 每周调度

最小目标文件：一个自有 `common/on_actions/my_weekly.txt`，以及需要的业务 effects。来源 `common/on_actions/com_weekly_on_action.txt`、`common/scripted_effects/com_weekly_event.txt` 和 `common/script_values/com_weekly_event_script_values.txt`。

```text
on_monthly_pulse = {
    on_actions = { my_schedule_weekly }
}
my_schedule_weekly = {
    effect = {
        com_run_weekly_event_country_effect = {
            weekday = 1
            on_action = my_weekly_country
        }
    }
}
my_weekly_country = {
    effect = {
        # 当前为 country scope；在这里调用自有业务 effect。
    }
}
```

这从全局月脉冲排程，内部遍历所有国家，weekday 0–6 为周日至周六；不要在每个国家的 pulse 中再调用调度器。只需要 JE 自身每周更新时直接使用 JE 原生 on_weekly_pulse。已经排程的回调可能在业务结束后到达，在业务 effect 内检查仍然有效的条件。

实机检查跨月、不同月长、目标星期和单国执行次数；新加调度器在旧档的首次启动时间也要验证。示例中的空业务体须替换，不部署空壳。

## Float Array

最小文件：自己的 scripted effect 文件与调用入口；通常无需改 CMF。来源 `common/scripted_effects/com_floatarray_effects.txt` 和 `com_floatarray_utils.txt`。

```text
# 同一个支持变量的 scope；只在初始化时创建。
com_floatarray_initialize = { NAME = my_array SIZE = 8 }
com_floatarray_set_index = { VALUE = 0 }
com_floatarray_set_value = { VALUE = 42 }
com_floatarray_set = { NAME = my_array SIZE = 8 }
com_floatarray_get = { NAME = my_array SIZE = 8 }
# 此时先消费/保存 var:com_fa_return，再做其他数组操作。
# 生命周期结束时：com_floatarray_clear = { NAME = my_array SIZE = 8 }
```

wrapper 检查声明大小与存储大小是否相符；仍由调用方约束索引 0..SIZE-1。验证首次创建、索引 0/末尾、写后读和清理；别在每次读取前重新初始化，避免抹掉数据。

## 生命周期与内部工具约束


- `create_struct` 通过 `create_character` 创建对象；`destroy_struct` 会 kill/free 角色。使用前读模板、角色类型和月度维护；不要移除框架内部 `is_struct`、`com_type` 等标识。
- Float Array 初始化为 `com_floatarray_initialize = { NAME = my_array SIZE = 8 }`。8 元素接口是 `com_floatarray_8_get/set/foreach/clear`；索引为 `var:com_fa_index`，写入为 `var:com_fa_value`，读取返回 `var:com_fa_return`。独立数组名不能隔离这些工作变量，嵌套操作要先保存需要的值。
- Dict 的源码声明数字键有 2047 上限，并使用固定点数打包。边界、负数和精度未做运行验证，不把它作为通用无损字典推荐。
- 周调度 effect 内部已有 `every_country`。不要放进国家逐个执行的 pulse 再反复调用，否则会重复排程。自建唯一的月度入口和周回调；示例 setter 默认没有接入月脉冲。
- `com_delay_event_switch` 当前列出 0–31 天分支，不是任意延迟调度器。
- `fix_variable_error` 是框架的变量/flag 报错抑制工具，不会修正拼错的变量、缺失初始化或错误 scope。
- global history 只负责新游戏初始化；已有存档需要独立的幂等初始化/迁移，不能假设新增侧栏或组织注册会自动补上。

