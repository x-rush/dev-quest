# CLI工具开发实战 - 构建现代化的Go命令行应用

> **阅读准备**：掌握函数、文件读写与错误处理，知道标准输入、标准输出和退出码；无需先学 Web 框架。

## 分阶段练习与验收

**最小阶段**：先做一个子命令并定义参数、标准输出和退出码。

**验收结果**：合法参数输出稳定结果；无效参数返回非零退出码和用法提示。

**扩展顺序**：配置文件、补全与插件属于后续扩展，不能挤掉输入错误测试。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

## 🎯 项目概述

本项目以一个任务运行器为载体，练习把“命令行输入”变成可预测的任务执行。先完成不依赖第三方服务的核心闭环：读取任务配置、解析依赖、按顺序执行命令并用退出码报告结果。插件、发布和跨平台分发是独立阶段，不能作为第一个可用版本的前提。

### 本项目结束时应能解释的事

- 命令、参数和 flag 分别承担什么输入责任；错误输入为什么必须在执行外部命令前失败。
- 配置文件、环境变量和命令行 flag 发生冲突时，哪一个优先，以及这个规则如何写进测试。
- 任务依赖为什么需要拓扑排序；出现环时如何报告完整的依赖链，而不是卡住或只输出模糊错误。
- 并发任务如何传递取消信号、收集第一个失败，以及为什么不能把所有任务都不加限制地启动。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `projects/practical-projects` |
| **难度** | ⭐⭐⭐ |
| **标签** | `#cli工具` `#cobra` `#命令行` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>
- 添加日志、进度条和彩色输出
- 支持插件系统和扩展机制
- 实现测试覆盖和发布流程

### 技术栈
- **Cobra**: 强大的CLI应用程序框架
- **Viper**: 完整的配置解决方案
- **urfave/cli**: 替代选择，轻量级CLI框架
- **logrus**: 结构化日志记录
- **progressbar**: 命令行进度条
- **tablewriter**: 表格输出格式化
- ** testify**: 测试工具包

---

## 🏗️ 项目架构设计

### 核心功能模块

```
task-runner/
├── cmd/                    # 命令定义
│   ├── root.go            # 根命令
│   ├── run.go             # 执行任务
│   ├── list.go            # 列出任务
│   ├── init.go            # 初始化项目
│   └── plugin.go          # 插件管理
├── internal/              # 内部实现
│   ├── config/            # 配置管理
│   ├── executor/          # 任务执行器
│   ├── parser/            # 任务文件解析
│   ├── dependency/        # 依赖解析
│   └── plugin/            # 插件系统
├── pkg/                   # 公共包
│   ├── utils/             # 工具函数
│   ├── logger/            # 日志系统
│   └── output/            # 输出格式化
├── plugins/               # 内置插件
│   ├── docker.go          # Docker任务插件
│   ├── git.go             # Git操作插件
│   └── deploy.go          # 部署插件
└── examples/              # 示例配置
    ├── simple.yaml        # 简单任务配置
    └── complex.yaml       # 复杂项目配置
```

### 任务配置示例

```yaml
# taskfile.yaml
version: "2.0"
env:
  GOOS: linux
  GOARCH: amd64

tasks:
  build:
    desc: "构建应用程序"
    deps: [clean, test]
    cmds:
      - go build -o bin/app ./cmd/main.go
      - echo "构建完成"
    sources:
      - "./**/*.go"
    generates:
      - "./bin/app"

  test:
    desc: "运行测试"
    cmds:
      - go test -v ./...
    sources:
      - "./**/*_test.go"

  clean:
    desc: "清理构建文件"
    cmds:
      - rm -rf bin/
      - rm -rf dist/

  deploy:
    desc: "部署到生产环境"
    deps: [build]
    env:
      DEPLOY_ENV: production
    cmds:
      - echo "正在部署到 {{.DEPLOY_ENV}}"
      - scp bin/app user@server:/opt/app/
      - ssh user@server "systemctl restart app"
```

---

## 🚀 核心实现

### 1. 主程序入口

```go
// main.go
package main

import (
	"fmt"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"go.uber.org/zap"
)

// NewRootCommand 构建根命令：抽出来供 main 与 cmd/root_test.go 复用，
// 测试可以直接调用本函数并注入输出缓冲与参数。
func NewRootCommand(logger *zap.Logger) *cobra.Command {
	rootCmd := &cobra.Command{
		Use:   "task",
		Short: "现代化的任务运行器",
		Long: `Task是一个现代化的任务运行器，支持依赖管理、并发执行和插件扩展。
