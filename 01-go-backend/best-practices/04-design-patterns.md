# Go设计模式实战 - 构建可维护可扩展的应用程序

## 🏗️ 设计模式概述

设计模式是软件开发中常见问题的可重用解决方案。在Go语言中，由于其独特的语言特性（如接口、组合、并发原语），设计模式的实现方式与传统面向对象语言有所不同。本文档将深入探讨Go中的设计模式，帮助你构建更加可维护、可扩展的应用程序。

### Go语言与设计模式
- **接口驱动**: Go的隐式接口实现让代码更加灵活
- **组合优于继承**: 通过嵌入结构体实现代码复用
- **并发友好**: 利用goroutine和channel实现并发模式
- **简洁哲学**: 避免过度设计，保持代码简洁

### 设计模式分类
1. **创建型模式**: 对象创建机制
2. **结构型模式**: 对象组合方式
3. **行为型模式**: 对象间通信和责任分配
4. **并发模式**: Go特有的并发设计模式

---

## 🏭 创建型模式

### 1. 单例模式 (Singleton)

确保一个类只有一个实例，并提供全局访问点。

```go
package singleton

import (
	"sync"
)

type Database struct {
	connection string
}

var (
	instance *Database
	once     sync.Once
)

func GetDatabase() *Database {
	once.Do(func() {
		instance = &Database{
			connection: "default-connection",
		}
	})
	return instance
}

// 带参数的单例模式
type Config struct {
	DatabaseURL string
	APIKey      string
}

var (
	configInstance *Config
	configOnce     sync.Once
)

func GetConfig(dbURL, apiKey string) *Config {
	configOnce.Do(func() {
		configInstance = &Config{
			DatabaseURL: dbURL,
			APIKey:      apiKey,
		}
	})
	return configInstance
}

// 测试单例模式
func ExampleSingleton() {
	db1 := GetDatabase()
	db2 := GetDatabase()

	// db1 和 db2 是同一个实例
	if db1 == db2 {
		fmt.Println("单例模式验证成功")
	}
}
```

### 2. 工厂模式 (Factory)

定义一个用于创建对象的接口，让子类决定实例化哪一个类。

```go
package factory

import "fmt"

// 产品接口
type PaymentGateway interface {
	Pay(amount float64) error
	Refund(transactionID string) error
}

// 具体产品
type StripeGateway struct {
	apiKey string
}

func (s *StripeGateway) Pay(amount float64) error {
	fmt.Printf("使用Stripe支付: %.2f\n", amount)
	return nil
}

func (s *StripeGateway) Refund(transactionID string) error {
	fmt.Printf("使用Stripe退款: %s\n", transactionID)
	return nil
}

type PayPalGateway struct {
	clientID string
	secret   string
}

func (p *PayPalGateway) Pay(amount float64) error {
	fmt.Printf("使用PayPal支付: %.2f\n", amount)
	return nil
}

func (p *PayPalGateway) Refund(transactionID string) error {
	fmt.Printf("使用PayPal退款: %s\n", transactionID)
	return nil
}

type AlipayGateway struct {
	appID string
}

func (a *AlipayGateway) Pay(amount float64) error {
	fmt.Printf("使用支付宝支付: %.2f\n", amount)
	return nil
}

func (a *AlipayGateway) Refund(transactionID string) error {
	fmt.Printf("使用支付宝退款: %s\n", transactionID)
	return nil
}

// 工厂函数
func NewPaymentGateway(gatewayType string, config map[string]string) (PaymentGateway, error) {
	switch gatewayType {
	case "stripe":
		return &StripeGateway{
			apiKey: config["api_key"],
		}, nil
	case "paypal":
		return &PayPalGateway{
			clientID: config["client_id"],
			secret:   config["secret"],
		}, nil
	case "alipay":
		return &AlipayGateway{
			appID: config["app_id"],
		}, nil
	default:
		return nil, fmt.Errorf("不支持的支付网关类型: %s", gatewayType)
	}
}

// 抽象工厂模式
type LoggerFactory interface {
	CreateLogger() Logger
	CreateFormatter() Formatter
}

type FileLoggerFactory struct{}

func (f *FileLoggerFactory) CreateLogger() Logger {
	return &FileLogger{}
}

func (f *FileLoggerFactory) CreateFormatter() Formatter {
	return &TextFormatter{}
}

type ConsoleLoggerFactory struct{}

func (c *ConsoleLoggerFactory) CreateLogger() Logger {
	return &ConsoleLogger{}
}

func (c *ConsoleLoggerFactory) CreateFormatter() Formatter {
	return &JSONFormatter{}
}

// 使用示例
func ExampleFactory() {
	// 简单工厂
	stripeConfig := map[string]string{
		"api_key": "sk_test_123",
	}
	stripe, _ := NewPaymentGateway("stripe", stripeConfig)
	stripe.Pay(100.50)

	// 抽象工厂
	var factory LoggerFactory = &FileLoggerFactory{}
	logger := factory.CreateLogger()
	formatter := factory.CreateFormatter()

	logger.Log("Hello, World!", formatter)
}
```

### 3. 建造者模式 (Builder)

将一个复杂对象的构建与其表示分离，使得同样的构建过程可以创建不同的表示。

```go
package builder

import "fmt"

// 产品
type User struct {
	ID        int
	Username  string
	Email     string
	FirstName string
	LastName  string
	Age       int
	Address   string
	Phone     string
	Active    bool
}

// 建造者接口
type UserBuilder interface {
	SetID(id int) UserBuilder
	SetUsername(username string) UserBuilder
	SetEmail(email string) UserBuilder
	SetName(firstName, lastName string) UserBuilder
	SetAge(age int) UserBuilder
	SetAddress(address string) UserBuilder
	SetPhone(phone string) UserBuilder
	SetActive(active bool) UserBuilder
	Build() *User
}

// 具体建造者
type ConcreteUserBuilder struct {
	user *User
}

func NewUserBuilder() UserBuilder {
	return &ConcreteUserBuilder{
		user: &User{},
	}
}

func (b *ConcreteUserBuilder) SetID(id int) UserBuilder {
	b.user.ID = id
	return b
}

func (b *ConcreteUserBuilder) SetUsername(username string) UserBuilder {
	b.user.Username = username
	return b
}

func (b *ConcreteUserBuilder) SetEmail(email string) UserBuilder {
	b.user.Email = email
	return b
}

func (b *ConcreteUserBuilder) SetName(firstName, lastName string) UserBuilder {
	b.user.FirstName = firstName
	b.user.LastName = lastName
	return b
}

func (b *ConcreteUserBuilder) SetAge(age int) UserBuilder {
	b.user.Age = age
	return b
}

func (b *ConcreteUserBuilder) SetAddress(address string) UserBuilder {
	b.user.Address = address
	return b
}

func (b *ConcreteUserBuilder) SetPhone(phone string) UserBuilder {
	b.user.Phone = phone
	return b
}

func (b *ConcreteUserBuilder) SetActive(active bool) UserBuilder {
	b.user.Active = active
	return b
}

func (b *ConcreteUserBuilder) Build() *User {
	return b.user
}

// 导演类
type UserDirector struct {
	builder UserBuilder
}

func NewUserDirector(builder UserBuilder) *UserDirector {
	return &UserDirector{builder: builder}
}

func (d *UserDirector) ConstructBasicUser(id int, username, email string) *User {
	return d.builder.
		SetID(id).
		SetUsername(username).
		SetEmail(email).
		SetActive(true).
		Build()
}

func (d *UserDirector) ConstructFullUser(id int, username, email, firstName, lastName string, age int) *User {
	return d.builder.
		SetID(id).
		SetUsername(username).
		SetEmail(email).
		SetName(firstName, lastName).
		SetAge(age).
		SetActive(true).
		Build()
}

// 使用示例
func ExampleBuilder() {
	// 使用建造者模式
	user := NewUserBuilder().
		SetID(1).
		SetUsername("johndoe").
		SetEmail("john@example.com").
		SetName("John", "Doe").
		SetAge(30).
		SetActive(true).
		Build()

	fmt.Printf("创建用户: %+v\n", user)

	// 使用导演类
	director := NewUserDirector(NewUserBuilder())
	basicUser := director.ConstructBasicUser(2, "alice", "alice@example.com")
	fullUser := director.ConstructFullUser(3, "bob", "bob@example.com", "Bob", "Smith", 25)

	fmt.Printf("基础用户: %+v\n", basicUser)
	fmt.Printf("完整用户: %+v\n", fullUser)
}
```

