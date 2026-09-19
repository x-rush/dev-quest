# 实战项目二 — 天气应用（网络 + 定位）

## 分阶段练习与验收

**最小阶段**：在可启动的 Expo + TypeScript 项目中安装下文依赖，把页面放在 Expo Router 的 `app/index.tsx`、Hook 放在根目录 `hooks/usePosition.ts`。先按“使用北京”按钮取得天气，再按“使用当前位置”请求权限。已有 Router 布局保留；示例 Provider 包住这一页即可，不要再套第二个同用途 Provider。

**验收结果**：拒绝定位仍能手选城市；断网显示错误或明确标记的旧数据。

**扩展顺序**：后台定位与复杂缓存放后，先覆盖权限和数据来源。

最小产物是能手选北京、主动定位、刷新和重试的一屏应用；任意城市搜索需要地理编码 API，属于后续扩展。输入为经纬度，输出为当前温度和三天最高温，不能把实时温度写成固定验收值。先检查字段、单位和行数，再处理权限与网络失败。

本轮只做官方文档核对和代码阅读，没有 Expo 构建、网络请求或 iOS/Android 运行证据。下面验收表是待在项目中执行的步骤，不代表已经通过。

> **文档简介**: 构建一个请求真实数据的天气 App：地理定位获取坐标、网络请求拉取天气、加载/错误/空态三态处理，掌握异步数据流的标准工程化写法
>
> **目标读者**: 完成待办应用后、准备处理网络与设备能力的中级学习者
>
> **前置知识**: 已完成 [待办应用](./01-todo-app.md)；理解 Hooks（见 [状态管理教程](../basics/04-state-hooks.md)）

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 操作指南（projects） |
| **难度** | ⭐⭐ |
| **标签** | `#天气` `#网络请求` `#定位` `#TanStackQuery` `#权限` |
| **更新日期** | 2026年9月 |

</details>

## 🎯 项目目标

- ✅ 请求系统权限并获取设备地理定位
- ✅ 用 TanStack Query 管理服务端状态（缓存/重试/失效）
- ✅ 独立处理加载、错误、空数据三种界面状态
- ✅ 理解"服务端状态"与"客户端状态"的分界

## 📐 需求定义

1. 用户选择固定城市，或按“使用当前位置”后请求定位权限 → 获取经纬度
2. 按坐标请求当前天气（以 Open-Meteo 免费 API 为例，无需密钥）
3. 展示：温度/天气码描述/未来 3 日预报
4. 手动刷新；失败显示重试按钮
5. 固定城市按钮作为定位失败的降级方案；城市名搜索随后接地理编码

## 🛠️ 安装与权限配置

```bash
npx expo install expo-location @tanstack/react-query
```

定位是敏感权限，必须声明用途文案（Config Plugin 方式，免改原生文件；机制见 [Expo 要点](../reference/framework-essentials/01-expo-essentials.md)）：