它旨在成为make的替代品，提供更好的用户体验和更强大的功能。`,
	}

	// 绑定配置
	cobra.OnInitialize(initConfig)

	// 添加子命令
	rootCmd.AddCommand(NewRunCommand(logger))
	rootCmd.AddCommand(NewListCommand(logger))
	rootCmd.AddCommand(NewInitCommand(logger))
	rootCmd.AddCommand(NewPluginCommand(logger))

	// 添加全局标志
	rootCmd.PersistentFlags().String("config", "", "配置文件路径")
	rootCmd.PersistentFlags().BoolP("verbose", "v", false, "详细输出")
	rootCmd.PersistentFlags().BoolP("dry-run", "d", false, "试运行模式")

	// 绑定Viper
	viper.BindPFlag("config", rootCmd.PersistentFlags().Lookup("config"))
	viper.BindPFlag("verbose", rootCmd.PersistentFlags().Lookup("verbose"))
	viper.BindPFlag("dry-run", rootCmd.PersistentFlags().Lookup("dry-run"))

	return rootCmd
}

func main() {
	// 初始化日志
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	// 执行命令
	if err := NewRootCommand(logger).Execute(); err != nil {
		logger.Fatal("命令执行失败", zap.Error(err))
		os.Exit(1)
	}
}

func initConfig() {
	if cfgFile := viper.GetString("config"); cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	} else {
		viper.SetConfigName("taskfile")
		viper.SetConfigType("yaml")
		viper.AddConfigPath(".")
		viper.AddConfigPath("$HOME/.task")
		viper.AddConfigPath("/etc/task/")
	}

	viper.AutomaticEnv()
	viper.SetEnvKeyReplacer(strings.NewReplacer("-", "_"))

	if err := viper.ReadInConfig(); err == nil {
		fmt.Println("使用配置文件:", viper.ConfigFileUsed())
	}
}
```

### 2. 任务执行命令

```go
// cmd/run.go
package cmd

import (
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
	"go.uber.org/zap"
	"gopkg.in/yaml.v2"
)

type Task struct {
	Name        string            `yaml:"name"`
	Desc        string            `yaml:"desc"`
	Deps        []string          `yaml:"deps"`
	Cmds        []string          `yaml:"cmds"`
	Env         map[string]string `yaml:"env"`
	Sources     []string          `yaml:"sources"`
	Generates   []string          `yaml:"generates"`
	Dir         string            `yaml:"dir"`
	IgnoreError bool              `yaml:"ignore_error"`
	Parallel    bool              `yaml:"parallel"`
}

type Taskfile struct {
	Version string            `yaml:"version"`
	Env     map[string]string `yaml:"env"`
	Tasks   map[string]*Task  `yaml:"tasks"`
}

func NewRunCommand(logger *zap.Logger) *cobra.Command {
	var (
		parallel   bool
		watch      bool
		force      bool
		skipDeps   bool
	)

	cmd := &cobra.Command{
		Use:   "run [task...]",
		Short: "执行指定的任务",
		Long:  "执行一个或多个任务，自动处理依赖关系和并发执行。",
		Args:  cobra.MinimumNArgs(1),
		Run: func(cmd *cobra.Command, args []string) {
			// 读取任务配置
			taskfile, err := loadTaskfile()
			if err != nil {
				logger.Fatal("加载任务文件失败", zap.Error(err))
			}

			// 创建执行器
			executor := NewTaskExecutor(logger, taskfile, TaskExecutorConfig{
				Parallel:  parallel,
				Watch:     watch,
				Force:     force,
				SkipDeps:  skipDeps,
				DryRun:    viper.GetBool("dry-run"),
				Verbose:   viper.GetBool("verbose"),
			})

			// 执行任务
			if err := executor.Execute(args...); err != nil {
				logger.Fatal("任务执行失败", zap.Error(err))
			}
		},
	}

	// 添加标志
	cmd.Flags().BoolVarP(&parallel, "parallel", "p", false, "并行执行任务")
	cmd.Flags().BoolVarP(&watch, "watch", "w", false, "监视文件变化并重新执行")
	cmd.Flags().BoolVarP(&force, "force", "f", false, "强制执行，忽略依赖检查")
	cmd.Flags().BoolVar(&skipDeps, "skip-deps", false, "跳过依赖任务")

	return cmd
}

func loadTaskfile() (*Taskfile, error) {
	data, err := os.ReadFile("taskfile.yaml")
	if err != nil {
		return nil, fmt.Errorf("读取taskfile.yaml失败: %w", err)
	}

	var taskfile Taskfile
	if err := yaml.Unmarshal(data, &taskfile); err != nil {
		return nil, fmt.Errorf("解析taskfile.yaml失败: %w", err)
	}

	// 设置全局环境变量
	for k, v := range taskfile.Env {
		if err := os.Setenv(k, v); err != nil {
			return nil, fmt.Errorf("设置环境变量失败: %w", err)
		}
	}

	return &taskfile, nil
}
```

