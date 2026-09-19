# 标准库待办命令行：第一个完整 Go 小项目

> 前置：完成变量、复合类型、函数、控制流与错误处理。适用环境：Go 1.27.1；只使用标准库，不需要网络、数据库或第三方依赖。

这不是一个“把所有后端组件装进来”的项目。它只解决一个明确问题：在一次命令执行中，把用户给出的待办标题保存到内存、列出来或删除。你将亲自经过输入、校验、状态改变、输出与测试五个环节；后续 Gin、GORM 和数据库项目只是把其中某些环节换成 HTTP 和持久化实现。

## 本课产物与运行方式

新建空目录 `todo-cli`，保存下面两个文件，然后依次运行命令。程序的状态只存在本次进程内，所以每条 `go run` 命令会从空列表开始；这是本课有意保留的边界，而不是数据丢失的 bug。

```text
todo-cli/
├── main.go
└── main_test.go
```

```bash
mkdir todo-cli
cd todo-cli
# 保存下文两个文件后：
go test ./...
go run . add "买牛奶"
go run . add ""
```

预期：测试通过；第一个 `add` 输出 `已添加 #1: 买牛奶`；空标题输出错误并以非零状态退出。因为每次 `go run` 都启动新进程，想观察列表、删除和错误路径，请运行后文的 `demo` 命令。

## 完整实现：main.go

```go
package main

import (
	"errors"
	"fmt"
	"io"
	"os"
	"strings"
)

var ErrEmptyTitle = errors.New("待办标题不能为空")

type Todo struct {
	ID    int
	Title string
}

type Store struct {
	nextID int
	items  []Todo
}

func (s *Store) Add(title string) (Todo, error) {
	title = strings.TrimSpace(title)
	if title == "" {
		return Todo{}, ErrEmptyTitle
	}
	s.nextID++
	todo := Todo{ID: s.nextID, Title: title}
	s.items = append(s.items, todo)
	return todo, nil
}

func (s *Store) List() []Todo {
	// 返回副本，调用者修改结果不会改写 Store 内部状态。
	return append([]Todo(nil), s.items...)
}

func (s *Store) Delete(id int) error {
	for index, todo := range s.items {
		if todo.ID == id {
			s.items = append(s.items[:index], s.items[index+1:]...)
			return nil
		}
	}
	return fmt.Errorf("待办 #%d 不存在", id)
}

func run(args []string, out io.Writer) error {
	store := &Store{}
	if len(args) == 0 {
		return errors.New("用法: todo-cli add <标题> | demo")
	}

	switch args[0] {
	case "add":
		if len(args) != 2 {
			return errors.New("add 需要且只需要一个标题")
		}
		todo, err := store.Add(args[1])
		if err != nil {
			return err
		}
		_, err = fmt.Fprintf(out, "已添加 #%d: %s\n", todo.ID, todo.Title)
		return err
	case "demo":
		for _, title := range []string{"买牛奶", "写 Go 测试"} {
			if _, err := store.Add(title); err != nil {
				return err
			}
		}
		if err := store.Delete(1); err != nil {
			return err
		}
		for _, todo := range store.List() {
			if _, err := fmt.Fprintf(out, "#%d %s\n", todo.ID, todo.Title); err != nil {
				return err
			}
		}
		return nil
	default:
		return fmt.Errorf("未知命令 %q", args[0])
	}
}

func main() {
	if err := run(os.Args[1:], os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, "错误:", err)
		os.Exit(1)
	}
}
```

`main` 只把真实命令行参数和输出设备交给 `run`。`run` 接受这两个参数，因此测试可以传入自建的参数切片和内存缓冲区，而无需启动新进程或修改全局状态。

## 验证与测试：main_test.go

```go
package main

import (
	"bytes"
	"errors"
	"strings"
	"testing"
)

func TestStoreAddAndDelete(t *testing.T) {
	store := &Store{}
	first, err := store.Add("  买牛奶  ")
	if err != nil {
		t.Fatal(err)
	}
	if first.ID != 1 || first.Title != "买牛奶" {
		t.Fatalf("添加结果 = %#v，want ID=1 且标题已去空白", first)
	}
	if err := store.Delete(first.ID); err != nil {
		t.Fatal(err)
	}
	if got := store.List(); len(got) != 0 {
		t.Fatalf("删除后列表 = %#v，want 空列表", got)
	}
}

func TestStoreRejectsEmptyTitle(t *testing.T) {
	_, err := (&Store{}).Add(" \t ")
	if !errors.Is(err, ErrEmptyTitle) {
		t.Fatalf("Add 空标题错误 = %v，want ErrEmptyTitle", err)
	}
}

func TestRunDemoAndUnknownCommand(t *testing.T) {
	var out bytes.Buffer
	if err := run([]string{"demo"}, &out); err != nil {
		t.Fatal(err)
	}
	if got := out.String(); got != "#2 写 Go 测试\n" {
		t.Fatalf("demo 输出 = %q", got)
	}
	if err := run([]string{"unknown"}, &out); err == nil || !strings.Contains(err.Error(), "未知命令") {
		t.Fatalf("未知命令错误 = %v", err)
	}
}
```

## 读代码时沿着数据走

`run` 接收命令参数并创建 `Store`。`add` 把标题交给 `Store.Add`：先去掉两端空白，再在空标题时返回同一个可识别错误，成功时分配 ID 并追加到切片。`demo` 故意在同一进程内添加两个项目、删除第一个，再输出剩余项目，因此可以观察状态变化。测试直接调用 `Store` 和 `run`，不需要启动进程，也能验证正常、边界和失败路径。

本例刻意不处理文件保存、并发访问、HTTP、认证或数据库。加入其中任何一个之前，先说明它解决的具体问题：例如“关闭程序后数据仍要保留”才引入文件或数据库；“多个 goroutine 同时改列表”才引入同步。

## 练习与验收

1. 为 `Delete` 写测试：删除 ID 99 时应返回包含 `不存在` 的错误，列表不能改变。
2. 新增 `done` 字段和 `Complete(id int)`；完成后 `demo` 的输出要能区分未完成与已完成。
3. 复制 `List` 的返回值后修改其中元素，证明 Store 内部标题不变。解释这为什么需要 `List` 返回副本。

每题先写失败测试，再补实现。通过条件是 `go test ./...` 通过，并且你能指出空标题在哪一行被拒绝、删除不存在 ID 为什么不影响状态。

## 下一步

接下来学习 [并发编程基础](../basics/07-concurrency-basics.md)，再阅读 [net/http](../reference/library-guides/03-net-http.md)。将本例转换为 HTTP API 时，保持 `Store` 的输入和错误语义，再只替换命令行入口；不要在还不能解释错误路径时先引入 Gin 或数据库。
