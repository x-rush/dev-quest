# 综合练习：可重启的控制台图书管理系统

## 阅读准备

前置是变量、集合、类、文件与异常处理：先完成 [异常处理](./06-exceptions.md)，并能解释 `try-with-resources` 为什么会在成功与失败路径都关闭资源。`record`、箭头 `switch` 可对照 [现代 Java 特性](./07-modern-features.md) 边做边学。本篇使用 Java 21 标准库，无 Maven、Gradle 或第三方依赖。

学完这些内容后，需要把它们组合成一次完整操作：解析输入、检查业务条件、修改状态、保存，最后报告结果。

完成条件是“借书后重新启动还能看到借出状态；输入或文件损坏时原数据保持不变”。仅打印成功消息不代表保存成功。

## 1. 需求和边界

每本书包含 ISBN、书名、作者、年份、状态。本练习把 ISBN 当作用户提供的唯一书号，不实现 ISBN 校验位算法，也不允许一个书号对应多册库存。

| 命令 | 规则 |
|---|---|
| `add <isbn> <title> <author> <year>` | 新书默认为可借；重复书号失败 |
| `find <isbn>` | 不存在则报错并返回非零退出码 |
| `search <keyword>` | 不区分大小写；无结果时成功输出空列表 |
| `borrow <isbn>` | 只允许“可借 → 已借出” |
| `return <isbn>` | 只允许“已借出 → 可借”；重复归还明确失败 |
| `list` | 按 ISBN 排序列出所有书 |

每次运行一个命令，便于 shell 自动化测试。`Book` 管字段约束；`Library` 管查找和状态转换；`load/save` 管存储格式；`main` 管参数、锁和退出码。为了直接复制运行，先放在一个文件中，理解后再拆文件。

数据存为 UTF-8 的**受限 TSV**：首行是 `dev-quest-books-v1`，后续各行五个字段以制表符分隔。文本允许中文、空格、分号和引号，但拒绝控制字符（含制表符和换行），因此不会产生分隔歧义。这不是通用 CSV 解析器；需要多行字段或导入 Excel CSV 时，应采用支持引号转义的 CSV 库。

## 2. 完整程序：Main.java

创建空目录，将整段保存为 `Main.java`。无需额外异常类或隐藏辅助函数。