### 4. 原型模式 (Prototype)

使用原型实例指定创建对象的种类，并通过拷贝这些原型创建新的对象。

```go
package prototype

import "fmt"

// 原型接口
type Cloneable interface {
	Clone() Cloneable
}

// 具体原型
type Document struct {
	Title    string
	Content  string
	Author   string
	Version  int
	Metadata map[string]string
}

func (d *Document) Clone() Cloneable {
	// 深拷贝
	newDoc := &Document{
		Title:   d.Title,
		Content: d.Content,
		Author:  d.Author,
		Version: d.Version + 1,
	}

	// 拷贝元数据
	newDoc.Metadata = make(map[string]string)
	for k, v := range d.Metadata {
		newDoc.Metadata[k] = v
	}

	return newDoc
}

// 原型管理器
type DocumentManager struct {
	prototypes map[string]Document
}

func NewDocumentManager() *DocumentManager {
	return &DocumentManager{
		prototypes: make(map[string]Document),
	}
}

func (dm *DocumentManager) AddPrototype(name string, doc Document) {
	dm.prototypes[name] = doc
}

func (dm *DocumentManager) CreateDocument(name string) (*Document, error) {
	prototype, exists := dm.prototypes[name]
	if !exists {
		return nil, fmt.Errorf("原型 '%s' 不存在", name)
	}

	cloned := prototype.Clone().(*Document)
	return cloned, nil
}

// 使用示例
func ExamplePrototype() {
	// 创建原型管理器
	manager := NewDocumentManager()

	// 注册原型
	reportPrototype := Document{
		Title:    "报告模板",
		Content:  "这是一个报告模板",
		Author:   "系统",
		Version:  1,
		Metadata: map[string]string{"type": "report", "category": "business"},
	}
	manager.AddPrototype("report", reportPrototype)

	contractPrototype := Document{
		Title:    "合同模板",
		Content:  "这是一个合同模板",
		Author:   "法务部",
		Version:  1,
		Metadata: map[string]string{"type": "contract", "category": "legal"},
	}
	manager.AddPrototype("contract", contractPrototype)

	// 创建新文档
	report, _ := manager.CreateDocument("report")
	report.Title = "Q4销售报告"
	report.Content = "这是Q4的销售数据报告"

	contract, _ := manager.CreateDocument("contract")
	contract.Title = "服务合同"
	contract.Content = "这是与客户的服务合同"

	fmt.Printf("报告: %+v\n", report)
	fmt.Printf("合同: %+v\n", contract)
}
```

---

## 🏗️ 结构型模式

### 1. 适配器模式 (Adapter)

将一个类的接口转换成客户希望的另外一个接口，使得原本由于接口不兼容而不能一起工作的那些类可以一起工作。

```go
package adapter

import "fmt"

// 目标接口
type MediaPlayer interface {
	Play(audioType, fileName string) error
}

// 被适配者
type AdvancedMediaPlayer interface {
	PlayVlc(fileName string) error
	PlayMp4(fileName string) error
}

// 具体被适配者
type VlcPlayer struct{}

func (v *VlcPlayer) PlayVlc(fileName string) error {
	fmt.Printf("播放VLC文件: %s\n", fileName)
	return nil
}

func (v *VlcPlayer) PlayMp4(fileName string) error {
	return fmt.Errorf("VLC播放器不支持MP4格式")
}

type Mp4Player struct{}

func (m *Mp4Player) PlayVlc(fileName string) error {
	return fmt.Errorf("MP4播放器不支持VLC格式")
}

func (m *Mp4Player) PlayMp4(fileName string) error {
	fmt.Printf("播放MP4文件: %s\n", fileName)
	return nil
}

// 适配器
type MediaAdapter struct {
	advancedMusicPlayer AdvancedMediaPlayer
}

func NewMediaAdapter(audioType string) *MediaAdapter {
	switch audioType {
	case "vlc":
		return &MediaAdapter{advancedMusicPlayer: &VlcPlayer{}}
	case "mp4":
		return &MediaAdapter{advancedMusicPlayer: &Mp4Player{}}
	default:
		return nil
	}
}

func (m *MediaAdapter) Play(audioType, fileName string) error {
	switch audioType {
	case "vlc":
		return m.advancedMusicPlayer.PlayVlc(fileName)
	case "mp4":
		return m.advancedMusicPlayer.PlayMp4(fileName)
	default:
		return fmt.Errorf("不支持的音频格式: %s", audioType)
	}
}

// 音频播放器（使用适配器）
type AudioPlayer struct {
	mediaAdapter *MediaAdapter
}

func (a *AudioPlayer) Play(audioType, fileName string) error {
	switch audioType {
	case "mp3":
		fmt.Printf("播放MP3文件: %s\n", fileName)
		return nil
	case "vlc", "mp4":
		if a.mediaAdapter == nil {
			a.mediaAdapter = NewMediaAdapter(audioType)
		}
		return a.mediaAdapter.Play(audioType, fileName)
	default:
		return fmt.Errorf("不支持的音频格式: %s", audioType)
	}
}

// 使用示例
func ExampleAdapter() {
	player := &AudioPlayer{}

	// 播放MP3（直接支持）
	player.Play("mp3", "song.mp3")

	// 播放VLC（需要适配器）
	player.Play("vlc", "movie.vlc")

	// 播放MP4（需要适配器）
	player.Play("mp4", "video.mp4")
}
```

### 2. 装饰器模式 (Decorator)

动态地给一个对象添加一些额外的职责。

