# 综合练习 - 控制台图书管理系统

> **文档简介**: 用现代 Java 风格实现一个控制台图书管理系统，综合运用 record、switch 表达式、Optional、Stream、try-with-resources 与简单文件持久化
>
> **目标读者**: 已学完本模块 basics 01-07 的学习者，需要一个综合落点
>
> **前置知识**: [现代 Java 特性](./07-modern-features.md)全部内容

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 教程 |
| **难度** | ⭐ |
| **标签** | `#综合项目` `#图书管理` `#Stream` `#Record` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 按"模型 → 服务 → 交互"三层组织一个小型控制台应用，并在真实代码中综合运用本模块全部现代特性

## 📋 需求与设计

**功能需求**：录入图书、按 ISBN 查找、按书名搜索、借出、归还、列出全部、保存（CSV 文件）。

**分层设计**：

```
Main（交互层：菜单循环、Scanner、switch 表达式）
 └── Library（服务层：业务规则、Stream 查询、状态校验）
      ├── Book record + BookStatus enum（模型层：不可变数据）
      └── books.csv（持久化：try-with-resources 读写）
```

## 📦 第一层：数据模型

```java
public enum BookStatus { AVAILABLE, BORROWED }

public record Book(String isbn, String title, String author, int year, BookStatus status) {

    public Book {                                  // 紧凑构造器：统一校验
        if (isbn == null || isbn.isBlank()) {
            throw new IllegalArgumentException("isbn 不能为空");
        }
        if (year < 1900 || year > 2100) {
            throw new IllegalArgumentException("年份不合法: " + year);
        }
    }

    public Book withStatus(BookStatus newStatus) { // 不可变更新：返回新实例
        return new Book(isbn, title, author, year, newStatus);
    }

    public boolean available() { return status == BookStatus.AVAILABLE; }

    public String toCsv() {                        // 序列化为一行
        return String.join(";", isbn, title, author, String.valueOf(year), status.name());
    }

    public static Book fromCsv(String line) {      // 反序列化
        var parts = line.split(";", -1);
        return new Book(parts[0], parts[1], parts[2],
                Integer.parseInt(parts[3]), BookStatus.valueOf(parts[4]));
    }
}
```

**旧写法对照**：这一层在 Java 8 时代 ≈ 100 行样板类；record + 紧凑构造器 + 静态工厂让它压缩到约 30 行且自带校验。

## ⚙️ 第二层：服务层

```java
public class Library {
    private final Map<String, Book> books = new HashMap<>();   // isbn -> Book

    public void add(Book book) {
        var existing = books.putIfAbsent(book.isbn(), book);   // 原子式防重复
        if (existing != null) {
            throw new DuplicateIsbnException(book.isbn());
        }
    }

    public Optional<Book> findByIsbn(String isbn) {            // Optional 表达可能缺失
        return Optional.ofNullable(books.get(isbn));
    }

    public List<Book> searchByTitle(String keyword) {          // Stream 声明式查询
        var k = keyword.toLowerCase();
        return books.values().stream()
                .filter(b -> b.title().toLowerCase().contains(k))
                .sorted(Comparator.comparing(Book::title))
                .toList();
    }

    public List<Book> listAll() {
        return books.values().stream()
                .sorted(Comparator.comparing(Book::isbn))
                .toList();
    }

    public void borrow(String isbn) {                          // 状态机：非法流转直接拒绝
        var newBook = findByIsbn(isbn)
                .orElseThrow(() -> new BookNotFoundException(isbn));
        if (!newBook.available()) {
            throw new IllegalStateException("图书已被借出: " + isbn);
        }
        books.put(isbn, newBook.withStatus(BookStatus.BORROWED));
    }

    public void giveBack(String isbn) {
        var newBook = findByIsbn(isbn)
                .orElseThrow(() -> new BookNotFoundException(isbn));
        books.put(isbn, newBook.withStatus(BookStatus.AVAILABLE));
    }
```

