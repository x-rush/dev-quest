# 安全实践 — 数据、网络与发布链路防护

> **文档简介**: 系统梳理 RN 应用的安全威胁面：敏感数据存储、网络安全、密钥保护、深链与依赖供应链，建立"默认安全"的工程清单
>
> **目标读者**: 准备上线或已运营真实用户数据应用的负责人
>
> **前置知识**: 已了解 [EAS Build](../../deployment/01-eas-build.md)（环境变量体系）与 [OTA 更新](../../deployment/03-ota-updates-observability.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#安全` `#SecureStore` `#网络安全` `#密钥保护` `#供应链` |
| **更新日期** | 2026年9月 |

## 🎯 学习目标

- ✅ 按数据分级选择正确的存储介质（明文/加密/硬件级）
- ✅ 加固网络层：TLS 策略、证书校验与越权防御
- ✅ 管住密钥与构建产物中的敏感信息
- ✅ 识别深链、WebView、OTA 与依赖的供应链风险

## 🗄️ 数据分级存储

**第一原则：客户端无秘密**。任何进 App 包或设备存储的东西都要按"会被逆向/被提取"来设计。

| 数据级别 | 示例 | 正确介质 |
|----------|------|---------|
| 非敏感 | 主题、列表缓存 | MMKV / AsyncStorage（明文可，见[库指南](../../reference/library-guides/02-native-and-device-libs.md)） |
| 敏感 | access token、个人资料 | `expo-secure-store`（iOS Keychain / Android Keystore 硬件加密） |
| 绝不落盘 | 长期有效凭证、支付凭据 | 服务端持有，客户端只持短期 token |

```ts
// expo-secure-store：系统级加密存储
import * as SecureStore from 'expo-secure-store';

await SecureStore.setItemAsync('access_token', token, {
  keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY, // 不随云备份迁移
});
const token = await SecureStore.getItemAsync('access_token');
```

**MMKV 与 SecureStore 分工**（MMKV 本身不加密）：速度敏感的非敏感数据走 MMKV；凭证一律 SecureStore；混合场景用"SecureStore 存加密 key + MMKV 存密文"组合。

## 🌐 网络安全

```ts
// fetch 层加固基线
const res = await fetch(url, {
  headers: { Authorization: `Bearer ${shortLivedToken}` }, // 短期 token + refresh 旋转
});

// 生产环境禁用明文流量：
// Android：usesCleartextTraffic=false（release 默认）；iOS：ATS 默认强制 HTTPS
// 例外域名必须在原生配置中显式声明并写明理由
```

**要点清单**：
- ✅ **全量 HTTPS**，ATS/Cleartext 例外逐域名审计，禁 `*` 例外
- ✅ **高敏感业务考虑证书锁定**（cert pinning），但注意轮换成本——锁死自己也是事故源
- ✅ **不做客户端鉴权判断**：任何"前端隐藏入口"都不算权限控制，服务端必须独立鉴权
- ❌ **不要信任客户端校验**：本地校验的 license/签名检查在越狱设备上均可绕过，只做体验层

## 🔑 密钥与构建产物

1. **`EXPO_PUBLIC_` 变量 = 公开信息**：会被内联进 JS 包，逆向即可读。第三方 SDK key 若必须内联，务必在服务端配置域名白名单/指纹限制
2. **秘密走服务端**：第三方 API 调用经由自己的后端代理，客户端只知"我的服务端地址"
3. **eas.json 不写密钥**：用 `eas env`（服务端加密存储）；`.env*` 一律进 `.gitignore`
4. **符号化文件管控**：dSYM/mapping 上传 Sentry 后从 CI 工件中清理

```bash
# 环境变量分级示例（EAS 服务端管理）
eas env:create --name EXPO_PUBLIC_API_URL --value https://api.example.com --environment production  # 可公开
# 注意：SECRET_* 类变量不存在 EXPO_PUBLIC 前缀，仅供 EAS 构建钩子/服务端使用
```

## 🔗 深链与 WebView

```json
// app.json 深链 scheme —— scheme 是公开的，任何 App 都能发起
{ "expo": { "scheme": "myapp" } }
```

```tsx
// 深链参数处理三原则
import { useLocalSearchParams } from 'expo-router';

export default function OAuthCallback() {
  const { code, state } = useLocalSearchParams<{ code: string; state: string }>();
  // 1. state 必须校验：防伪造回调（发起时随机生成并与服务端比对）
  // 2. 参数不可信：校验格式与来源，不直接拼进请求或 WebView URL
  // 3. 敏感动作二次确认：深链直接触发支付/授权的必须落地页确认
  return null;
}
```

**WebView 红线**：只加载白名单域名；禁用 `javaScriptEnabled` 除非必需；不要通过 URL 注入 token（用 postMessage/安全桥接）。

## 📡 OTA 与供应链

- **OTA 通道完整性**：expo-updates 走 HTTPS + 校验机制，不自建裸 HTTP 更新源；OTA 内容同样受 [OTA 边界](../../deployment/03-ota-updates-observability.md) 约束（原生行为变更必须走商店审核）
- **依赖审计**：`npm audit` 进 CI；锁文件提交；新依赖看维护活跃度与原生代码量
- **Codegen/TurboModule 规格文件进版本控制**，保证原生接口可审计

## ✅ 要点回顾

- ✅ **数据分级**：MMKV（非敏感）→ SecureStore（敏感）→ 服务端（绝不落盘）
- ✅ **客户端无秘密**：EXPO_PUBLIC 可逆读，秘密在服务端或受限白名单
- ✅ **深链参数按不可信输入处理**，state 校验 + 落地确认
- ❌ **不要用前端隐藏代替权限控制**，服务端鉴权是唯一防线
- ❌ **不要在 WebView/深链里传 token**，通道即泄露面

## ❓ 常见问题

**Q1: SecureStore 有大小限制吗？**
A: Android Keystore 单条约 2KB（大值需自加密后分块），iOS Keychain 无硬限但保持小体积是好习惯。

**Q2: 证书锁定导致 App 全量请求失败？**
A: 典型的"锁过期"事故：pin 备份证书 + 服务端轮换提前发版；个人项目建议只在支付等链路使用。

**Q3: 如何检测包里是否泄露了密钥？**
A: 构建后解包检查（unzip aab / strings binary），配合 CI 跑 gitleaks 类扫描，把"密钥不进包"变成门禁。

---

## 🔗 相关文档

- 📖 [原生与设备能力库指南](../../reference/library-guides/02-native-and-device-libs.md) — 存储类库对比与权限说明
- 📖 [Expo 要点](../../reference/framework-essentials/01-expo-essentials.md) — Config Plugins 对原生安全配置的托管
- 📄 [EAS Build 构建流程](../../deployment/01-eas-build.md) — 环境变量与凭据托管的操作层
- 📄 [OTA 更新与可观测性](../../deployment/03-ota-updates-observability.md) — OTA 通道与商店边界
- 🚀 [生产级移动应用](../../projects/04-production-mobile-app.md) — 安全项在生产清单中的位置
- 🎓 [新架构解析](../architecture/01-new-architecture.md) — Codegen/规格文件可审计性的机制背景
