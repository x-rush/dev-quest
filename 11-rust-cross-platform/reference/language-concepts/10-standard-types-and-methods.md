# Rust 常用标准类型、方法与宏

Rust 的日常能力分布在原始类型方法、标准类型、trait 与宏中，不能机械照搬 Python 的“全局内置函数清单”。前置知识：所有权、借用、enum、泛型；暂时不理解泛型时，先把 `Option<T>` 读成“可能有一个 T”。本页是必要能力参考，完整签名从对应类型文档进入。

## 完整例子：错误怎样保留下来

运行 `cargo new parse-numbers`、`cd parse-numbers`，替换 `src/main.rs`，运行 `cargo run` 与 `cargo test`。无需第三方依赖。预期输出 `[2, 7, 10]` 和 `true`；4 个测试覆盖正常输入、空输入、非法文本和整数越界，运行证据见[验证报告](../../../shared-resources/tools/document-quality/reports/go-rust-project-validation.md)。

```rust
fn parse_all(input: &[&str]) -> Result<Vec<i32>, std::num::ParseIntError> {
    input.iter().map(|text| text.parse::<i32>()).collect()
}

fn main() -> Result<(), std::num::ParseIntError> {
    let mut values = parse_all(&["7", "2", "10"])?;
    values.sort();
    println!("{values:?}");
    println!("{}", parse_all(&["bad"]).is_err());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::parse_all;

    #[test]
    fn preserves_input_order() {
        assert_eq!(parse_all(&["7", "2", "10"]).unwrap(), [7, 2, 10]);
    }

    #[test]
    fn empty_input_is_success() {
        assert_eq!(parse_all(&[]).unwrap(), Vec::<i32>::new());
    }

    #[test]
    fn rejects_invalid_item_instead_of_dropping_it() {
        assert!(parse_all(&["7", "bad", "2"]).is_err());
    }

    #[test]
    fn rejects_integer_overflow() {
        assert!(parse_all(&["2147483648"]).is_err());
    }
}
```

`map` 产出一串 Result；收集目标明确为 `Result<Vec<_>, _>` 时，成功项收进 Vec，遇到错误则返回错误。这与 `filter_map(|s| s.parse().ok())` 不同：后者会丢掉失败项及错误信息。导入数据时选哪个策略是产品规则，应显式说明。

## Option 与 Result：缺失不是失败

| 方法/模式 | 对 Option 的含义 | 对 Result 的含义 |
|---|---|---|
| `match` | 分别处理 Some/None | 分别处理 Ok/Err |
| `map(f)` | 有值时变换 | 成功时变换 |
| `and_then(f)` | 串联另一个可缺失步骤 | 串联另一个可失败步骤 |
| `unwrap_or(default)` | 缺失时使用默认值 | 失败时使用默认值，错误被丢弃 |
| `unwrap_or_else(f)` | 需要时才计算默认值 | 需要时根据错误计算替代值 |
| `as_ref()` | 借用内部值 | 借用内部成功值或错误 |
| `unwrap()/expect(message)` | None 时 panic | Err 时 panic；expect 增加上下文 |