```go
package decorator

import "fmt"

// 组件接口
type Component interface {
	Operation() string
}

// 具体组件
type ConcreteComponent struct{}

func (c *ConcreteComponent) Operation() string {
	return "基础组件"
}

// 装饰器基类
type Decorator struct {
	component Component
}

func (d *Decorator) Operation() string {
	return d.component.Operation()
}

// 具体装饰器
type ConcreteDecoratorA struct {
	Decorator
	addedState string
}

func NewConcreteDecoratorA(component Component) *ConcreteDecoratorA {
	return &ConcreteDecoratorA{
		Decorator: Decorator{component: component},
		addedState: "新增状态A",
	}
}

func (d *ConcreteDecoratorA) Operation() string {
	return d.component.Operation() + " + 装饰器A(" + d.addedState + ")"
}

type ConcreteDecoratorB struct {
	Decorator
}

func NewConcreteDecoratorB(component Component) *ConcreteDecoratorB {
	return &ConcreteDecoratorB{
		Decorator: Decorator{component: component},
	}
}

func (d *ConcreteDecoratorB) Operation() string {
	return d.component.Operation() + " + 装饰器B"
}

func (d *ConcreteDecoratorB) AddedBehavior() {
	fmt.Println("装饰器B的额外行为")
}

// 实际应用：日志装饰器
type Logger interface {
	Log(message string) error
}

type BasicLogger struct{}

func (l *BasicLogger) Log(message string) error {
	fmt.Printf("[LOG] %s\n", message)
	return nil
}

type TimestampDecorator struct {
	logger Logger
}

func NewTimestampDecorator(logger Logger) *TimestampDecorator {
	return &TimestampDecorator{logger: logger}
}

func (d *TimestampDecorator) Log(message string) error {
	timestamp := fmt.Sprintf("[%s]", time.Now().Format("2006-01-02 15:04:05"))
	return d.logger.Log(timestamp + " " + message)
}

type LevelDecorator struct {
	logger Logger
	level  string
}

func NewLevelDecorator(logger Logger, level string) *LevelDecorator {
	return &LevelDecorator{logger: logger, level: level}
}

func (d *LevelDecorator) Log(message string) error {
	levelTag := fmt.Sprintf("[%s]", strings.ToUpper(d.level))
	return d.logger.Log(levelTag + " " + message)
}

// 使用示例
func ExampleDecorator() {
	// 基础组件
	component := &ConcreteComponent{}
	fmt.Println("基础组件:", component.Operation())

	// 装饰后的组件
	decoratedA := NewConcreteDecoratorA(component)
	decoratedB := NewConcreteDecoratorB(decoratedA)
	fmt.Println("装饰后:", decoratedB.Operation())
	decoratedB.AddedBehavior()

	// 实际应用：日志装饰器
	basicLogger := &BasicLogger{}

	// 添加时间戳装饰器
	timestampLogger := NewTimestampDecorator(basicLogger)
	timestampLogger.Log("这是一条日志")

	// 添加级别装饰器
	levelLogger := NewLevelDecorator(timestampLogger, "error")
	levelLogger.Log("发生错误")
}
```

### 3. 外观模式 (Facade)

为一个复杂的子系统提供一个简化的统一接口。

```go
package facade

import "fmt"

// 子系统A
class CPU {
public void start() {
    System.out.println("CPU启动");
}

public void execute() {
    System.out.println("CPU执行指令");
}

public void shutdown() {
    System.out.println("CPU关闭");
}
}

// 子系统B
class Memory {
public void load(long position, byte[] data) {
    System.out.println("内存加载数据到位置: " + position);
}

public void free() {
    System.out.println("内存释放");
}
}

// 子系统C
class HardDrive {
public byte[] read(long lba, int size) {
    System.out.println("硬盘读取数据: LBA=" + lba + ", 大小=" + size);
    return new byte[size];
}
}

// 外观类
class ComputerFacade {
    private CPU cpu;
    private Memory memory;
    private HardDrive hardDrive;

    public ComputerFacade() {
        this.cpu = new CPU();
        this.memory = new Memory();
        this.hardDrive = new HardDrive();
    }

    public void start() {
        System.out.println("计算机启动中...");
        cpu.start();
        memory.load(0, hardDrive.read(0, 1024));
        cpu.execute();
        System.out.println("计算机启动完成");
    }

    public void shutdown() {
        System.out.println("计算机关闭中...");
        cpu.shutdown();
        memory.free();
        System.out.println("计算机关闭完成");
    }
}

// 使用示例
public class FacadeExample {
    public static void main(String[] args) {
        ComputerFacade computer = new ComputerFacade();
        computer.start();
        computer.shutdown();
    }
}
```

### 4. 代理模式 (Proxy)

为其他对象提供一种代理以控制对这个对象的访问。

```go
package proxy

import "fmt"

// 主题接口
type Subject interface {
	Request() string
}

// 真实主题
type RealSubject struct{}

func (r *RealSubject) Request() string {
	return "真实主题的响应"
}

// 代理
type Proxy struct {
	realSubject *RealSubject
	accessCount int
}

func (p *Proxy) Request() string {
	if p.realSubject == nil {
		p.realSubject = &RealSubject{}
	}

	p.accessCount++
	fmt.Printf("代理访问次数: %d\n", p.accessCount)

	// 可以在这里添加额外的逻辑，如权限检查、缓存等
	return p.realSubject.Request()
}

func (p *Proxy) GetAccessCount() int {
	return p.accessCount
}

// 虚拟代理：延迟加载
type VirtualProxy struct {
	realSubject *RealSubject
	initialized bool
}

func (p *VirtualProxy) Request() string {
	if !p.initialized {
		fmt.Println("初始化真实主题...")
		p.realSubject = &RealSubject{}
		p.initialized = true
	}

	return p.realSubject.Request()
}

// 保护代理：访问控制
type ProtectionProxy struct {
	realSubject *RealSubject
	userRole    string
}

func NewProtectionProxy(role string) *ProtectionProxy {
	return &ProtectionProxy{
		realSubject: &RealSubject{},
		userRole:    role,
	}
}

func (p *ProtectionProxy) Request() string {
	if p.userRole != "admin" {
		return "访问被拒绝：需要管理员权限"
	}

	return p.realSubject.Request()
}

// 使用示例
func ExampleProxy() {
	// 普通代理
	proxy := &Proxy{}
	fmt.Println(proxy.Request())
	fmt.Println(proxy.Request())
	fmt.Printf("总访问次数: %d\n", proxy.GetAccessCount())

	// 虚拟代理
	virtualProxy := &VirtualProxy{}
	fmt.Println("第一次访问:", virtualProxy.Request())
	fmt.Println("第二次访问:", virtualProxy.Request())

	// 保护代理
	adminProxy := NewProtectionProxy("admin")
	userProxy := NewProtectionProxy("user")

	fmt.Println("管理员访问:", adminProxy.Request())
	fmt.Println("普通用户访问:", userProxy.Request())
}
```

### 5. 组合模式 (Composite)

将对象组合成树形结构以表示"部分-整体"的层次结构。

```go
package composite

import "fmt"

// 组件接口
type Component interface {
	Add(component Component) error
	Remove(component Component) error
	GetChild(index int) Component
	Operation() string
}

// 叶子组件
type Leaf struct {
	name string
}

func NewLeaf(name string) *Leaf {
	return &Leaf{name: name}
}

func (l *Leaf) Add(component Component) error {
	return fmt.Errorf("不能向叶子节点添加子节点")
}

func (l *Leaf) Remove(component Component) error {
	return fmt.Errorf("不能从叶子节点移除子节点")
}

func (l *Leaf) GetChild(index int) Component {
	return nil
}

func (l *Leaf) Operation() string {
	return l.name
}

// 复合组件
type Composite struct {
	name     string
	children []Component
}

func NewComposite(name string) *Composite {
	return &Composite{
		name:     name,
		children: make([]Component, 0),
	}
}

func (c *Composite) Add(component Component) error {
	c.children = append(c.children, component)
	return nil
}

func (c *Composite) Remove(component Component) error {
	for i, child := range c.children {
		if child == component {
			c.children = append(c.children[:i], c.children[i+1:]...)
			return nil
		}
	}
	return fmt.Errorf("子节点不存在")
}

func (c *Composite) GetChild(index int) Component {
	if index < 0 || index >= len(c.children) {
		return nil
	}
	return c.children[index]
}

func (c *Composite) Operation() string {
	result := c.name + "["
	for i, child := range c.children {
		if i > 0 {
			result += ", "
		}
		result += child.Operation()
	}
	result += "]"
	return result
}

// 使用示例：文件系统
type FileSystemComponent interface {
	GetName() string
	GetSize() int64
	Print(prefix string)
}

type File struct {
	name string
	size int64
}

func (f *File) GetName() string {
	return f.name
}

func (f *File) GetSize() int64 {
	return f.size
}

func (f *File) Print(prefix string) {
	fmt.Printf("%s%s (%d bytes)\n", prefix, f.name, f.size)
}

type Directory struct {
	name     string
	children []FileSystemComponent
}

func NewDirectory(name string) *Directory {
	return &Directory{
		name:     name,
		children: make([]FileSystemComponent, 0),
	}
}

func (d *Directory) GetName() string {
	return d.name
}

func (d *Directory) GetSize() int64 {
	var total int64
	for _, child := range d.children {
		total += child.GetSize()
	}
	return total
}

func (d *Directory) Add(component FileSystemComponent) {
	d.children = append(d.children, component)
}

func (d *Directory) Remove(component FileSystemComponent) {
	for i, child := range d.children {
		if child == component {
			d.children = append(d.children[:i], d.children[i+1:]...)
			break
		}
	}
}

func (d *Directory) Print(prefix string) {
	fmt.Printf("%s%s/\n", prefix, d.name)
	for _, child := range d.children {
		child.Print(prefix + "  ")
	}
}

// 使用示例
func ExampleComposite() {
	// 简单组合
	leaf1 := NewLeaf("叶子1")
	leaf2 := NewLeaf("叶子2")
	leaf3 := NewLeaf("叶子3")

	composite1 := NewComposite("复合1")
	composite1.Add(leaf1)
	composite1.Add(leaf2)

	composite2 := NewComposite("复合2")
	composite2.Add(composite1)
	composite2.Add(leaf3)

	fmt.Println("组合结构:", composite2.Operation())

	// 文件系统示例
	root := NewDirectory("根目录")

	docs := NewDirectory("文档")
	docs.Add(&File{"README.md", 1024})
	docs.Add(&File{"LICENSE", 2048})

	src := NewDirectory("源代码")
	src.Add(&File{"main.go", 4096})
	src.Add(&File{"utils.go", 2048})

	root.Add(docs)
	root.Add(src)

	fmt.Println("\n文件系统结构:")
	root.Print("")
	fmt.Printf("总大小: %d bytes\n", root.GetSize())
}
```

