# java.math 导览

> **文档简介**: 任意精度数值——BigDecimal 的 scale/精度/舍入模式全表、compareTo vs equals 陷阱、除法必须指定舍入、BigInteger、MathContext
>
> **目标读者**: 需要精确数值计算（金额、比例、大整数）的开发者
>
> **前置知识**: 基本类型与浮点陷阱见 [变量与类型](../../basics/03-variables-types.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#BigDecimal` `#BigInteger` `#精确计算` `#标准库` |
| **更新日期** | `2026年9月` |

</details>

## 📌 定义

`java.math` 提供**十进制精确**数值类型：`BigDecimal`（任意精度十进制数，适用于明确精度与舍入规则的计算）与 `BigInteger`（任意大小整数），配套 `RoundingMode` 舍入模式与 `MathContext` 精度上下文。核心模型：值 = `unscaledValue × 10^(-scale)`。

> 示例给出预期行为与规范依据。本轮环境未提供 Java 编译器，未复现历史运行记录；请在项目约定 JDK 上编译验证。

## 📖 语法 / 签名

### 构造三选一（预期）

| 写法 | 结果 | 结论 |
|------|------|------|
| `new BigDecimal("0.1")` | 精确的 0.1 | ✅ 首选 |
| `BigDecimal.valueOf(0.1)` | 等价字符串构造（走 `Double.toString`） | ✅ double 值入库时用 |
| `new BigDecimal(0.1)` | `0.1000000000000000055511151231257827...`（scale 55） | ❌ 二进制误差原样带入 |

### precision vs scale（预期）

```java
new BigDecimal("120.00").precision();   // 5：有效数字位数
new BigDecimal("120.00").scale();       // 2：小数位数
new BigDecimal("120.00").stripTrailingZeros();
// 1.2E+2，scale 从 2 变 -1（预期）
```

### RoundingMode 全表（2.5 / -2.5 舍到 0 位，预期行为）

| RoundingMode | 2.5 | -2.5 | 语义 |
|--------------|-----|------|------|
| `HALF_UP` | 3 | -3 | 四舍五入（最常见的"教学舍入"） |
| `HALF_EVEN` | 2 | -2 | 恰好中点时取相邻偶数，减少某些重复舍入中的方向偏差 |
| `HALF_DOWN` | 2 | -2 | 取最近值，恰好中点时向零 |
| `UP` | 3 | -3 | 远离零 |
| `DOWN` | 2 | -2 | 趋向零（截断） |
| `CEILING` | 3 | -2 | 向正无穷 |
| `FLOOR` | 2 | -3 | 向负无穷 |
| `UNNECESSARY` | 抛异常 | 抛异常 | 断言无需舍入，非精确时抛 `ArithmeticException`（预期） |

### 核心方法

```java
// equals 连 scale 一起比（预期）
new BigDecimal("1.0").equals(new BigDecimal("1.00"));      // false！
new BigDecimal("1.0").compareTo(new BigDecimal("1.00"));   // 0：数值比较 ✅

// 除不尽必须指定舍入（预期）
new BigDecimal("1").divide(new BigDecimal("3"));
// ArithmeticException: Non-terminating decimal expansion; no exact representable decimal result.
new BigDecimal("1").divide(new BigDecimal("3"), 4, RoundingMode.HALF_UP);  // 0.3333
new BigDecimal("1").divide(new BigDecimal("3"), MathContext.DECIMAL128);   // 34 位精度

// 字符串构造才能拿到十进制的 1.005（预期）
new BigDecimal("1.005").setScale(2, RoundingMode.HALF_UP);  // 1.01
new BigDecimal(1.005).setScale(2, RoundingMode.HALF_UP);    // 1.00（二进制误差先入为主）
```

### BigInteger 与 MathContext

```java
BigInteger.valueOf(2).pow(100);                 // 31 位整数，超 long 无压力（预期）
BigInteger.valueOf(-7).remainder(BigInteger.valueOf(3));   // -1：符号随被除数（预期）
BigInteger.valueOf(-7).mod(BigInteger.valueOf(3));         //  2：模数必须为正，结果非负（预期）
BigInteger.valueOf(12).gcd(BigInteger.valueOf(18));        // 6

MathContext.DECIMAL32 / DECIMAL64 / DECIMAL128 / UNLIMITED   // 精度上下文常量
BigDecimal.TWO                               // Java 19+ 常量（预期）
```

## 💡 示例

```java
import java.math.BigDecimal;
import java.math.RoundingMode;

public class MoneyDemo {
    public static void main(String[] args) {
        BigDecimal price = new BigDecimal("19.99");
        BigDecimal qty   = BigDecimal.valueOf(3);
        BigDecimal total = price.multiply(qty)
                                .setScale(2, RoundingMode.HALF_EVEN);
        System.out.println(total);                              // 59.97
        System.out.println(total.compareTo(BigDecimal.ZERO));   // 1（>0）
        // BigDecimal 不可变：add/multiply 返回结果且不修改原对象，不承诺每次新分配
    }
}
```

## ⚠️ 常见陷阱

- ❌ **用 `equals` 判数值相等**：连 scale 一起比，`1.0` 与 `1.00` 不等（预期）。
  ✅ `compareTo(...) == 0`；要归一 scale 用 `stripTrailingZeros()`。
- ❌ **`new BigDecimal(double)`**：把 double 的二进制误差原样带入（预期 0.1 → 55 位小数）。
  ✅ 字符串构造或 `BigDecimal.valueOf(double)`。
- ❌ **`divide` 不指定舍入**：除不尽直接抛 `ArithmeticException`（预期原文见上）。
  ✅ 需要可舍入结果时给 scale + RoundingMode 或有限精度 MathContext；若要求精确除法，可以保留失败并处理。
- ❌ **用 double 做钱再转 BigDecimal**：误差在转之前已发生（预期 1.005 舍出 1.00）。
  ✅ 全链路 BigDecimal（或最小单位 long 分/厘）。
- ❌ **以为 BigDecimal 可变、原地修改**：算术方法不修改原对象，必须使用返回结果。
  ✅ 必须接住返回值：`x = x.add(y)`。

<!-- full-library-explanation -->
## 精确表示不等于已经定义业务舍入规则

BigDecimal 保存未缩放整数与 scale，因此 1.0 和 1.00 数值相同，却有不同表示。HashSet 根据 equals 区分它们，按自然顺序的 TreeSet 根据 compareTo 将它们视为同一排序键；选择集合前先确定业务想比较数值还是表示。

scale 描述十进制缩放，precision 描述有效数字位数。MathContext 的 4 位精度不是小数点后 4 位。舍入应放在明确的业务边界：三份各 0.005 的费用，逐项舍到两位再求和，与先求和再舍入可能不同。类型只能按你指定的规则计算，不能替你选择规则。

**练习**：分别计算上述两种总和并写明预期；再用 1÷8 与 1÷3 对照无舍入 divide，前者可精确结束，后者应失败。HALF_DOWN 是取最近值、恰好中点向零，例如 2.51 舍到整数仍是 3，不是看到首位小数为 5 就舍去。金额也可按明确最小单位使用整数，但要同时规定币种、范围和溢出处理。

## 🔗 相关条目

- 📄 **[标准库核心速查](./01-standard-library.md)** — 数值类型速查段
- 📄 **[java.text 与时间格式化](./07-java-text-and-time-format.md)** — BigDecimal 的展示层 NumberFormat/DecimalFormat
- 📄 **[变量与类型](../../basics/03-variables-types.md)** — double/float 浮点陷阱根源
- 🌐 **[BigDecimal (Javadoc 21)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/math/BigDecimal.html)** — 权威来源

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
