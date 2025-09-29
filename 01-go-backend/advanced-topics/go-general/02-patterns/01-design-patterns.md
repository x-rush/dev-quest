# Go设计模式实战

## 目录
- [设计模式概述](#设计模式概述)
- [创建型模式](#创建型模式)
- [结构型模式](#结构型模式)
- [行为型模式](#行为型模式)
- [并发模式](#并发模式)
- [函数式模式](#函数式模式)
- [架构模式](#架构模式)
- [设计原则](#设计原则)
- [最佳实践](#最佳实践)

## 设计模式概述

### 什么是设计模式
设计模式是软件设计中常见问题的典型解决方案。它们是经过反复验证的、可重用的设计方案，能够帮助开发者编写更加灵活、可维护和可扩展的代码。

### 设计模式的分类
1. **创建型模式**：关注对象的创建过程
2. **结构型模式**：关注对象的组合
3. **行为型模式**：关注对象间的交互
4. **并发模式**：专门针对并发编程的模式
5. **函数式模式**：利用Go的函数特性
6. **架构模式**：更高层次的系统组织方式

### 设计模式在Go中的特点
- **简洁性**：Go语言的简洁性使得模式实现更加直接
- **接口优先**：充分利用Go的接口特性
- **组合优于继承**：使用组合而非继承
- **并发友好**：原生支持并发编程

## 创建型模式

### 1. 单例模式 (Singleton)

确保一个类只有一个实例，并提供一个全局访问点。

```go
// 懒汉式单例
type Singleton struct {
    data string
}

var (
    instance *Singleton
    once     sync.Once
)

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{data: "initial data"}
    })
    return instance
}

func (s *Singleton) GetData() string {
    return s.data
}

func (s *Singleton) SetData(data string) {
    s.data = data
}
```

### 2. 工厂模式 (Factory)

定义一个创建对象的接口，让子类决定实例化哪一个类。

```go
// 产品接口
type Product interface {
    Use() string
}

// 具体产品A
type ConcreteProductA struct{}

func (p *ConcreteProductA) Use() string {
    return "Using Product A"
}

// 具体产品B
type ConcreteProductB struct{}

func (p *ConcreteProductB) Use() string {
    return "Using Product B"
}

// 工厂接口
type Factory interface {
    CreateProduct() Product
}

// 具体工厂A
type ConcreteFactoryA struct{}

func (f *ConcreteFactoryA) CreateProduct() Product {
    return &ConcreteProductA{}
}

// 具体工厂B
type ConcreteFactoryB struct{}

func (f *ConcreteFactoryB) CreateProduct() Product {
    return &ConcreteProductB{}
}

// 使用示例
func main() {
    var factory Factory

    factory = &ConcreteFactoryA{}
    productA := factory.CreateProduct()
    fmt.Println(productA.Use())

    factory = &ConcreteFactoryB{}
    productB := factory.CreateProduct()
    fmt.Println(productB.Use())
}
```

### 3. 建造者模式 (Builder)

将一个复杂对象的构建与其表示分离，使得同样的构建过程可以创建不同的表示。

```go
// 产品
type Computer struct {
    CPU     string
    RAM     string
    Storage string
    GPU     string
}

// 建造者接口
type ComputerBuilder interface {
    SetCPU(string) ComputerBuilder
    SetRAM(string) ComputerBuilder
    SetStorage(string) ComputerBuilder
    SetGPU(string) ComputerBuilder
    Build() *Computer
}

// 具体建造者
type GamingComputerBuilder struct {
    computer *Computer
}

func NewGamingComputerBuilder() *GamingComputerBuilder {
    return &GamingComputerBuilder{
        computer: &Computer{},
    }
}

func (b *GamingComputerBuilder) SetCPU(cpu string) ComputerBuilder {
    b.computer.CPU = cpu
    return b
}

func (b *GamingComputerBuilder) SetRAM(ram string) ComputerBuilder {
    b.computer.RAM = ram
    return b
}

func (b *GamingComputerBuilder) SetStorage(storage string) ComputerBuilder {
    b.computer.Storage = storage
    return b
}

func (b *GamingComputerBuilder) SetGPU(gpu string) ComputerBuilder {
    b.computer.GPU = gpu
    return b
}

func (b *GamingComputerBuilder) Build() *Computer {
    return b.computer
}

// 指导者
type ComputerDirector struct {
    builder ComputerBuilder
}

func NewComputerDirector(builder ComputerBuilder) *ComputerDirector {
    return &ComputerDirector{builder: builder}
}

func (d *ComputerDirector) ConstructGamingComputer() *Computer {
    return d.builder.
        SetCPU("Intel Core i9").
        SetRAM("32GB DDR4").
        SetStorage("1TB NVMe SSD").
        SetGPU("NVIDIA RTX 3080").
        Build()
}

// 使用示例
func main() {
    builder := NewGamingComputerBuilder()
    director := NewComputerDirector(builder)

    gamingComputer := director.ConstructGamingComputer()
    fmt.Printf("Gaming Computer: %+v\n", gamingComputer)
}
```

### 4. 原型模式 (Prototype)

用原型实例指定创建对象的种类，并通过拷贝这些原型创建新的对象。

```go
// 原型接口
type Prototype interface {
    Clone() Prototype
    GetInfo() string
}

// 具体原型
type Document struct {
    title    string
    content  string
    author   string
    metadata map[string]string
}

func (d *Document) Clone() Prototype {
    newDoc := &Document{
        title:   d.title,
        content: d.content,
        author:  d.author,
    }

    // 深拷贝metadata
    newDoc.metadata = make(map[string]string)
    for k, v := range d.metadata {
        newDoc.metadata[k] = v
    }

    return newDoc
}

func (d *Document) GetInfo() string {
    return fmt.Sprintf("Document: %s by %s", d.title, d.author)
}

// 原型管理器
type PrototypeManager struct {
    prototypes map[string]Prototype
}

func NewPrototypeManager() *PrototypeManager {
    return &PrototypeManager{
        prototypes: make(map[string]Prototype),
    }
}

func (pm *PrototypeManager) Register(name string, prototype Prototype) {
    pm.prototypes[name] = prototype
}

func (pm *PrototypeManager) Create(name string) (Prototype, error) {
    prototype, exists := pm.prototypes[name]
    if !exists {
        return nil, fmt.Errorf("prototype %s not found", name)
    }
    return prototype.Clone(), nil
}

// 使用示例
func main() {
    manager := NewPrototypeManager()

    // 注册原型
    report := &Document{
        title:   "Monthly Report",
        author:  "John Doe",
        content: "This is a monthly report template",
        metadata: map[string]string{
            "type":     "report",
            "period":   "monthly",
            "version":  "1.0",
        },
    }
    manager.Register("report", report)

    // 克隆原型
    newReport, _ := manager.Create("report")
    newDoc := newReport.(*Document)
    newDoc.title = "Q1 2024 Report"
    newDoc.content = "Q1 2024 performance data"

    fmt.Println(newDoc.GetInfo())
    fmt.Printf("Metadata: %+v\n", newDoc.metadata)
}
```

## 结构型模式

### 1. 适配器模式 (Adapter)

将一个类的接口转换成客户端期望的另一个接口。

```go
// 目标接口
type Target interface {
    Request() string
}

// 被适配者
type Adaptee struct{}

func (a *Adaptee) SpecificRequest() string {
    return "Specific request from Adaptee"
}

// 适配器
type Adapter struct {
    adaptee *Adaptee
}

func NewAdapter(adaptee *Adaptee) *Adapter {
    return &Adapter{adaptee: adaptee}
}

func (a *Adapter) Request() string {
    return fmt.Sprintf("Adapter: %s", a.adaptee.SpecificRequest())
}

// 使用示例
func main() {
    adaptee := &Adaptee{}
    adapter := NewAdapter(adaptee)

    fmt.Println(adapter.Request())
}
```

### 2. 桥接模式 (Bridge)

将抽象部分与实现部分分离，使它们都可以独立变化。

```go
// 实现接口
type DrawingAPI interface {
    DrawCircle(x, y, radius float64)
    DrawRectangle(x, y, width, height float64)
}

// 具体实现1
type VectorDrawing struct{}

func (v *VectorDrawing) DrawCircle(x, y, radius float64) {
    fmt.Printf("Vector circle at (%.1f, %.1f) with radius %.1f\n", x, y, radius)
}

func (v *VectorDrawing) DrawRectangle(x, y, width, height float64) {
    fmt.Printf("Vector rectangle at (%.1f, %.1f) size %.1fx%.1f\n", x, y, width, height)
}

// 具体实现2
type RasterDrawing struct{}

func (r *RasterDrawing) DrawCircle(x, y, radius float64) {
    fmt.Printf("Raster circle at (%.1f, %.1f) with radius %.1f\n", x, y, radius)
}

func (r *RasterDrawing) DrawRectangle(x, y, width, height float64) {
    fmt.Printf("Raster rectangle at (%.1f, %.1f) size %.1fx%.1f\n", x, y, width, height)
}

// 抽象形状
type Shape struct {
    api DrawingAPI
}

func (s *Shape) SetAPI(api DrawingAPI) {
    s.api = api
}

// 具体形状
type Circle struct {
    Shape
    x, y, radius float64
}

func NewCircle(x, y, radius float64, api DrawingAPI) *Circle {
    return &Circle{
        Shape: Shape{api: api},
        x:     x,
        y:     y,
        radius: radius,
    }
}

func (c *Circle) Draw() {
    c.api.DrawCircle(c.x, c.y, c.radius)
}

func (c *Circle) Resize(factor float64) {
    c.radius *= factor
}

type Rectangle struct {
    Shape
    x, y, width, height float64
}

func NewRectangle(x, y, width, height float64, api DrawingAPI) *Rectangle {
    return &Rectangle{
        Shape:  Shape{api: api},
        x:      x,
        y:      y,
        width:  width,
        height: height,
    }
}

func (r *Rectangle) Draw() {
    r.api.DrawRectangle(r.x, r.y, r.width, r.height)
}

func (r *Rectangle) Resize(factor float64) {
    r.width *= factor
    r.height *= factor
}

// 使用示例
func main() {
    vectorAPI := &VectorDrawing{}
    rasterAPI := &RasterDrawing{}

    circle := NewCircle(10, 10, 5, vectorAPI)
    circle.Draw()

    rectangle := NewRectangle(20, 20, 15, 10, rasterAPI)
    rectangle.Draw()

    // 切换API
    circle.SetAPI(rasterAPI)
    circle.Draw()
}
```

### 3. 组合模式 (Composite)

将对象组合成树形结构以表示"部分-整体"的层次结构。

```go
// 组件接口
type Component interface {
    Add(component Component)
    Remove(component Component)
    GetChild(index int) Component
    Operation() string
}

// 叶子节点
type Leaf struct {
    name string
}

func (l *Leaf) Add(component Component) {
    // 叶子节点不能添加子节点
}

func (l *Leaf) Remove(component Component) {
    // 叶子节点不能移除子节点
}

func (l *Leaf) GetChild(index int) Component {
    return nil // 叶子节点没有子节点
}

func (l *Leaf) Operation() string {
    return fmt.Sprintf("Leaf: %s", l.name)
}

// 组合节点
type Composite struct {
    name     string
    children []Component
}

func (c *Composite) Add(component Component) {
    c.children = append(c.children, component)
}

func (c *Composite) Remove(component Component) {
    for i, child := range c.children {
        if child == component {
            c.children = append(c.children[:i], c.children[i+1:]...)
            break
        }
    }
}

func (c *Composite) GetChild(index int) Component {
    if index >= 0 && index < len(c.children) {
        return c.children[index]
    }
    return nil
}

func (c *Composite) Operation() string {
    var result strings.Builder
    result.WriteString(fmt.Sprintf("Composite: %s\n", c.name))

    for _, child := range c.children {
        childResult := child.Operation()
        lines := strings.Split(childResult, "\n")
        for _, line := range lines {
            if line != "" {
                result.WriteString(fmt.Sprintf("  %s\n", line))
            }
        }
    }

    return result.String()
}

// 使用示例
func main() {
    // 创建文件系统
    root := &Composite{name: "root"}

    documents := &Composite{name: "documents"}
    images := &Composite{name: "images"}

    // 添加目录
    root.Add(documents)
    root.Add(images)

    // 添加文件
    documents.Add(&Leaf{name: "report.pdf"})
    documents.Add(&Leaf{name: "presentation.pptx"})

    images.Add(&Leaf{name: "photo1.jpg"})
    images.Add(&Leaf{name: "photo2.png"})

    // 显示文件系统
    fmt.Println(root.Operation())
}
```

### 4. 装饰器模式 (Decorator)

动态地给一个对象添加一些额外的职责。

```go
// 组件接口
type Beverage interface {
    Cost() float64
    Description() string
}

// 具体组件
type Espresso struct{}

func (e *Espresso) Cost() float64 {
    return 1.99
}

func (e *Espresso) Description() string {
    return "Espresso"
}

// 装饰器
type CondimentDecorator struct {
    beverage Beverage
}

func (c *CondimentDecorator) Cost() float64 {
    return c.beverage.Cost()
}

func (c *CondimentDecorator) Description() string {
    return c.beverage.Description()
}

// 具体装饰器
type Milk struct {
    CondimentDecorator
}

func NewMilk(beverage Beverage) *Milk {
    return &Milk{CondimentDecorator: CondimentDecorator{beverage: beverage}}
}

func (m *Milk) Cost() float64 {
    return m.beverage.Cost() + 0.10
}

func (m *Milk) Description() string {
    return fmt.Sprintf("%s, Milk", m.beverage.Description())
}

type Mocha struct {
    CondimentDecorator
}

func NewMocha(beverage Beverage) *Mocha {
    return &Mocha{CondimentDecorator: CondimentDecorator{beverage: beverage}}
}

func (m *Mocha) Cost() float64 {
    return m.beverage.Cost() + 0.20
}

func (m *Mocha) Description() string {
    return fmt.Sprintf("%s, Mocha", m.beverage.Description())
}

type Whip struct {
    CondimentDecorator
}

func NewWhip(beverage Beverage) *Whip {
    return &Whip{CondimentDecorator: CondimentDecorator{beverage: beverage}}
}

func (w *Whip) Cost() float64 {
    return w.beverage.Cost() + 0.15
}

func (w *Whip) Description() string {
    return fmt.Sprintf("%s, Whip", w.beverage.Description())
}

// 使用示例
func main() {
    // 订一杯Espresso
    beverage := &Espresso{}
    fmt.Printf("%s: $%.2f\n", beverage.Description(), beverage.Cost())

    // 加牛奶
    beverage = NewMilk(beverage)
    fmt.Printf("%s: $%.2f\n", beverage.Description(), beverage.Cost())

    // 加Mocha
    beverage = NewMocha(beverage)
    fmt.Printf("%s: $%.2f\n", beverage.Description(), beverage.Cost())

    // 加奶泡
    beverage = NewWhip(beverage)
    fmt.Printf("%s: $%.2f\n", beverage.Description(), beverage.Cost())
}
```

### 5. 外观模式 (Facade)

为子系统中的一组接口提供一个一致的界面。

```go
// 子系统A
class CPU {
    public void freeze() { System.out.println("CPU frozen"); }
    public void jump(long position) { System.out.println("CPU jump to " + position); }
    public void execute() { System.out.println("CPU executing"); }
}

// 子系统B
class Memory {
    public void load(long position, byte[] data) {
        System.out.println("Memory load at " + position);
    }
}

// 子系统C
class HardDrive {
    public byte[] read(long lba, int size) {
        System.out.println("HardDrive read at " + lba);
        return new byte[size];
    }
}

// 外观
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
        System.out.println("Computer starting...");
        cpu.freeze();
        memory.load(0, hardDrive.read(0, 1024));
        cpu.jump(0);
        cpu.execute();
        System.out.println("Computer started");
    }
}

// 使用示例
public class Main {
    public static void main(String[] args) {
        ComputerFacade computer = new ComputerFacade();
        computer.start();
    }
}
```

### 6. 享元模式 (Flyweight)

运用共享技术来有效地支持大量细粒度的对象。

```go
// 享元接口
type Flyweight interface {
    Operation(extrinsicState string)
}

// 具体享元
type ConcreteFlyweight struct {
    intrinsicState string
}

func (f *ConcreteFlyweight) Operation(extrinsicState string) {
    fmt.Printf("Intrinsic: %s, Extrinsic: %s\n", f.intrinsicState, extrinsicState)
}

// 享元工厂
type FlyweightFactory struct {
    flyweights map[string]Flyweight
}

func NewFlyweightFactory() *FlyweightFactory {
    return &FlyweightFactory{
        flyweights: make(map[string]Flyweight),
    }
}

func (f *FlyweightFactory) GetFlyweight(key string) Flyweight {
    if flyweight, exists := f.flyweights[key]; exists {
        return flyweight
    }

    flyweight := &ConcreteFlyweight{intrinsicState: key}
    f.flyweights[key] = flyweight
    return flyweight
}

func (f *FlyweightFactory) GetFlyweightCount() int {
    return len(f.flyweights)
}

// 使用示例
func main() {
    factory := NewFlyweightFactory()

    // 获取享元对象
    flyweight1 := factory.GetFlyweight("A")
    flyweight1.Operation("State1")

    flyweight2 := factory.GetFlyweight("A")
    flyweight2.Operation("State2")

    flyweight3 := factory.GetFlyweight("B")
    flyweight3.Operation("State3")

    fmt.Printf("Total flyweights created: %d\n", factory.GetFlyweightCount())
}
```

### 7. 代理模式 (Proxy)

为其他对象提供一种代理以控制对这个对象的访问。

```go
// 主题接口
type Subject interface {
    Request() string
}

// 真实主题
type RealSubject struct{}

func (r *RealSubject) Request() string {
    return "RealSubject: Handling request"
}

// 代理
type Proxy struct {
    realSubject *RealSubject
    accessGranted bool
}

func NewProxy(accessGranted bool) *Proxy {
    return &Proxy{
        accessGranted: accessGranted,
    }
}

func (p *Proxy) Request() string {
    if !p.accessGranted {
        return "Proxy: Access denied"
    }

    if p.realSubject == nil {
        p.realSubject = &RealSubject{}
    }

    return "Proxy: " + p.realSubject.Request()
}

// 使用示例
func main() {
    // 无权限访问
    proxy1 := NewProxy(false)
    fmt.Println(proxy1.Request())

    // 有权限访问
    proxy2 := NewProxy(true)
    fmt.Println(proxy2.Request())
}
```

## 行为型模式

### 1. 责任链模式 (Chain of Responsibility)

使多个对象都有机会处理请求，从而避免请求的发送者和接收者之间的耦合关系。

```go
// 处理者接口
type Handler interface {
    SetNext(handler Handler) Handler
    Handle(request string) string
}

// 抽象处理者
type AbstractHandler struct {
    next Handler
}

func (a *AbstractHandler) SetNext(handler Handler) Handler {
    a.next = handler
    return handler
}

func (a *AbstractHandler) Handle(request string) string {
    if a.next != nil {
        return a.next.Handle(request)
    }
    return ""
}

// 具体处理者1
class MonkeyHandler extends AbstractHandler {
    @Override
    public String handle(String request) {
        if (request.equals("Banana")) {
            return "Monkey: I'll eat the " + request + ".\n";
        }
        return super.handle(request);
    }
}

// 具体处理者2
class SquirrelHandler extends AbstractHandler {
    @Override
    public String handle(String request) {
        if (request.equals("Nut")) {
            return "Squirrel: I'll eat the " + request + ".\n";
        }
        return super.handle(request);
    }
}

// 具体处理者3
class DogHandler extends AbstractHandler {
    @Override
    public String handle(String request) {
        if (request.equals("MeatBall")) {
            return "Dog: I'll eat the " + request + ".\n";
        }
        return super.handle(request);
    }
}

// 使用示例
public class Main {
    private static AbstractHandler getChainOfHandlers() {
        AbstractHandler monkey = new MonkeyHandler();
        AbstractHandler squirrel = new SquirrelHandler();
        AbstractHandler dog = new DogHandler();

        monkey.setNext(squirrel).setNext(dog);
        return monkey;
    }

    public static void main(String[] args) {
        AbstractHandler chain = getChainOfHandlers();

        System.out.println(chain.handle("Nut")); // Squirrel handles
        System.out.println(chain.handle("Banana")); // Monkey handles
        System.out.println(chain.handle("Coffee")); // No handler
    }
}
```

### 2. 命令模式 (Command)

将一个请求封装为一个对象，从而使你可用不同的请求对客户进行参数化。

```go
// 命令接口
type Command interface {
    Execute()
    Undo()
}

// 接收者
class Light {
    public void turnOn() {
        System.out.println("Light is on");
    }

    public void turnOff() {
        System.out.println("Light is off");
    }
}

// 具体命令
class LightOnCommand implements Command {
    private Light light;

    public LightOnCommand(Light light) {
        this.light = light;
    }

    public void execute() {
        light.turnOn();
    }

    public void undo() {
        light.turnOff();
    }
}

class LightOffCommand implements Command {
    private Light light;

    public LightOffCommand(Light light) {
        this.light = light;
    }

    public void execute() {
        light.turnOff();
    }

    public void undo() {
        light.turnOn();
    }
}

// 调用者
class RemoteControl {
    private Command command;
    private Command lastCommand;
    private Stack<Command> commandHistory = new Stack<>();

    public void setCommand(Command command) {
        this.command = command;
    }

    public void pressButton() {
        command.execute();
        commandHistory.push(command);
        lastCommand = command;
    }

    public void pressUndo() {
        if (!commandHistory.isEmpty()) {
            Command cmd = commandHistory.pop();
            cmd.undo();
        }
    }
}

// 使用示例
public class Main {
    public static void main(String[] args) {
        Light light = new Light();
        Command lightOn = new LightOnCommand(light);
        Command lightOff = new LightOffCommand(light);

        RemoteControl remote = new RemoteControl();

        remote.setCommand(lightOn);
        remote.pressButton();

        remote.setCommand(lightOff);
        remote.pressButton();

        remote.pressUndo(); // Undo last command
    }
}
```

### 3. 解释器模式 (Interpreter)

给定一种语言，定义它的文法的一种表示，并定义一个解释器。

```go
// 表达式接口
interface Expression {
    boolean interpret(String context);
}

// 终结符表达式
class TerminalExpression implements Expression {
    private String data;

    public TerminalExpression(String data) {
        this.data = data;
    }

    public boolean interpret(String context) {
        return context.contains(data);
    }
}

// 非终结符表达式
class OrExpression implements Expression {
    private Expression expr1;
    private Expression expr2;

    public OrExpression(Expression expr1, Expression expr2) {
        this.expr1 = expr1;
        this.expr2 = expr2;
    }

    public boolean interpret(String context) {
        return expr1.interpret(context) || expr2.interpret(context);
    }
}

class AndExpression implements Expression {
    private Expression expr1;
    private Expression expr2;

    public AndExpression(Expression expr1, Expression expr2) {
        this.expr1 = expr1;
        this.expr2 = expr2;
    }

    public boolean interpret(String context) {
        return expr1.interpret(context) && expr2.interpret(context);
    }
}

// 使用示例
public class Main {
    public static Expression getMaleExpression() {
        Expression robert = new TerminalExpression("Robert");
        Expression john = new TerminalExpression("John");
        return new OrExpression(robert, john);
    }

    public static Expression getMarriedWomanExpression() {
        Expression julie = new TerminalExpression("Julie");
        Expression married = new TerminalExpression("Married");
        return new AndExpression(julie, married);
    }

    public static void main(String[] args) {
        Expression isMale = getMaleExpression();
        Expression isMarriedWoman = getMarriedWomanExpression();

        System.out.println("John is male? " + isMale.interpret("John"));
        System.out.println("Julie is a married woman? " + isMarriedWoman.interpret("Married Julie"));
    }
}
```

### 4. 迭代器模式 (Iterator)

提供一种方法顺序访问一个聚合对象中各个元素，而又不需暴露该对象的内部表示。

```go
// 迭代器接口
type Iterator interface {
    HasNext() bool
    Next() interface{}
}

// 聚合接口
type Aggregate interface {
    CreateIterator() Iterator
}

// 具体聚合
type NameRepository struct {
    names []string
}

func NewNameRepository() *NameRepository {
    return &NameRepository{
        names: []string{"Robert", "John", "Julie", "Lora"},
    }
}

func (n *NameRepository) CreateIterator() Iterator {
    return &NameIterator{
        names:  n.names,
        index:  0,
    }
}

// 具体迭代器
type NameIterator struct {
    names  []string
    index  int
}

func (n *NameIterator) HasNext() bool {
    return n.index < len(n.names)
}

func (n *NameIterator) Next() interface{} {
    if n.HasNext() {
        name := n.names[n.index]
        n.index++
        return name
    }
    return nil
}

// 使用示例
func main() {
    namesRepository := NewNameRepository()

    for iter := namesRepository.CreateIterator(); iter.HasNext(); {
        name := iter.Next()
        fmt.Println(name)
    }
}
```

### 5. 中介者模式 (Mediator)

用一个中介对象来封装一系列的对象交互。

```go
// 中介者接口
type Mediator interface {
    SendMessage(message string, colleague Colleague)
    AddColleague(colleague Colleague)
}

// 同事接口
type Colleague interface {
    ReceiveMessage(message string)
    SendMessage(message string)
}

// 具体中介者
class ChatMediator implements Mediator {
    private List<Colleague> colleagues;

    public ChatMediator() {
        this.colleagues = new ArrayList<>();
    }

    public void addColleague(Colleague colleague) {
        colleagues.add(colleague);
    }

    public void sendMessage(String message, Colleague sender) {
        for (Colleague colleague : colleagues) {
            if (colleague != sender) {
                colleague.receiveMessage(message);
            }
        }
    }
}

// 具体同事
class User implements Colleague {
    private String name;
    private Mediator mediator;

    public User(String name, Mediator mediator) {
        this.name = name;
        this.mediator = mediator;
        mediator.addColleague(this);
    }

    public void receiveMessage(String message) {
        System.out.println(name + " received: " + message);
    }

    public void sendMessage(String message) {
        System.out.println(name + " sending: " + message);
        mediator.sendMessage(message, this);
    }
}

// 使用示例
public class Main {
    public static void main(String[] args) {
        Mediator mediator = new ChatMediator();

        User john = new User("John", mediator);
        User jane = new User("Jane", mediator);
        User bob = new User("Bob", mediator);

        john.sendMessage("Hello everyone!");
        jane.sendMessage("Hi John!");
    }
}
```

### 6. 备忘录模式 (Memento)

在不破坏封装性的前提下，捕获一个对象的内部状态，并在该对象之外保存这个状态。

```go
// 备忘录
class Memento {
    private String state;

    public Memento(String state) {
        this.state = state;
    }

    public String getState() {
        return state;
    }
}

// 原发器
class Originator {
    private String state;

    public void setState(String state) {
        this.state = state;
        System.out.println("State set to: " + state);
    }

    public String getState() {
        return state;
    }

    public Memento saveStateToMemento() {
        return new Memento(state);
    }

    public void getStateFromMemento(Memento memento) {
        state = memento.getState();
        System.out.println("State restored from memento: " + state);
    }
}

// 负责人
class CareTaker {
    private List<Memento> mementoList = new ArrayList<>();

    public void add(Memento state) {
        mementoList.add(state);
    }

    public Memento get(int index) {
        return mementoList.get(index);
    }
}

// 使用示例
public class Main {
    public static void main(String[] args) {
        Originator originator = new Originator();
        CareTaker careTaker = new CareTaker();

        originator.setState("State #1");
        originator.setState("State #2");
        careTaker.add(originator.saveStateToMemento());

        originator.setState("State #3");
        careTaker.add(originator.saveStateToMemento());

        originator.setState("State #4");
        System.out.println("Current State: " + originator.getState());

        originator.getStateFromMemento(careTaker.get(0));
        System.out.println("First saved State: " + originator.getState());

        originator.getStateFromMemento(careTaker.get(1));
        System.out.println("Second saved State: " + originator.getState());
    }
}
```

### 7. 观察者模式 (Observer)

定义对象间的一种一对多的依赖关系，当一个对象的状态发生改变时，所有依赖于它的对象都得到通知并被自动更新。

```go
// 观察者接口
type Observer interface {
    Update(temperature, humidity, pressure float64)
}

// 主题接口
type Subject interface {
    RegisterObserver(observer Observer)
    RemoveObserver(observer Observer)
    NotifyObservers()
}

// 具体主题
type WeatherData struct {
    observers   []Observer
    temperature float64
    humidity    float64
    pressure    float64
}

func NewWeatherData() *WeatherData {
    return &WeatherData{
        observers: make([]Observer, 0),
    }
}

func (w *WeatherData) RegisterObserver(observer Observer) {
    w.observers = append(w.observers, observer)
}

func (w *WeatherData) RemoveObserver(observer Observer) {
    for i, obs := range w.observers {
        if obs == observer {
            w.observers = append(w.observers[:i], w.observers[i+1:]...)
            break
        }
    }
}

func (w *WeatherData) NotifyObservers() {
    for _, observer := range w.observers {
        observer.Update(w.temperature, w.humidity, w.pressure)
    }
}

func (w *WeatherData) SetMeasurements(temperature, humidity, pressure float64) {
    w.temperature = temperature
    w.humidity = humidity
    w.pressure = pressure
    w.NotifyObservers()
}

// 具体观察者
type CurrentConditionsDisplay struct {
    temperature float64
    humidity    float64
}

func NewCurrentConditionsDisplay(weatherData *WeatherData) *CurrentConditionsDisplay {
    display := &CurrentConditionsDisplay{}
    weatherData.RegisterObserver(display)
    return display
}

func (d *CurrentConditionsDisplay) Update(temperature, humidity, pressure float64) {
    d.temperature = temperature
    d.humidity = humidity
    d.Display()
}

func (d *CurrentConditionsDisplay) Display() {
    fmt.Printf("Current conditions: %.1fF degrees and %.1f%% humidity\n", d.temperature, d.humidity)
}

// 使用示例
func main() {
    weatherData := NewWeatherData()

    currentDisplay := NewCurrentConditionsDisplay(weatherData)

    weatherData.SetMeasurements(80, 65, 30.4)
    weatherData.SetMeasurements(82, 70, 29.2)
    weatherData.SetMeasurements(78, 90, 29.2)
}
```

### 8. 状态模式 (State)

允许一个对象在其内部状态改变时改变它的行为。

```go
// 状态接口
type State interface {
    InsertCoin()
    PressButton()
    Dispense()
}

// 上下文
type GumballMachine struct {
    soldOutState     State
    noCoinState      State
    hasCoinState     State
    soldState        State
    winnerState      State

    state        State
    count        int
}

func NewGumballMachine(count int) *GumballMachine {
    machine := &GumballMachine{
        count: count,
    }

    machine.soldOutState = &SoldOutState{machine: machine}
    machine.noCoinState = &NoCoinState{machine: machine}
    machine.hasCoinState = &HasCoinState{machine: machine}
    machine.soldState = &SoldState{machine: machine}
    machine.winnerState = &WinnerState{machine: machine}

    if count > 0 {
        machine.state = machine.noCoinState
    } else {
        machine.state = machine.soldOutState
    }

    return machine
}

func (g *GumballMachine) InsertCoin() {
    g.state.InsertCoin()
}

func (g *GumballMachine) PressButton() {
    g.state.PressButton()
    g.state.Dispense()
}

func (g *GumballMachine) ReleaseBall() {
    fmt.Println("A gumball comes rolling out the slot...")
    g.count--
}

func (g *GumballMachine) GetCount() int {
    return g.count
}

func (g *GumballMachine) SetState(state State) {
    g.state = state
}

func (g *GumballMachine) GetSoldOutState() State    { return g.soldOutState }
func (g *GumballMachine) GetNoCoinState() State     { return g.noCoinState }
func (g *GumballMachine) GetHasCoinState() State    { return g.hasCoinState }
func (g *GumballMachine) GetSoldState() State       { return g.soldState }
func (g *GumballMachine) GetWinnerState() State     { return g.winnerState }

// 具体状态
type NoCoinState struct {
    machine *GumballMachine
}

func (s *NoCoinState) InsertCoin() {
    fmt.Println("You inserted a coin")
    s.machine.SetState(s.machine.GetHasCoinState())
}

func (s *NoCoinState) PressButton() {
    fmt.Println("You turned, but there's no coin")
}

func (s *NoCoinState) Dispense() {
    fmt.Println("You need to pay first")
}

type HasCoinState struct {
    machine *GumballMachine
}

func (s *HasCoinState) InsertCoin() {
    fmt.Println("You can't insert another coin")
}

func (s *HasCoinState) PressButton() {
    fmt.Println("You turned...")
    winner := rand.Intn(10) == 0
    if winner && s.machine.GetCount() > 1 {
        s.machine.SetState(s.machine.GetWinnerState())
    } else {
        s.machine.SetState(s.machine.GetSoldState())
    }
}

func (s *HasCoinState) Dispense() {
    fmt.Println("No gumball dispensed")
}

type SoldState struct {
    machine *GumballMachine
}

func (s *SoldState) InsertCoin() {
    fmt.Println("Please wait, we're already giving you a gumball")
}

func (s *SoldState) PressButton() {
    fmt.Println("Turning twice doesn't get you another gumball")
}

func (s *SoldState) Dispense() {
    s.machine.ReleaseBall()
    if s.machine.GetCount() == 0 {
        s.machine.SetState(s.machine.GetSoldOutState())
    } else {
        s.machine.SetState(s.machine.GetNoCoinState())
    }
}

type SoldOutState struct {
    machine *GumballMachine
}

func (s *SoldOutState) InsertCoin() {
    fmt.Println("You can't insert a coin, the machine is sold out")
}

func (s *SoldOutState) PressButton() {
    fmt.Println("You turned, but there are no gumballs")
}

func (s *SoldOutState) Dispense() {
    fmt.Println("No gumball dispensed")
}

type WinnerState struct {
    machine *GumballMachine
}

func (s *WinnerState) InsertCoin() {
    fmt.Println("Please wait, we're already giving you a gumball")
}

func (s *WinnerState) PressButton() {
    fmt.Println("Turning twice doesn't get you another gumball")
}

func (s *WinnerState) Dispense() {
    fmt.Println("YOU'RE A WINNER! You get two gumballs for your coin")
    s.machine.ReleaseBall()
    if s.machine.GetCount() == 0 {
        s.machine.SetState(s.machine.GetSoldOutState())
    } else {
        s.machine.ReleaseBall()
        if s.machine.GetCount() > 0 {
            s.machine.SetState(s.machine.GetNoCoinState())
        } else {
            fmt.Println("Oops, out of gumballs!")
            s.machine.SetState(s.machine.GetSoldOutState())
        }
    }
}

// 使用示例
func main() {
    machine := NewGumballMachine(5)

    fmt.Println("Machine with 5 gumballs:")
    machine.InsertCoin()
    machine.PressButton()

    fmt.Println("\nMachine with 4 gumballs:")
    machine.InsertCoin()
    machine.PressButton()

    fmt.Println("\nMachine with 3 gumballs:")
    machine.InsertCoin()
    machine.PressButton()
}
```

### 9. 策略模式 (Strategy)

定义一系列算法，把它们一个个封装起来，并且使它们可相互替换。

```go
// 策略接口
type PaymentStrategy interface {
    Pay(amount float64) bool
}

// 具体策略
type CreditCardPayment struct {
    cardNumber string
    cvv        string
    expiryDate string
}

func NewCreditCardPayment(cardNumber, cvv, expiryDate string) *CreditCardPayment {
    return &CreditCardPayment{
        cardNumber: cardNumber,
        cvv:        cvv,
        expiryDate: expiryDate,
    }
}

func (p *CreditCardPayment) Pay(amount float64) bool {
    fmt.Printf("Paid %.2f using Credit Card ending with %s\n", amount, p.cardNumber[len(p.cardNumber)-4:])
    return true
}

type PayPalPayment struct {
    email    string
    password string
}

func NewPayPalPayment(email, password string) *PayPalPayment {
    return &PayPalPayment{
        email:    email,
        password: password,
    }
}

func (p *PayPalPayment) Pay(amount float64) bool {
    fmt.Printf("Paid %.2f using PayPal account %s\n", amount, p.email)
    return true
}

type WeChatPayment struct {
    qrCode string
}

func NewWeChatPayment(qrCode string) *WeChatPayment {
    return &WeChatPayment{qrCode: qrCode}
}

func (p *WeChatPayment) Pay(amount float64) bool {
    fmt.Printf("Paid %.2f using WeChat Pay\n", amount)
    return true
}

// 上下文
type ShoppingCart struct {
    items    []string
    strategy PaymentStrategy
}

func NewShoppingCart() *ShoppingCart {
    return &ShoppingCart{
        items: make([]string, 0),
    }
}

func (c *ShoppingCart) AddItem(item string) {
    c.items = append(c.items, item)
}

func (c *ShoppingCart) SetPaymentStrategy(strategy PaymentStrategy) {
    c.strategy = strategy
}

func (c *ShoppingCart) Checkout() float64 {
    total := 0.0
    for _, item := range c.items {
        total += 10.0 // 假设每个商品10元
    }

    if c.strategy != nil {
        c.strategy.Pay(total)
    } else {
        fmt.Println("Please set a payment strategy first")
    }

    return total
}

// 使用示例
func main() {
    cart := NewShoppingCart()
    cart.AddItem("Laptop")
    cart.AddItem("Mouse")
    cart.AddItem("Keyboard")

    // 使用信用卡支付
    cart.SetPaymentStrategy(NewCreditCardPayment("1234567890123456", "123", "12/25"))
    cart.Checkout()

    // 使用PayPal支付
    cart.SetPaymentStrategy(NewPayPalPayment("user@example.com", "password"))
    cart.Checkout()

    // 使用微信支付
    cart.SetPaymentStrategy(NewWeChatPayment("qr123456"))
    cart.Checkout()
}
```

### 10. 模板方法模式 (Template Method)

定义一个操作中的算法的骨架，而将一些步骤延迟到子类中。

```go
// 抽象类
abstract class CaffeineBeverage {
    final void prepareRecipe() {
        boilWater();
        brew();
        pourInCup();
        addCondiments();
    }

    abstract void brew();

    abstract void addCondiments();

    void boilWater() {
        System.out.println("Boiling water");
    }

    void pourInCup() {
        System.out.println("Pouring into cup");
    }
}

// 具体子类
class Tea extends CaffeineBeverage {
    void brew() {
        System.out.println("Steeping the tea");
    }

    void addCondiments() {
        System.out.println("Adding lemon");
    }
}

class Coffee extends CaffeineBeverage {
    void brew() {
        System.out.println("Dripping coffee through filter");
    }

    void addCondiments() {
        System.out.println("Adding sugar and milk");
    }
}

// 使用示例
public class Main {
    public static void main(String[] args) {
        CaffeineBeverage tea = new Tea();
        tea.prepareRecipe();

        CaffeineBeverage coffee = new Coffee();
        coffee.prepareRecipe();
    }
}
```

### 11. 访问者模式 (Visitor)

表示一个作用于某对象结构中的各元素的操作。

```go
// 访问者接口
type Visitor interface {
    VisitBook(book *Book)
    VisitFruit(fruit *Fruit)
}

// 元素接口
type Element interface {
    Accept(visitor Visitor)
}

// 具体元素
type Book struct {
    price float64
}

func NewBook(price float64) *Book {
    return &Book{price: price}
}

func (b *Book) Accept(visitor Visitor) {
    visitor.VisitBook(b)
}

type Fruit struct {
    price float64
}

func NewFruit(price float64) *Fruit {
    return &Fruit{price: price}
}

func (f *Fruit) Accept(visitor Visitor) {
    visitor.VisitFruit(f)
}

// 具体访问者
type ShoppingCartVisitor struct {
    total float64
}

func (v *ShoppingCartVisitor) VisitBook(book *Book) {
    cost := book.price
    if cost > 50 {
        cost -= 5 // 书籍折扣
    }
    v.total += cost
    fmt.Printf("Book price: %.2f\n", cost)
}

func (v *ShoppingCartVisitor) VisitFruit(fruit *Fruit) {
    cost := fruit.price * 0.8 // 水果8折
    v.total += cost
    fmt.Printf("Fruit price: %.2f\n", cost)
}

// 使用示例
func main() {
    items := []Element{
        NewBook(60),
        NewBook(40),
        NewFruit(10),
        NewFruit(20),
    }

    visitor := &ShoppingCartVisitor{}

    for _, item := range items {
        item.Accept(visitor)
    }

    fmt.Printf("Total cost: %.2f\n", visitor.total)
}
```

## 并发模式

### 1. 生产者-消费者模式

```go
// 生产者-消费者模式
type Item struct {
    Data string
}

type Producer struct {
    id      int
    queue   chan<- Item
    done    <-chan struct{}
    wg      *sync.WaitGroup
}

type Consumer struct {
    id      int
    queue   <-chan Item
    done    <-chan struct{}
    wg      *sync.WaitGroup
}

func NewProducer(id int, queue chan<- Item, done <-chan struct{}, wg *sync.WaitGroup) *Producer {
    return &Producer{
        id:    id,
        queue: queue,
        done:  done,
        wg:    wg,
    }
}

func (p *Producer) Produce() {
    defer p.wg.Done()

    for i := 0; ; i++ {
        select {
        case <-p.done:
            return
        default:
            item := Item{Data: fmt.Sprintf("Producer %d - Item %d", p.id, i)}
            p.queue <- item
            fmt.Printf("Producer %d produced: %s\n", p.id, item.Data)
            time.Sleep(time.Millisecond * time.Duration(rand.Intn(1000)))
        }
    }
}

func NewConsumer(id int, queue <-chan Item, done <-chan struct{}, wg *sync.WaitGroup) *Consumer {
    return &Consumer{
        id:    id,
        queue: queue,
        done:  done,
        wg:    wg,
    }
}

func (c *Consumer) Consume() {
    defer c.wg.Done()

    for {
        select {
        case <-c.done:
            return
        case item, ok := <-c.queue:
            if !ok {
                return
            }
            fmt.Printf("Consumer %d consumed: %s\n", c.id, item.Data)
            time.Sleep(time.Millisecond * time.Duration(rand.Intn(1000)))
        }
    }
}

// 使用示例
func main() {
    const (
        numProducers = 3
        numConsumers = 2
        queueSize    = 10
    )

    queue := make(chan Item, queueSize)
    done := make(chan struct{})
    var wg sync.WaitGroup

    // 创建生产者
    for i := 1; i <= numProducers; i++ {
        producer := NewProducer(i, queue, done, &wg)
        wg.Add(1)
        go producer.Produce()
    }

    // 创建消费者
    for i := 1; i <= numConsumers; i++ {
        consumer := NewConsumer(i, queue, done, &wg)
        wg.Add(1)
        go consumer.Consume()
    }

    // 运行一段时间后停止
    time.Sleep(5 * time.Second)
    close(done)

    wg.Wait()
    close(queue)
}
```

### 2. 工作池模式

```go
// 工作池模式
type Task struct {
    ID  int
    Data interface{}
}

type Worker struct {
    id         int
    taskQueue  chan Task
    resultChan chan Result
    quit       chan struct{}
}

type Result struct {
    WorkerID int
    TaskID   int
    Output   interface{}
    Err      error
}

func NewWorker(id int, taskQueue chan Task, resultChan chan Result) *Worker {
    return &Worker{
        id:         id,
        taskQueue:  taskQueue,
        resultChan: resultChan,
        quit:       make(chan struct{}),
    }
}

func (w *Worker) Start() {
    go func() {
        for {
            select {
            case task := <-w.taskQueue:
                result := w.Process(task)
                w.resultChan <- result
            case <-w.quit:
                return
            }
        }
    }()
}

func (w *Worker) Process(task Task) Result {
    // 模拟处理任务
    time.Sleep(time.Millisecond * time.Duration(rand.Intn(1000)))

    result := Result{
        WorkerID: w.id,
        TaskID:   task.ID,
        Output:   fmt.Sprintf("Processed task %d by worker %d", task.ID, w.id),
    }

    return result
}

func (w *Worker) Stop() {
    close(w.quit)
}

type WorkerPool struct {
    workers    []*Worker
    taskQueue  chan Task
    resultChan chan Result
    numWorkers int
}

func NewWorkerPool(numWorkers, queueSize int) *WorkerPool {
    pool := &WorkerPool{
        taskQueue:  make(chan Task, queueSize),
        resultChan: make(chan Result, queueSize),
        numWorkers: numWorkers,
    }

    // 创建工作线程
    for i := 1; i <= numWorkers; i++ {
        worker := NewWorker(i, pool.taskQueue, pool.resultChan)
        pool.workers = append(pool.workers, worker)
        worker.Start()
    }

    return pool
}

func (p *WorkerPool) Submit(task Task) {
    p.taskQueue <- task
}

func (p *WorkerPool) GetResults() <-chan Result {
    return p.resultChan
}

func (p *WorkerPool) Stop() {
    for _, worker := range p.workers {
        worker.Stop()
    }
    close(p.taskQueue)
    close(p.resultChan)
}

// 使用示例
func main() {
    const (
        numWorkers = 4
        queueSize  = 100
        numTasks   = 20
    )

    pool := NewWorkerPool(numWorkers, queueSize)
    defer pool.Stop()

    // 提交任务
    for i := 1; i <= numTasks; i++ {
        task := Task{
            ID:  i,
            Data: fmt.Sprintf("Task %d data", i),
        }
        pool.Submit(task)
    }

    // 收集结果
    resultsCollected := 0
    for result := range pool.GetResults() {
        fmt.Printf("Result: %s\n", result.Output)
        resultsCollected++

        if resultsCollected >= numTasks {
            break
        }
    }
}
```

### 3. Futures/Promises模式

```go
// Future/Promise模式
type Future struct {
    result interface{}
    err    error
    done   chan struct{}
    once   sync.Once
}

type Promise struct {
    future *Future
}

func NewPromise() (*Future, *Promise) {
    future := &Future{
        done: make(chan struct{}),
    }
    promise := &Promise{future: future}
    return future, promise
}

func (f *Future) Get() (interface{}, error) {
    <-f.done
    return f.result, f.err
}

func (f *Future) GetWithTimeout(timeout time.Duration) (interface{}, error) {
    select {
    case <-f.done:
        return f.result, f.err
    case <-time.After(timeout):
        return nil, fmt.Errorf("timeout")
    }
}

func (p *Promise) Resolve(result interface{}) {
    p.future.once.Do(func() {
        p.future.result = result
        close(p.future.done)
    })
}

func (p *Promise) Reject(err error) {
    p.future.once.Do(func() {
        p.future.err = err
        close(p.future.done)
    })
}

// 任务执行器
type Executor struct {
    workers chan struct{}
}

func NewExecutor(maxWorkers int) *Executor {
    return &Executor{
        workers: make(chan struct{}, maxWorkers),
    }
}

func (e *Executor) Execute(task func() (interface{}, error)) *Future {
    future, promise := NewPromise()

    go func() {
        e.workers <- struct{}{} // 获取工作线程
        defer func() { <-e.workers }() // 释放工作线程

        result, err := task()
        if err != nil {
            promise.Reject(err)
        } else {
            promise.Resolve(result)
        }
    }()

    return future
}

// 使用示例
func main() {
    executor := NewExecutor(3)

    // 异步任务1
    future1 := executor.Execute(func() (interface{}, error) {
        time.Sleep(2 * time.Second)
        return "Task 1 completed", nil
    })

    // 异步任务2
    future2 := executor.Execute(func() (interface{}, error) {
        time.Sleep(1 * time.Second)
        return "Task 2 completed", nil
    })

    // 异步任务3（会失败）
    future3 := executor.Execute(func() (interface{}, error) {
        time.Sleep(3 * time.Second)
        return nil, fmt.Errorf("task 3 failed")
    })

    // 等待结果
    result1, err1 := future1.Get()
    fmt.Printf("Task 1: %v, %v\n", result1, err1)

    result2, err2 := future2.GetWithTimeout(5 * time.Second)
    fmt.Printf("Task 2: %v, %v\n", result2, err2)

    result3, err3 := future3.Get()
    fmt.Printf("Task 3: %v, %v\n", result3, err3)
}
```

### 4. 读写锁模式

```go
// 读写锁模式
type DataStore struct {
    data   map[string]interface{}
    rwLock sync.RWMutex
}

func NewDataStore() *DataStore {
    return &DataStore{
        data: make(map[string]interface{}),
    }
}

func (ds *DataStore) Read(key string) (interface{}, bool) {
    ds.rwLock.RLock()
    defer ds.rwLock.RUnlock()

    value, exists := ds.data[key]
    return value, exists
}

func (ds *DataStore) Write(key string, value interface{}) {
    ds.rwLock.Lock()
    defer ds.rwLock.Unlock()

    ds.data[key] = value
}

func (ds *DataStore) Delete(key string) {
    ds.rwLock.Lock()
    defer ds.rwLock.Unlock()

    delete(ds.data, key)
}

func (ds *DataStore) Size() int {
    ds.rwLock.RLock()
    defer ds.rwLock.RUnlock()

    return len(ds.data)
}

// 读取器
type Reader struct {
    id   int
    store *DataStore
    wg    *sync.WaitGroup
}

func NewReader(id int, store *DataStore, wg *sync.WaitGroup) *Reader {
    return &Reader{
        id:    id,
        store: store,
        wg:    wg,
    }
}

func (r *Reader) Read(keys []string) {
    defer r.wg.Done()

    for i := 0; i < 10; i++ {
        key := keys[rand.Intn(len(keys))]
        value, exists := r.store.Read(key)
        if exists {
            fmt.Printf("Reader %d: %s = %v\n", r.id, key, value)
        } else {
            fmt.Printf("Reader %d: %s not found\n", r.id, key)
        }
        time.Sleep(time.Millisecond * 100)
    }
}

// 写入器
type Writer struct {
    id   int
    store *DataStore
    wg    *sync.WaitGroup
}

func NewWriter(id int, store *DataStore, wg *sync.WaitGroup) *Writer {
    return &Writer{
        id:    id,
        store: store,
        wg:    wg,
    }
}

func (w *Writer) Write(keys []string) {
    defer w.wg.Done()

    for i := 0; i < 5; i++ {
        key := keys[rand.Intn(len(keys))]
        value := fmt.Sprintf("Writer %d - Value %d", w.id, i)
        w.store.Write(key, value)
        fmt.Printf("Writer %d: wrote %s = %s\n", w.id, key, value)
        time.Sleep(time.Millisecond * 200)
    }
}

// 使用示例
func main() {
    const (
        numReaders = 5
        numWriters = 2
    )

    store := NewDataStore()
    var wg sync.WaitGroup

    // 初始化数据
    keys := []string{"key1", "key2", "key3", "key4", "key5"}
    for _, key := range keys {
        store.Write(key, "initial value")
    }

    // 创建读取器
    for i := 1; i <= numReaders; i++ {
        reader := NewReader(i, store, &wg)
        wg.Add(1)
        go reader.Read(keys)
    }

    // 创建写入器
    for i := 1; i <= numWriters; i++ {
        writer := NewWriter(i, store, &wg)
        wg.Add(1)
        go writer.Write(keys)
    }

    wg.Wait()
    fmt.Printf("Final store size: %d\n", store.Size())
}
```

## 函数式模式

### 1. 函数式选项模式

```go
// 函数式选项模式
type Server struct {
    host     string
    port     int
    timeout  time.Duration
    maxConns int
    tls      bool
}

type Option func(*Server)

func WithHost(host string) Option {
    return func(s *Server) {
        s.host = host
    }
}

func WithPort(port int) Option {
    return func(s *Server) {
        s.port = port
    }
}

func WithTimeout(timeout time.Duration) Option {
    return func(s *Server) {
        s.timeout = timeout
    }
}

func WithMaxConns(maxConns int) Option {
    return func(s *Server) {
        s.maxConns = maxConns
    }
}

func WithTLS(tls bool) Option {
    return func(s *Server) {
        s.tls = tls
    }
}

func NewServer(opts ...Option) *Server {
    server := &Server{
        host:     "localhost",
        port:     8080,
        timeout:  30 * time.Second,
        maxConns: 100,
        tls:      false,
    }

    for _, opt := range opts {
        opt(server)
    }

    return server
}

// 使用示例
func main() {
    server1 := NewServer()
    server2 := NewServer(
        WithHost("0.0.0.0"),
        WithPort(9090),
        WithTLS(true),
    )
    server3 := NewServer(
        WithHost("127.0.0.1"),
        WithPort(8081),
        WithTimeout(10*time.Second),
        WithMaxConns(50),
    )

    fmt.Printf("Server1: %+v\n", server1)
    fmt.Printf("Server2: %+v\n", server2)
    fmt.Printf("Server3: %+v\n", server3)
}
```

### 2. 中间件模式

```go
// 中间件模式
type Middleware func(http.Handler) http.Handler

func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        log.Printf("Started %s %s", r.Method, r.URL.Path)

        next.ServeHTTP(w, r)

        log.Printf("Completed %s %s in %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func AuthenticationMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "Unauthorized", http.StatusUnauthorized)
            return
        }

        // 验证token
        if !isValidToken(token) {
            http.Error(w, "Invalid token", http.StatusUnauthorized)
            return
        }

        next.ServeHTTP(w, r)
    })
}

func RateLimitMiddleware(next http.Handler) http.Handler {
    limiter := rate.NewLimiter(rate.Limit(10), 30) // 10 requests per second, burst 30

    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if !limiter.Allow() {
            http.Error(w, "Rate limit exceeded", http.StatusTooManyRequests)
            return
        }

        next.ServeHTTP(w, r)
    })
}

func CORSHandler(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "*")
        w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }

        next.ServeHTTP(w, r)
    })
}

// 中间件链
func ChainMiddleware(middlewares ...Middleware) Middleware {
    return func(next http.Handler) http.Handler {
        handler := next
        for i := len(middlewares) - 1; i >= 0; i-- {
            handler = middlewares[i](handler)
        }
        return handler
    }
}

// 辅助函数
func isValidToken(token string) bool {
    // 简化的token验证
    return token == "valid-token"
}

// 使用示例
func main() {
    // 创建路由
    router := http.NewServeMux()

    // 定义处理器
    helloHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, World!")
    })

    // 应用中间件链
    handler := ChainMiddleware(
        LoggingMiddleware,
        CORSHandler,
        RateLimitMiddleware,
        AuthenticationMiddleware,
    )(helloHandler)

    router.Handle("/", handler)

    // 启动服务器
    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", router))
}
```

### 3. 装饰器模式（函数式）

```go
// 函数式装饰器模式
type Processor func(string) string

func BasicProcessor(input string) string {
    return strings.ToUpper(input)
}

func LoggingDecorator(processor Processor) Processor {
    return func(input string) string {
        log.Printf("Processing: %s", input)
        result := processor(input)
        log.Printf("Result: %s", result)
        return result
    }
}

func TimingDecorator(processor Processor) Processor {
    return func(input string) string {
        start := time.Now()
        result := processor(input)
        duration := time.Since(start)
        log.Printf("Processing took: %v", duration)
        return result
    }
}

func CacheDecorator(processor Processor) Processor {
    cache := make(map[string]string)

    return func(input string) string {
        if result, exists := cache[input]; exists {
            log.Printf("Cache hit for: %s", input)
            return result
        }

        log.Printf("Cache miss for: %s", input)
        result := processor(input)
        cache[input] = result
        return result
    }
}

func RetryDecorator(processor Processor, maxRetries int) Processor {
    return func(input string) string {
        var lastError error

        for i := 0; i < maxRetries; i++ {
            result := processor(input)
            if result != "" {
                return result
            }
            lastError = fmt.Errorf("attempt %d failed", i+1)
            time.Sleep(time.Duration(i+1) * time.Second)
        }

        log.Printf("All retries failed: %v", lastError)
        return ""
    }
}

// 装饰器构建器
func DecorateProcessor(processor Processor, decorators ...func(Processor) Processor) Processor {
    result := processor
    for _, decorator := range decorators {
        result = decorator(result)
    }
    return result
}

// 使用示例
func main() {
    // 基础处理器
    basicProcessor := BasicProcessor

    // 使用装饰器链
    decoratedProcessor := DecorateProcessor(
        basicProcessor,
        LoggingDecorator,
        TimingDecorator,
        CacheDecorator,
        RetryDecorator,
    )

    // 测试
    input := "hello world"
    result := decoratedProcessor(input)
    fmt.Printf("Final result: %s\n", result)

    // 再次测试（应该命中缓存）
    result2 := decoratedProcessor(input)
    fmt.Printf("Cached result: %s\n", result2)
}
```

## 架构模式

### 1. 分层架构模式

```go
// 分层架构模式
// 实体层
type User struct {
    ID        int       `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

// 仓储接口（数据访问层）
type UserRepository interface {
    FindByID(id int) (*User, error)
    FindByEmail(email string) (*User, error)
    Save(user *User) error
    Update(user *User) error
    Delete(id int) error
}

// 业务逻辑层
type UserService struct {
	repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}

func (s *UserService) CreateUser(username, email string) (*User, error) {
    // 验证输入
    if username == "" || email == "" {
        return nil, fmt.Errorf("username and email are required")
    }

    // 检查邮箱是否已存在
    existingUser, err := s.repo.FindByEmail(email)
    if err == nil && existingUser != nil {
        return nil, fmt.Errorf("email already exists")
    }

    // 创建用户
    user := &User{
		Username:  username,
		Email:     email,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

    err = s.repo.Save(user)
    if err != nil {
        return nil, fmt.Errorf("failed to create user: %v", err)
    }

    return user, nil
}

func (s *UserService) GetUserByID(id int) (*User, error) {
    user, err := s.repo.FindByID(id)
    if err != nil {
        return nil, fmt.Errorf("failed to get user: %v", err)
    }
    return user, nil
}

// 表现层/控制器
type UserController struct {
	service *UserService
}

func NewUserController(service *UserService) *UserController {
    return &UserController{service: service}
}

func (c *UserController) CreateUser(w http.ResponseWriter, r *http.Request) {
    var req struct {
		Username string `json:"username"`
		Email    string `json:"email"`
	}

    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    user, err := c.service.CreateUser(req.Username, req.Email)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

func (c *UserController) GetUser(w http.ResponseWriter, r *http.Request) {
    idStr := r.URL.Query().Get("id")
    id, err := strconv.Atoi(idStr)
    if err != nil {
        http.Error(w, "invalid user ID", http.StatusBadRequest)
        return
    }

    user, err := c.service.GetUserByID(id)
    if err != nil {
        http.Error(w, err.Error(), http.StatusNotFound)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(user)
}

// 使用示例
func main() {
    // 初始化各层
    userRepo := NewInMemoryUserRepository() // 假设的实现
    userService := NewUserService(userRepo)
    userController := NewUserController(userService)

    // 设置路由
    http.HandleFunc("/users", userController.CreateUser)
    http.HandleFunc("/users/get", userController.GetUser)

    log.Println("Server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

### 2. 依赖注入模式

```go
// 依赖注入模式
// 依赖容器
type Container struct {
    services map[string]interface{}
    mutex    sync.RWMutex
}

func NewContainer() *Container {
    return &Container{
        services: make(map[string]interface{}),
    }
}

func (c *Container) Register(name string, service interface{}) {
    c.mutex.Lock()
    defer c.mutex.Unlock()

    c.services[name] = service
}

func (c *Container) Get(name string) (interface{}, error) {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    service, exists := c.services[name]
    if !exists {
        return nil, fmt.Errorf("service %s not found", name)
    }

    return service, nil
}

func (c *Container) MustGet(name string) interface{} {
    service, err := c.Get(name)
    if err != nil {
        panic(err)
    }
    return service
}

// 服务定义
type Database interface {
    Query(query string) (interface{}, error)
}

type Logger interface {
    Log(message string)
}

type Cache interface {
    Get(key string) (interface{}, error)
    Set(key string, value interface{}) error
}

// 具体服务实现
type PostgreSQL struct {
    connectionString string
}

func NewPostgreSQL(connStr string) *PostgreSQL {
    return &PostgreSQL{connectionString: connStr}
}

func (p *PostgreSQL) Query(query string) (interface{}, error) {
    // 实现数据库查询
    return fmt.Sprintf("Query result for: %s", query), nil
}

type ConsoleLogger struct{}

func NewConsoleLogger() *ConsoleLogger {
    return &ConsoleLogger{}
}

func (l *ConsoleLogger) Log(message string) {
    fmt.Printf("[LOG] %s\n", message)
}

type RedisCache struct {
    host string
}

func NewRedisCache(host string) *RedisCache {
    return &RedisCache{host: host}
}

func (r *RedisCache) Get(key string) (interface{}, error) {
    // 实现缓存获取
    return nil, fmt.Errorf("key not found")
}

func (r *RedisCache) Set(key string, value interface{}) error {
    // 实现缓存设置
    return nil
}

// 使用依赖的服务
type UserService struct {
    db     Database
    logger Logger
    cache  Cache
}

func NewUserService(db Database, logger Logger, cache Cache) *UserService {
    return &UserService{
        db:     db,
        logger: logger,
        cache:  cache,
    }
}

func (s *UserService) GetUser(id string) (interface{}, error) {
    s.logger.Log(fmt.Sprintf("Getting user with ID: %s", id))

    // 先尝试从缓存获取
    cached, err := s.cache.Get(id)
    if err == nil {
        return cached, nil
    }

    // 从数据库获取
    result, err := s.db.Query(fmt.Sprintf("SELECT * FROM users WHERE id = %s", id))
    if err != nil {
        return nil, err
    }

    // 缓存结果
    s.cache.Set(id, result)

    return result, nil
}

// 依赖注入配置
func ConfigureContainer() *Container {
    container := NewContainer()

    // 注册依赖
    container.Register("database", NewPostgreSQL("postgres://user:pass@localhost/db"))
    container.Register("logger", NewConsoleLogger())
    container.Register("cache", NewRedisCache("localhost:6379"))

    // 注册UserService
    container.Register("userService", func() *UserService {
        db := container.MustGet("database").(Database)
        logger := container.MustGet("logger").(Logger)
        cache := container.MustGet("cache").(Cache)
        return NewUserService(db, logger, cache)
    })

    return container
}

// 使用示例
func main() {
    // 配置依赖容器
    container := ConfigureContainer()

    // 获取服务
    userService := container.MustGet("userService").(*UserService)

    // 使用服务
    user, err := userService.GetUser("123")
    if err != nil {
        fmt.Printf("Error: %v\n", err)
        return
    }

    fmt.Printf("User: %v\n", user)
}
```

## 设计原则

### SOLID原则

#### 1. 单一职责原则 (SRP)
一个类应该只有一个引起变化的原因。

```go
// 违反SRP的例子
type User struct {
    ID       int
    Username string
    Email    string
}

func (u *User) Save() error {
    // 保存到数据库的逻辑
    fmt.Printf("Saving user %s to database\n", u.Username)
    return nil
}

func (u *User) SendEmail() error {
    // 发送邮件的逻辑
    fmt.Printf("Sending email to %s\n", u.Email)
    return nil
}

// 符合SRP的重构
type User struct {
    ID       int
    Username string
    Email    string
}

type UserRepository struct{}

func (r *UserRepository) Save(user *User) error {
    fmt.Printf("Saving user %s to database\n", user.Username)
    return nil
}

type EmailService struct{}

func (s *EmailService) SendEmail(to, subject, body string) error {
    fmt.Printf("Sending email to %s: %s\n", to, subject)
    return nil
}

// 使用
func main() {
    user := &User{ID: 1, Username: "john", Email: "john@example.com"}

    userRepo := &UserRepository{}
    emailService := &EmailService{}

    userRepo.Save(user)
    emailService.SendEmail(user.Email, "Welcome", "Welcome to our platform!")
}
```

#### 2. 开放封闭原则 (OCP)
软件实体应该对扩展开放，对修改封闭。

```go
// 违反OCP的例子
type AreaCalculator struct{}

func (a *AreaCalculator) Area(shape interface{}) float64 {
    switch s := shape.(type) {
    case *Rectangle:
        return s.Width * s.Height
    case *Circle:
        return math.Pi * s.Radius * s.Radius
    default:
        return 0
    }
}

type Rectangle struct {
    Width  float64
    Height float64
}

type Circle struct {
    Radius float64
}

// 符合OCP的重构
type Shape interface {
    Area() float64
}

type Rectangle struct {
    Width  float64
    Height float64
}

func (r *Rectangle) Area() float64 {
    return r.Width * r.Height
}

type Circle struct {
    Radius float64
}

func (c *Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

type Triangle struct {
    Base   float64
    Height float64
}

func (t *Triangle) Area() float64 {
    return 0.5 * t.Base * t.Height
}

type AreaCalculator struct{}

func (a *AreaCalculator) TotalArea(shapes []Shape) float64 {
    total := 0.0
    for _, shape := range shapes {
        total += shape.Area()
    }
    return total
}
```

#### 3. 里氏替换原则 (LSP)
子类型必须能够替换其基类型。

```go
// 违反LSP的例子
type Bird interface {
    Fly()
}

type Sparrow struct{}

func (s *Sparrow) Fly() {
    fmt.Println("Sparrow is flying")
}

type Ostrich struct{}

func (o *Ostrich) Fly() {
    panic("Ostrich cannot fly!")
}

// 符合LSP的重构
type Bird interface {
    Move()
}

type FlyingBird interface {
    Bird
    Fly()
}

type Sparrow struct{}

func (s *Sparrow) Move() {
    fmt.Println("Sparrow is moving")
}

func (s *Sparrow) Fly() {
    fmt.Println("Sparrow is flying")
}

type Ostrich struct{}

func (o *Ostrich) Move() {
    fmt.Println("Ostrich is running")
}

// 使用
func MakeBirdMove(bird Bird) {
    bird.Move()
}

func MakeBirdFly(bird FlyingBird) {
    bird.Fly()
}
```

#### 4. 接口隔离原则 (ISP)
客户端不应该被迫依赖于它不使用的方法。

```go
// 违反ISP的例子
type Worker interface {
    Work()
    Eat()
    Sleep()
}

type HumanWorker struct{}

func (h *HumanWorker) Work() {
    fmt.Println("Human is working")
}

func (h *HumanWorker) Eat() {
    fmt.Println("Human is eating")
}

func (h *HumanWorker) Sleep() {
    fmt.Println("Human is sleeping")
}

type RobotWorker struct{}

func (r *RobotWorker) Work() {
    fmt.Println("Robot is working")
}

func (r *RobotWorker) Eat() {
    // 机器人不需要吃饭
    panic("Robot cannot eat!")
}

func (r *RobotWorker) Sleep() {
    // 机器人不需要睡觉
    panic("Robot cannot sleep!")
}

// 符合ISP的重构
type Workable interface {
    Work()
}

type Eatable interface {
    Eat()
}

type Sleepable interface {
    Sleep()
}

type HumanWorker struct{}

func (h *HumanWorker) Work() {
    fmt.Println("Human is working")
}

func (h *HumanWorker) Eat() {
    fmt.Println("Human is eating")
}

func (h *HumanWorker) Sleep() {
    fmt.Println("Human is sleeping")
}

type RobotWorker struct{}

func (r *RobotWorker) Work() {
    fmt.Println("Robot is working")
}
```

#### 5. 依赖倒置原则 (DIP)
高层模块不应该依赖于低层模块，二者都应该依赖于抽象。

```go
// 违反DIP的例子
type MySQLDatabase struct{}

func (m *MySQLDatabase) Save(data string) {
    fmt.Printf("Saving to MySQL: %s\n", data)
}

type UserService struct {
    db *MySQLDatabase
}

func NewUserService() *UserService {
    return &UserService{
        db: &MySQLDatabase{},
    }
}

func (s *UserService) SaveUser(data string) {
    s.db.Save(data)
}

// 符合DIP的重构
type Database interface {
    Save(data string) error
}

type MySQLDatabase struct{}

func (m *MySQLDatabase) Save(data string) error {
    fmt.Printf("Saving to MySQL: %s\n", data)
    return nil
}

type PostgreSQLDatabase struct{}

func (p *PostgreSQLDatabase) Save(data string) error {
    fmt.Printf("Saving to PostgreSQL: %s\n", data)
    return nil
}

type UserService struct {
    db Database
}

func NewUserService(db Database) *UserService {
    return &UserService{db: db}
}

func (s *UserService) SaveUser(data string) error {
    return s.db.Save(data)
}
```

## 最佳实践

### 1. 选择合适的设计模式

```go
// 根据场景选择合适的设计模式
type PatternSelector struct{}

func (p *PatternSelector) SelectPattern(problem string) string {
    patterns := map[string]string{
        "需要创建复杂对象":           "建造者模式",
        "需要对象的唯一实例":         "单例模式",
        "需要解耦对象创建":           "工厂模式",
        "需要在不修改原有代码的情况下扩展功能": "装饰器模式",
        "需要处理对象的树形结构":       "组合模式",
        "需要简化复杂对象的创建":       "外观模式",
        "需要共享细粒度对象":         "享元模式",
        "需要控制对象的访问":         "代理模式",
        "需要处理请求的链式处理":       "责任链模式",
        "需要将请求封装为对象":         "命令模式",
        "需要解释语言语法":           "解释器模式",
        "需要遍历聚合对象":           "迭代器模式",
        "需要简化对象间的通信":         "中介者模式",
        "需要保存和恢复对象状态":       "备忘录模式",
        "需要对象间的一对多依赖":       "观察者模式",
        "需要根据状态改变行为":         "状态模式",
        "需要封装算法族":           "策略模式",
        "需要定义算法骨架":           "模板方法模式",
        "需要在不改变数据结构的情况下添加新操作": "访问者模式",
    }

    if pattern, exists := patterns[problem]; exists {
        return pattern
    }
    return "请重新分析问题"
}
```

### 2. 避免过度设计

```go
// 简单解决方案优先
type SimpleUserService struct {
    users map[string]*User
}

func NewSimpleUserService() *SimpleUserService {
    return &SimpleUserService{
        users: make(map[string]*User),
    }
}

func (s *SimpleUserService) CreateUser(username, email string) (*User, error) {
    if username == "" || email == "" {
        return nil, fmt.Errorf("invalid input")
    }

    user := &User{
        Username:  username,
        Email:     email,
        CreatedAt: time.Now(),
    }

    s.users[email] = user
    return user, nil
}

func (s *SimpleUserService) GetUser(email string) (*User, error) {
    user, exists := s.users[email]
    if !exists {
        return nil, fmt.Errorf("user not found")
    }
    return user, nil
}

// 复杂的解决方案（可能过度设计）
type ComplexUserService struct {
    validators  []UserValidator
    processors  []UserProcessor
    notifiers   []UserNotifier
    storage     UserStorage
    cache       UserCache
    logger      Logger
    metrics     MetricsCollector
}

type UserValidator interface {
    Validate(user *User) error
}

type UserProcessor interface {
    Process(user *User) error
}

type UserNotifier interface {
    Notify(user *User) error
}

type UserStorage interface {
    Save(user *User) error
    Find(email string) (*User, error)
}

type UserCache interface {
    Set(user *User) error
    Get(email string) (*User, error)
}

// 只在真正需要时才使用复杂的设计
```

### 3. 设计模式组合使用

```go
// 组合使用多个设计模式
type NotificationService struct {
    // 策略模式：不同的通知策略
    strategies map[string]NotificationStrategy

    // 工厂模式：创建通知策略
    factory NotificationStrategyFactory

    // 观察者模式：监听通知事件
    observers []NotificationObserver

    // 装饰器模式：增强通知功能
    decorator NotificationDecorator

    // 单例模式：确保服务唯一性
    instance *NotificationService
}

type NotificationStrategy interface {
    Send(to, subject, message string) error
}

type NotificationStrategyFactory interface {
    CreateStrategy(type string) NotificationStrategy
}

type NotificationObserver interface {
    OnNotificationSent(to, subject string)
}

type NotificationDecorator interface {
    Decorate(strategy NotificationStrategy) NotificationStrategy
}

// 实际实现...
```

### 4. 设计模式与Go语言特性结合

```go
// 利用Go的interface和struct组合实现设计模式
type Plugin interface {
    Name() string
    Execute() error
}

type PluginManager struct {
    plugins map[string]Plugin
    mutex   sync.RWMutex
}

func NewPluginManager() *PluginManager {
    return &PluginManager{
        plugins: make(map[string]Plugin),
    }
}

func (m *PluginManager) Register(plugin Plugin) {
    m.mutex.Lock()
    defer m.mutex.Unlock()

    m.plugins[plugin.Name()] = plugin
}

func (m *PluginManager) Execute(name string) error {
    m.mutex.RLock()
    defer m.mutex.RUnlock()

    plugin, exists := m.plugins[name]
    if !exists {
        return fmt.Errorf("plugin %s not found", name)
    }

    return plugin.Execute()
}

// 利用Go的channel实现观察者模式
type Event struct {
    Type    string
    Payload interface{}
}

type EventBus struct {
    subscribers map[string]chan Event
    mutex       sync.RWMutex
}

func NewEventBus() *EventBus {
    return &EventBus{
        subscribers: make(map[string]chan Event),
    }
}

func (b *EventBus) Subscribe(eventType string) chan Event {
    b.mutex.Lock()
    defer b.mutex.Unlock()

    ch := make(chan Event, 100)
    b.subscribers[eventType] = ch
    return ch
}

func (b *EventBus) Publish(event Event) {
    b.mutex.RLock()
    defer b.mutex.RUnlock()

    if ch, exists := b.subscribers[event.Type]; exists {
        ch <- event
    }
}
```

这个Go设计模式实战文档涵盖了23种经典设计模式在Go语言中的实现，包括创建型、结构型、行为型模式，以及Go特有的并发模式和函数式模式。每种模式都提供了详细的代码示例和使用场景，同时包含了SOLID设计原则和最佳实践的指导。这些设计模式和原则可以帮助开发者编写更加灵活、可维护和可扩展的Go代码。