<!-- project-file: Main.java -->
```java
import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

public class Main {
    enum BookStatus { AVAILABLE, BORROWED }

    record Book(String isbn, String title, String author, int year, BookStatus status) {
        Book {
            isbn = text(isbn, "isbn");
            title = text(title, "书名");
            author = text(author, "作者");
            if (year < 1 || year > 2100) {
                throw new IllegalArgumentException("年份须在 1–2100 之间");
            }
            Objects.requireNonNull(status, "status");
        }

        Book withStatus(BookStatus value) {
            return new Book(isbn, title, author, year, value);
        }

        String toTsv() {
            return String.join("\t", isbn, title, author, Integer.toString(year), status.name());
        }

        static Book fromTsv(String line) {
            String[] fields = line.split("\t", -1);
            if (fields.length != 5) {
                throw new IllegalArgumentException("记录必须有 5 个字段");
            }
            return new Book(fields[0], fields[1], fields[2], Integer.parseInt(fields[3]),
                    BookStatus.valueOf(fields[4]));
        }
    }

    static String text(String value, String label) {
        if (value == null || value.isBlank() || value.length() > 240
                || value.codePoints().anyMatch(Character::isISOControl)) {
            throw new IllegalArgumentException(label + "须为 1–240 个 UTF-16 单元的非空文本，不能含控制字符");
        }
        return value.strip();
    }

    static final class Library {
        private final Map<String, Book> books = new HashMap<>();

        void add(Book book) {
            // 当前线程中的防重复逻辑；HashMap 不提供并发原子性。
            if (books.putIfAbsent(book.isbn(), book) != null) {
                throw new IllegalArgumentException("重复 ISBN: " + book.isbn());
            }
        }

        Optional<Book> findByIsbn(String isbn) {
            return Optional.ofNullable(books.get(text(isbn, "isbn")));
        }

        Book require(String isbn) {
            return findByIsbn(isbn)
                    .orElseThrow(() -> new IllegalArgumentException("未找到: " + isbn));
        }

        List<Book> listAll() {
            return books.values().stream().sorted(Comparator.comparing(Book::isbn)).toList();
        }

        List<Book> searchByTitle(String keyword) {
            String normalized = text(keyword, "关键词").toLowerCase(Locale.ROOT);
            return listAll().stream()
                    .filter(book -> book.title().toLowerCase(Locale.ROOT).contains(normalized))
                    .toList();
        }

        void borrow(String isbn) {
            Book book = require(isbn);
            if (book.status() != BookStatus.AVAILABLE) {
                throw new IllegalStateException("图书已被借出: " + isbn);
            }
            books.put(book.isbn(), book.withStatus(BookStatus.BORROWED));
        }

        void giveBack(String isbn) {
            Book book = require(isbn);
            if (book.status() != BookStatus.BORROWED) {
                throw new IllegalStateException("图书尚未借出: " + isbn);
            }
            books.put(book.isbn(), book.withStatus(BookStatus.AVAILABLE));
        }
    }

    static Library load(Path file) throws IOException {
        if (Files.isSymbolicLink(file)) {
            throw new IOException("数据路径不能是符号链接");
        }
        List<String> lines;
        try {
            lines = Files.readAllLines(file, StandardCharsets.UTF_8);
        } catch (NoSuchFileException e) {
            return new Library(); // 仅“没有文件”代表首次启动；权限/解码错误继续抛出。
        }
        if (lines.isEmpty() || !lines.getFirst().equals("dev-quest-books-v1")) {
            throw new IOException("存储格式或版本不正确");
        }
        Library result = new Library();
        for (int i = 1; i < lines.size(); i++) {
            try {
                result.add(Book.fromTsv(lines.get(i)));
            } catch (IllegalArgumentException e) {
                throw new IOException("第 " + (i + 1) + " 行无效: " + e.getMessage(), e);
            }
        }
        return result; // 全部解析成功后才交给调用者，不返回半加载结果。
    }

    static void save(Path file, Library library) throws IOException {
        List<String> lines = new ArrayList<>();
        lines.add("dev-quest-books-v1");
        library.listAll().forEach(book -> lines.add(book.toTsv()));
        Path temp = Files.createTempFile(file.getParent(), ".books-", ".tmp");
        try {
            Files.write(temp, lines, StandardCharsets.UTF_8);
            // 不支持原子移动时抛出异常；不能降级为直接截断原文件。
            Files.move(temp, file, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
        } finally {
            Files.deleteIfExists(temp);
        }
    }

    static void arity(String[] args, int expected) {
        if (args.length != expected) {
            throw new IllegalArgumentException("参数数量错误；用法: java Main <数据文件> <命令> [参数]");
        }
    }

    static boolean dispatch(Library library, String[] args) {
        switch (args[1]) {
            case "add" -> {
                arity(args, 6);
                library.add(new Book(args[2], args[3], args[4], Integer.parseInt(args[5]), BookStatus.AVAILABLE));
            }
            case "borrow" -> { arity(args, 3); library.borrow(args[2]); }
            case "return" -> { arity(args, 3); library.giveBack(args[2]); }
            case "find" -> {
                arity(args, 3);
                System.out.println(library.require(args[2]).toTsv());
                return false;
            }
            case "search" -> {
                arity(args, 3);
                library.searchByTitle(args[2]).forEach(book -> System.out.println(book.toTsv()));
                return false;
            }
            case "list" -> {
                arity(args, 2);
                library.listAll().forEach(book -> System.out.println(book.toTsv()));
                return false;
            }
            default -> throw new IllegalArgumentException("未知命令: " + args[1]);
        }
        return true;
    }

    public static void main(String[] args) {
        int exitCode = 0;
        try {
            if (args.length < 2) {
                throw new IllegalArgumentException("用法: java Main <数据文件> add|find|search|borrow|return|list [参数]");
            }
            Path file = Path.of(args[0]).toAbsolutePath().normalize();
            if (Files.exists(file, LinkOption.NOFOLLOW_LINKS)
                    && !Files.isRegularFile(file, LinkOption.NOFOLLOW_LINKS)) {
                throw new IOException("数据路径必须是普通文件");
            }
            Path lockFile = file.resolveSibling(file.getFileName() + ".lock");
            try (FileChannel channel = FileChannel.open(lockFile, StandardOpenOption.CREATE, StandardOpenOption.WRITE);
                 var lock = channel.lock()) {
                Library library = load(file);
                if (dispatch(library, args)) {
                    save(file, library);
                    System.out.println("已保存"); // 磁盘提交成功才报告成功。
                }
            }
        } catch (IOException | IllegalArgumentException | IllegalStateException e) {
            System.err.println("操作失败: " + e.getMessage());
            exitCode = 1;
        }
        System.exit(exitCode);
    }
}
```

## 3. 编译、运行和重启

确认 `java -version` 和 `javac -version` 都为 21 或更高。`--release 21` 把示例限定在 Java 21 API 与语言级别，不需要 preview 参数。

```bash
javac --release 21 -encoding UTF-8 Main.java
java Main books.tsv add 978-1 "Java; 入门" "Alice" 2024
java Main books.tsv add 978-2 "并发基础" "Bob" 2023
java Main books.tsv list
java Main books.tsv borrow 978-1
java Main books.tsv find 978-1
java Main books.tsv return 978-1
java Main books.tsv search Java
```

`add`、`borrow`、`return` 成功时输出 `已保存`。第一次 `find 978-1` 应以 `BORROWED` 结尾；归还后应是 `AVAILABLE`。每个命令都是新 JVM 进程，因此后续读取证明状态来自磁盘。

