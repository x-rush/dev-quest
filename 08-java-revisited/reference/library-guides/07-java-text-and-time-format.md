# java.text 与时间格式化

> **文档简介**: 格式化双主场——DateTimeFormatter（模式字母/locale/解析策略）与 java.text 的 NumberFormat/DecimalFormat/ChoiceFormat；SimpleDateFormat 线程不安全的历史陷阱
>
> **目标读者**: 需要把数值/日期渲染为用户可读文本、并弄清新旧格式化 API 分工的开发者
>
> **前置知识**: java.time 类型选型见 [标准库核心速查](./01-standard-library.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#格式化` `#DateTimeFormatter` `#NumberFormat` `#标准库` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

格式化 = **对象 ↔ 文本** 的双向转换：日期时间走 `java.time.format.DateTimeFormatter`（线程安全、现代首选），数值/货币走 `java.text.NumberFormat`/`DecimalFormat`；`SimpleDateFormat` 是被 java.time 取代的历史遗留——**非线程安全**。

> 示例给出预期行为与规范依据。本轮环境未提供 Java 编译器，未复现历史运行记录；请在项目约定 JDK 上编译验证。

## 📖 语法 / 签名

### DateTimeFormatter 模式字母（常用）

| 字母 | 含义 | 示例输出（2026-09-14 14:30:05） |
|------|------|------|
| `yyyy` / `uuuu` | 年（纪元年 / 纯年） | 2026 |
| `MM` / `MMM` / `MMMM` | 月：数字 / 简名 / 全名 | 09 / 9月(zh-CN) / September(en) |
| `dd` | 日 | 14 |
| `HH` / `hh` | 时：0-23 / 1-12 | 14 / 02 |
| `mm` / `ss` | 分 / 秒 | 30 / 05 |
| `S`（个数 = 位数） | 小数秒（纳秒小数部分，不带点；`.123` 带点须模式写 `.SSS`） | `S`→`1`、`SSS`→`123`、`.SSS`→`.123`（以 .123456789 计，预期） |
| `a` | 上午/下午 | 下午 |
| `E` / `EEEE` | 星期缩写 / 全名 | 周一 / 星期一 |
| `z` / `Z` / `X` | 时区名 / 偏移(+0800) / ISO 偏移(Z) | CST / +0800 / Z |

> 预期：`yyyy/MM/dd` → `2026/09/14`；`MMMM`+en → `September`；`MMM`+zh-CN → `9月`；`ofLocalizedDate(FULL)`+zh-CN → `2026年9月14日星期一`。

```java
var fmt = DateTimeFormatter.ofPattern("yyyy年MM月dd日 HH:mm");
java.time.LocalDateTime.of(2026, 9, 14, 14, 30).format(fmt);                    // 定制模式
d.format(DateTimeFormatter.ofPattern("MMMM", Locale.ENGLISH));  // 显式传 locale
d.format(DateTimeFormatter.ofLocalizedDate(FormatStyle.FULL)
        .withLocale(Locale.CHINA));                       // 本地化格式
LocalDate.parse("2026-09-14");                            // ISO 常量直接解析（预期）
```

**线程安全**：`DateTimeFormatter` 不可变，可以静态共享（不可变性与线程安全属于其 API 契约）。

### 解析策略 ResolverStyle（预期）

| 策略 | 解析 `2026-02-30`（uuuu-MM-dd） | 结论 |
|------|------|------|
| `SMART`（ofPattern 默认） | `2026-02-28` | 无效日期收敛到月末 |
| `STRICT` | 抛 `DateTimeParseException` | 严格校验；年要用 `uuuu` 而非 `yyyy` |
| `LENIENT` | 滚到 `2026-03-02` | 越界进位，一般别用 |

### java.text：数值与区间

```java
NumberFormat.getInstance(Locale.CHINA).format(1234567.891);   // "1,234,567.891"（预期）
NumberFormat.getCurrencyInstance(Locale.US).format(1234.5);   // "$1,234.50"（预期）
new DecimalFormat("#,##0.00").format(1234.5);                 // "1,234.50"（预期；# 可选位、0 必占位）
new DecimalFormat("0%").format(0.256);                        // "26%"（自动 ×100）
df.parse("1,234.50");                                         // Number，反格式化回读（预期）

new ChoiceFormat("0#免费|1#起步价|2#计价").format(1.5);        // "起步价"：下限区间匹配（预期）
```

### SimpleDateFormat 为什么被取代

- **线程不安全**（javadoc 明示内部有可变 Calendar）：共享实例并发格式化会产出错误甚至错乱文本——具体失败频率取决于并发时序，不应引用缺少代码与环境的固定数字。
- 所在的 `Date`/`Calendar` API 本身可变，Calendar 的月份通常从 0 起且有时区模型；Date 表示时间点但旧访问方法容易混淆本地时区，已被 java.time 全线取代。

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

- ❌ **静态共享 `SimpleDateFormat`**：并发下产出错误结果（不能依赖某个固定错误率判断安全）。
  ✅ `DateTimeFormatter` 静态常量；或线程内 `ThreadLocal` 临时兜底遗留代码。
- ❌ **STRICT 模式配 `yyyy` 解析**：`yyyy` 是纪元年（year-of-era），STRICT 下需要 era 信息。
  ✅ STRICT 场景统一用 `uuuu`。
- ❌ **格式化不含 locale**：月名/星期名/货币符号随宿主环境漂移。
  ✅ 用户可见文本显式 `withLocale(...)`；机器可读输出用 ISO 常量。
- ❌ **以为 `#` 会把整数位的 0 一并省掉**：`#.##` 对 0.5 输出的是 `0.5`（`#` 只省略多余的小数位 0，整数位至少保留一位；连前导 0 都不要时模式写 `.##` 才输出 `.5`）。
  ✅ 需要固定位用 `0`：`0.00` → `0.50`。
- ❌ **用 `format` 输出的字符串再当唯一持久化格式**：格式一改数据全坏。
  ✅ 持久化用 ISO-8601（`Instant`/`LocalDate.toString`）或时间戳，展示层才用 pattern。

<!-- full-library-explanation -->
## 时间类型先决定能表达什么，再选格式

LocalDate 只有年月日，无法格式化小时；LocalDateTime 包含本地日期和时间，但仍没有时区，不能单独确定全球时间轴上的某一瞬间。Instant 表示瞬间，展示给用户时再结合 ZoneId。跨夏令时的本地时间可能不存在或对应两个瞬间，需要业务明确处理。

给用户看的月份、货币和数字分组受 Locale 影响；机器接口则应约定固定格式和严格解析。DateTimeFormatter.ofPattern 默认 SMART，而 ISO_LOCAL_DATE 采用严格解析，不能把所有 formatter 的默认策略混为一谈。yyyy 是纪元年，uuuu 是历法年，YYYY 是基于周的年，年末日期可能不同。

**练习**：用 STRICT 的 uuuu-MM-dd 解析 2024-02-29 与 2025-02-29，前者成功、后者失败；把同一 Instant 分别转为 UTC 与 Asia/Shanghai，日期可能不同但瞬间相同。NumberFormat.parse 可能只消费文本前缀，验证输入时还要检查 ParsePosition 到达末尾。DecimalFormat 与 SimpleDateFormat 都是可变对象，不要无同步共享实例。

## 🔗 相关条目

- 📄 **[标准库核心速查](./01-standard-library.md)** — java.time 类型选型与 LocalDate/ZonedDateTime 全表
- 📄 **[java.math 导览](./06-java-math.md)** — 被格式化的精确数值从哪来
- 📄 **[字符串不可变语义](../language-concepts/07-string-immutability-pool.md)** — formatted/String.format 的底座
- 🌐 **[DateTimeFormatter (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/time/format/DateTimeFormatter.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