---

## 🔄 行为型模式

### 1. 观察者模式 (Observer)

定义对象间的一种一对多依赖关系，使得每当一个对象状态发生改变时，其相关依赖对象皆得到通知并被自动更新。

```go
package observer

import "fmt"

// 观察者接口
type Observer interface {
	Update(subject Subject)
}

// 主题接口
type Subject interface {
	RegisterObserver(observer Observer)
	RemoveObserver(observer Observer)
	NotifyObservers()
}

// 具体主题
type WeatherStation struct {
	temperature float64
	humidity    float64
	observers   []Observer
}

func NewWeatherStation() *WeatherStation {
	return &WeatherStation{
		observers: make([]Observer, 0),
	}
}

func (ws *WeatherStation) RegisterObserver(observer Observer) {
	ws.observers = append(ws.observers, observer)
}

func (ws *WeatherStation) RemoveObserver(observer Observer) {
	for i, obs := range ws.observers {
		if obs == observer {
			ws.observers = append(ws.observers[:i], ws.observers[i+1:]...)
			break
		}
	}
}

func (ws *WeatherStation) NotifyObservers() {
	for _, observer := range ws.observers {
		observer.Update(ws)
	}
}

func (ws *WeatherStation) SetMeasurements(temperature, humidity float64) {
	ws.temperature = temperature
	ws.humidity = humidity
	ws.NotifyObservers()
}

func (ws *WeatherStation) GetTemperature() float64 {
	return ws.temperature
}

func (ws *WeatherStation) GetHumidity() float64 {
	return ws.humidity
}

// 具体观察者
type PhoneDisplay struct {
	name string
}

func NewPhoneDisplay(name string) *PhoneDisplay {
	return &PhoneDisplay{name: name}
}

func (pd *PhoneDisplay) Update(subject Subject) {
	if ws, ok := subject.(*WeatherStation); ok {
		fmt.Printf("%s显示: 温度 %.1f°C, 湿度 %.1f%%\n",
			pd.name, ws.GetTemperature(), ws.GetHumidity())
	}
}

type TVDisplay struct {
	name string
}

func NewTVDisplay(name string) *TVDisplay {
	return &TVDisplay{name: name}
}

func (td *TVDisplay) Update(subject Subject) {
	if ws, ok := subject.(*WeatherStation); ok {
		fmt.Printf("%s显示: 天气更新 - 温度 %.1f°C\n",
			td.name, ws.GetTemperature())
	}
}

// 事件系统实现
type EventManager struct {
	subscribers map[string][]func(interface{})
}

func NewEventManager() *EventManager {
	return &EventManager{
		subscribers: make(map[string][]func(interface{})),
	}
}

func (em *EventManager) Subscribe(eventType string, handler func(interface{})) {
	em.subscribers[eventType] = append(em.subscribers[eventType], handler)
}

func (em *EventManager) Unsubscribe(eventType string, handler func(interface{})) {
	if handlers, exists := em.subscribers[eventType]; exists {
		for i, h := range handlers {
			if &h == &handler {
				em.subscribers[eventType] = append(handlers[:i], handlers[i+1:]...)
				break
			}
		}
	}
}

func (em *EventManager) Publish(eventType string, data interface{}) {
	if handlers, exists := em.subscribers[eventType]; exists {
		for _, handler := range handlers {
			handler(data)
		}
	}
}

// 使用示例
func ExampleObserver() {
	// 天气站示例
	weatherStation := NewWeatherStation()

	phone1 := NewPhoneDisplay("iPhone")
	phone2 := NewPhoneDisplay("Android")
	tv := NewTVDisplay("智能电视")

	weatherStation.RegisterObserver(phone1)
	weatherStation.RegisterObserver(phone2)
	weatherStation.RegisterObserver(tv)

	fmt.Println("第一次更新:")
	weatherStation.SetMeasurements(25.5, 60.0)

	fmt.Println("\n移除一个观察者:")
	weatherStation.RemoveObserver(phone2)
	weatherStation.SetMeasurements(26.0, 65.0)

	// 事件系统示例
	eventManager := NewEventManager()

	// 订阅事件
	eventManager.Subscribe("user_created", func(data interface{}) {
		if user, ok := data.(map[string]interface{}); ok {
			fmt.Printf("用户创建事件: %s\n", user["name"])
		}
	})

	eventManager.Subscribe("user_deleted", func(data interface{}) {
		if userID, ok := data.(string); ok {
			fmt.Printf("用户删除事件: %s\n", userID)
		}
	})

	// 发布事件
	eventManager.Publish("user_created", map[string]interface{}{
		"id":   "123",
		"name": "张三",
	})

	eventManager.Publish("user_deleted", "456")
}
```

### 2. 策略模式 (Strategy)

定义一系列的算法，把它们一个个封装起来，并且使它们可相互替换。

