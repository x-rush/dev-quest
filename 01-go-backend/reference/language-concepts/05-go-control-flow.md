# Go 控制流程速查手册

> **文档简介**: Go语言控制流程的完整参考手册，包含条件语句、循环、跳转语句的快速查阅
>
> **目标读者**: Go开发者，需要快速查阅Go控制流程语法的开发者
>
> **前置知识**: Go语言基础语法、数据类型
>
> **预计时长**: 30分钟速查

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/language-concepts` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#控制流程` `#语法速查` `#条件语句` `#循环` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 快速索引

### 条件语句
- [if语句](#if语句)
- [switch语句](#switch语句)
- [类型断言](#类型断言)

### 循环语句
- [for循环](#for循环)
- [range循环](#range循环)
- [循环控制](#循环控制)

### 跳转语句
- [break](#break)
- [continue](#continue)
- [goto](#goto)
- [defer](#defer)

## 📖 条件语句

### if语句
```go
// 基本if语句
if x > 10 {
    fmt.Println("x is greater than 10")
}

// if-else语句
if x > 10 {
    fmt.Println("greater")
} else {
    fmt.Println("less or equal")
}

// if-else if-else语句
if x > 100 {
    fmt.Println("very large")
} else if x > 10 {
    fmt.Println("large")
} else {
    fmt.Println("small")
}

// 带初始化的if语句
if y := x * 2; y > 50 {
    fmt.Println("y is large:", y)
}
```

### switch语句
```go
// 基本switch
switch day {
case "Monday":
    fmt.Println("Start of week")
case "Friday":
    fmt.Println("End of week")
default:
    fmt.Println("Middle of week")
}

// switch表达式
switch {
case x < 0:
    fmt.Println("negative")
case x == 0:
    fmt.Println("zero")
case x > 0:
    fmt.Println("positive")
}

// 多个case值
switch grade {
case "A", "B":
    fmt.Println("Excellent")
case "C":
    fmt.Println("Good")
default:
    fmt.Println("Need improvement")
}
```

## 📖 循环语句

### for循环
```go
// 基本for循环
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// 类似while循环
for x < 100 {
    x *= 2
}

// 无限循环
for {
    if condition {
        break
    }
}
```

### range循环
```go
// 遍历切片
nums := []int{1, 2, 3, 4, 5}
for i, num := range nums {
    fmt.Printf("Index: %d, Value: %d\n", i, num)
}

// 遍历映射
m := map[string]int{"a": 1, "b": 2}
for key, value := range m {
    fmt.Printf("Key: %s, Value: %d\n", key, value)
}

// 遍历字符串
for i, char := range "hello" {
    fmt.Printf("Index: %d, Char: %c\n", i, char)
}
```

## 📖 跳转语句

### break
```go
// 跳出循环
for i := 0; i < 10; i++ {
    if i == 5 {
        break
    }
    fmt.Println(i)
}

// 跳出switch
switch x {
case 1:
    fmt.Println("one")
    break
case 2:
    fmt.Println("two")
    break
}
```

### continue
```go
// 跳过当前迭代
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        continue
    }
    fmt.Println(i) // 只打印奇数
}
```

### defer
```go
// 延迟执行函数
func readFile() {
    file, err := os.Open("test.txt")
    if err != nil {
        return
    }
    defer file.Close() // 函数结束时执行
    
    // 使用文件...
}
```

### 类型断言

对接口使用 `value, ok := x.(T)`，匹配失败时 ok 为 false，不会像单返回值断言那样 panic。多个类型分支用 type switch。类型断言不是数值转换：`int(floatValue)` 与 `x.(int)` 解决不同问题。

### 循环控制

break 结束最近的 for/switch/select，continue 开始最近 for 的下一次迭代。嵌套循环需要退出外层时可使用标签；先明确要退出哪一层，避免在 switch 内 break 后误以为已经退出外面的 for。

### goto

goto 跳到同一函数内的标签，不能跳入新的作用域或跨过导致变量尚未声明的路径。通常优先使用 return、循环和带标签 break；只有线性清理等确实更清晰的场景才考虑 goto。

```go
// main 内片段，已 import fmt
var x any = "7"
if value, ok := x.(int); ok {
    fmt.Println(value)
} else {
    fmt.Println("不是 int") // 字符串数字不是 int
}
```

验收：把 x 改成整数 7，输出应变为 7；再解释为何字符串到整数需要解析而不能靠断言完成。

<!-- full-library-explanation -->
## 先判断循环变量代表什么

前置是布尔表达式与切片。if 要求布尔条件，不能把整数直接当真假；switch 默认在命中分支后结束，不需要像某些语言那样在每个 case 末尾写 break。range 的结果随被遍历对象变化，字符串的索引是字节偏移，值是解码得到的 rune。

完整程序保存为 main.go 后运行：

```go
package main
import "fmt"
func main() {
    for index, value := range "Go中" {
        fmt.Printf("%d %c\n", index, value)
    }
    fmt.Println(len("Go中"))
}
```

输出三行 `0 G`、`1 o`、`2 中`，最后是 `5`。练习：将字符串改为“中Go”，索引应为 0、3、4。再解释为什么对字符串按任意字节位置切片可能切断 UTF-8 编码。for 中的 break 只退出最近相关循环或 switch/select，跨层退出需要明确标签，不能靠缩进判断。

下面的完整程序同时固定验证 `continue`、默认不贯穿的 `switch`、带标签 `break`，以及字符串 `range` 的字节索引。保存为 `main.go` 后可直接运行：

<!-- terra-seventeenth-case: go-control-flow-labelled-range -->
```go
package main

import "fmt"

func main() {
	kept := []int{}
	for n := 1; n <= 5; n++ {
		if n%2 == 0 {
			continue
		}
		kept = append(kept, n)
	}

	word := ""
	switch len(kept) {
	case 3:
		word = "three" // Go does not fall through by default.
	default:
		word = "other"
	}

	steps := 0
outer:
	for row := 0; row < 3; row++ {
		for column := 0; column < 3; column++ {
			steps++
			if row == 1 && column == 1 {
				break outer
			}
		}
	}

	indexes := []int{}
	for index := range "Go中" {
		indexes = append(indexes, index)
	}
	fmt.Printf("kept=%v switch=%s steps=%d indexes=%v\n", kept, word, steps, indexes)
}
```

预期输出为 `kept=[1 3 5] switch=three steps=5 indexes=[0 1 2]`。这只说明 `range` 给出每个 rune 起始的字节偏移；它不是字符计数。

## 🔗 相关资源

- **深入学习**: [basics/06-control-structures.md](../../basics/06-control-structures.md)
- **相关文档**: [reference/language-concepts/04-go-data-types.md](04-go-data-types.md)
- **实践参考**: [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)

---

**更新日志**: 2026年9月 - 创建控制流程速查手册


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
