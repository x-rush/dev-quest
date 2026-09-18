# 安全实践 - 数据、网络与发布防线

> **文档简介**: 覆盖 Android 应用四条安全防线的原理解析与落地清单：本地数据存储、网络传输、组件暴露面、代码与密钥防护
>
> **目标读者**: 准备面向真实用户发布、需对用户数据负责的中高级学习者
>
> **前置知识**: [生态集成](../../frameworks/03-ecosystem-integration.md)、[发布构建](../../deployment/01-release-build.md)、[应用架构](../architecture/01-app-architecture.md)

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `05-kotlin-compose` |
| **象限** | 深度解释（advanced-topics） |
| **难度** | ⭐⭐⭐ |
| **标签** | `#keystore` `#datastore-security` `#network-security` `#play-integrity` |
| **更新日期** | `2026年9月` |

</details>

---

## 威胁模型先行

移动端默认**不可信设备**假设：root/模拟器、被反编译的 APK、被截屏的界面、被抓包的流量。
四条防线按"攻击面 × 实施成本"排序：

```
① 数据存储（最常失守）→ ② 网络传输 → ③ 组件暴露面 → ④ 代码与密钥
```

## 1️⃣ 本地数据防线

原则：**数据敏感度决定存储位置，明文 SharedPreferences 一票否决**。

| 数据类型 | 正确归宿 |
|----------|---------|
| Token、密码、生物识别种子 | Android Keystore 保护的密文 + DataStore |
| 用户偏好（主题/语言） | DataStore（Preferences 或 Proto） |
| 业务数据 | Room（可选 SQLCipher 加密整库） |
| 大文件/媒体 | app 私有目录，FileProvider 受控共享 |

```kotlin
// 用 Keystore 密钥加密后，再交给 DataStore 落盘
// 注：androidx.security-crypto 的 EncryptedSharedPreferences 已弃用，
//     官方建议走 Keystore + 自行加密（或 Tink）路线
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

suspend fun saveToken(token: String) {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        .apply { init(Cipher.ENCRYPT_MODE, secretKeyFromKeystore()) }
    val sealed = cipher.doFinal(token.toByteArray())          // 密文
    val iv = cipher.iv                                        // 随机 IV 与密文一并落盘
    dataStore.edit { prefs ->
        prefs[Keys.TOKEN] = Base64.encodeToString(sealed + iv, Base64.NO_WRAP)
    }
}
```

- Keystore 密钥绑定硬件安全区（TEE/StrongBox），App 数据被提取也无法离线解密；
- 声明 `dataExtractionRules` 把敏感数据排除出云备份（Android 12+）：

```xml
<!-- android:dataExtractionRules 指向的 rules 文件 -->
<data-extraction-rules>
    <cloud-backup>
        <exclude domain="sharedpref" path="secure_prefs.xml"/>
    </cloud-backup>
</data-extraction-rules>
```

## 2️⃣ 网络防线

- **默认 HTTPS**：Android 9+ 默认禁明文，勿为图省事添加 `usesCleartextTraffic="true"`；
  确需明文的调试环境用 `networkSecurityConfig` 按 domain 白名单放行
- **证书锁定（certificate pinning）慎用**：锁定 SPKI 且至少保留一个备份 pin、有轮换预案；
  否则改走 Play Integrity + 服务端风控路线（更稳）
- **响应不盲信**：服务端异常也可能返回 200 + 错误 JSON，[错误转译层](../../projects/04-production-android-app.md)是统一收口点

```xml
<!-- network_security_config.xml：仅对调试用地址放行明文 -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="false">10.0.2.2</domain>
    </domain-config>
</network-security-config>
```

## 3️⃣ 组件暴露面

| 风险 | 加固 |
|------|------|
| 被第三方拉起的 Activity/Service/Receiver | `android:exported` 保持默认 false，导出组件逐一确认 intent-filter |
| 界面被截屏/录屏/最近任务预览 | 敏感界面窗口加 `FLAG_SECURE` |
| 日志泄露 token | 敏感值不入 Logcat；release 由 R8 移除日志调用 |
| 备份带走数据 | `dataExtractionRules`/`fullBackupContent` 排除敏感库 |

```kotlin
// 敏感界面：防截屏 + 最近任务遮罩
window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
```

权限最小化：每个权限请求前先问"不做这个功能会怎样"；运行时权限的申请 UX 见
[天气应用](../../projects/02-weather-app.md)（拒权降级而非崩溃）。

## 4️⃣ 代码与密钥防线

- **密钥永不进仓**：`keystore.properties`/CI Secrets 注入（流程见 [发布构建](../../deployment/01-release-build.md)
  与 [CI/CD](../../deployment/03-ci-cd-observability.md)）；Secret 类 API 凭据尽量放服务端代理
- **R8 全开**：混淆 + 树摇抬高逆向成本（keep 规则示例见发布构建）
- **完整性校验**：Play Integrity API 让服务端验证请求来自正版、未篡改的应用
- **依赖面**：第三方 SDK 是隐性数据出口——上架前按 [Play 数据安全表单](../../deployment/02-play-store-release.md) 逐项核对 SDK 的数据收集行为

```kotlin
// 服务端配合：每次敏感操作前校验完整性 verdict
val verdict = integrityManager.requestIntegrityToken(
    IntegrityTokenRequest.builder().setNonce(nonceFromServer).build()
)
```

## 🎨 最佳实践

先列出数据：公开缓存、个人资料、登录凭据分别需要多长保留期、是否允许备份、何时删除。选择存储与密钥方案后，用退出登录、备份恢复和设备锁定等场景验证，而不是只检查“启用了加密”。

截图限制、完整性信号等只能保护特定边界，不能取代服务端授权。客户端中的服务秘密不能靠混淆或放进原生库保证不可提取。证书锁定若采用，必须同时准备轮换和恢复；按真实威胁与维护能力选，不把它写成普遍必需或普遍无用。

## 🔗 相关文档

- 📖 概念字典：[AndroidX 官方库指南](../../reference/library-guides/01-androidx-libraries.md) ｜ [第三方库指南](../../reference/library-guides/02-third-party-libs.md)
- 📖 操作指南：[发布构建](../../deployment/01-release-build.md) ｜ [Play Store 上架流程](../../deployment/02-play-store-release.md)
- 🎓 延伸解释：[应用架构](../architecture/01-app-architecture.md) ｜ [生产级 Android 应用](../../projects/04-production-android-app.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
