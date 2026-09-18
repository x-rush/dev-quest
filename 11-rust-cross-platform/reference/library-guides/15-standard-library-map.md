# Rust 常用标准库地图

前置知识：模块、Result、所有权与借用。先会用标准库完成文件、数据结构、线程和错误处理，再按需求引入 Tokio、Serde 或应用框架。`std`、`core`、`alloc` 有不同运行环境假设；本页面向普通操作系统上的 std 应用，嵌入式 no_std 另作专题。

## 按任务查入口

| 任务 | 模块与常用入口 | 先学会的边界 |
|---|---|---|
| 字符串和动态数组 | `std::string::String`、`std::vec::Vec`、切片方法 | 拥有数据还是借用；长度与容量 |
| 键值、去重、队列 | `std::collections::{HashMap, HashSet, BTreeMap, VecDeque}` | 哈希表顺序无保证；BTreeMap 依键排序 |
| 文件读写 | `std::fs::{read, read_to_string, write, File}` | 错误传播、内存用量、覆盖行为 |
| 流式输入输出 | `std::io::{Read, Write, BufRead, BufReader, BufWriter}` | 部分读写、刷新、缓冲区；不能假定一次 read 填满 |
| 路径 | `std::path::{Path, PathBuf}` | 用路径 API 组合；路径不保证 UTF-8，避免强行 unwrap |
| 参数与环境 | `std::env::{args_os, var, current_dir}` | 环境值可能缺失或不是 Unicode；参数存在不代表格式合法 |
| 时间 | `std::time::{Instant, Duration, SystemTime}` | 测耗时用 Instant；系统时钟可能调整 |
| OS 线程 | `std::thread::{spawn, scope, sleep}` | join、错误处理、线程并非越多越快 |
| 共享状态 | `std::sync::{Arc, Mutex, RwLock}` | Arc 只解决共享所有权；内部可变数据仍须同步 |
| 消息通信 | `std::sync::mpsc` | 发送者/接收者关闭、阻塞与容量设计 |
| 网络基础 | `std::net::{TcpListener, TcpStream, UdpSocket}` | 是传输层能力，不自动实现 HTTP、TLS 或重试 |
| 子进程 | `std::process::Command` | 参数分开传；检查退出状态；管道可能需要持续读取 |
| 类型转换与迭代 | `std::convert`、`std::iter` | 失败型转换、消费与借用 |
| 错误契约 | `std::error::Error`、`std::fmt` | 展示上下文与底层原因；别向用户泄漏敏感内部信息 |

官方入口：[标准库总览](https://doc.rust-lang.org/std/)。在类型页面同时看 Methods、Trait Implementations、错误条件与稳定版本标注。页面里标成 Experimental 的条目不能直接当稳定基线。

## 完整练习：按行统计非空任务

创建 Cargo 二进制项目，在项目目录建立 UTF-8 文件 `tasks.txt`，包含两行文本，中间留一空行，例如 `read`、空行、`test`。将下面代码放入 `src/main.rs`，执行 `cargo run -- tasks.txt`，预期输出 `2`。本轮未在本机 Rust 工具链执行。

```rust
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::path::Path;

fn count_tasks(path: &Path) -> io::Result<usize> {
    let reader = BufReader::new(File::open(path)?);
    let mut count = 0;
    for line in reader.lines() {
        if !line?.trim().is_empty() {
            count += 1;
        }
    }
    Ok(count)
}

fn main() -> io::Result<()> {
    let path = std::env::args_os().nth(1).ok_or_else(|| {
        io::Error::new(io::ErrorKind::InvalidInput, "usage: counter <path>")
    })?;
    println!("{}", count_tasks(Path::new(&path))?);
    Ok(())
}
```

File::open 可能失败，读每一行也可能失败，所以两个位置都需要传播错误。BufReader 减少细碎系统调用；lines 逐行产生 String，避免一次读入全文件，但超长单行仍占内存。这个程序按 UTF-8 文本处理，不是任意二进制文件计数器。读取与缓冲契约见 [BufRead](https://doc.rust-lang.org/std/io/trait.BufRead.html)。

## 什么不在标准库里

JSON/通用序列化通常使用 Serde 生态；异步 I/O 应用使用 Tokio 等运行时；HTTP 客户端/服务、TLS、数据库与复杂日期时区各有专门库。标准库有 Future 和 TCP，不能据此认为已经内置完整异步 HTTP 服务。先让上面的同步 CLI 可靠处理错误，再看[Tokio](12-tokio-guide.md)和 [Serde](13-serde-guide.md)。

## 验收与扩展

无参数、文件不存在、空文件、含空白行分别验证。成功路径输出计数；失败路径应非零退出，不返回假计数 0。扩展为“输出每种标签的次数”时用 BTreeMap 保证稳定的字典序输出，再写测试比较完整输出。暂时不引入数据库或桌面框架；这些工具不帮助解释本例的文件与错误边界。

返回[模块导读](../../LEARNING_GUIDE.md)与[标准类型参考](../language-concepts/10-standard-types-and-methods.md)。