```go
package strategy

import "fmt"

// 策略接口
type PaymentStrategy interface {
	Pay(amount float64) error
}

// 具体策略
type CreditCardStrategy struct {
	cardNumber string
	cvv        string
	expiryDate string
}

func (cc *CreditCardStrategy) Pay(amount float64) error {
	fmt.Printf("使用信用卡支付 %.2f (卡号: %s)\n", amount, cc.cardNumber[:4]+"****"+cc.cardNumber[len(cc.cardNumber)-4:])
	return nil
}

type PayPalStrategy struct {
	email    string
	password string
}

func (pp *PayPalStrategy) Pay(amount float64) error {
	fmt.Printf("使用PayPal支付 %.2f (邮箱: %s)\n", amount, pp.email)
	return nil
}

type WeChatPayStrategy struct {
	qrCode string
}

func (wcp *WeChatPayStrategy) Pay(amount float64) error {
	fmt.Printf("使用微信支付 %.2f (二维码: %s)\n", amount, wcp.qrCode)
	return nil
}

type AlipayStrategy struct {
	account string
}

func (ap *AlipayStrategy) Pay(amount float64) error {
	fmt.Printf("使用支付宝支付 %.2f (账户: %s)\n", amount, ap.account)
	return nil
}

// 上下文
type PaymentContext struct {
	strategy PaymentStrategy
}

func (pc *PaymentContext) SetStrategy(strategy PaymentStrategy) {
	pc.strategy = strategy
}

func (pc *PaymentContext) ExecutePayment(amount float64) error {
	if pc.strategy == nil {
		return fmt.Errorf("请先设置支付策略")
	}
	return pc.strategy.Pay(amount)
}

// 策略工厂
type PaymentStrategyFactory struct{}

func (f *PaymentStrategyFactory) CreateStrategy(paymentType string, details map[string]string) (PaymentStrategy, error) {
	switch paymentType {
	case "credit_card":
		return &CreditCardStrategy{
			cardNumber: details["card_number"],
			cvv:        details["cvv"],
			expiryDate: details["expiry_date"],
		}, nil
	case "paypal":
		return &PayPalStrategy{
			email:    details["email"],
			password: details["password"],
		}, nil
	case "wechat":
		return &WeChatPayStrategy{
			qrCode: details["qr_code"],
		}, nil
	case "alipay":
		return &AlipayStrategy{
			account: details["account"],
		}, nil
	default:
		return nil, fmt.Errorf("不支持的支付方式: %s", paymentType)
	}
}

// 使用示例
func ExampleStrategy() {
	// 创建支付上下文
	paymentContext := &PaymentContext{}

	// 使用信用卡支付
	creditCard := &CreditCardStrategy{
		cardNumber: "1234567890123456",
		cvv:        "123",
		expiryDate: "12/25",
	}
	paymentContext.SetStrategy(creditCard)
	paymentContext.ExecutePayment(100.50)

	// 切换到支付宝
	alipay := &AlipayStrategy{
		account: "user@example.com",
	}
	paymentContext.SetStrategy(alipay)
	paymentContext.ExecutePayment(200.75)

	// 使用策略工厂
	factory := &PaymentStrategyFactory{}
	wechatStrategy, _ := factory.CreateStrategy("wechat", map[string]string{
		"qr_code": "wechat_qr_123",
	})
	paymentContext.SetStrategy(wechatStrategy)
	paymentContext.ExecutePayment(50.25)
}
```

### 3. 命令模式 (Command)

将一个请求封装为一个对象，从而使你可用不同的请求对客户进行参数化。

```go
package command

import "fmt"

// 命令接口
type Command interface {
	Execute() error
	Undo() error
}

// 接收者
type Light struct {
	name string
}

func NewLight(name string) *Light {
	return &Light{name: name}
}

func (l *Light) TurnOn() {
	fmt.Printf("%s 灯已打开\n", l.name)
}

func (l *Light) TurnOff() {
	fmt.Printf("%s 灯已关闭\n", l.name)
}

func (l *Light) Dim(level int) {
	fmt.Printf("%s 灯已调节到 %d%%\n", l.name, level)
}

// 具体命令
type LightOnCommand struct {
	light *Light
}

func NewLightOnCommand(light *Light) *LightOnCommand {
	return &LightOnCommand{light: light}
}

func (c *LightOnCommand) Execute() error {
	c.light.TurnOn()
	return nil
}

func (c *LightOnCommand) Undo() error {
	c.light.TurnOff()
	return nil
}

type LightOffCommand struct {
	light *Light
}

func NewLightOffCommand(light *Light) *LightOffCommand {
	return &LightOffCommand{light: light}
}

func (c *LightOffCommand) Execute() error {
	c.light.TurnOff()
	return nil
}

func (c *LightOffCommand) Undo() error {
	c.light.TurnOn()
	return nil
}

type DimLightCommand struct {
	light   *Light
	level   int
	prevLevel int
}

func NewDimLightCommand(light *Light, level int) *DimLightCommand {
	return &DimLightCommand{
		light: light,
		level: level,
	}
}

func (c *DimLightCommand) Execute() error {
	c.light.Dim(c.level)
	return nil
}

func (c *DimLightCommand) Undo() error {
	// 这里简化处理，实际应该保存之前的状态
	c.light.Dim(100)
	return nil
}

// 调用者
type RemoteControl struct {
	commands []Command
	history  []Command
}

func NewRemoteControl() *RemoteControl {
	return &RemoteControl{
		commands: make([]Command, 0),
		history:  make([]Command, 0),
	}
}

func (rc *RemoteControl) SetCommand(command Command) {
	rc.commands = append(rc.commands, command)
}

func (rc *RemoteControl) ExecuteCommands() error {
	for _, command := range rc.commands {
		if err := command.Execute(); err != nil {
			return err
		}
		rc.history = append(rc.history, command)
	}
	return nil
}

func (rc *RemoteControl) UndoLastCommand() error {
	if len(rc.history) == 0 {
		return fmt.Errorf("没有可撤销的命令")
	}

	lastCommand := rc.history[len(rc.history)-1]
	if err := lastCommand.Undo(); err != nil {
		return err
	}

	rc.history = rc.history[:len(rc.history)-1]
	return nil
}

// 宏命令
type MacroCommand struct {
	commands []Command
}

func NewMacroCommand(commands []Command) *MacroCommand {
	return &MacroCommand{commands: commands}
}

func (mc *MacroCommand) Execute() error {
	for _, command := range mc.commands {
		if err := command.Execute(); err != nil {
			return err
		}
	}
	return nil
}

func (mc *MacroCommand) Undo() error {
	// 反向执行撤销
	for i := len(mc.commands) - 1; i >= 0; i-- {
		if err := mc.commands[i].Undo(); err != nil {
			return err
		}
	}
	return nil
}

// 使用示例
func ExampleCommand() {
	// 创建设备
	livingRoomLight := NewLight("客厅")
	bedroomLight := NewLight("卧室")

	// 创建命令
	livingRoomOn := NewLightOnCommand(livingRoomLight)
	livingRoomOff := NewLightOffCommand(livingRoomLight)
	bedroomOn := NewLightOnCommand(bedroomLight)
	bedroomDim := NewDimLightCommand(bedroomLight, 50)

	// 创建遥控器
	remote := NewRemoteControl()

	// 设置命令
	remote.SetCommand(livingRoomOn)
	remote.SetCommand(bedroomOn)
	remote.SetCommand(bedroomDim)

	// 执行命令
	fmt.Println("执行命令:")
	remote.ExecuteCommands()

	// 撤销最后一个命令
	fmt.Println("\n撤销最后一个命令:")
	remote.UndoLastCommand()

	// 宏命令示例
	fmt.Println("\n宏命令示例:")
	macro := NewMacroCommand([]Command{
		NewLightOnCommand(livingRoomLight),
		NewDimLightCommand(livingRoomLight, 75),
		NewLightOnCommand(bedroomLight),
	})

	fmt.Println("执行宏命令:")
	macro.Execute()

	fmt.Println("撤销宏命令:")
	macro.Undo()
}
```

### 4. 状态模式 (State)

允许一个对象在其内部状态改变时改变它的行为。

