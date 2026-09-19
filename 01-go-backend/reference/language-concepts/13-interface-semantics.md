# 接口（Interface）语义

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

接口是**方法集合的约定**：只要类型实现了接口声明的全部方法，即自动满足该接口（隐式实现，无需 `implements`）。接口值在运行时是一对 `(动态类型, 动态值)`——理解这个二元组是解开 nil 接口陷阱与类型断言行为的钥匙。

## 📖 语法 / 签名

```go
// 接口声明与隐式实现
type Speaker interface {
    Speak() string
}
type Dog struct{}
func (d Dog) Speak() string { return "汪" }  // 实现即满足，无需声明

// 空接口与 any：无任何方法要求，一切类型都满足
func Print(v any) {}   // any 是 interface{} 的别名

// 接口组合：小接口拼大接口
type ReadWriter interface {
    io.Reader
    io.Writer
}

// 类型断言
v := x.(T)        // 若动态类型不是 T → panic
v, ok := x.(T)    // comma-ok：不是 T 时 ok=false，不 panic

// type switch：按动态类型分派
switch v := x.(type) {
case int:    // v 是 int
case string: // v 是 string
default:     // v 保持接口类型
}
```

**接口值的两个 nil，务必分清**：

| 状态 | `i == nil` | 解释 |
|------|------------|------|
| `var i I`（零值接口） | true | 动态类型与动态值都是 nil |
| `var p *T = nil; var i I = p` | **false** | 动态类型 = `*T`，动态值 = nil——"装了 nil 指针的接口"≠ nil 接口 |

方法实现由动态类型决定，动态值作为接收者传入：`i.M()` 会以 nil 接收者调用 `(*T).M`，方法内部需自行处理 nil 接收者。

## 💡 示例

<!-- doc-verify:go-interface-typed-nil -->
```go
package main

import (
	"errors"
	"fmt"
)

type MyErr struct{ msg string }

func (e *MyErr) Error() string { return e.msg }

// 经典陷阱：返回具体指针类型的 nil，装进 error 后不再是 nil
func mightFail(fail bool) error {
	var perr *MyErr       // 惯用的包内具体错误类型
	if fail {
		perr = &MyErr{msg: "boom"}
	}
	return perr           // ❌ 即使 perr==nil，返回的 error 也不等于 nil
}

func mightFailOK(fail bool) error {
	if fail {
		var perr *MyErr
		perr = &MyErr{msg: "boom"}
		return perr           // ✅ 只在有错误时才返回具体类型
	}
	return nil                // ✅ 显式返回字面量 nil
}

func main() {
	// 1. nil 接口陷阱（核心）
	if err := mightFail(false); err != nil {
		fmt.Println("误判为失败！动态类型:", fmt.Sprintf("%T", err))
		// 输出：误判为失败！动态类型: *main.MyErr
	}
	if err := mightFailOK(false); err == nil {
		fmt.Println("正确：err == nil")
	}

	// 2. 类型断言与 type switch
	var x any = 42
	if n, ok := x.(int); ok {
		fmt.Println("是 int:", n)
	}
	switch v := x.(type) {
	case string:
		fmt.Println("string", v)
	case int:
		fmt.Println("int", v)
	default:
		fmt.Println("其他", v)
	}

	// 3. 断言到另一个接口（检查能力）
	var w any = errors.New("e")
	if _, ok := w.(interface{ Unwrap() error }); ok {
		fmt.Println("支持 Unwrap 的错误")
	}
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：函数返回值为接口 `error`，内部却 `return 具体指针变量`（可能为 nil）。
- ✅ **正确做法**：只在确有错误时返回具体类型，无错时 `return nil` 字面量；这是 Go 最著名的接口陷阱。
- ❌ **错误做法**：对可能不是目标类型的接口值用单值断言 `v := x.(T)`。
- ✅ **正确做法**：comma-ok 双值形式 `v, ok := x.(T)`；确定类型才用单值形式。
- ❌ **错误做法**：认为给接口存了 nil 指针还能靠 `i == nil` 兜底。
- ✅ **正确做法**：nil 判断在装包之前做；或将"空状态"建模为显式的 `ErrNotFound` 值而非 nil 指针。
- ❌ **错误做法**：值接收者实现了接口，却把 `T` 装进接口后调用指针方法。
- ✅ **正确做法**：方法集规则——`T` 的方法集只含值接收者方法，`*T` 含两者；需要指针方法就必须装 `&T`。
- ❌ **错误做法**：用接口当泛型容器，到处断言取回数据。
- ✅ **正确做法**：优先考虑泛型（见 generics 条目）；接口用于"行为抽象"，泛型用于"类型抽象"。

<!-- full-library-explanation -->
## 接口保存类型信息，不只是一个地址

前置是方法集与 nil 指针。接口值可以描述为动态类型加动态值；只有两者都缺失时接口才等于 nil。把 *MyErr 的 nil 放入 error 后，类型仍是 *MyErr，因此 err != nil 成立。

练习运行本页 mightFail(false) 与 mightFailOK(false)，比较 `%T` 和 `err == nil`。然后在 MyErr.Error 内增加 nil 接收者判断，观察“方法能否处理 nil”与“接口是否等于 nil”是不同问题；修改方法不会改变接口中已经存在的类型信息。

类型断言的目标也可以是另一个接口，此时检查动态类型是否实现该接口，并非要求两个接口类型名称相同。比较两个接口值时，若相同动态类型的值不可比较（例如切片），可能 panic；any 不会把任意对象变成安全的 map 键。

## 🔗 相关条目

- 📄 **[nil 语义汇总](./15-nil-semantics.md)** - 接口 nil 判断全表
- 📄 **[Go 泛型](./09-generics.md)** - 接口 vs 类型参数
- 📄 **[errors 标准库](../library-guides/09-errors.md)** - error 接口的工程化用法
- 📄 **[Go 面向对象概念](./06-go-oop-concepts.md)** - 方法集与嵌入
- 🌐 **[Go FAQ: nil error](https://go.dev/doc/faq#nil_error)** - 官方对 nil 陷阱的解释
- 🌐 **[pkg.go.dev/builtin#error](https://pkg.go.dev/builtin#error)** - error 接口定义

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