### 3. 任务执行器

```go
// internal/executor/executor.go
package executor

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"go.uber.org/zap"
)

// Task/Taskfile 与 cmd 包中 loadTaskfile 解析的类型一致（分块展示，此处内联定义）
type Task struct {
	Name        string            `yaml:"name"`
	Desc        string            `yaml:"desc"`
	Deps        []string          `yaml:"deps"`
	Cmds        []string          `yaml:"cmds"`
	Env         map[string]string `yaml:"env"`
	Sources     []string          `yaml:"sources"`
	Generates   []string          `yaml:"generates"`
	Dir         string            `yaml:"dir"`
	IgnoreError bool              `yaml:"ignore_error"`
	Parallel    bool              `yaml:"parallel"`
}

type Taskfile struct {
	Version string            `yaml:"version"`
	Env     map[string]string `yaml:"env"`
	Tasks   map[string]*Task  `yaml:"tasks"`
}

type TaskExecutor struct {
	logger      *zap.Logger
	taskfile    *Taskfile
	config      TaskExecutorConfig
	running     sync.Map
	completed   map[string]bool
	mu          sync.RWMutex
	cancelFunc  context.CancelFunc
}

type TaskExecutorConfig struct {
	Parallel  bool
	Watch     bool
	Force     bool
	SkipDeps  bool
	DryRun    bool
	Verbose   bool
}

func NewTaskExecutor(logger *zap.Logger, taskfile *Taskfile, config TaskExecutorConfig) *TaskExecutor {
	return &TaskExecutor{
		logger:    logger,
		taskfile:  taskfile,
		config:    config,
		completed: make(map[string]bool),
	}
}

func (e *TaskExecutor) Execute(taskNames ...string) error {
	ctx, cancel := context.WithCancel(context.Background())
	e.cancelFunc = cancel
	defer cancel()

	// 解析执行顺序
	executionOrder, err := e.resolveDependencies(taskNames...)
	if err != nil {
		return fmt.Errorf("解析依赖关系失败: %w", err)
	}

	if e.config.Verbose {
		e.logger.Info("执行顺序", zap.Strings("tasks", executionOrder))
	}

	// 执行任务
	if e.config.Parallel {
		return e.executeParallel(ctx, executionOrder)
	}
	return e.executeSequential(ctx, executionOrder)
}

func (e *TaskExecutor) resolveDependencies(taskNames ...string) ([]string, error) {
	var order []string
	visited := make(map[string]bool)
	visiting := make(map[string]bool)

	var dfs func(taskName string) error
	dfs = func(taskName string) error {
		if visited[taskName] {
			return nil
		}
		if visiting[taskName] {
			return fmt.Errorf("检测到循环依赖: %s", taskName)
		}

		visiting[taskName] = true
		defer delete(visiting, taskName)

		task, exists := e.taskfile.Tasks[taskName]
		if !exists {
			return fmt.Errorf("任务不存在: %s", taskName)
		}

		// 解析依赖
		if !e.config.SkipDeps {
			for _, dep := range task.Deps {
				if err := dfs(dep); err != nil {
					return err
				}
			}
		}

		visited[taskName] = true
		order = append(order, taskName)
		return nil
	}

	for _, taskName := range taskNames {
		if err := dfs(taskName); err != nil {
			return nil, err
		}
	}

	return order, nil
}

func (e *TaskExecutor) executeSequential(ctx context.Context, taskNames []string) error {
	for _, taskName := range taskNames {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			if err := e.executeTask(ctx, taskName); err != nil {
				return err
			}
		}
	}
	return nil
}

func (e *TaskExecutor) executeParallel(ctx context.Context, taskNames []string) error {
	var wg sync.WaitGroup
	errChan := make(chan error, len(taskNames))
	semaphore := make(chan struct{}, 10) // 限制并发数

	for _, taskName := range taskNames {
		wg.Add(1)
		go func(name string) {
			defer wg.Done()

			select {
			case <-ctx.Done():
				errChan <- ctx.Err()
				return
			case semaphore <- struct{}{}:
				defer func() { <-semaphore }()

				if err := e.executeTask(ctx, name); err != nil {
					errChan <- err
					return
				}
			}
		}(taskName)
	}

	wg.Wait()
	close(errChan)

	for err := range errChan {
		if err != nil {
			return err
		}
	}

	return nil
}

func (e *TaskExecutor) executeTask(ctx context.Context, taskName string) error {
	e.mu.RLock()
	if e.completed[taskName] {
		e.mu.RUnlock()
		return nil
	}
	e.mu.RUnlock()

	// 检查是否已在运行
	if _, running := e.running.LoadOrStore(taskName, struct{}{}); running {
		return nil
	}
	defer e.running.Delete(taskName)

	task := e.taskfile.Tasks[taskName]

	e.logger.Info("开始执行任务", zap.String("task", taskName))

	// 任务环境变量不再通过 os.Setenv 设置：
	// os.Setenv 修改的是进程级全局状态，本执行器并发运行多个任务时
	// 存在数据竞争且会相互污染，改为在 executeCommand 中通过 exec.Cmd.Env 注入

	// 检查是否需要重新构建
	if !e.config.Force && !e.shouldRun(task) {
		e.logger.Info("跳过任务，文件未发生变化", zap.String("task", taskName))
		e.mu.Lock()
		e.completed[taskName] = true
		e.mu.Unlock()
		return nil
	}

	// 执行命令
	for i, cmd := range task.Cmds {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
			if err := e.executeCommand(ctx, task, cmd, i == 0); err != nil {
				if !task.IgnoreError {
					return fmt.Errorf("任务 '%s' 执行失败: %w", taskName, err)
				}
				e.logger.Warn("命令执行失败但继续执行",
					zap.String("task", taskName),
					zap.String("command", cmd),
					zap.Error(err))
			}
		}
	}

	e.mu.Lock()
	e.completed[taskName] = true
	e.mu.Unlock()

	e.logger.Info("任务执行完成", zap.String("task", taskName))
	return nil
}

func (e *TaskExecutor) executeCommand(ctx context.Context, task *Task, cmd string, isFirst bool) error {
	// 支持模板语法
	cmd = os.ExpandEnv(cmd)

	if e.config.DryRun {
		e.logger.Info("试运行", zap.String("command", cmd))
		return nil
	}

	if e.config.Verbose {
		e.logger.Info("执行命令", zap.String("command", cmd))
	}

	// 解析命令
	parts := strings.Fields(cmd)
	if len(parts) == 0 {
		return nil
	}

	// 创建命令
	command := exec.CommandContext(ctx, parts[0], parts[1:]...)

	// 设置工作目录
	if task.Dir != "" {
		command.Dir = task.Dir
	}

	// 注入任务环境变量（并发安全：只影响本子进程，不改进程级全局环境）
	if len(task.Env) > 0 {
		env := make([]string, 0, len(task.Env))
		for k, v := range task.Env {
			env = append(env, k+"="+os.ExpandEnv(v))
		}
		command.Env = append(os.Environ(), env...)
	}

	// 设置标准输入输出
	command.Stdout = os.Stdout
	command.Stderr = os.Stderr

	// 执行命令
	return command.Run()
}

func (e *TaskExecutor) shouldRun(task *Task) bool {
	// 如果没有源文件或生成文件，总是运行
	if len(task.Sources) == 0 || len(task.Generates) == 0 {
		return true
	}

	// 检查生成文件是否存在
	var maxSourceTime time.Time
	for _, source := range task.Sources {
		files, err := filepath.Glob(source)
		if err != nil {
			return true
		}
		for _, file := range files {
			info, err := os.Stat(file)
			if err != nil {
				return true
			}
			if info.ModTime().After(maxSourceTime) {
				maxSourceTime = info.ModTime()
			}
		}
	}

	// 检查生成文件
	for _, generated := range task.Generates {
		files, err := filepath.Glob(generated)
		if err != nil {
			return true
		}
		for _, file := range files {
			info, err := os.Stat(file)
			if err != nil || info.ModTime().Before(maxSourceTime) {
				return true
			}
		}
	}

	return false
}
```

