# Tauri 2 桌面打包：tauri build、bundle 配置与产物矩阵

> **文档简介**: 把 Tauri 2 工程变成可分发安装包——`tauri build` 的三阶段流水线、`tauri icon` 图标矩阵生成、`bundle` 配置分区（Windows NSIS/MSI、macOS DMG、Linux AppImage/deb/rpm）逐字段讲清，并给出各平台产物落点表与更新签名产物的衔接。
>
> **目标读者**: 已跑通 tauri dev、要向用户分发桌面应用的开发者
>
> **前置知识**: [Tauri 2 架构](./01-tauri-2-architecture.md)（配置区块全景）、[插件体系](./02-tauri-plugins.md)（updater 签名闭环）
>
> **预计时长**: 2-3 小时

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `11-rust-cross-platform` |
| **象限** | 操作指南（frameworks/） |
| **难度** | ⭐⭐ 进阶 |
| **标签** | `#rust` `#tauri` `#packaging` `#release` |
| **更新日期** | `2026年9月` |

> 版本基线见模块 [README](../README.md)（Tauri 2.11，2026-09-16 核实）。`bundle` 全字段以[官方配置参考](https://v2.tauri.app/reference/config/)为准。

## 🎯 学习目标

完成本篇后，你将能够：

- ✅ **说清流水线**: 复述 `tauri build` 从前端构建到打包器产物的三个阶段
- ✅ **配置图标**: 用 `tauri icon` 一次生成全平台图标矩阵并接入 bundle
- ✅ **分区写配置**: 按平台写出 windows/macos/linux 的打包细则
- ✅ **定位产物**: 拿到构建产物后说出每种安装包在 `target/*/bundle/` 下的落点

## 📋 目录

- [核心概念](#核心概念)
- [实践指南](#实践指南)
- [代码示例](#代码示例)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [模式不变量](#模式不变量)
- [相关资源](#相关资源)

---

## 🔍 核心概念

### 概念一：tauri build 的三阶段流水线

**定义**: `tauri build` 不是一条 cargo 命令，而是编排器，依次执行：

1. **前端产物**: 执行 `build.beforeBuildCommand`（如 `npm run build`），产出 `frontendDist`（`../dist`）里的静态资源——它们会被**嵌入二进制**
2. **Rust 编译**: 对 `src-tauri` 执行 release 模式编译（`cargo build --release`），嵌入配置与前端资源
3. **打包器（bundler）**: 按 `bundle.targets` 为当前宿主系统生成安装包，落入 `target/release/bundle/` 下各子目录

**推论一**: 改了 `tauri.conf.json` 必须重新 build（`generate_context!` 编译期读取配置，dev 同理）。
**推论二**: 打包器只生成**当前操作系统**的安装包——Linux 机器上跑不出 DMG，Windows 机器上跑不出 AppImage；跨平台产物靠 CI 矩阵或目标平台机器。

### 概念二：bundle 配置分区——targets 与三个平台区块

**定义**: `bundle` 是配置中"打进安装包的一切"的声明区：

| 字段 | 作用 | 关键默认值 |
|------|------|-----------|
| `active` | 是否启用打包器 | `false`（必须显式开启） |
| `targets` | 要生成的包类型 | 可写 `"all"`（按宿主平台取全量） |
| `icon` | 图标路径数组 | 指向 `icons/` 下的 ico/icns/png |
| `createUpdaterArtifacts` | 生成更新签名产物 | `false`（接 updater 才开） |
| `windows` | NSIS/MSI 细则 | — |
| `macOS`（注意大写 OS） | DMG/签名细则 | — |
| `linux` | AppImage/deb/rpm 细则 | — |

`targets` 的合法值：`"nsis"`、`"msi"`、`"app"`、`"dmg"`、`"appimage"`、`"deb"`、`"rpm"`、`"all"`（大小写不敏感），也可用数组按需组合。

各平台子区块的高频字段：

- `windows.nsis`：`installMode`（`"currentUser"` 为默认，免管理员权限；可选 `"perMachine"`）、`compression`（默认 `"lzma"`，体积最小但打包最慢）、`languages`、`displayLanguageSelector`
- `macOS`：`minimumSystemVersion`（默认 `"10.13"`）、`hardenedRuntime`（默认 `true`，公证的前置条件）、`signingIdentity`、`entitlements`
- `linux`：`deb.depends`（依赖包数组）、`appimage`、`rpm`

### 概念三：产物矩阵与更新签名产物

**定义**: 打包器把产物按类型分目录放在 `src-tauri/target/release/bundle/` 下：

| 平台 | 目录 | 产物（文件名以构建输出为准） |
|------|------|------------------------------|
| Windows | `nsis/` | `<名称>_<版本>_<arch>-setup.exe` 安装向导 |
| Windows | `msi/` | `<名称>_<版本>_<arch>_<语言>.msi` |
| macOS | `macos/` | `<名称>.app` 应用束 |
| macOS | `dmg/` | `<名称>_<版本>_<arch>.dmg` 镜像 |
| Linux | `appimage/` | `<名称>_<版本>_<arch>.AppImage` |
| Linux | `deb/` | `<名称>_<版本>_<arch>.deb` |
| Linux | `rpm/` | `<名称>_<版本>_<arch>.rpm` |

开启 `createUpdaterArtifacts` 后，安装包旁边会多出对应的 `.sig` 签名文件——它们与 [02 篇](./02-tauri-plugins.md) updater 的 `pubkey` 验签配对，构成"检查-下载-重启"更新的信任链。调试版构建（`tauri build --debug`）产物落在 `target/debug/bundle/`，体积更大且未优化，仅供排查。

---

## 🛠️ 实践指南

### 步骤一：生成图标矩阵

**目标**: 一张源图产出全平台所需图标

**操作指南**:

```bash
# 在 Tauri 项目根目录执行；源图建议 ≥1024×1024 正方形透明底 PNG
npm run tauri icon ./app-icon.png
```

命令把 `icon.ico`、`icon.icns`、各尺寸 PNG 与 Square*Logo.png（Windows 商店规格）写入 `src-tauri/icons/`——即 `bundle.icon` 默认指向的目录。

**验证方法**: `ls src-tauri/icons/` 出现全尺寸图标集；重新 build 后安装包与窗口图标随之更新。

### 步骤二：选定 targets

**目标**: 为分发渠道精确圈定安装包类型

**操作指南**: 编辑 `tauri.conf.json` 的 `bundle` 区块（见"示例一"）：开发期用 `"targets": "all"` 看全貌；定型后按渠道收敛（如官网分发 Windows 用 `["nsis"]`、Linux 用 `["appimage"]`）。

**验证方法**: `npm run tauri build` 结束后 `src-tauri/target/release/bundle/` 下只出现所选类型的子目录。

### 步骤三：写平台细则

**目标**: NSIS 免管理员安装 + Linux 声明依赖 + macOS 最低系统

**操作指南**: 按"示例二"补齐三个平台区块；`deb.depends` 按实际用到的系统库填写（如 `libwebkit2gtk-4.1-0`）。

**验证方法**: Windows 上双击 setup 无 UAC 弹窗（currentUser 模式）；`dpkg -I *.deb` 显示声明的依赖。

### 步骤四：构建并核对产物

**目标**: 完整跑通 build 并确认签名产物

**操作指南**: 执行"示例三"的构建序列；需要指定架构时用 `--target`（如 macOS 通用二进制 `universal-apple-darwin`，需先装好对应 rust target）。

**验证方法**: 产物表（概念三）逐一核对存在；开启 updater 后 `.sig` 文件与安装包成对出现。

---

## 💻 代码示例

### 示例一：tauri.conf.json——bundle 基础区块

```json
{
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "createUpdaterArtifacts": true
  }
}
```

**关键点解析**:
- `active: false` 是默认值——漏写它时 `tauri build` 只编译二进制、不产安装包
- `targets: "all"` 按宿主平台展开全量；上架/官网渠道定型后建议收敛为显式数组
- `icon` 数组同时列出 ico/icns/png，打包器按目标平台各取所需

### 示例二：三平台细则区块

```json
{
  "bundle": {
    "windows": {
      "nsis": {
        "installMode": "currentUser",
        "compression": "lzma",
        "languages": ["SimpChinese", "English"],
        "displayLanguageSelector": false
      }
    },
    "macOS": {
      "minimumSystemVersion": "10.13",
      "hardenedRuntime": true,
      "signingIdentity": "-"
    },
    "linux": {
      "deb": { "depends": ["libwebkit2gtk-4.1-0"] },
      "appimage": { "bundleMediaFramework": false }
    }
  }
}
```

**关键点解析**:
- 键名是 **`macOS`**（大写 OS），写成 `macos` 会被 schema 校验拒绝
- `signingIdentity: "-"` 表示 ad-hoc 签名（本机分发可用）；上架需换成 Developer ID 证书并公证
- `installMode: "currentUser"` 装进用户目录、不触发 UAC；`perMachine` 需管理员且写 Program Files

### 示例三：构建与产物核对（bash，只写不执行）

```bash
# 1) 生成图标矩阵（源图 ≥1024x1024 PNG）
npm run tauri icon ./app-icon.png

# 2) 全量构建（宿主平台 all targets）
npm run tauri build

# 3) 只构建指定类型（过滤 targets，跳过无关打包器）
npm run tauri build -- --bundles nsis,msi     # Windows CI 常用
npm run tauri build -- --bundles appimage,deb # Linux CI 常用

# 4) macOS 通用二进制（Intel + Apple Silicon，需先 rustup target add 两个 triple）
npm run tauri build -- --target universal-apple-darwin

# 5) 核对产物落点（版本号/arch 以构建输出为准）
ls src-tauri/target/release/bundle/
#   nsis/    <名称>_<版本>_<arch>-setup.exe (+ .sig)
#   msi/     <名称>_<版本>_<arch>_<语言>.msi (+ .sig)
#   macos/   <名称>.app
#   dmg/     <名称>_<版本>_<arch>.dmg (+ .sig)
#   appimage/<名称>_<版本>_<arch>.AppImage (+ .sig)
#   deb/     <名称>_<版本>_<arch>.deb

# 6) 签名产物与公钥配对校验（衔接 02 篇 updater 信任链）
ls src-tauri/target/release/bundle/nsis/*.sig
```

---

## 🎨 最佳实践

### ✅ 推荐做法

- **CI 按 OS 分片**: Windows 跑 nsis+msi、macOS 跑 dmg、Linux 跑 appimage+deb+rpm——打包器只认宿主 OS，矩阵化是唯一正路
- **定型后收敛 targets**: `"all"` 会为每个可用打包器都花时间（NSIS 的 lzma 压缩尤其慢），按渠道显式列出可显著缩短 CI
- **图标先行**: 用 `tauri icon` 从单源图生成，避免手工维护十几个尺寸文件导致漏更新

### ❌ 避免陷阱

- **在 Linux 上追 Windows 产物**: 打包器无跨 OS 打包能力；"在这台机器上顺便把 dmg 也出了"不存在
- **忘记 `bundle.active`**: 构建成功却找不到 bundle/ 目录，十有八九是 `active` 还是默认的 `false`
- **改配置不重编**: `tauri.conf.json` 经 `generate_context!` 编译进二进制，改完必须重新 build（dev 也要重启才能生效）

---

## ❓ 常见问题

### Q1: `tauri build` 成功了但 `bundle/` 目录不存在？

**A**: 依次查：① `bundle.active` 是否为 `true`（默认 false，只编译不打包）；② `bundle.targets` 是否写成了当前宿主 OS 不支持的类型（如 Linux 上写 `dmg`）；③ 是否用了 `--no-bundle` 类调试参数。产物落点见概念三产物表。

### Q2: NSIS 的 `installMode` 该选 `currentUser` 还是 `perMachine`？

**A**: 默认 `currentUser`：免管理员、写入用户 AppData，适合工具类应用的无感安装；`perMachine` 写 Program Files、需要 UAC，适合企业统一部署场景。两者也影响升级——同 identifier 的应用应固定一种模式，混用会造成新旧安装位置分裂。

### Q3: macOS 的 `hardenedRuntime` 为什么默认开启、ad-hoc 签名能分发吗？

**A**: hardened runtime 是 Apple 公证（notarization）的硬性前提，默认开启省去上架前的回头改动。`signingIdentity: "-"` 的 ad-hoc 签名产物在本机与测试群分发可用，但首次打开要绕 Gatekeeper 提示；正式分发必须换 Developer ID 证书 + 公证流程。

---

## 🧭 模式不变量

1. **分发产物是平台函数**: 安装包格式由目标用户的操作系统决定，构建机只能产出自己 OS 的包——"跨平台分发"的正确实现是构建矩阵，不是单个万能产物
2. **嵌入即冻结**: 前端资源与配置在编译期进入二进制，"改个配置文件就生效"对 Tauri 应用不成立，一切变更走重新构建
3. **签名链先于分发链**: 安装包的更新签名（.sig + pubkey）必须在第一个用户拿到包之前设计好，事后补签无法覆盖已分发的旧版
4. **图标是单源派生物**: 所有平台图标尺寸从一个源图生成，手工分尺寸维护必然漂移

---

## 🔗 相关资源

### 📖 延伸阅读

- **指南**: [Tauri 2 架构](./01-tauri-2-architecture.md) - tauri.conf.json 全景与 identifier 语义
- **指南**: [Tauri 插件体系](./02-tauri-plugins.md) - updater 签名闭环（pubkey/端点/relaunch）
- **项目**: [02 Tauri 桌面笔记](../projects/02-tauri-notes-app.md) - 本篇打包流程的实战载体

### 🛠️ 工具资源

- **官方文档**: [Tauri 分发指南](https://v2.tauri.app/distribute/) - 签名/公证/商店上架全流程
- **配置参考**: [bundle 字段全集](https://v2.tauri.app/reference/config/#bundleconfig) - 本篇字段的权威定义
- **CLI 参考**: [tauri build 命令](https://v2.tauri.app/reference/cli/) - `--target`/`--bundles`/`--debug` 全参数

---

## 📝 总结

### 核心要点回顾

1. **三阶段流水线**: 前端产物 → release 编译 → 打包器，配置经 `generate_context!` 编译期冻结
2. **bundle 分区**: `active`/`targets`/`icon` 是总开关，`windows`/`macOS`（大写）/`linux` 各管细则
3. **产物有固定落点**: `target/release/bundle/<类型>/` 分目录，updater 开启后 `.sig` 与安装包成对

### 学习成果检查

- [ ] 复述 tauri build 三阶段并解释"改配置必须重编"
- [ ] 用 tauri icon 从单源图生成全平台图标
- [ ] 写出含 NSIS installMode 与 deb.depends 的完整 bundle 配置
- [ ] 说出至少四种安装包在 bundle/ 下的子目录

---

**文档版本**: v1.0.0
**最后更新**: 2026年9月
**维护团队**: Dev Quest Team
