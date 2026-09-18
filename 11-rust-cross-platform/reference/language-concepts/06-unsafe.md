# unsafe Rust

## 概述

Rust 的安全承诺是：健全的安全 Rust 代码不会自行引入未定义行为（UB）；但依赖库内部不健全的 unsafe、FFI 或编译器缺陷仍可能破坏这一保证。`unsafe` 并不关闭借用检查、也不改变类型系统，只是**开放五种编译器无法自动验证的操作**，把正确性责任从编译器转移到程序员，并要求用"安全封装"把风险约束在边界内。本篇覆盖超能力清单、裸指针、Send/Sync 实现边界、安全封装模式与典型 UB。基线 Rust 1.98.1 / edition 2024（见[模块 README](../../README.md)）。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#rust` `#reference` `#unsafe` `#裸指针` `#Send-Sync` |
| **更新日期** | `2026年9月` |

</details>

## 条目 1：unsafe 关键字与五种超能力

📌 **定义**: `unsafe` 标记"此处依赖程序员担保"的三种语法位置——**unsafe 块**、**unsafe fn**、**unsafe trait**。edition 2024 下，unsafe fn 体内执行 unsafe 操作同样需要显式 unsafe 块（`unsafe_op_in_unsafe_fn` 默认告警，依赖对应 edition 的 lint 配置）。

📖 **五种超能力全表**:

| # | 超能力 | 典型语法 | 编译器为什么无法验证 |
|---|--------|---------|---------------------|
| 1 | 解引用裸指针 | `*p` | 指针可能悬垂/未对齐/别名 |
| 2 | 调用 unsafe 函数/方法（含 FFI `extern`） | `f()` | 前置条件是文档契约，无法静态检查 |
| 3 | 访问/修改 `static mut` | `COUNTER += 1` | 跨线程访问无法静态判定 |
| 4 | 实现 unsafe trait | `unsafe impl Send for T` | 契约是类型级承诺（如线程约束） |
| 5 | 读 union 字段 | `u.field` | 当前活跃变体只有程序员知道 |

**static mut 特别注记**（edition 2024，依赖对应 edition 的 lint 配置）：经引用访问 `static mut`（`&COUNTER`）为**硬错误**（`static_mut_refs` deny）；取地址须用 `&raw const` / `&raw mut` 或 `addr_of!`，跨线程计数场景直接改用原子类型（`AtomicUsize`）。

💡 **示例**（unsafe trait + unsafe fn，edition 2024 示例，本轮未运行）:

```rust
// unsafe trait：实现者必须担保契约
unsafe trait Zeroable {
    /// 契约：全零位是本类型的合法值
    unsafe fn zeroed(&mut self);
}

struct Packet([u8; 4]);

unsafe impl Zeroable for Packet {
    unsafe fn zeroed(&mut self) {
        // SAFETY: [u8; 4] 的全零位是合法值，指针来自 &mut self 且对齐有效
        unsafe {
            std::ptr::write_bytes(self as *mut Packet, 0, 1);
        }
    }
}

fn main() {
    let mut p = Packet([1, 2, 3, 4]);
    unsafe { p.zeroed(); } // 调用 unsafe 方法必须显式 unsafe 块
    println!("{:?}", p.0); // [0, 0, 0, 0]
}
```

⚠️ **常见陷阱**: unsafe **不豁免借用检查**——unsafe 块内用引用违规照样编译失败；`unsafe` 块的语义是"我担保此处满足被调用者的前置条件"，不是"关掉检查器"。