### 4. 插件系统

```go
// internal/plugin/plugin.go
package plugin

import (
	"context"
	"fmt"
	"plugin"

	"go.uber.org/zap"
)

type Plugin interface {
	Name() string
	Version() string
	Initialize(logger *zap.Logger, config map[string]interface{}) error
	Commands() []Command
	Execute(ctx context.Context, cmd Command, args []string) error
}

type Command struct {
	Name        string
	Description string
	Args        []Argument
	Flags       []Flag
}

type Argument struct {
	Name        string
	Description string
	Required    bool
}

type Flag struct {
	Name        string
	Description string
	Type        string // "string", "int", "bool"
	Default     interface{}
}

type PluginManager struct {
	logger  *zap.Logger
	plugins map[string]Plugin
}

func NewPluginManager(logger *zap.Logger) *PluginManager {
	return &PluginManager{
		logger:  logger,
		plugins: make(map[string]Plugin),
	}
}

func (pm *PluginManager) LoadPlugin(path string) error {
	plug, err := plugin.Open(path)
	if err != nil {
		return fmt.Errorf("加载插件失败: %w", err)
	}

	// 查找导出的New函数
	symNew, err := plug.Lookup("New")
	if err != nil {
		return fmt.Errorf("插件未导出New函数: %w", err)
	}

	newFunc, ok := symNew.(func() Plugin)
	if !ok {
		return fmt.Errorf("New函数签名不正确")
	}

	// 创建插件实例
	pluginInstance := newFunc()

	// 初始化插件
	if err := pluginInstance.Initialize(pm.logger, nil); err != nil {
		return fmt.Errorf("插件初始化失败: %w", err)
	}

	pm.plugins[pluginInstance.Name()] = pluginInstance
	pm.logger.Info("插件加载成功",
		zap.String("name", pluginInstance.Name()),
		zap.String("version", pluginInstance.Version()))

	return nil
}

func (pm *PluginManager) GetPlugin(name string) (Plugin, bool) {
	plugin, exists := pm.plugins[name]
	return plugin, exists
}

func (pm *PluginManager) ListPlugins() []Plugin {
	var plugins []Plugin
	for _, plugin := range pm.plugins {
		plugins = append(plugins, plugin)
	}
	return plugins
}
```

