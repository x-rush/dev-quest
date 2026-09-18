# 安全实践 — 数据、网络与发布链路防护

> **文档简介**: 系统梳理 RN 应用的安全威胁面：敏感数据存储、网络安全、密钥保护、深链与依赖供应链，建立"默认安全"的工程清单
>
> **目标读者**: 准备上线或已运营真实用户数据应用的负责人
>
> **前置知识**: 已了解 [EAS Build](../../deployment/01-eas-build.md)（环境变量体系）与 [OTA 更新](../../deployment/03-ota-updates-observability.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `04-multiplatform-apps` |
| **象限** | 解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#安全` `#SecureStore` `#网络安全` `#密钥保护` `#供应链` |
| **更新日期** | 2026年9月 |

</details>

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
| 敏感 | access token、个人资料 | `expo-secure-store`（iOS Keychain / Android 由 Keystore 密钥保护的加密存储） |
| 绝不落盘 | 长期有效凭证、支付凭据 | 服务端持有，客户端只持短期 token |

```ts
// expo-secure-store：系统级加密存储
import * as SecureStore from 'expo-secure-store';

const issuedToken = '替换为登录服务返回的短期令牌';
await SecureStore.setItemAsync('access_token', issuedToken, {
  keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY, // 不随云备份迁移
});
const token = await SecureStore.getItemAsync('access_token');
```

**MMKV 与 SecureStore 分工**（MMKV 可配置加密，默认存储与密钥管理仍需明确）：速度敏感的非敏感数据走 MMKV；凭证一律 SecureStore；混合场景用"SecureStore 存加密 key + MMKV 存密文"组合。

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

**WebView 红线**：只加载白名单域名；禁用 `javaScriptEnabled` 除非必需；不要通过 URL 注入 token；消息桥接也需验证来源、消息类型与权限。

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
A: 不要把 2KB 写成 Android Keystore 的通用限制。底层平台可能拒绝大值，某些历史 iOS 版本有约 2KB 限制；只保存小型凭证并处理失败，大对象按其存储需求另行设计。

**Q2: 证书锁定导致 App 全量请求失败？**
A: 典型的"锁过期"事故：pin 备份证书 + 服务端轮换提前发版；个人项目建议只在支付等链路使用。

**Q3: 如何检测包里是否泄露了密钥？**
A: 构建后解包检查（unzip aab / strings binary），配合 CI 跑 gitleaks 类扫描，把"密钥不进包"变成门禁。

---

<!-- full-library-explanation -->
## 用一次账户切换检查数据边界

登录态不仅是一枚 token。页面缓存、查询缓存、磁盘缓存、通知中的内容和后台请求，都可能携带上一个账户的数据。退出登录时应停止或隔离旧请求、清除该账户的缓存与凭证，并让服务端按协议撤销会话。仅跳回登录页仍可能在下次登录时展示旧数据。

SecureStore 用于少量秘密值，不是个人资料数据库。Android 的值由 Keystore 相关密钥保护，不能据此保证每台设备都采用硬件安全存储。API 调用要处理原生错误、凭证缺失和认证失效。[官方存储说明](https://docs.expo.dev/versions/latest/sdk/securestore/)也提醒不要把它当作不可替代数据的唯一副本。

练习：A 登录并加载个人信息，触发一个延迟请求，退出后用 B 登录，再让 A 的旧请求完成。验收：B 页面没有出现 A 数据；日志没有 token；服务端不因客户端传入 A 的 ID 就返回其记录。另测卸载重装与生物识别设置变化，记录凭证是否仍可读及如何恢复登录。

WebView 的 postMessage 不是自动安全通道：还要限制页面来源、导航与消息结构，避免把高权限操作直接暴露给任意网页。环境变量是否加 PUBLIC 前缀也不能证明秘密不会进包；判断标准是它最终是否被编译进客户端产物。

## 🔗 相关文档

- 📖 [原生与设备能力库指南](../../reference/library-guides/02-native-and-device-libs.md) — 存储类库对比与权限说明
- 📖 [Expo 要点](../../reference/framework-essentials/01-expo-essentials.md) — Config Plugins 对原生安全配置的托管
- 📄 [EAS Build 构建流程](../../deployment/01-eas-build.md) — 环境变量与凭据托管的操作层
- 📄 [OTA 更新与可观测性](../../deployment/03-ota-updates-observability.md) — OTA 通道与商店边界
- 🚀 [生产级移动应用](../../projects/04-production-mobile-app.md) — 安全项在生产清单中的位置
- 🎓 [新架构解析](../architecture/01-new-architecture.md) — Codegen/规格文件可审计性的机制背景


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
