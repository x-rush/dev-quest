// parsego: 对 Go 代码片段做语法验证，三级包装梯
// 用法: parsego <filelist.txt>  每行一个片段文件路径
// 输出 JSONL: {file, level, ok, err}
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"go/parser"
	"go/token"
	"os"
	"strings"
)

type result struct {
	File  string `json:"file"`
	Level int    `json:"level"`
	OK    bool   `json:"ok"`
	Err   string `json:"err,omitempty"`
}

func tryParse(name, src string) (bool, string) {
	fset := token.NewFileSet()
	_, err := parser.ParseFile(fset, name, src, parser.AllErrors)
	if err == nil {
		return true, ""
	}
	msg := err.Error()
	// 去掉 "file:line:col: " 前缀，只留错误正文
	if i := strings.Index(msg, ": "); i >= 0 {
		parts := strings.SplitN(msg, ": ", 2)
		if len(parts) == 2 && strings.Contains(parts[0], ":") {
			msg = parts[1]
		}
	}
	return false, msg
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: parsego <filelist>")
		os.Exit(2)
	}
	w := bufio.NewWriter(os.Stdout)
	defer w.Flush()
	enc := json.NewEncoder(w)

	f, err := os.Open(os.Args[1])
	if err != nil {
		panic(err)
	}
	defer f.Close()

	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 1024*1024), 8*1024*1024)
	for sc.Scan() {
		path := strings.TrimSpace(sc.Text())
		if path == "" {
			continue
		}
		src, err := os.ReadFile(path)
		if err != nil {
			enc.Encode(result{File: path, Level: -1, OK: false, Err: "read: " + err.Error()})
			continue
		}
		s := string(src)
		if strings.Contains(s, "package ") {
			ok, e := tryParse(path, s)
			enc.Encode(result{File: path, Level: 0, OK: ok, Err: e})
			continue
		}
		// level 0: 原样（可能凭空语法合法的完整声明）
		if ok, _ := tryParse(path, s); ok {
			enc.Encode(result{File: path, Level: 0, OK: true})
			continue
		}
		// level 1: 补 package
		ok1, e1 := tryParse(path, "package p\n"+s)
		if ok1 {
			enc.Encode(result{File: path, Level: 1, OK: true})
			continue
		}
		// level 2: 包进函数体（语句型片段）
		ok2, e2 := tryParse(path, "package p\nfunc _s() {\n"+s+"\n}")
		if ok2 {
			enc.Encode(result{File: path, Level: 2, OK: true})
		} else {
			// 报告信息量更大的那个错误（优先 level1 的声明级错误）
			enc.Encode(result{File: path, Level: 2, OK: false, Err: e1 + " | wrapped: " + e2})
		}
	}
}