---

## 🎨 用户体验增强

### 1. 彩色输出和进度条

```go
// pkg/output/output.go
package output

import (
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/fatih/color"
	"github.com/schollz/progressbar/v3"
)

var (
	Success = color.New(color.FgGreen).SprintfFunc()
	Error   = color.New(color.FgRed).SprintfFunc()
	Warning = color.New(color.FgYellow).SprintfFunc()
	Info    = color.New(color.FgCyan).SprintfFunc()
	Bold    = color.New(color.Bold).SprintfFunc()
)

type Output struct {
	verbose bool
}

func NewOutput(verbose bool) *Output {
	return &Output{verbose: verbose}
}

func (o *Output) Success(format string, args ...interface{}) {
	fmt.Println(Success(format, args...))
}

func (o *Output) Error(format string, args ...interface{}) {
	fmt.Fprintln(os.Stderr, Error(format, args...))
}

func (o *Output) Warning(format string, args ...interface{}) {
	fmt.Println(Warning(format, args...))
}

func (o *Output) Info(format string, args ...interface{}) {
	if o.verbose {
		fmt.Println(Info(format, args...))
	}
}

// Task 任务信息（对应 cmd 包中 Taskfile 解析出的任务）
type Task struct {
	Name string
	Desc string
	Deps []string
	Cmds []string
}

func (o *Output) PrintTaskList(tasks []Task) {
	table := [][]string{
		{"Task", "Description", "Dependencies", "Commands"},
	}

	for _, task := range tasks {
		deps := strings.Join(task.Deps, ", ")
		cmds := fmt.Sprintf("%d commands", len(task.Cmds))
		table = append(table, []string{
			task.Name,
			task.Desc,
			deps,
			cmds,
		})
	}

	PrintTable(table)
}

func PrintTable(data [][]string) {
	if len(data) == 0 {
		return
	}

	// 计算每列最大宽度
	colWidths := make([]int, len(data[0]))
	for _, row := range data {
		for i, cell := range row {
			if len(cell) > colWidths[i] {
				colWidths[i] = len(cell)
			}
		}
	}

	// 打印表格
	for i, row := range data {
		for j, cell := range row {
			fmt.Printf(" %-*s ", colWidths[j], cell)
			if j < len(row)-1 {
				fmt.Print("│")
			}
		}
		fmt.Println()

		// 打印分隔线
		if i == 0 {
			for j, width := range colWidths {
				fmt.Print("─")
				for k := 0; k < width; k++ {
					fmt.Print("─")
				}
				fmt.Print("─")
				if j < len(colWidths)-1 {
					fmt.Print("┼")
				}
			}
			fmt.Println()
		}
	}
}

func CreateProgressBar(total int64, description string) *progressbar.ProgressBar {
	return progressbar.NewOptions64(
		total,
		progressbar.OptionSetDescription(description),
		progressbar.OptionSetWriter(os.Stderr),
		progressbar.OptionShowCount(),
		progressbar.OptionShowIts(),
		progressbar.OptionSetItsString(""),
		progressbar.OptionOnCompletion(func() {
			fmt.Fprint(os.Stderr, "\n")
		}),
		progressbar.OptionThrottle(100*time.Millisecond),
		progressbar.OptionSetRenderBlankState(true),
		progressbar.OptionSpinnerType(14),
		progressbar.OptionFullWidth(),
		// 修复：progressbar/v3 没有 ElapsedTimeString / DescriptionString 字符串选项
		// （此前文档虚构）；用 OptionSetElapsedTime + OptionShowElapsedTimeOnFinish 达到同样效果
		progressbar.OptionSetElapsedTime(true),
		progressbar.OptionShowElapsedTimeOnFinish(),
	)
}
```

### 2. 配置验证和自动补全

