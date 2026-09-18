# 实战项目二 — 天气应用（网络 + 定位）

## 分阶段练习与验收

**最小阶段**：先用固定城市取得天气，再申请定位。

**验收结果**：拒绝定位仍能手选城市；断网显示错误或明确标记的旧数据。

**扩展顺序**：后台定位与复杂缓存放后，先覆盖权限和数据来源。

建议保存一份正常输入、一份失败输入、实际输出和对应测试。先完成以上阶段再扩展正文中的完整设计；遇到省略实现或未定义依赖，应按文档上下文补齐，不能把代码片段拼接后当作已经验证的完整工程。

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

1. 启动后请求定位权限 → 获取经纬度
2. 按坐标请求当前天气（以 Open-Meteo 免费 API 为例，无需密钥）
3. 展示：温度/天气码描述/未来 3 日预报
4. 手动刷新；失败显示重试按钮
5. 手动输入城市名作为定位失败的降级方案

## 🛠️ 安装与权限配置

```bash
npx expo install expo-location @tanstack/react-query
```

定位是敏感权限，必须声明用途文案（Config Plugin 方式，免改原生文件；机制见 [Expo 要点](../reference/framework-essentials/01-expo-essentials.md)）：

```json
// app.json
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
import { useEffect, useState } from 'react';
import * as Location from 'expo-location';

export type Position = { latitude: number; longitude: number };

export function usePosition() {
  const [position, setPosition] = useState<Position | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      // 第一步：请求权限（区分"未决定"与"被拒绝"两种失败）
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setError('定位权限被拒绝，请手动输入城市');
        return;
      }
      // 第二步：取坐标。中精度足够天气场景，省电且更快
      const loc = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      setPosition({ latitude: loc.coords.latitude, longitude: loc.coords.longitude });
    })();
  }, []);

  return { position, error };
}
```

### 第二步：TanStack Query 拉取天气

```tsx
// app/index.tsx —— 服务端状态交给 Query 管理
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query';
import { ActivityIndicator, Pressable, ScrollView, Text, View } from 'react-native';

const queryClient = new QueryClient();

// 天气 API 响应的局部类型（Open-Meteo 返回 JSON）
interface Weather {
  current: { temperature_2m: number; weather_code: number };
  daily: { time: string[]; temperature_2m_max: number[] };
}

// 天气码 → 中文描述（精简示例，WMO codes 子集）
const weatherText: Record<number, string> = { 0: '晴', 1: '多云', 3: '阴', 61: '小雨', 71: '小雪' };

async function fetchWeather(pos: Position): Promise<Weather> {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${pos.latitude}&longitude=${pos.longitude}&current=temperature_2m,weather_code&daily=temperature_2m_max&forecast_days=3`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`天气服务异常：HTTP ${res.status}`); // 非 2xx 转异常，Query 才会重试
  return res.json() as Promise<Weather>;
}

function WeatherScreen() {
  const { position, error: geoError } = usePosition();
  const qc = useQueryClient();

  // enabled 守卫：没有坐标时不发请求
  const { data, isPending, isError, error, refetch } = useQuery({
    queryKey: ['weather', position?.latitude, position?.longitude], // 坐标变化即视为新查询
    queryFn: () => fetchWeather(position!),
    enabled: !!position,
    staleTime: 10 * 60 * 1000,   // 10 分钟内命中缓存，避免重复请求
    retry: 2,                    // 网络抖动自动重试两次
  });

  if (geoError) return <Text>{geoError}</Text>;             // 定位失败态
  if (isPending) return <ActivityIndicator size="large" />; // 加载态
  if (isError) return (                                     // 请求失败态：给重试出口
    <View>
      <Text>加载失败：{error.message}</Text>
      <Pressable onPress={() => refetch()}><Text>重试</Text></Pressable>
    </View>
  );

  return (
    <ScrollView>
      <Text style={{ fontSize: 48 }}>{Math.round(data.current.temperature_2m)}°C</Text>
      <Text>{weatherText[data.current.weather_code] ?? '未知天气'}</Text>
      {data.daily.time.map((day, i) => (
        <Text key={day}>{day}：最高 {data.daily.temperature_2m_max[i]}°C</Text>
      ))}
      {/* 手动刷新触发缓存失效重取 */}
      <Pressable onPress={() => qc.invalidateQueries({ queryKey: ['weather'] })}>
        <Text>刷新</Text>
      </Pressable>
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

## ✅ 最佳实践

天气查询依赖位置和权限，应先表示“尚未授权”“定位中”“请求失败”“已有数据”这些不同状态，再决定何时发请求。HTTP 非成功响应要按 API 契约转换为失败，否则 fetch 的 Promise 正常返回也可能被误画成成功天气。

Query 可以统一缓存和重试，但不是禁止手写状态；引入它的收益是减少重复同步逻辑。若已经用 Query 管服务端结果，避免再在另一个 store 手动维护同一份天气。客户端中的服务秘密可被提取，真正需要保密的凭据留在服务端，并验证拒绝权限时仍有可用反馈。

## ❓ 常见问题

**Q1: Android 真机定位一直超时？**
A: 模拟器默认有虚拟坐标，真机需检查系统定位服务开关；必要时引导用户去系统设置。

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