🔗 **相关条目**: [条目 2：裸指针](#条目-2裸指针-const-t--mut-t)

## 条目 2：裸指针 `*const T` / `*mut T`

📌 **定义**: 裸指针是无生命周期、无别名保证、可为空/悬垂的地址。通常创建裸指针本身不需要 unsafe，但原始引用与别名约束不会因转换而自动消失，**解引用需要**。`*const T` 不可写，`*mut T` 可写；两者默认 `!Send` `!Sync`。

📖 **创建途径**（均为安全操作）:

| 写法 | 语义 |
|------|------|
| `&x as *const T` / `&mut x as *mut T` | 从引用转换；之后访问仍须满足来源、有效性与别名规则 |
| `&raw const x` / `&raw mut x`、`addr_of!` / `addr_of_mut!` | 不经中间引用取地址（绕开对齐/初始化限制，edition 2024 下访问 `static mut` 的正道） |
| `slice::as_ptr()` / `as_mut_ptr()` | 取切片首元素地址 |
| `Box::into_raw(b)` | 转出所有权，此后须 `Box::from_raw` 手动释放 |

**常用方法表**:

| 方法 | 安全性 | 语义 |
|------|--------|------|
| `is_null()` | 安全 | 判空 |
| `as_ref()` / `as_mut()` | unsafe | 升级为 `Option<&T>`（空指针得 `None`，悬垂仍 UB） |
| `add(n)` / `offset(n)` | unsafe | 偏移（前提：结果仍在同一分配内） |
| `wrapping_add(n)` | 安全 | 允许越界数值，但不可解引 |
| `read()` / `write()` | unsafe | 按值读/写（对齐不保证时用 `read_unaligned` 等变体） |
| `copy_nonoverlapping()` / `copy()` | unsafe | 内存搬运（memcpy / memmove 语义） |

💡 **示例**（edition 2024 示例，本轮未运行）:

```rust
fn main() {
    let mut x: i32 = 5;

    // 创建裸指针本身是安全操作，访问时仍必须证明别名和有效性
    let pm = &raw mut x;
    let pc = pm as *const i32; // 两者源自同一可写位置；以下按顺序访问

    unsafe {
        // 超能力 1：解引用裸指针
        println!("*pc = {}", *pc);
        *pm = 10;
        println!("*pm = {}", *pm);
    }
    println!("x = {x}");

    // 常用指针方法：as_ref/add 需在 unsafe 块中调用，is_null 本身安全
    let arr = [10i32, 20, 30];
    let p = arr.as_ptr();
    unsafe {
        assert_eq!(p.as_ref(), Some(&10));
        println!("p.add(2) = {}", *p.add(2)); // 30（前提：偏移后仍在分配内）
    }
    println!("is_null(pc) = {}", pc.is_null());
}
```

⚠️ **常见陷阱**: 裸指针的读写不经过借用检查——同一位置的两把"裸"访问是否冲突，全靠程序员维持不变量；`as_ref()` 只解决判空，悬垂指针升级为引用后仍是 UB。

🔗 **相关条目**: [条目 3：安全封装模式](#条目-3安全封装模式)、[条目 5：典型 UB 清单](#条目-5典型-ub-清单)

## 条目 3：安全封装模式

📌 **定义**: unsafe 的工程纪律是"**把 unsafe 压到最小面积，用安全 API 把不变量关进类型**"：外部使用者无论怎么调用都无法触发 UB，unsafe 只出现在建立不变量的构造点、恢复不变量的析构点、依赖不变量的解引用点。

📖 **模式清单**:

1. **不变量集中在唯一构造点建立**：构造函数校验/排序/分配，坏输入返回 `Result`/`Option` 而不是带病上岗
2. **Drop 恢复所有权**：谁 `into_raw` 谁 `from_raw`，避免双重释放
3. **unsafe 面最小化**：每个 unsafe 块对应一条可检查的不变量，不写"大 unsafe 函数"
4. **SAFETY 注释**：惯用 `// SAFETY: ...` 逐条列出前置条件与满足理由
5. **不泄漏抽象**：公开方法在任何输入序列下都维持不变量；内部表示（裸指针/布局假设）不出现在公开 API 签名里

**标准库例证**：`Box`/`Vec`/`String` 内部都是这类封装；`Vec::set_len` 是 unsafe fn，其文档列出的安全性前置条件就是"封装契约"的样板。

💡 **示例**（手写 Box，edition 2024 示例，本轮未运行）:

```rust
use std::ops::Deref;
use std::marker::PhantomData;

// 手写 Box：演示"unsafe 面最小化 + 不变量集中在构造/析构"的安全封装模式
struct MyBox<T> {
    ptr: *mut T,
    _owns: PhantomData<T>,
}

impl<T> MyBox<T> {
    fn new(value: T) -> Self {
        // 不变量在这里建立：ptr 永远来自 Box::into_raw（非空、独占、可安全释放）
        MyBox {
            ptr: Box::into_raw(Box::new(value)),
            _owns: PhantomData,
        }
    }
}

impl<T> Drop for MyBox<T> {
    fn drop(&mut self) {
        // SAFETY: ptr 由 Box::into_raw 创建，只在此处恢复所有权一次，不会双重释放
        unsafe {
            drop(Box::from_raw(self.ptr));
        }
    }
}

impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T {
        // SAFETY: 不变量保证 ptr 有效、非空、生命周期覆盖 self
        unsafe { &*self.ptr }
    }
}

fn main() {
    let b = MyBox::new(String::from("安全封装"));
    // Deref 解引：像用 T 一样用 MyBox<T>
    println!("{} 长度 {}", *b, b.len());
}
```

⚠️ **常见陷阱**: 封装破洞最常见于把内部 `*mut` 泄漏进 `pub` 字段/返回值；其次是在非构造路径绕过校验直接改状态（提供 `as_raw()` 之类逃生口时须同步文档契约）。

🔗 **相关条目**: [条目 2：裸指针](#条目-2裸指针-const-t--mut-t)、[智能指针全表](./07-smart-pointers.md)（std 中的封装成品）

## 条目 4：Send/Sync 的 unsafe 实现边界

📌 **定义**: `Send` = 所有权可跨线程转移；`Sync` = `&T` 可跨线程共享（`T: Sync` ⇔ `&T: Send`）。两者是 **unsafe marker auto trait**：编译器按"字段全部满足则类型满足"自动推导，但也可 `unsafe impl` 手动承诺——承诺错了就是数据竞争。

📖 **自动推导与例外**: 含 `*const T`/`*mut T` 字段的类型默认 `!Send` `!Sync`（编译器无法证明指针指向数据的线程约束）——这正是 unsafe impl 的主战场。

**常见类型线程约束表**:

| 类型 | Send | Sync | 备注 |
|------|------|------|------|
| `Rc<T>` | ✗ | ✗ | 非原子计数 |
| `RefCell<T>` / `Cell<T>` | ✓（T: Send） | ✗ | 运行时借用检查非线程安全 |
| `*const T` / `*mut T` | ✗ | ✗ | 手动 unsafe impl 的对象 |
| `Mutex<T>` | ✓（T: Send） | ✓（T: Send） | 独占访问由锁保护 |
| `RwLock<T>` | ✓（T: Send） | ✓（T: Send + Sync） | 并行共享读取还要求 T: Sync |
| `Arc<T>` | ✓ | ✓ | 要求 `T: Send + Sync` |

**unsafe impl 契约清单**（实现前逐条自证）:

1. 指针指向的分配在所有使用期内有效（生命周期覆盖）
2. 并发访问模式满足别名规则（无 `&mut` 别名、无数据竞争）
3. 跨线程的可见性/同步由谁保证（锁？原子？join 的 happens-before？）
4. 不做平台相关的布局假设（`repr(Rust)` 布局不承诺字段偏移）

💡 **示例**（edition 2024 示例，本轮未运行；含一个实测踩到的陷阱）:

```rust
use std::thread;

fn main() {
    let mut data = vec![1u8, 2, 3];
    // 作用域线程保证借用在线程结束前有效，不必手写裸指针 Send 承诺。
    thread::scope(|scope| {
        scope.spawn(|| {
            for value in &mut data { *value *= 2; }
        });
    });
    println!("{:?}", data); // [2, 4, 6]
}
```

**分离捕获陷阱**（规则说明）：edition 2021 起闭包按**字段**捕获——`move || { 用到 raw.ptr }` 捕获的是 `*mut u8` 本身而非 `RawSlice`，`unsafe impl Send for RawSlice` 完全不生效，编译照样失败。包装类型的整体移动也不能替代对所有权与生命周期的证明。本例改用 scoped thread 表达借用边界，避免为可用安全 API 完成的任务手写 Send。

⚠️ **常见陷阱**: `unsafe impl Send` 只该出现在"编译器无法看到、但人类可以证明"的场合（指针所有权语义、join 同步）；给"只是懒得重构"的场景开这个口子 = 把数据竞争编译通过。

🔗 **相关条目**: [条目 3：安全封装模式](#条目-3安全封装模式)、[条目 5：典型 UB 清单](#条目-5典型-ub-清单)

## 条目 5：典型 UB 清单

📌 **定义**: UB（未定义行为）是"编译器可以假设它不发生"的事件——一旦发生，整个程序的行为都不可信，**症状可能出现在远离根因的位置**。以下是 unsafe Rust 的高危清单。

📖 **清单**:

| # | 行为 | 说明 |
|---|------|------|
| 1 | 悬垂解引用 | use after free / use after move（地址仍可读 ≠ 合法） |
| 2 | 越界读写 | `p.add(k)` 结果超出所在分配 |
| 3 | 未对齐读写 | 指针不满足类型对齐要求（对齐敏感场景用 `read_unaligned`） |
| 4 | 读取未初始化内存 | `MaybeUninit` 未初始化就当 `T` 读（先 `write`/`assume_init`） |
| 5 | 违反引用别名规则 | `&mut` 存活期间存在其他访问（含经裸指针的写） |
| 6 | 无效值解引用 | `bool` 非 0/1、枚举判别值不在定义内、空 `&T` |
| 7 | 数据竞争 | 多线程无同步地并发写写/读写同一位置 |
| 8 | 移动已 Pin 的数据 | 破坏 `Pin` 承诺，自引用悬垂（见 [Future·Pin·Waker](./08-async-internals.md)） |
| 9 | 双重释放 | Box::from_raw 对同一分配恢复所有权两次；内存泄漏本身不是 UB |
| 10 | 布局越权 | 对 `repr(Rust)` 类型做字段偏移指针算术（布局不受承诺） |

**检测工具**: Miri（rustup 官方组件，在支持的环境解释执行，检测所执行路径中的多种 UB）是 unsafe 代码的必跑关卡；`-Z sanitizer=thread`（thread-sanitizer）补充多线程竞争检测。

⚠️ **常见陷阱**: "测试跑通了"对 UB 无意义——优化级别变化（`-O`）就可能让潜伏 UB 爆炸；对 unsafe 代码的正确验证顺序是 Miri → release 构建 → 压测。

## 相关文档

- 📄 **[所有权字典](./01-ownership-dictionary.md)** — 别名规则（条目 5 的根基）的完整表述
- 📄 **[智能指针全表](./07-smart-pointers.md)** — Box/Arc/Mutex 等"已封装好的 unsafe 成品"
- 📄 **[Future·Pin·Waker](./08-async-internals.md)** — Pin 契约与移动禁忌（UB 条目 8 展开）
- 📄 **[所有权与借用教程](../../basics/02-ownership-borrowing.md)** — unsafe 之前的借用检查基础

---

**文档版本**: v2.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team


<!-- full-library-explanation -->
## 安全封装需要对所有合法调用成立

前置是所有权、生命周期、布局与指针。unsafe 块只表示由人证明前置条件，不能把“这一次 main 中没有出错”推广成安全 API。对一个裸指针构成的切片，需要同时说明分配仍存活、对齐正确、范围有效、元素初始化、别名权限和线程同步。长度在范围内只是其中一项；从任意地址构造指针并不建立这些保证。

审查一个拥有裸指针的类型时，先画出创建、移动、借用和析构路径。析构应恰好恢复一次所有权，panic 及提前返回也不能留下双重释放。需要声明其逻辑拥有 T 的封装，还应考虑 PhantomData<T> 对 drop checking、variance 和自动 trait 推导的影响。暴露裸指针本身不一定不安全，但任何能从安全调用进入 UB 的路径都说明封装不健全。

练习：对 split_at_mut 的实现写出 mid<=len 与两段不重叠的证明，包含 mid=0 和 mid=len。优先使用标准库已有实现；手写练习用于理解契约，不应用作替换库实现的理由。Miri 可以发现被执行路径上的多种未定义行为，但不是全程序正确性证明，还受平台和 FFI 支持限制。正确性依据首先是安全契约及其证明，再用测试、Miri 和适用的 sanitizer 增加证据。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