```go
// internal/config/validator.go
package config

import (
	"fmt"
	"reflect"
	"strings"

	"github.com/go-playground/validator/v10"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var validate = validator.New()

type Config struct {
	Version    string            `mapstructure:"version" validate:"required,semver"`
	Env        map[string]string `mapstructure:"env"`
	Tasks      map[string]Task   `mapstructure:"tasks" validate:"required,min=1,dive"`
	Includes   []string          `mapstructure:"includes"`
	Variables  map[string]string `mapstructure:"vars"`
	Plugins    map[string]PluginConfig `mapstructure:"plugins"`
}

type Task struct {
	Name        string   `mapstructure:"name" validate:"required"`
	Desc        string   `mapstructure:"desc"`
	Deps        []string `mapstructure:"deps" validate:"dive,required"`
	Cmds        []string `mapstructure:"cmds" validate:"required,min=1,dive,required"`
	Env         map[string]string `mapstructure:"env"`
	Sources     []string `mapstructure:"sources" validate:"dive,required"`
	Generates   []string `mapstructure:"generates" validate:"dive,required"`
	Dir         string   `mapstructure:"dir"`
	IgnoreError bool     `mapstructure:"ignore_error"`
	Parallel    bool     `mapstructure:"parallel"`
}

type PluginConfig struct {
	Enabled bool                   `mapstructure:"enabled"`
	Config  map[string]interface{} `mapstructure:"config"`
}

func ValidateConfig(v *viper.Viper) (*Config, error) {
	var config Config

	// 解析配置
	if err := v.Unmarshal(&config); err != nil {
		return nil, fmt.Errorf("配置解析失败: %w", err)
	}

	// 验证配置
	if err := validate.Struct(config); err != nil {
		return nil, fmt.Errorf("配置验证失败: %w", err)
	}

	// 验证任务依赖
	for taskName, task := range config.Tasks {
		for _, dep := range task.Deps {
			if _, exists := config.Tasks[dep]; !exists {
				return nil, fmt.Errorf("任务 '%s' 依赖的任务 '%s' 不存在", taskName, dep)
			}
		}
	}

	return &config, nil
}

func GenerateCompletion(cmd *cobra.Command) {
	// 生成bash自动补全
	cmd.RegisterFlagCompletionFunc("task", func(cmd *cobra.Command, args []string, toComplete string) ([]string, cobra.ShellCompDirective) {
		// 读取任务文件获取任务列表
		if tasks, err := loadTaskNames(); err == nil {
			var completions []string
			for _, task := range tasks {
				if strings.HasPrefix(task, toComplete) {
					completions = append(completions, task)
				}
			}
			return completions, cobra.ShellCompDirectiveNoFileComp
		}
		return nil, cobra.ShellCompDirectiveNoFileComp
	})
}
```

---

## 🧪 测试覆盖

### 1. 单元测试

```go
// internal/executor/executor_test.go
package executor

import (
	"context"
	"os"
	"path/filepath"
	"testing"
	"time"

	"go.uber.org/zap"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestTaskExecutor_Execute(t *testing.T) {
	logger, _ := zap.NewDevelopment()

	tests := []struct {
		name        string
		taskfile    *Taskfile
		tasks       []string
		expectError bool
	}{
		{
			name: "简单任务执行",
			taskfile: &Taskfile{
				Version: "2.0",
				Tasks: map[string]*Task{
					"hello": {
						Name: "hello",
						Cmds: []string{"echo 'Hello, World!'"},
					},
				},
			},
			tasks:       []string{"hello"},
			expectError: false,
		},
		{
			name: "依赖任务执行",
			taskfile: &Taskfile{
				Version: "2.0",
				Tasks: map[string]*Task{
					"build": {
						Name: "build",
						Deps: []string{"test"},
						Cmds: []string{"echo 'Building'"},
					},
					"test": {
						Name: "test",
						Cmds: []string{"echo 'Testing'"},
					},
				},
			},
			tasks:       []string{"build"},
			expectError: false,
		},
		{
			name: "不存在的任务",
			taskfile: &Taskfile{
				Version: "2.0",
				Tasks:   map[string]*Task{},
			},
			tasks:       []string{"nonexistent"},
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			executor := NewTaskExecutor(logger, tt.taskfile, TaskExecutorConfig{})

			err := executor.Execute(tt.tasks...)

			if tt.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestTaskExecutor_ResolveDependencies(t *testing.T) {
	taskfile := &Taskfile{
		Version: "2.0",
		Tasks: map[string]*Task{
			"app": {
				Name: "app",
				Deps: []string{"build", "test"},
			},
			"build": {
				Name: "build",
				Deps: []string{"clean"},
			},
			"test": {
				Name: "test",
				Deps: []string{"clean"},
			},
			"clean": {
				Name: "clean",
			},
		},
	}

	executor := NewTaskExecutor(nil, taskfile, TaskExecutorConfig{})

	order, err := executor.resolveDependencies("app")
	require.NoError(t, err)

	// 验证执行顺序
	expected := []string{"clean", "build", "test", "app"}
	assert.Equal(t, expected, order)
}

func TestTaskExecutor_ShouldRun(t *testing.T) {
	// 创建临时文件
	tempDir := t.TempDir()
	sourceFile := filepath.Join(tempDir, "main.go")
	generatedFile := filepath.Join(tempDir, "main")

	// 写入源文件
	os.WriteFile(sourceFile, []byte("package main"), 0644)

	// 设置文件时间
	oldTime := time.Now().Add(-1 * time.Hour)
	os.Chtimes(sourceFile, oldTime, oldTime)

	task := &Task{
		Name:      "build",
		Sources:   []string{sourceFile},
		Generates: []string{generatedFile},
	}

	executor := &TaskExecutor{}

	// 第一次执行，生成文件不存在，应该运行
	assert.True(t, executor.shouldRun(task))

	// 创建生成文件，设置时间为现在
	os.WriteFile(generatedFile, []byte("binary"), 0644)

	// 生成文件比源文件新，不应该运行
	assert.False(t, executor.shouldRun(task))

	// 更新源文件时间
	newTime := time.Now()
	os.Chtimes(sourceFile, newTime, newTime)

	// 源文件比生成文件新，应该运行
	assert.True(t, executor.shouldRun(task))
}
```

