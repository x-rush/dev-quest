# Go 泛型（Type Parameters）

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

## 📌 定义

泛型让函数与类型可以**接受类型参数**：同一份代码在编译期安全地适配多种类型，替代过去"接口 + 类型断言"或"代码生成"的写法。约束（constraint）声明类型参数必须具备的能力，编译器据此做静态检查。

## 📖 语法 / 签名

```go
// 泛型函数：[T 约束] 声明类型参数
func Map[T, R any](s []T, f func(T) R) []R

// 约束：any = 任意类型；comparable = 可比较（可作 map key）
// 接口类型可直接内联写出约束（类型集）
type Number interface {
    ~int | ~int64 | ~float64        // ~ 表示"底层类型为…"的近似匹配
}

func Sum[T Number](xs []T) T {
    var total T
    for _, x := range xs {
        total += x
    }
    return total
}

// 泛型类型：类型参数作用于整个结构体
type Stack[T any] struct {
    items []T
}
func (s *Stack[T]) Push(v T) { s.items = append(s.items, v) }
func (s *Stack[T]) Pop() (T, bool) { /* ... */ }

// 调用：类型推断通常可省略方括号
Sum([]int{1, 2, 3})
Map([]string{"a"}, func(s string) int { return len(s) })
```

| 元素 | 类型 | 说明 |
|------|------|------|
| `[T any]` | 类型参数列表 | 跟在函数名/类型名后，多参数用逗号分隔 |
| `any` | 预声明约束 | `interface{}` 的别名，无任何要求 |
| `comparable` | 预声明约束 | 支持 `==`/`!=`，可作 map 的 key |
| `~T` | 约束语法 | 匹配底层类型为 T 的所有类型（含自定义类型） |
| `\|` | 约束联合 | 类型集取并集 |

## 💡 示例

```go
package main

import "fmt"

type Ordered interface {
	~int | ~int64 | ~float64 | ~string
}

func Max[T Ordered](a, b T) T {
	if a > b {
		return a
	}
	return b
}

// 泛型容器：任意元素的键值存储，key 必须 comparable
type Cache[K comparable, V any] struct {
	data map[K]V
}

func NewCache[K comparable, V any]() *Cache[K, V] {
	return &Cache[K, V]{data: make(map[K]V)}
}

func (c *Cache[K, V]) Set(k K, v V) { c.data[k] = v }
func (c *Cache[K, V]) Get(k K) (V, bool) {
	v, ok := c.data[k]
	return v, ok
}

func main() {
	fmt.Println(Max(3, 7), Max("apple", "banana"))

	c := NewCache[string, int]()
	c.Set("hits", 42)
	if v, ok := c.Get("hits"); ok {
		fmt.Println(v)
	}
}
```

下面这段是可直接执行的最小完整程序。它同时验证类型推断、`~int` 对命名类型的匹配，以及泛型容器的“零值 + ok”读取约定；其中 `Score` 不需要显式转换为 `int`。

<!-- terra-thirteenth-case: go-generics-named-type -->
<!-- doc-verify:go-generics-named-type -->
```go
package main

import "fmt"

type Number interface { ~int | ~int64 }
type Score int

func Sum[T Number](xs []T) T {
	var total T
	for _, x := range xs { total += x }
	return total
}

type Cache[K comparable, V any] struct { values map[K]V }
func NewCache[K comparable, V any]() *Cache[K, V] { return &Cache[K, V]{values: map[K]V{}} }
func (c *Cache[K, V]) Get(key K) (V, bool) { value, ok := c.values[key]; return value, ok }

func main() {
	fmt.Printf("score=%d\n", Sum([]Score{1, 2, 3}))
	cache := NewCache[string, int]()
	value, found := cache.Get("missing")
	fmt.Printf("missing=%d,%t\n", value, found)
}
```

与库层结合的典型场景：ORM/Redis 客户端等框架提供基于泛型的强类型查询入口，把"返回结构体类型是否匹配"的检查从运行时移到编译期——泛型是这些 API 的语言基石。

## ⚠️ 常见陷阱

- ❌ **错误做法**：把泛型当"更好的接口"到处使用，先写 `func F[T any](x T)` 再想约束。
- ✅ **正确做法**：先问"所有允许的类型需要哪些共同操作"；需要动态行为时接口仍是首选，泛型只消除重复的类型转换。
- ❌ **错误做法**：在方法上声明新的类型参数（Go 不支持泛型方法）。
- ✅ **正确做法**：类型参数只能声明在函数或类型定义上；需要额外类型灵活性时调整类型本身的参数。
- ❌ **错误做法**：约束写成 `int | int64` 而用户传入 `type MyID int` 编译失败。
- ✅ **正确做法**：用 `~int | ~int64` 匹配底层类型，接受命名的自定义类型。
- ❌ **错误做法**：对 map 取值后不检查存在性就使用。
- ✅ **正确做法**：`v, ok := m[k]` 双值接收；泛型容器同理。
- ❌ **错误做法**：为两个类型的不同写一套泛型抽象，代码反而更难读。
- ✅ **正确做法**：只在重复出现 ≥2 次、且逻辑与类型无关时才抽象；具体类型直写往往更清晰。

<!-- full-library-explanation -->
## 约束决定函数体可以做什么

前置是接口、函数与自定义类型。T any 不代表可以随意对 T 做加法，而是允许任意类型，因此函数体只能使用对所有允许类型都有效的操作。加入 ~int 约束后，编译器才知道加法或比较有意义；~ 还允许底层类型是 int 的命名类型。

练习定义 `type Score int`，用本页 Sum 对 `[]Score{1, 2, 3}` 求和，应得到 Score 类型的 6。将约束中的 ~int 改成 int，应拒绝 Score。再给约束加入 string，思考相同 + 符号现在也可能表示连接，函数名称与业务含义是否仍准确。

泛型保留静态类型关系，接口表达运行时行为集合，两者可组合。自定义 Max 示例并未定义浮点 NaN 的特殊业务规则；即便类型满足约束，也仍需要规定异常值的处理。编译通过不等于业务输入都合理。

## 🔗 相关条目

- 📄 **[Go 数据类型详解](./04-go-data-types.md)** - 底层类型与类型集的基础
- 📄 **[Go 面向对象概念](./06-go-oop-concepts.md)** - 接口 vs 类型参数的取舍
- 📄 **[Go 并发基础](./08-concurrency-basics.md)** - 泛型容器与并发安全的组合
- 📄 **[GORM ORM 速查](../framework-essentials/02-gorm-orm.md)** - 基于泛型的强类型数据访问 API
- 🌐 **[Go 泛型教程（官方）](https://go.dev/doc/tutorial/generics)** - 权威来源

---

*最后更新: 2026年09月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
