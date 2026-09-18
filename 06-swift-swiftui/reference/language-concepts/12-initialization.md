# Swift 构造过程：让对象从创建起就有效

前置：struct、class、Optional。构造器的工作是建立实例不变量，例如容量必须为正。成功构造后，调用方不必反复猜对象是否“初始化了一半”。以下独立代码块分别使用，不要将同名类型重复放入同一文件；本轮未在 Swift 工具链编译运行。

## 值类型：默认值、逐成员与自定义构造

```swift
struct Point {
    var x: Double
    var y: Double = 0
}
let p = Point(x: 2) // 合成的逐成员构造器使用 y 的默认值
print(p.x, p.y)    // 2.0 0.0

extension Point {
    init(diagonal value: Double) { self.init(x: value, y: value) }
}
```

在结构体主体中添加自定义 init 通常会抑制合成入口；把额外入口放在 extension 中可保留适用的合成构造器。合成入口有访问级别规则，公开类型不等于自动获得 public 逐成员构造器；库 API 应显式声明对外入口。

## 可失败构造与抛错构造

```swift
struct PositiveCount {
    let value: Int
    init?(_ value: Int) {
        guard value > 0 else { return nil }
        self.value = value
    }
}
print(PositiveCount(0) == nil) // true
print(PositiveCount(3)?.value as Any) // Optional(3)
```

失败路径可以在全部属性赋值前返回 nil；成功路径才必须完成初始化。init? 使调用表达式产生可选结果，并不把构造器内部的 self 变成可选值。只需表达“不能构造”时用 init?；需要区分非法格式、范围错误等原因时用 throws。init! 或强制解包会把失败转为崩溃，不适合作为正常输入处理。

## 类：指定、便利与 required

指定构造器负责本类属性，并按规则向直接父类的指定构造器委派。便利构造器先横向调用本类其他构造器。required 表示子类必须提供或继承该入口，不意味着同一个签名要声明两次。

```swift
class Document {
    var title: String
    required init(title: String) { self.title = title }
    convenience init() { self.init(title: "未命名") }
}

class Report: Document {
    var pages: Int
    required init(title: String) {
        pages = 0
        super.init(title: title)
    }
    init(title: String, pages: Int) {
        self.pages = pages
        super.init(title: title)
    }
}
print(Report().title) // 未命名：适用规则下继承便利构造器
```

初始化自己引入的存储属性后再 super.init，之后才能按规则使用完整 self。actor 没有类的继承层级，不能把类的 required/convenience/两段式继承规则原样套给 actor。构造器继承细则以 [官方 Initialization](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/initialization/)为准。

## 属性包装器与资源寿命

`_name` 表示包装器存储，`name` 访问 wrappedValue，`$name` 访问包装器提供的 projectedValue。memberwise 参数形状取决于包装器的构造入口与声明，不能说只要有 init(projectedValue:) 就自动多出一个任意的 `$name` 参数。SwiftUI State 的初值也不是父参数变化后会自动重新应用的同步通道。

deinit 用于实例释放时的收尾，但不能保证进程终止前执行。需要可靠保存或异步关闭的资源应提供显式 save/close 操作。现代 Swift 的非拷贝类型也可能定义 deinit，不应绝对地说所有 struct 都不允许。

## 练习与反馈

设计 Capacity 类型，拒绝 0、负数及超过业务上限的值；再为缓存提供默认容量和显式容量两个入口。验收：所有成功构造的实例都满足同一范围，失败不会创建半有效对象；不要用 max(1, input) 悄悄把非法输入变成另一种请求，除非产品明确需要钳制。

继续阅读：[属性包装器](./09-property-wrappers.md)、[ARC](./10-value-types-arc.md)、[错误处理](./08-error-handling.md)。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