### 2. 集成测试

```go
// cmd/root_test.go
package cmd

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap"
)

func TestRootCommand(t *testing.T) {
	// 创建临时目录
	tempDir := t.TempDir()
	os.Chdir(tempDir)

	// 创建测试配置文件
	config := `
version: "2.0"
tasks:
  hello:
    desc: "Say hello"
    cmds:
      - echo "Hello, World!"

  test:
    desc: "Run tests"
    cmds:
      - echo "Running tests..."
`

	err := os.WriteFile("taskfile.yaml", []byte(config), 0644)
	require.NoError(t, err)

	tests := []struct {
		name        string
		args        []string
		expectError bool
		expectOut   string
	}{
		{
			name:        "显示帮助",
			args:        []string{"--help"},
			expectError: false,
			expectOut:   "Task是一个现代化的任务运行器",
		},
		{
			name:        "执行任务",
			args:        []string{"run", "hello"},
			expectError: false,
			expectOut:   "Hello, World!",
		},
		{
			name:        "列出任务",
			args:        []string{"list"},
			expectError: false,
			expectOut:   "hello",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// 创建根命令（NewRootCommand 定义见 main.go）
			rootCmd := NewRootCommand(zap.NewNop())

			// 设置输出缓冲
			out := &bytes.Buffer{}
			rootCmd.SetOut(out)
			rootCmd.SetErr(out)

			// 执行命令
			rootCmd.SetArgs(tt.args)
			err := rootCmd.Execute()

			if tt.expectError {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}

			if tt.expectOut != "" {
				assert.Contains(t, out.String(), tt.expectOut)
			}
		})
	}
}

func TestInitCommand(t *testing.T) {
	tempDir := t.TempDir()
	os.Chdir(tempDir)

	// 执行初始化命令
	rootCmd := NewRootCommand(zap.NewNop())
	rootCmd.SetArgs([]string{"init"})

	err := rootCmd.Execute()
	require.NoError(t, err)

	// 验证文件是否创建
	assert.FileExists(t, "taskfile.yaml")
	assert.FileExists(t, ".gitignore")

	// 验证配置文件内容
	content, err := os.ReadFile("taskfile.yaml")
	require.NoError(t, err)

	assert.Contains(t, string(content), "version: \"2.0\"")
	assert.Contains(t, string(content), "build:")
	assert.Contains(t, string(content), "test:")
}
```

---

## 📦 发布和分发

### 1. 构建配置