> `borrow`/`add` 抛出的 `BookNotFoundException`/`DuplicateIsbnException` 是继承 `RuntimeException` 的简单业务异常（构造器把 isbn 拼进消息），设计原则见[异常处理](./06-exceptions.md)。

## 🖥️ 第三层：交互层

```java
public class Main {

    public static void main(String[] args) {
        var library = new Library();
        var scanner = new Scanner(System.in);
        while (true) {
            printMenu();
            var choice = scanner.nextLine().strip();
            if (choice.equals("0")) return;                    // 退出
            dispatch(choice, library, scanner);                // 分发交给 switch 表达式
        }
    }

    private static void dispatch(String choice, Library lib, Scanner in) {
        try {
            switch (choice) {
                case "1" -> lib.add(readBook(in));
                case "2" -> lib.findByIsbn(read(in, "ISBN"))
                        .ifPresentOrElse(System.out::println,
                                () -> System.out.println("未找到"));
                case "3" -> lib.searchByTitle(read(in, "书名关键字"))
                        .forEach(System.out::println);
                case "4" -> lib.borrow(read(in, "ISBN"));
                case "5" -> lib.giveBack(read(in, "ISBN"));
                case "6" -> lib.listAll().forEach(System.out::println);
                default -> System.out.println("无效选项");
            }
        } catch (RuntimeException e) {                         // 统一兜底：消息友好、不中断主循环
            System.out.println("操作失败: " + e.getMessage());
        }
    }

    private static Book readBook(Scanner in) {
        return new Book(read(in, "ISBN"), read(in, "书名"),
                read(in, "作者"), Integer.parseInt(read(in, "年份")),
                BookStatus.AVAILABLE);
    }

    private static String read(Scanner in, String label) {
        System.out.print(label + ": ");
        return in.nextLine().strip();
    }

    private static void printMenu() {
        System.out.println("""
                ===== 图书管理系统 =====
                1.录入  2.按ISBN查  3.按书名搜
                4.借出  5.归还      6.全部列出
                0.退出
                ========================""" );               // 文本块画菜单
    }
}
```

## 💾 扩展：CSV 持久化（try-with-resources 实战）

```java
public void save(Path file) throws IOException {
    try (var writer = Files.newBufferedWriter(file)) {
        for (Book b : listAll()) {
            writer.write(b.toCsv());
            writer.newLine();
        }
    }
}
```

加载是对称的一行式组合（建议动手实现）：`try (var lines = Files.lines(path)) { lines.map(Book::fromCsv).forEach(library::add); }`——注意 `Files.lines` 返回的流必须关闭，是 try-with-resources 的经典应用场景。

## ✅ 现代特性对照清单

| 特性 | 使用位置 |
|------|---------|
| record + 紧凑构造器 | Book 数据模型 |
| enum 状态机 | BookStatus |
| Optional | findByIsbn 契约 |
| Stream（filter/sorted/toList） | searchByTitle/listAll/文件加载 |
| switch 表达式箭头语法 | 菜单分发 |
| try-with-resources | CSV 读写 |
| 自定义 RuntimeException | BookNotFoundException 等 |
| 文本块 | 菜单打印 |

## 🎯 练习与实践

### 基础练习
1. 按三层结构完整敲出本系统，跑通全部菜单，并故意触发重复 ISBN、借出已借出图书的异常路径

### 进阶挑战
1. 增加"按作者统计图书数量"（`Collectors.groupingBy` + `counting`）
2. 增加借阅人模型，用 `record BorrowRecord(String isbn, String user, LocalDate date)` 记录借阅历史，并用 `Map<String, List<BorrowRecord>>` + `computeIfAbsent` 实现按人查询

## 🔗 相关文档

- 📄 **[现代 Java 特性](./07-modern-features.md)** - 本项目特性来源
- 📄 **[现代 Java 速查](../reference/quick-references/01-java-cheatsheet.md)** - 写代码时的案头速查
- 📄 **[标准库核心](../reference/library-guides/01-standard-library.md)** - Files/Path 与 java.time 用法
