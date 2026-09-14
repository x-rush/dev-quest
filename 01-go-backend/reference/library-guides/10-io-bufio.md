# io / bufio - 流式读写接口层

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

io 包用两个极小接口定义了 Go 的**流世界**：`Reader`（`Read(p []byte)`）与 `Writer`（`Write(p []byte)`）——文件、网络、压缩、加密全部实现同一对接口，于是 `io.Copy` 等工具可组合万物。bufio 在其上加**缓冲层**，把系统调用次数降到最少。心智模型——**接口组合即能力**（`io.ReadWriteCloser`），工具函数吃接口，不关心底层是什么。

## 📖 语法 / 签名

```go
// 两大接口
type Reader interface { Read(p []byte) (n int, err error) }
type Writer interface { Write(p []byte) (n int, err error) }
// Read 约定：读满或无数据即返回（不保证填满 p）；流结束 err = io.EOF

// 组合接口表达能力
rwc io.ReadWriteCloser   // 同时可读写且可关闭
rc  io.ReadCloser        // HTTP body 的典型类型

// 高频工具函数
io.Copy(dst Writer, src Reader) (n int64, err error)  // 拷到 EOF（EOF 不算错）
io.ReadAll(r Reader) ([]byte, error)                  // 一次读尽（内容大时慎用）
io.ReadFull(r Reader, buf []byte) (int, error)        // 恰好填满 buf 或报错
io.MultiReader(rs ...Reader) Reader                   // 逻辑串联多个流
io.TeeReader(r Reader, w Writer) Reader               // 边读边写（旁路记录）
strings.NewReader(s) / bytes.NewBuffer(b)             // 内存流适配器

// bufio：缓冲
br := bufio.NewReader(r)            // 默认 4096 字节缓冲
bw := bufio.NewWriter(w)            // 攒够或 Flush 才真正写出
sc := bufio.NewScanner(r)           // 行/token 扫描（默认按行）
sc.Buffer(buf, maxCap)              // 调大 token 上限
sc.Split(bufio.ScanWords)           // 换分词规则
```

**Scanner 默认 64K 上限**：`bufio.Scanner` 内部缓冲默认最大 token 约 64 KB（`bufio.MaxScanTokenSize`）；更长的行会触发 `bufio.Scanner: token too long` 且**静默停止**（Scan 返回 false）。处理大行必须 `sc.Buffer(make([]byte, 0, 64*1024), max)` 显式调大。

## 💡 示例

```go
package main

import (
	"bufio"
	"fmt"
	"io"
	"strings"
)

func main() {
	// 1. io.ReadAll + strings.NewReader：内存流
	b, _ := io.ReadAll(strings.NewReader("hello io"))
	fmt.Println(string(b)) // hello io

	// 2. io.Copy 串联：任意 Reader → Writer
	var out strings.Builder
	n, _ := io.Copy(&out, strings.NewReader("copied"))
	fmt.Println(out.String(), n) // copied 6

	// 3. MultiReader：多流串联，按序读完
	mr := io.MultiReader(strings.NewReader("A"), strings.NewReader("B"))
	all, _ := io.ReadAll(mr)
	fmt.Println(string(all)) // AB

	// 4. bufio.Scanner 按行读（最常用的文件遍历姿势）
	sc := bufio.NewScanner(strings.NewReader("l1\nl2\nl3"))
	for sc.Scan() {
		fmt.Println(sc.Text()) // l1 l2 l3 各一行
	}
	fmt.Println(sc.Err()) // <nil>（正常结束必须为 nil）

	// 5. 64K 陷阱重现与解法：Buffer 调大上限
	big := strings.Repeat("x", 100*1024)
	sc2 := bufio.NewScanner(strings.NewReader(big + "\n"))
	fmt.Println(sc2.Scan(), sc2.Err()) // false token too long

	sc3 := bufio.NewScanner(strings.NewReader(big + "\n"))
	sc3.Buffer(make([]byte, 0, 64*1024), 200*1024) // 上限调到 200K
	fmt.Println(sc3.Scan(), len(sc3.Text()))       // true 102400

	// 6. bufio.Writer：必须 Flush
	bw := bufio.NewWriter(&out)
	bw.WriteString("buffered") // 还在缓冲区，out 尚无内容
	bw.Flush()                 // 此刻才真正写出
	fmt.Println(out.String())  // copiedbuffered
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：把 `Read(p)` 返回的 `n` 忽略、假设 p 一定被填满。
- ✅ **正确做法**：每次按 `n` 处理；需要"恰好 n 字节"用 `io.ReadFull`。
- ❌ **错误做法**：自己把 `io.EOF` 当错误上报。
- ✅ **正确做法**：`io.Copy/io.ReadAll` 已消化 EOF；手写循环里 `err == io.EOF` 是正常结束，返回 nil。
- ❌ **错误做法**：Scanner 遇到大行静默跳过没发现（`token too long`）。
- ✅ **正确做法**：循环后检查 `sc.Err()`；预期大行先 `sc.Buffer` 调上限。
- ❌ **错误做法**：`defer f.Close()` 与 `defer bw.Flush()` 顺序写反——LIFO 会先 Close 后 Flush，数据丢失。
- ✅ **正确做法**：先注册 `defer f.Close()`，再注册 `defer bw.Flush()`（后注册先执行：Flush → Close）。
- ❌ **错误做法**：对大文件用 io.ReadAll 一口读进内存。
- ✅ **正确做法**：`io.Copy` 流式搬运或 Scanner 按行处理；ReadAll 仅限内容可控的小数据。
- ❌ **错误做法**：函数参数收 `*os.File` 具体类型。
- ✅ **正确做法**：参数收 `io.Reader/io.Writer`，可测性（bytes.Buffer 替身）与组合性立涨。

## 🔗 相关条目

- 📄 **[os 包](./11-os.md)** - 文件作为 io.Reader/Writer 的来源
- 📄 **[net/http 包](./03-net-http.md)** - resp.Body 即 io.ReadCloser
- 📄 **[encoding/json 包](./04-encoding-json.md)** - Encoder/Decoder 流式编解码
- 📄 **[接口语义](../language-concepts/13-interface-semantics.md)** - 小接口组合的设计哲学
- 🌐 **[pkg.go.dev/io](https://pkg.go.dev/io)** - 官方文档
- 🌐 **[pkg.go.dev/bufio](https://pkg.go.dev/bufio)** - 官方文档

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