```go
package state

import "fmt"

// 状态接口
type State interface {
	InsertCoin() error
	PressButton() error
	EjectCoin() error
	Refill(count int) error
	GetCount() int
}

// 上下文
type GumballMachine struct {
	count       int
	state       State
	hasCoin     State
	noCoin      State
	sold        State
	soldOut     State
	winnerState State
}

func NewGumballMachine(count int) *GumballMachine {
	machine := &GumballMachine{
		count: count,
	}

	machine.hasCoin = &HasCoinState{machine: machine}
	machine.noCoin = &NoCoinState{machine: machine}
	machine.sold = &SoldState{machine: machine}
	machine.soldOut = &SoldOutState{machine: machine}
	machine.winnerState = &WinnerState{machine: machine}

	if count > 0 {
		machine.state = machine.noCoin
	} else {
		machine.state = machine.soldOut
	}

	return machine
}

func (gm *GumballMachine) SetState(state State) {
	gm.state = state
}

func (gm *GumballMachine) InsertCoin() error {
	return gm.state.InsertCoin()
}

func (gm *GumballMachine) PressButton() error {
	return gm.state.PressButton()
}

func (gm *GumballMachine) EjectCoin() error {
	return gm.state.EjectCoin()
}

func (gm *GumballMachine) Refill(count int) error {
	return gm.state.Refill(count)
}

func (gm *GumballMachine) GetCount() int {
	return gm.state.GetCount()
}

func (gm *GumballMachine) ReleaseBall() {
	fmt.Println("一个糖果从机器中出来...")
	if gm.count > 0 {
		gm.count--
	}
}

// 具体状态
type NoCoinState struct {
	machine *GumballMachine
}

func (s *NoCoinState) InsertCoin() error {
	fmt.Println("你投入了一枚硬币")
	s.machine.SetState(s.machine.hasCoin)
	return nil
}

func (s *NoCoinState) PressButton() error {
	fmt.Println("你需要先投入硬币")
	return fmt.Errorf("没有硬币")
}

func (s *NoCoinState) EjectCoin() error {
	fmt.Println("你没有投入硬币")
	return fmt.Errorf("没有硬币")
}

func (s *NoCoinState) Refill(count int) error {
	s.machine.count += count
	fmt.Printf("重新装填了 %d 个糖果\n", count)
	return nil
}

func (s *NoCoinState) GetCount() int {
	return s.machine.count
}

type HasCoinState struct {
	machine *GumballMachine
}

func (s *HasCoinState) InsertCoin() error {
	fmt.Println("你已经投入了一枚硬币")
	return fmt.Errorf("已有硬币")
}

func (s *HasCoinState) PressButton() error {
	fmt.Println("你按下了按钮...")
	s.machine.SetState(s.machine.sold)
	return nil
}

func (s *HasCoinState) EjectCoin() error {
	fmt.Println("硬币被退回")
	s.machine.SetState(s.machine.noCoin)
	return nil
}

func (s *HasCoinState) Refill(count int) error {
	return fmt.Errorf("机器正在使用中，不能重新装填")
}

func (s *HasCoinState) GetCount() int {
	return s.machine.count
}

type SoldState struct {
	machine *GumballMachine
}

func (s *SoldState) InsertCoin() error {
	fmt.Println("请等待，正在发放糖果")
	return fmt.Errorf("正在处理中")
}

func (s *SoldState) PressButton() error {
	fmt.Println("你已经按过了按钮")
	return fmt.Errorf("重复按按钮")
}

func (s *SoldState) EjectCoin() error {
	fmt.Println("已经按了按钮，不能退回硬币")
	return fmt.Errorf("不能退回硬币")
}

func (s *SoldState) Refill(count int) error {
	return fmt.Errorf("机器正在使用中，不能重新装填")
}

func (s *SoldState) GetCount() int {
	return s.machine.count
}

type SoldOutState struct {
	machine *GumballMachine
}

func (s *SoldOutState) InsertCoin() error {
	fmt.Println("机器已售空，硬币被退回")
	return fmt.Errorf("机器售空")
}

func (s *SoldOutState) PressButton() error {
	fmt.Println("机器已售空")
	return fmt.Errorf("机器售空")
}

func (s *SoldOutState) EjectCoin() error {
	fmt.Println("你没有投入硬币")
	return fmt.Errorf("没有硬币")
}

func (s *SoldOutState) Refill(count int) error {
	s.machine.count += count
	fmt.Printf("重新装填了 %d 个糖果\n", count)
	if s.machine.count > 0 {
		s.machine.SetState(s.machine.noCoin)
	}
	return nil
}

func (s *SoldOutState) GetCount() int {
	return s.machine.count
}

type WinnerState struct {
	machine *GumballMachine
}

func (s *WinnerState) InsertCoin() error {
	fmt.Println("请等待，正在发放糖果")
	return fmt.Errorf("正在处理中")
}

func (s *WinnerState) PressButton() error {
	fmt.Println("你已经按过了按钮")
	return fmt.Errorf("重复按按钮")
}

func (s *WinnerState) EjectCoin() error {
	fmt.Println("已经按了按钮，不能退回硬币")
	return fmt.Errorf("不能退回硬币")
}

func (s *WinnerState) Refill(count int) error {
	return fmt.Errorf("机器正在使用中，不能重新装填")
}

func (s *WinnerState) GetCount() int {
	return s.machine.count
}

// 使用示例
func ExampleState() {
	gumballMachine := NewGumballMachine(5)

	fmt.Println("初始状态:", gumballMachine.GetCount(), "个糖果")

	gumballMachine.InsertCoin()
	gumballMachine.PressButton()

	fmt.Println("剩余糖果:", gumballMachine.GetCount())

	gumballMachine.InsertCoin()
	gumballMachine.EjectCoin()
	gumballMachine.InsertCoin()
	gumballMachine.PressButton()

	fmt.Println("剩余糖果:", gumballMachine.GetCount())

	// 测试售空状态
	for i := 0; i < 3; i++ {
		gumballMachine.InsertCoin()
		gumballMachine.PressButton()
		fmt.Println("剩余糖果:", gumballMachine.GetCount())
	}

	// 测试重新装填
	gumballMachine.Refill(10)
	fmt.Println("重新装填后:", gumballMachine.GetCount(), "个糖果")
}
```

---

## ⚡ 并发模式

### 1. Worker Pool模式

创建固定数量的worker来处理任务队列。

```go
package concurrent

import (
	"fmt"
	"sync"
	"time"
)

type Task struct {
	ID    int
	Data  interface{}
	Process func(interface{}) error
}

type Worker struct {
	id         int
	taskQueue  chan Task
	workerPool chan chan Task
	quit       chan bool
}

func NewWorker(id int, workerPool chan chan Task) *Worker {
	return &Worker{
		id:         id,
		taskQueue:  make(chan Task),
		workerPool: workerPool,
		quit:       make(chan bool),
	}
}

func (w *Worker) Start() {
	go func() {
		for {
			// 将worker的任务队列放回worker池
			w.workerPool <- w.taskQueue

			select {
			case task := <-w.taskQueue:
				fmt.Printf("Worker %d 开始处理任务 %d\n", w.id, task.ID)
				if err := task.Process(task.Data); err != nil {
					fmt.Printf("Worker %d 处理任务 %d 失败: %v\n", w.id, task.ID, err)
				} else {
					fmt.Printf("Worker %d 完成任务 %d\n", w.id, task.ID)
				}

			case <-w.quit:
				fmt.Printf("Worker %d 停止\n", w.id)
				return
			}
		}
	}()
}

func (w *Worker) Stop() {
	go func() {
		w.quit <- true
	}()
}

type WorkerPool struct {
	workers       []*Worker
	workerPool    chan chan Task
	taskQueue     chan Task
	maxWorkers    int
	stop          chan bool
	wg            sync.WaitGroup
}

func NewWorkerPool(maxWorkers int) *WorkerPool {
	pool := &WorkerPool{
		workerPool: make(chan chan Task, maxWorkers),
		taskQueue:  make(chan Task, 100),
		maxWorkers: maxWorkers,
		stop:       make(chan bool),
	}

	// 创建worker
	for i := 0; i < maxWorkers; i++ {
		worker := NewWorker(i, pool.workerPool)
		pool.workers = append(pool.workers, worker)
		worker.Start()
	}

	// 启动任务分发器
	pool.startDispatcher()

	return pool
}

func (wp *WorkerPool) startDispatcher() {
	wp.wg.Add(1)
	go func() {
		defer wp.wg.Done()
		for {
			select {
			case task := <-wp.taskQueue:
				// 从worker池中获取可用的worker
				workerQueue := <-wp.workerPool
				workerQueue <- task

			case <-wp.stop:
				fmt.Println("任务分发器停止")
				return
			}
		}
	}()
}

func (wp *WorkerPool) AddTask(task Task) {
	wp.taskQueue <- task
}

func (wp *WorkerPool) Stop() {
	close(wp.stop)
	wp.wg.Wait()

	// 停止所有worker
	for _, worker := range wp.workers {
		worker.Stop()
	}
}

// 使用示例
func ExampleWorkerPool() {
	// 创建worker pool
	pool := NewWorkerPool(3)
	defer pool.Stop()

	// 添加任务
	for i := 0; i < 10; i++ {
		taskID := i
		task := Task{
			ID:   taskID,
			Data: fmt.Sprintf("任务数据 %d", taskID),
			Process: func(data interface{}) error {
				fmt.Printf("处理数据: %v\n", data)
				time.Sleep(time.Second) // 模拟处理时间
				return nil
			},
		}
		pool.AddTask(task)
	}

	// 等待任务完成
	time.Sleep(5 * time.Second)
}
```

