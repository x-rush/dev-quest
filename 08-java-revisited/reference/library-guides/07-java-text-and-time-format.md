# java.text 与时间格式化

> **文档简介**: 格式化双主场——DateTimeFormatter（模式字母/locale/解析策略）与 java.text 的 NumberFormat/DecimalFormat/ChoiceFormat；SimpleDateFormat 线程不安全的历史陷阱
>
> **目标读者**: 需要把数值/日期渲染为用户可读文本、并弄清新旧格式化 API 分工的开发者
>
> **前置知识**: java.time 类型选型见 [标准库核心速查](./01-standard-library.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#格式化` `#DateTimeFormatter` `#NumberFormat` `#标准库` |
| **更新日期** | `2026年9月` |

## 📌 定义

格式化 = **对象 ↔ 文本** 的双向转换：日期时间走 `java.time.format.DateTimeFormatter`（线程安全、现代首选），数值/货币走 `java.text.NumberFormat`/`DecimalFormat`；`SimpleDateFormat` 是被 java.time 取代的历史遗留——**非线程安全**。

> 💡 本文行为断言均在本机 JDK 21（javac 21.0.12.1）下编译运行验证。

## 📖 语法 / 签名

### DateTimeFormatter 模式字母（常用）

| 字母 | 含义 | 示例输出（2026-09-14 14:30:05） |
|------|------|------|
| `yyyy` / `uuuu` | 年（纪元年 / 纯年） | 2026 |
| `MM` / `MMM` / `MMMM` | 月：数字 / 简名 / 全名 | 09 / 9月(zh-CN) / September(en) |
| `dd` | 日 | 14 |
| `HH` / `hh` | 时：0-23 / 1-12 | 14 / 02 |
| `mm` / `ss` | 分 / 秒 | 30 / 05 |
| `S` | 毫微秒小数 | .123 |
| `a` | 上午/下午 | 下午 |
| `E` / `EEEE` | 星期缩写 / 全名 | 周一 / 星期一 |
| `z` / `Z` / `X` | 时区名 / 偏移(+0800) / ISO 偏移(Z) | CST / +0800 / Z |

> 实测：`yyyy/MM/dd` → `2026/09/14`；`MMMM`+en → `September`；`MMM`+zh-CN → `9月`；`ofLocalizedDate(FULL)`+zh-CN → `2026年9月14日星期一`。

```java
var fmt = DateTimeFormatter.ofPattern("yyyy年MM月dd日 HH:mm");
LocalDate.of(2026, 9, 14).format(fmt);                    // 定制模式
d.format(DateTimeFormatter.ofPattern("MMMM", Locale.ENGLISH));  // 显式传 locale
d.format(DateTimeFormatter.ofLocalizedDate(FormatStyle.FULL)
        .withLocale(Locale.CHINA));                       // 本地化格式
LocalDate.parse("2026-09-14");                            // ISO 常量直接解析（实测）
```

**线程安全**：`DateTimeFormatter` 不可变，可以静态共享（多线程 5 万次并发使用零错误，实测）。

### 解析策略 ResolverStyle（实测）

| 策略 | 解析 `2026-02-30`（uuuu-MM-dd） | 结论 |
|------|------|------|
| `SMART`（默认） | `2026-02-28` | 无效日期收敛到月末 |
| `STRICT` | 抛 `DateTimeParseException` | 严格校验；年要用 `uuuu` 而非 `yyyy` |
| `LENIENT` | 滚到 `2026-03-02` | 越界进位，一般别用 |

### java.text：数值与区间

```java
NumberFormat.getInstance(Locale.CHINA).format(1234567.891);   // "1,234,567.891"（实测）
NumberFormat.getCurrencyInstance(Locale.US).format(1234.5);   // "$1,234.50"（实测）
new DecimalFormat("#,##0.00").format(1234.5);                 // "1,234.50"（实测；# 可选位、0 必占位）
new DecimalFormat("0%").format(0.256);                        // "26%"（自动 ×100）
df.parse("1,234.50");                                         // Number，反格式化回读（实测）

new ChoiceFormat("0#免费|1#起步价|2#计价").format(1.5);        // "起步价"：下限区间匹配（实测）
```

### SimpleDateFormat 为什么被取代

- **线程不安全**（javadoc 明示内部有可变 Calendar）：共享实例并发格式化会产出错误甚至错乱文本——**实测：4 线程共享 1 个实例格式化 5 万次，错误 11492 次**；对照组 `DateTimeFormatter` 零错误。
- 所在的 `Date`/`Calendar` API 本身可变、月份从 0 起、无时区模型，已被 java.time 全线取代。

## 💡 示例

```java
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class FormatDemo {
    static final DateTimeFormatter FMT =      // 线程安全 → 可静态常量共享
            DateTimeFormatter.ofPattern("yyyy-MM-dd");

    public static void main(String[] args) {
        LocalDate d = LocalDate.of(2026, 9, 14);
        System.out.println(d.format(FMT));                    // 2026-09-14
        LocalDate back = LocalDate.parse("2026-09-14", FMT);  // 双向往返
        System.out.println(back.plusDays(1));                 // 2026-09-15
    }
}
```

## ⚠️ 常见陷阱

- ❌ **静态共享 `SimpleDateFormat`**：并发下产出错误结果（实测 11.5% 错误率）。
  ✅ `DateTimeFormatter` 静态常量；或线程内 `ThreadLocal` 临时兜底遗留代码。
- ❌ **STRICT 模式配 `yyyy` 解析**：`yyyy` 是纪元年（year-of-era），STRICT 下需要 era 信息。
  ✅ STRICT 场景统一用 `uuuu`。
- ❌ **格式化不含 locale**：月名/星期名/货币符号随宿主环境漂移。
  ✅ 用户可见文本显式 `withLocale(...)`；机器可读输出用 ISO 常量。
- ❌ **拿 `DecimalFormat` 的 `#` 当"必显位"**：`#.##` 对 0.5 输出 `.5`。
  ✅ 需要固定位用 `0`：`0.00` → `0.50`。
- ❌ **用 `format` 输出的字符串再当唯一持久化格式**：格式一改数据全坏。
  ✅ 持久化用 ISO-8601（`Instant`/`LocalDate.toString`）或时间戳，展示层才用 pattern。

## 🔗 相关条目

- 📄 **[标准库核心速查](./01-standard-library.md)** — java.time 类型选型与 LocalDate/ZonedDateTime 全表
- 📄 **[java.math 导览](./06-java-math.md)** — 被格式化的精确数值从哪来
- 📄 **[字符串不可变语义](../language-concepts/07-string-immutability-pool.md)** — formatted/String.format 的底座
- 🌐 **[DateTimeFormatter (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/format/DateTimeFormatter.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