`Option::ok_or/ok_or_else` 把缺失转换成指定错误。`Result::map_err` 变换错误，`Result::ok` 会丢弃错误。`?` 提前传播，不能不分返回类型地从任意函数里使用。参数表达式先求值，因此 `unwrap_or(expensive())` 即使已有值仍计算 expensive；闭包版可延后执行。参考 [Option](https://doc.rust-lang.org/std/option/enum.Option.html)与 [Result](https://doc.rust-lang.org/std/result/enum.Result.html)。

## 集合、字符串与迭代

| 能力 | 输入输出与修改行为 | 边界 |
|---|---|---|
| `Vec::new/with_capacity` | 建立动态数组；预留容量 | capacity 不是 len，预留不产生元素 |
| `push/pop` | 尾部增删；pop 返回 Option | 空 Vec 的 pop 是 None |
| `get/get_mut` | 可选的共享/可变借用 | 下标 `v[i]` 越界会 panic，get 则返回 None |
| `len/is_empty` | 元素数/是否为空 | 与字符串的字节长度不要混用 |
| `sort/sort_unstable` | 原地排序 | 不稳定版不保留等价元素的相对顺序 |
| `retain` | 原地保留符合条件的项 | 与迭代器 filter 再收集不同 |
| `String::from/to_string` | 创建拥有所有权的文本 | `&str` 是借用视图，不等于 String |
| `push_str/clear` | 修改 String 内容 | clear 清空长度，不意味着立刻释放容量 |
| `trim/split/lines` | 获取借用片段或迭代器 | 不自动分配一组新的 String |
| `parse::<T>()` | 文本转实现 FromStr 的类型 | 返回 Result，失败不能假定为 0 |
| `chars/bytes` | Unicode 标量值 / UTF-8 字节遍历 | chars 不总等于人眼看到的字形簇 |
| `HashMap::insert/get/entry` | 存取键值；就地处理占用/空缺 | 遍历顺序不应作稳定输出契约；需要排序可用 BTreeMap |

字符串不能直接以整数下标获取“第几个字符”。切字节区间还必须落在 UTF-8 边界；UI 文本的字形簇处理通常需要额外 Unicode 库。查 [String](https://doc.rust-lang.org/std/string/struct.String.html)、[Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html)、[HashMap](https://doc.rust-lang.org/std/collections/struct.HashMap.html)。

迭代器应先看元素类型：`iter` 常给出 `&T`，`iter_mut` 给出 `&mut T`，集合的 `into_iter` 通常消费集合取得 T。`map/filter/take/enumerate/zip` 等组合操作通常是惰性的；`collect/sum/fold/for_each` 或 for 循环消费它们。`find/any/all` 可以提前停止，不能假定每项副作用都会运行。`cloned` 调用 Clone，`copied` 需要 Copy。完整协议见 [Iterator](https://doc.rust-lang.org/std/iter/trait.Iterator.html)。

## 常用宏与转换

| 名称 | 返回或效果 | 注意 |
|---|---|---|
| `vec!` | Vec | 重复元素形式遵循 Clone 语义 |
| `format!` | String | 只构造文本，不输出 |
| `println!/eprintln!` | 输出到标准输出/错误 | 输出格式 `{:?}` 要求 Debug，`{}` 通常要求 Display |
| `assert!/assert_eq!/assert_ne!` | 条件不满足 panic | 可用于测试与必须保持的不变量 |
| `matches!` | bool | 检查模式是否匹配，不提取返回绑定供外部使用 |
| `dbg!` | 打印到标准错误并返回传入值 | 可能移动传入值；需要保留所有权可观察引用 |
| `todo!/unimplemented!` | 执行时 panic | 不能留在声称已实现的成功路径 |
| `panic!/unreachable!` | 触发 panic | 不能代替对正常用户输入错误的 Result 处理 |
| `include_str!/include_bytes!` | 编译期包含内容 | 修改资源后需要重新编译；不是运行时读取文件 |
| `env!/option_env!` | 编译期环境值 | 与 `std::env::var` 的运行时读取不同 |

`From/Into` 表示转换约定，`TryFrom/TryInto` 允许失败；`Default` 提供类型默认值；`Clone` 的复制深度取决于类型，Arc 的 clone 增加共享持有者。不要把所有标准 trait 当成编译器魔法；它们可以由用户类型实现，但必须遵守各自契约。

## 练习与验收

把输入改为 `["7", "bad", "2"]`：当前 parse_all 应返回 Err；再单独实现“跳过错误”和“收集所有错误位置”两种策略，说明它们服务的需求不同。不得只用 unwrap 把失败变成 panic。最后让空输入得到 Ok 的空 Vec，检查这一行为是否符合调用方约定。

下一篇：[常用标准库地图](../library-guides/15-standard-library-map.md)。返回[模块导读](../../LEARNING_GUIDE.md)。