### 2. Pipeline模式

将处理流程分解为多个阶段，每个阶段专注于特定的处理任务。

```go
package concurrent

import (
	"context"
	"fmt"
	"sync"
)

// Pipeline阶段
type Stage func(ctx context.Context, in <-chan interface{}) <-chan interface{}

// 创建阶段
func CreateStage(process func(interface{}) interface{}) Stage {
	return func(ctx context.Context, in <-chan interface{}) <-chan interface{} {
		out := make(chan interface{})

		go func() {
			defer close(out)

			for data := range in {
				select {
				case <-ctx.Done():
					return
				case out <- process(data):
				}
			}
		}()

		return out
	}
}

// 创建源阶段
func Source(ctx context.Context, data []interface{}) <-chan interface{} {
	out := make(chan interface{})

	go func() {
		defer close(out)

		for _, item := range data {
			select {
			case <-ctx.Done():
				return
			case out <- item:
			}
		}
	}()

	return out
}

// 创建汇阶段
func Sink(ctx context.Context, in <-chan interface{}, process func(interface{})) {
	go func() {
		for data := range in {
			select {
			case <-ctx.Done():
				return
			default:
				process(data)
			}
		}
	}()
}

// 构建pipeline
func BuildPipeline(ctx context.Context, source []interface{}, stages ...Stage) <-chan interface{} {
	var in <-chan interface{} = Source(ctx, source)

	for _, stage := range stages {
		in = stage(ctx, in)
	}

	return in
}

// 使用示例
func ExamplePipeline() {
	ctx := context.Background()

	// 示例：数据处理pipeline
	data := []interface{}{
		"  hello  ",
		"  world  ",
		"  golang  ",
	}

	// 定义处理阶段
	stages := []Stage{
		// 清理空格
		CreateStage(func(data interface{}) interface{} {
			if str, ok := data.(string); ok {
				return strings.TrimSpace(str)
			}
			return data
		}),

		// 转换为大写
		CreateStage(func(data interface{}) interface{} {
			if str, ok := data.(string); ok {
				return strings.ToUpper(str)
			}
			return data
		}),

		// 添加前缀
		CreateStage(func(data interface{}) interface{} {
			if str, ok := data.(string); ok {
				return "处理后的: " + str
			}
			return data
		}),
	}

	// 构建pipeline
	out := BuildPipeline(ctx, data, stages...)

	// 处理结果
	Sink(ctx, out, func(result interface{}) {
		fmt.Println(result)
	})

	// 等待处理完成
	time.Sleep(1 * time.Second)
}
```

### 3. Fan-out/Fan-in模式

将工作分发到多个worker，然后收集结果。

```go
package concurrent

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// Fan-out: 将数据分发到多个worker
func FanOut(ctx context.Context, in <-chan interface{}, workers int) []<-chan interface{} {
	out := make([]<-chan interface{}, workers)

	for i := 0; i < workers; i++ {
		out[i] = fanOutWorker(ctx, in, i)
	}

	return out
}

func fanOutWorker(ctx context.Context, in <-chan interface{}, workerID int) <-chan interface{} {
	out := make(chan interface{})

	go func() {
		defer close(out)

		for data := range in {
			select {
			case <-ctx.Done():
				return
			case out <- processWithWorker(data, workerID):
			}
		}
	}()

	return out
}

func processWithWorker(data interface{}, workerID int) interface{} {
	time.Sleep(time.Millisecond * 100) // 模拟处理时间
	return fmt.Sprintf("Worker %d 处理: %v", workerID, data)
}

// Fan-in: 合并多个channel
func FanIn(ctx context.Context, channels []<-chan interface{}) <-chan interface{} {
	out := make(chan interface{})

	var wg sync.WaitGroup
	wg.Add(len(channels))

	for _, ch := range channels {
		go func(c <-chan interface{}) {
			defer wg.Done()

			for data := range c {
				select {
				case <-ctx.Done():
					return
				case out <- data:
				}
			}
		}(ch)
	}

	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

// 使用示例
func ExampleFanOutFanIn() {
	ctx := context.Background()

	// 创建数据源
	data := make(chan interface{})
	go func() {
		defer close(data)
		for i := 0; i < 10; i++ {
			data <- fmt.Sprintf("任务 %d", i)
		}
	}()

	// Fan-out: 分发到3个worker
	workers := FanOut(ctx, data, 3)

	// Fan-in: 合并结果
	results := FanIn(ctx, workers)

	// 处理结果
	for result := range results {
		fmt.Println(result)
	}
}
```

---

## 🎯 设计模式最佳实践

### 1. 模式选择指南

#### 创建型模式选择
- **单例模式**: 需要全局唯一实例时使用
- **工厂模式**: 需要创建复杂对象或依赖注入时使用
- **建造者模式**: 需要创建复杂对象且有多种配置选项时使用
- **原型模式**: 需要快速创建相似对象时使用

#### 结构型模式选择
- **适配器模式**: 需要兼容不同接口时使用
- **装饰器模式**: 需要动态添加功能时使用
- **外观模式**: 需要简化复杂子系统时使用
- **代理模式**: 需要控制对象访问时使用
- **组合模式**: 需要表示树形结构时使用

#### 行为型模式选择
- **观察者模式**: 需要实现事件通知时使用
- **策略模式**: 需要在运行时切换算法时使用
- **命令模式**: 需要将操作封装为对象时使用
- **状态模式**: 需要根据状态改变行为时使用

#### 并发模式选择
- **Worker Pool**: 需要处理大量独立任务时使用
- **Pipeline**: 需要多阶段数据处理时使用
- **Fan-out/Fan-in**: 需要并行处理时使用

### 2. Go特有考虑

#### 接口设计
```go
// 好的接口设计
type Storage interface {
	Save(key string, value []byte) error
	Load(key string) ([]byte, error)
	Delete(key string) error
}

// 避免过大的接口
// 不要这样做
type BadStorage interface {
	Save(key string, value []byte) error
	Load(key string) ([]byte, error)
	Delete(key string) error
	Backup() error
	Restore() error
	Compress() error
	Encrypt() error
	// ... 更多方法
}
```