```yaml
# .goreleaser.yaml
project_name: task

before:
  hooks:
    - go mod tidy
    - go generate ./...

builds:
  - id: task
    main: ./main.go
    binary: task
    goos:
      - linux
      - darwin
      - windows
    goarch:
      - amd64
      - arm64
      - "386"
    ldflags:
      - -s -w
      - -X "main.Version={{.Version}}"
      - -X "main.Commit={{.Commit}}"
      - -X "main.Date={{.Date}}"

archives:
  - format: tar.gz
    format_overrides:
      - goos: windows
        format: zip
    name_template: >-
      task_{{ .Version }}_
      {{- title .Os }}_
      {{- if eq .Arch "amd64" }}x86_64
      {{- else if eq .Arch "386" }}i386
      {{- else }}{{ .Arch }}{{ end }}
    files:
      - LICENSE
      - README.md
      - completions/*

checksum:
  name_template: "checksums.txt"

snapshot:
  name_template: "{{ incpatch .Version }}-next"

changelog:
  sort: asc
  filters:
    exclude:
      - "^docs:"
      - "^test:"
      - "^ci:"

brews:
  - name: task
    homepage: https://github.com/yourusername/task
    tap:
      owner: yourusername
      name: homebrew-tap
    commit_author:
      name: goreleaserbot
      email: goreleaser@carlosbecker.com

scoop:
  bucket:
    owner: yourusername
    name: scoop-bucket
  commit_author:
    name: goreleaserbot
    email: goreleaser@carlosbecker.com

npm:
  - name: task-runner
    package_name: "@yourusername/task"
    homepage: https://github.com/yourusername/task
    description: "A modern task runner for Go projects"
```

### 2. GitHub Actions CI/CD

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.25'

      - name: Import GPG key
        uses: crazy-max/ghaction-import-gpg@v6
        with:
          gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
          passphrase: ${{ secrets.GPG_PASSPHRASE }}

      - name: Run GoReleaser
        uses: goreleaser/goreleaser-action@v5
        with:
          distribution: goreleaser
          version: latest
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GPG_FINGERPRINT: ${{ secrets.GPG_FINGERPRINT }}
```

---

## 🎯 分阶段成果与验收

不要把下面的清单视为“阅读本文后已经掌握”。每个阶段都应留下命令、输入文件、实际输出和失败用例；只有这些证据存在，才算完成该阶段。

| 阶段 | 要交付的最小产物 | 必做失败用例 | 通过标准 |
|---|---|---|---|
| 1. 命令边界 | `task-runner list` 与 `task-runner run <name>`；明确 stdout、stderr 和退出码 | 缺少 `<name>`、未知任务、未知 flag | 合法调用列出或执行目标；三类错误都不执行 shell 命令，且返回非零退出码 |
| 2. 配置读取 | 一个可提交的 `taskfile.yaml` 样例与对应 Go 配置类型 | YAML 语法错误、任务缺 `cmds`、环境变量覆盖配置 | 错误指出文件和字段；记录并测试配置、环境变量、flag 的优先级 |
| 3. 依赖图 | 拓扑排序函数和三节点配置样例 | `build → test → build` 环；依赖不存在 | 无环图每个依赖先于使用者执行；环与缺失依赖给出可定位的名称 |
| 4. 进程执行 | 使用 `exec.CommandContext` 的执行器；每个任务有名称、开始/结束时间和退出状态 | 子进程非零退出、超时、父进程取消 | 失败保留 stderr 摘要和失败任务名；取消后不再启动尚未开始的任务 |
| 5. 有界并发 | 可配置的 worker 上限，而不是每个任务一个 goroutine | 两个任务争用同一临时文件；一个任务先失败 | 同时运行数不超过上限；失败策略（立即取消或继续收集）由配置和测试共同定义 |
| 6. 可观察输出 | 机器可读 JSON 日志或稳定的键值字段 | 命令失败、取消、配置解析失败 | 每条关键记录至少带 task、event、duration 或 error；不记录令牌、完整环境变量或命令中的密钥 |
| 7. 可选扩展 | shell 补全、文件监视、插件或发布配置中的任一项 | 扩展加载失败或平台不支持 | 核心 `run` 命令仍可用；扩展故障不会改变核心任务的退出码语义 |

### 推荐的验证顺序

先为阶段 1 到 3 写纯函数测试：参数解析、配置校验和依赖排序不需要启动真实子进程。阶段 4 用临时脚本或受控命令制造成功、失败和超时；不要拿真实部署命令当测试夹具。阶段 5 再加入并发，测试中用 channel 控制执行顺序，确认上限和取消行为。最后才考虑 Cobra、Viper、日志库或发布工具的具体选型。

### 完成后你应能做出的工程判断

当项目规模很小时，标准库 `flag` 加 `os/exec` 往往足够；当子命令、补全和帮助文档成为主要复杂度时，再引入 Cobra。配置层应把“读取来源”和“业务校验”分开：Viper 能合并来源，但不能替你定义哪些字段组合有效。结构化日志的价值是按字段检索一次任务的全过程，不是把普通文本日志改成 JSON。性能优化也必须先有可复现的任务数量、依赖形状和耗时基线；并发更多并不必然更快，可能只是让资源争用更严重。

本项目的发布、包管理和 CI/CD 部分只提供学习契约与模板。它们需要仓库权限、签名密钥和目标平台环境，不能因文档中有工作流片段就标记为已交付或已验证。

---

*最后更新: 2026年9月*

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