以下配置合并到 `app.json`。Config Plugin 改动需要重新构建原生应用才生效，热刷新不能验证新权限文案；见 [Expo Location 官方配置](https://docs.expo.dev/versions/latest/sdk/location/)。

```json
{
  "expo": {
    "plugins": [
      [
        "expo-location",
        {
          "locationWhenInUsePermission": "用于获取您所在位置的天气信息。"
        }
      ]
    ]
  }
}
```

## 💻 核心实现

### 第一步：定位 Hook

```ts
// hooks/usePosition.ts —— 把设备能力封装成可复用 Hook（模式见 basics/04）
import { useState } from 'react';
import * as Location from 'expo-location';

export type Position = { latitude: number; longitude: number };

export function usePosition() {
  const [position, setPosition] = useState<Position | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [locating, setLocating] = useState(false);

  async function locate() {
    setLocating(true);
    setError(null);
    setPosition(null);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setError('定位权限被拒绝，可以使用北京查询');
        return;
      }
      // Balanced 是精度请求，不保证所有设备都能立即定位。
      const loc = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      setPosition({ latitude: loc.coords.latitude, longitude: loc.coords.longitude });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '定位失败，请检查系统定位服务');
    } finally {
      setLocating(false);
    }
  }

  return { position, error, locating, locate };
}
```

### 第二步：TanStack Query 拉取天气

```tsx
// app/index.tsx —— 服务端状态交给 Query 管理
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';
import { usePosition, type Position } from '../hooks/usePosition';
import { useState } from 'react';

const queryClient = new QueryClient();

// 天气 API 响应的局部类型（Open-Meteo 返回 JSON）
interface Weather {
  current: { temperature_2m: number; weather_code: number };
  daily: { time: string[]; temperature_2m_max: number[] };
}

// 天气码 → 中文描述（精简示例，WMO codes 子集）
const weatherText: Record<number, string> = { 0: '晴', 1: '多云', 3: '阴', 61: '小雨', 71: '小雪' };

async function fetchWeather(pos: Position): Promise<Weather> {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${pos.latitude}&longitude=${pos.longitude}&current=temperature_2m,weather_code&daily=temperature_2m_max&forecast_days=3&timezone=auto`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`天气服务异常：HTTP ${res.status}`); // 非 2xx 转异常，Query 才会重试
  const body = await res.json();
  // 类型断言不会验证远端 JSON；在读字段前检查本屏使用的最小契约。
  if (!Number.isFinite(body?.current?.temperature_2m) ||
      !Number.isFinite(body?.current?.weather_code) ||
      !Array.isArray(body?.daily?.time) || body.daily.time.length !== 3 ||
      !body.daily.time.every((day: unknown) => typeof day === 'string') ||
      !Array.isArray(body?.daily?.temperature_2m_max) ||
      body.daily.temperature_2m_max.length !== 3 ||
      !body.daily.temperature_2m_max.every((value: unknown) => typeof value === 'number' && Number.isFinite(value))) {
    throw new Error('天气数据缺失或格式不符');
  }
  return body as Weather;
}

