# TypeScript 类型模式 — RN 工程实践

> **难度**: ⭐⭐ | **前置**: TS 基础 + React Navigation 使用经验

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 字典 |
| **难度** | ⭐⭐ |
| **标签** | `#TypeScript` `#类型推导` `#Codegen` `#泛型` |
| **更新日期** | `2026年9月` |

</details>

## 模式一：导航参数类型（ParamList）

### 描述
把"路由名 → 参数"映射声明成一个对象类型，让 `navigate`/`route.params` 获得全链路类型推导。

### 语法和示例
```tsx
// types/navigation.ts —— 全局唯一，集中维护
export type RootStackParamList = {
  Home: undefined;
  Detail: { itemId: string; from?: 'home' | 'search' };
  Edit: { id?: string } | undefined;  // 可选参数
};

// 为 useNavigation 补全类型
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
```

```tsx
// 组件侧：Props 类型直接由 Screen 类型导出
import type { NativeStackScreenProps } from '@react-navigation/native-stack';

type DetailProps = NativeStackScreenProps<RootStackParamList, 'Detail'>;

export default function Detail({ route, navigation }: DetailProps) {
  const { itemId, from } = route.params; // 自动推导，无需断言
  // 导航应由事件触发，不能在每次渲染时无条件跳转。
  return null;
}
```

### 陷阱
- ParamList 必须与 Screen 注册名一致，拼写错误编译期即可暴露——这是类型化的最大收益
- Tabs/Drawer 各自的 ParamList 分别声明再嵌套引用

## 模式二：组件 Props 与样式类型

### 描述
RN 组件的样式类型来自 `react-native` 导出的 `StyleProp<T>` 系列，不要手写 `{ width: number }` 这类残缺类型。

### 语法和示例
```tsx
import type { ReactNode } from 'react';
import { StyleSheet, type StyleProp, type ViewStyle, type TextStyle } from 'react-native';

interface CardProps {
  title: string;
  children?: ReactNode;
  style?: StyleProp<ViewStyle>;       // 兼容数组样式
  titleStyle?: StyleProp<TextStyle>;
  onPress?: () => void;
}

export function Card({ title, children, style }: CardProps) {
  return null;
}

// StyleSheet.create 返回值自动获得字面量类型，供其他文件引用
const styles = StyleSheet.create({
  card: { padding: 12 },
});
export type CardStyle = typeof styles.card;
```

### 陷阱
- `StyleSheet.create` 的对象不要标 `any`，否则失去拼写检查
- 从组件导出样式类型（`typeof styles.x`）比重复手写更不易漂移

## 模式三：列表 Item 的判别联合

### 描述
混合类型列表（如"待办 + 分组标题 + 广告位"）用判别联合 + 收窄，渲染时类型安全。

### 语法和示例
```tsx
type Row =
  | { kind: 'todo'; id: string; title: string; done: boolean }
  | { kind: 'header'; id: string; label: string }
  | { kind: 'ad'; id: string; imageUrl: string };

const keyExtractor = (r: Row) => r.id;

const renderItem = ({ item }: { item: Row }) => {
  switch (item.kind) {
    case 'todo':   return <TodoRow title={item.title} done={item.done} />;
    case 'header': return <HeaderRow label={item.label} />;
    case 'ad':     return <AdRow uri={item.imageUrl} />;
  }
};
```

### 陷阱
- `kind` 字段是判别键，必须字面量类型；写成 `string` 会丢失收窄能力

## 模式四：Context 的非空安全封装

### 描述
用"Provider + 自定义 Hook + 非空校验"三件套，让 useContext 不返回 `null`。

### 语法和示例
```tsx
const Ctx = createContext<State | null>(null);

export function useApp() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useApp 必须在 Provider 内使用'); // fail fast
  return ctx;
}
```