#### 错误处理
```go
// 自定义错误类型
type StorageError struct {
	Operation string
	Key       string
	Err       error
}

func (e *StorageError) Error() string {
	return fmt.Sprintf("storage %s failed for key %s: %v", e.Operation, e.Key, e.Err)
}

func (e *StorageError) Unwrap() error {
	return e.Err
}

// 错误包装
func (s *Storage) Save(key string, value []byte) error {
	if err := s.backend.Save(key, value); err != nil {
		return &StorageError{
			Operation: "save",
			Key:       key,
			Err:       err,
		}
	}
	return nil
}
```

#### 并发安全
```go
// 使用sync.Map而不是map+mutex的示例
type Cache struct {
	data sync.Map
}

func (c *Cache) Get(key string) (interface{}, bool) {
	return c.data.Load(key)
}

func (c *Cache) Set(key string, value interface{}) {
	c.data.Store(key, value)
}

func (c *Cache) Delete(key string) {
	c.data.Delete(key)
}
```

### 3. 性能考虑

#### 内存分配
```go
// 重用对象减少GC压力
type ObjectPool struct {
	pool chan *Object
}

func NewObjectPool(size int) *ObjectPool {
	return &ObjectPool{
		pool: make(chan *Object, size),
	}
}

func (p *ObjectPool) Get() *Object {
	select {
	case obj := <-p.pool:
		return obj
	default:
		return &Object{} // 如果池为空，创建新对象
	}
}

func (p *ObjectPool) Put(obj *Object) {
	select {
	case p.pool <- obj:
	default:
		// 池满了，丢弃对象
	}
}
```

#### 批量处理
```go
// 批量处理减少锁竞争
type BatchProcessor struct {
	buffer    []interface{}
	batchSize int
	processor func([]interface{})
	mu        sync.Mutex
}

func (bp *BatchProcessor) Add(item interface{}) {
	bp.mu.Lock()
	defer bp.mu.Unlock()

	bp.buffer = append(bp.buffer, item)

	if len(bp.buffer) >= bp.batchSize {
		bp.flush()
	}
}

func (bp *BatchProcessor) flush() {
	if len(bp.buffer) == 0 {
		return
	}

	batch := make([]interface{}, len(bp.buffer))
	copy(batch, bp.buffer)

	go bp.processor(batch)

	bp.buffer = bp.buffer[:0]
}
```

---

## 📋 实战项目

### 1. 设计模式在Web框架中的应用

```go
package webframework

import (
	"context"
	"net/http"
)

// 中间件模式
type Middleware func(http.Handler) http.Handler

type Router struct {
	middlewares []Middleware
	routes      map[string]map[string]http.Handler
}

func NewRouter() *Router {
	return &Router{
		routes: make(map[string]map[string]http.Handler),
	}
}

func (r *Router) Use(middleware Middleware) {
	r.middlewares = append(r.middlewares, middleware)
}

func (r *Router) Handle(method, path string, handler http.Handler) {
	if _, ok := r.routes[path]; !ok {
		r.routes[path] = make(map[string]http.Handler)
	}
	r.routes[path][method] = handler
}

func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	// 查找路由
	handlers, ok := r.routes[req.URL.Path]
	if !ok {
		http.NotFound(w, req)
		return
	}

	handler, ok := handlers[req.Method]
	if !ok {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// 应用中间件
	for _, middleware := range r.middlewares {
		handler = middleware(handler)
	}

	handler.ServeHTTP(w, req)
}

// 常用中间件
func LoggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		next.ServeHTTP(w, r)

		fmt.Printf("%s %s %v\n", r.Method, r.URL.Path, time.Since(start))
	})
}

func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		token := r.Header.Get("Authorization")
		if token == "" {
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		// 验证token...
		next.ServeHTTP(w, r)
	})
}

// 使用示例
func ExampleWebFramework() {
	router := NewRouter()

	// 使用中间件
	router.Use(LoggingMiddleware)
	router.Use(AuthMiddleware)

	// 添加路由
	router.Handle("GET", "/", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Hello, World!"))
	}))

	// 启动服务器
	http.ListenAndServe(":8080", router)
}
```

### 2. 设计模式在微服务中的应用

```go
package microservices

import (
	"context"
	"fmt"
	"time"
)

// 服务发现模式
type ServiceDiscovery interface {
	Register(service *ServiceInstance) error
	Deregister(serviceID string) error
	Discover(serviceName string) ([]*ServiceInstance, error)
	Watch(serviceName string) (<-chan []*ServiceInstance, error)
}

type ServiceInstance struct {
	ID      string
	Name    string
	Address string
	Port    int
	Metadata map[string]string
}

// 负载均衡模式
type LoadBalancer interface {
	Next(services []*ServiceInstance) (*ServiceInstance, error)
}

type RoundRobinLoadBalancer struct {
	counter int
}

func (lb *RoundRobinLoadBalancer) Next(services []*ServiceInstance) (*ServiceInstance, error) {
	if len(services) == 0 {
		return nil, fmt.Errorf("no available services")
	}

	service := services[lb.counter%len(services)]
	lb.counter++

	return service, nil
}

// 断路器模式
type CircuitBreaker struct {
	maxFailures  int
	resetTimeout time.Duration

	failures    int
	lastFailure time.Time
	state       string // "closed", "open", "half-open"
}

func (cb *CircuitBreaker) Call(ctx context.Context, fn func() error) error {
	if cb.state == "open" {
		if time.Since(cb.lastFailure) < cb.resetTimeout {
			return fmt.Errorf("circuit breaker is open")
		}
		cb.state = "half-open"
	}

	err := fn()
	if err != nil {
		cb.failures++
		cb.lastFailure = time.Now()

		if cb.failures >= cb.maxFailures {
			cb.state = "open"
		}
		return err
	}

	cb.failures = 0
	cb.state = "closed"
	return nil
}

// 使用示例
func ExampleMicroservices() {
	// 服务发现
	var discovery ServiceDiscovery = &ConsulDiscovery{}

	// 注册服务
	service := &ServiceInstance{
		ID:      "user-service-1",
		Name:    "user-service",
		Address: "localhost",
		Port:    8080,
	}

	discovery.Register(service)

	// 服务发现
	instances, _ := discovery.Discover("user-service")

	// 负载均衡
	var lb LoadBalancer = &RoundRobinLoadBalancer{}
	target, _ := lb.Next(instances)

	// 断路器
	cb := &CircuitBreaker{
		maxFailures:  5,
		resetTimeout: 30 * time.Second,
	}

	err := cb.Call(context.Background(), func() error {
		// 调用远程服务
		return callRemoteService(target)
	})

	if err != nil {
		fmt.Printf("服务调用失败: %v\n", err)
	}
}
```

---

## 🎯 总结

设计模式是软件开发中宝贵的经验总结，在Go语言中应用设计模式时需要考虑：

### 关键要点
1. **简化优先**: Go语言强调简洁，避免过度设计
2. **接口驱动**: 充分利用Go的接口特性
3. **组合优于继承**: 使用结构体嵌入实现代码复用
4. **并发友好**: 利用Go的并发特性实现高效模式
5. **错误处理**: 遵循Go的错误处理约定

### 最佳实践
- 选择合适的设计模式解决特定问题
- 不要为了使用模式而使用模式
- 保持代码的可读性和可维护性
- 考虑性能和内存使用
- 编写测试验证模式实现

### 持续学习
- 阅读优秀开源项目的源代码
- 参与技术社区讨论
- 实践和应用设计模式
- 分享经验和见解

通过掌握这些设计模式，你将能够构建更加优雅、可维护、可扩展的Go应用程序。

---

*最后更新: 2025年9月*