function WeatherScreen() {
  const { position: devicePosition, error: geoError, locating, locate } = usePosition();
  const [source, setSource] = useState<'manual' | 'device' | null>(null);
  const position = source === 'manual'
    ? { latitude: 39.9, longitude: 116.4 }
    : source === 'device' ? devicePosition : null;
  const qc = useQueryClient();

  // enabled 守卫：没有坐标时不发请求
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['weather', position?.latitude, position?.longitude], // 坐标变化即视为新查询
    queryFn: () => fetchWeather(position!),
    enabled: !!position,
    staleTime: 10 * 60 * 1000,   // 10 分钟内视为新鲜；手动失效仍可触发请求
    retry: 2,                    // 网络抖动自动重试两次
  });

  return (
    <ScrollView>
      <Pressable onPress={() => setSource('manual')}>
        <Text>使用北京</Text>
      </Pressable>
      <Pressable disabled={locating} onPress={() => { setSource('device'); void locate(); }}>
        <Text>使用当前位置</Text>
      </Pressable>
      <Text>{source === 'manual' ? '数据位置：北京' : source === 'device' ? '数据位置：设备坐标' : '请选择位置'}</Text>
      {source === 'device' && geoError ? <Text>{geoError}</Text> : null}
      {(source === 'device' && locating) || isLoading ? <ActivityIndicator size="large" /> : null}
      {isError ? <View>
        <Text>加载失败：{error.message}{data ? '（下方为缓存旧数据）' : ''}</Text>
        <Pressable onPress={() => void refetch()}><Text>重试</Text></Pressable>
      </View> : null}
      {data ? <View>
      <Text style={{ fontSize: 48 }}>{Math.round(data.current.temperature_2m)}°C</Text>
      <Text>{weatherText[data.current.weather_code] ?? '未知天气'}</Text>
      {data.daily.time.map((day, i) => (
        <Text key={day}>{day}：最高 {data.daily.temperature_2m_max[i]}°C</Text>
      ))}
      {/* 手动刷新触发缓存失效重取 */}
      <Pressable onPress={() => qc.invalidateQueries({ queryKey: ['weather'] })}>
        <Text>刷新</Text>
      </Pressable>
      </View> : null}
    </ScrollView>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WeatherScreen />
    </QueryClientProvider>
  );
}
```

## 从固定城市到设备位置的验收顺序

| 操作与输入 | 应观察的输出 | 失败后先回查 |
|---|---|---|
| 刚打开页面，不选位置 | 有选择按钮，无无限天气加载动画 | 无缓存的禁用查询仍可处于 pending，不能只按 isPending 画 spinner |
| 点击使用北京 | 当前温度、描述、三行日期和最高温 | 请求坐标、daily 字段、timezone、HTTP 状态和响应契约 |
| 点击当前位置并拒绝权限 | 拒绝提示，仍能点击北京 | 不要让权限错误提前 return 掉整个界面 |
| 授权但关闭系统定位服务 | 错误提示，定位动画结束 | catch/finally 是否覆盖设备 API 拒绝 |
| 无缓存时断网再查城市 | 重试结束后显示错误和重试按钮 | retry: 2 会额外重试两次，不是立即报错 |
| 有数据时断网再刷新 | 若重取失败，明确标记缓存旧数据 | 保留 data 和 error 两种信息，不能把旧数据描述成最新 |

Open-Meteo 的 daily 参数与时区规则按[官方预报 API](https://open-meteo.com/en/docs)核对；这里显式使用 `timezone=auto`。Query v5 的 `isLoading` 为 `isPending && isFetching`，适合此处禁用查询尚未开始的情况，见[官方禁用查询指南](https://tanstack.com/query/latest/docs/framework/react/guides/disabling-queries)。本例不接管 AppState、后台定位或持久化缓存；杀进程后保留天气需另行实现。

## ✅ 最佳实践

天气查询依赖位置和权限，应先表示“尚未授权”“定位中”“请求失败”“已有数据”这些不同状态，再决定何时发请求。HTTP 非成功响应要按 API 契约转换为失败，否则 fetch 的 Promise 正常返回也可能被误画成成功天气。

Query 可以统一缓存和重试，但不是禁止手写状态；引入它的收益是减少重复同步逻辑。若已经用 Query 管服务端结果，避免再在另一个 store 手动维护同一份天气。客户端中的服务秘密可被提取，真正需要保密的凭据留在服务端，并验证拒绝权限时仍有可用反馈。

## ❓ 常见问题

**Q1: Android 真机定位一直超时？**
A: 模拟器也需要配置或注入位置，不能假定必有默认坐标；真机需检查系统定位服务、应用权限和定位环境。已有权限不等于定位请求必定成功。

**Q2: iOS 上传 App Store 被拒说权限说明不清？**
A: 用途文案要写清"用这个权限做什么"，且在使用时弹出；核对 `locationWhenInUsePermission` 文案。

**Q3: 天气码怎么补全？**
A: Open-Meteo 使用 WMO weather codes，完整映射表见其官方文档，建议封装成 `weather-code.ts` 常量文件并补测试。

---

## 🔗 相关文档

- 📖 [状态与数据请求库指南](../reference/library-guides/01-state-and-data.md) — TanStack Query 完整用法与 Zustand 分工
- 📖 [原生与设备能力库指南](../reference/library-guides/02-native-and-device-libs.md) — 定位/传感器类库总览
- 📖 [RN 核心 API 字典](../reference/language-concepts/01-rn-core-api.md) — ActivityIndicator 等 API 细节
- 📄 [状态管理 — useState/useEffect 与自定义 Hook](../basics/04-state-hooks.md) — usePosition 的封装模式来源
- 🚀 [聊天应用实战](./03-chat-app.md) — 下一个项目：从拉数据到实时推送
- 🎓 [启动优化](../advanced-topics/performance/02-startup-optimization.md) — 为什么 staleTime 缓存对启动体验至关重要


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