### 陷阱
- 模块级 createContext 的默认对象不会每次渲染重建；若缺少 Provider 属于错误，可用 null + 抛错显式暴露
- Hook 抛错信息写清 Provider 名称，降低排障成本

## 模式五：TurboModule 规约（Codegen）

### 描述
新架构下用 TypeScript 规约（Spec）声明原生接口，Codegen 据此生成受支持平台的接口代码，RNOH 的生成与注册须核对其工具链——类型即契约。

### 语法和示例
```ts
// NativeBattery.ts —— 必须放在被 codegenConfig 扫描的目录
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  getLevel(): Promise<number>;              // Promise 参数自动映射
  addListener(eventName: string): void;     // 事件模块固定写法
  removeListeners(count: number): void;
}

export default TurboModuleRegistry.getEnforcing<Spec>('Battery');
```

```json
// package.json 中的 codegen 配置
{
  "codegenConfig": {
    "name": "RNBatterySpec",
    "type": "modules",
    "jsSrcsDir": "src/specs"
  }
}
```

### 陷阱
- Spec 文件不能使用泛型；支持的类型范围以 Codegen 文档为准
- `jsSrcsDir` 路径写错时 Codegen 静默跳过，表现为原生方法 undefined

## 模式六：平台分支值的类型收窄

### 描述
`Platform.select` 的结果类型可用泛型参数显式标注，避免推断出宽泛类型。

### 语法和示例
```tsx
type Theme = 'light' | 'dark';
const initialTheme: Theme = Platform.select<Theme>({
  ios: 'light',
  android: 'dark',
  default: 'light',
});
```

<!-- full-library-explanation -->
## 类型约束在哪一刻有效

ParamList 检查你写出的导航调用；服务端 JSON、深链和磁盘旧数据进入程序时没有自动获得该保证。`as DetailParams` 只是告诉编译器相信你，不会拒绝空 ID。对外部值先校验，再构造内部类型。

```ts
// 纯 TypeScript，可在 strict 模式下单独检查
type DetailParams = { id: string };
function parseDetail(input: unknown): DetailParams | null {
  if (typeof input !== 'object' || input === null || !('id' in input)) return null;
  return typeof input.id === 'string' && input.id.trim() !== ''
    ? { id: input.id } : null;
}
console.log(parseDetail({ id: '42' }), parseDetail({ id: 42 }));
// { id: '42' }、null
```

### 可直接提取的运行案例

该程序只验证外部参数进入内部形状前的 JavaScript 检查；React Navigation 的 `ParamList` 编译期约束和设备导航行为不在此范围。

```js
function parseDetail(input) {
  if (typeof input !== 'object' || input === null || !('id' in input)) return null;
  return typeof input.id === 'string' && input.id.trim() !== '' ? { id: input.id } : null;
}

const actual = [parseDetail({ id: '42' }), parseDetail({ id: 42 }), parseDetail({ id: '  ' }), parseDetail(null)];
const expected = [{ id: '42' }, null, null, null];
if (JSON.stringify(actual) !== JSON.stringify(expected)) throw new Error(JSON.stringify(actual));
console.log('Detail parameter boundary contracts passed');
```

练习：新增 Row 的 `loading` 分支，令 switch 的 default 调用接收 never 的穷尽检查函数。验收：遗漏新分支会得到编译错误；将网络响应改成错误形状时，由解析函数返回可处理的失败，而不是依赖编译器发现运行时数据问题。

## 🔗 相关文档

- 📄 **[Hooks 速查](./03-hooks-reference.md)**: 自定义 Hook 与类型结合
- 📄 **[React Navigation API 速查](../framework-essentials/02-navigation-essentials.md)**: ParamList 的运行时对应物
- 📄 **[原生模块桥接教程](../../basics/06-native-modules.md)**: Codegen 的完整实操流程
- 📄 **[故障排除](../quick-references/02-troubleshooting.md)**: 类型相关构建报错

*相关教程: [导航类型推导实战](../../basics/05-navigation.md)*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