数据文件相对当前工作目录定位。锁文件 `books.tsv.lock` 可以一直保留；进程退出会释放锁，**不要在运行中删除锁文件**。不同进程必须使用同一实际目录与路径，避免符号链接别名绕开锁。

## 4. 为什么这样组织

`record` 自动生成访问器、相等性等方法，但不会自动校验字段；紧凑构造器负责拒绝非法状态。`withStatus` 返回新值，其他引用不会被偷偷修改。

`Optional<Book>` 表示查询可能没有结果；`require` 只在“必须存在”的动作上把缺失转为异常。重复借出和重复归还都会失败，读者不必猜测重复命令是成功、忽略还是异常。

`Locale.ROOT` 避免默认语言环境改变大小写转换，例如土耳其语环境的 `I`。搜索只是 Unicode 小写后的子串匹配，不是完整的自然语言检索或无重音搜索。

锁覆盖“加载 → 检查 → 更新 → 保存”，防止两个遵循协议的进程从旧文件开始并相互覆盖。`HashMap.putIfAbsent` 只简化当前线程中的防重复，并不让 `HashMap` 变成并发集合。固定锁文件与数据文件分开，因为数据文件保存时会被替换。

写临时文件后移动，使新内容准备完成前原文件仍然存在。本例要求文件系统支持原子移动；Java 对 `ATOMIC_MOVE` 下目标已存在的处理保留了提供者差异，替换已有文件也必须在目标平台实测。[Files.move 官方契约](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/nio/file/Files.html#move(java.nio.file.Path,java.nio.file.Path,java.nio.file.CopyOption...)) 说明了这些边界。失败时返回 1，不采用更弱的覆盖方式兜底。

本练习适用于受控本地目录，不包含数据库事务、断电落盘保证或网络文件系统并发保证。内存能否加载全部图书也是规模约束；共享服务和大量记录应引入数据库。

## 5. 验收矩阵

用独立测试文件执行失败案例，操作前后比较数据文件字节或 SHA-256。Bash 看 `$?`，PowerShell 看 `$LASTEXITCODE`。

| 场景 | 预期 |
|---|---|
| 新增、借出、退出、查询、归还、再次查询 | 每次启动后状态正确 |
| 同一 ISBN 新增两次 | 第二次退出 1；原记录不变 |
| 借出未知 ISBN、重复借出或重复归还 | 退出 1；存储字节不变 |
| 年份 `abc`、空白标题、额外参数 | 退出 1，不报告已保存 |
| 标题含 `;`、引号、中文 | 重启后完整保留；含制表符/换行则拒绝 |
| 损坏头部、缺字段、未知状态、重复 ISBN、非法 UTF-8 | 加载失败；新增不能覆盖原文件 |
| 数据路径是目录，或父目录不可写 | 退出 1；原数据保留 |
| 多个进程同时新增不同书号 | 所有成功提交的书都保留 |

[首项目验证器](../../shared-resources/tools/document-quality/verify_php_java_projects.py) 直接抽取本篇程序，编译后通过真实 CLI 执行；[报告](../../shared-resources/tools/document-quality/reports/php-java-projects.md) 给出实测范围。通过只证明报告中的环境与案例，不代表所有平台文件系统行为相同。

## 失败回查与下一步

编译失败时先核对第 3 节两个版本命令与 `--release 21`，工具链缺失回 [环境搭建](./01-environment-setup.md)。重启后查不到书，先核对命令的当前目录和 `books.tsv` 实际路径；输入错误仍输出“已保存”，沿 `main` 的异常出口回查 [异常处理](./06-exceptions.md)。原子移动失败则按第 4 节检查目标文件系统，保留失败信息和原数据，不跳过保存错误继续验收。

保存第 5 节的命令、退出码及文件前后对比结果后，阅读 [Spring Boot 入门](../frameworks/01-spring-boot-basics.md)，再进入 [TODO REST API](../projects/01-todo-api.md)。下一项目先将命令参数换为 HTTP 请求并验证校验、状态码与错误响应；它使用内存存储，重启会清空数据，与本课的 TSV 持久化边界不同。迁移领域规则时先保持非法输入不修改状态，再按下一项目指引接入数据库。

## 6. 递进练习

1. **拆文件**：把 `Book`、`BookStatus`、`Library` 移入同一包的独立源文件。保持输出和失败契约，重新运行验收矩阵。
2. **删除**：实现 `remove`，先规定借出中的书能否删除，再测试未知 ISBN 与重复删除。
3. **菜单**：菜单负责收集参数，复用领域方法；输入结束（EOF）应正常退出，不能把 `Scanner.nextLine()` 失败无限重试。
4. **数据库**：将 ISBN 设为唯一键，在事务中更新借阅状态；用两个客户端同时借一本书，确认最多一个成功。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [标准库核心](../reference/library-guides/01-standard-library.md) · [通用术语](../../shared-resources/glossary.md)
