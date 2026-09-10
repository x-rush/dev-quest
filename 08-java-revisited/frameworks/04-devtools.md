# 开发工具链 - Maven/Gradle、DevTools 与 Actuator

> **文档简介**: 打磨 Java 日常开发体验：构建工具选型与常用命令、DevTools 热重载提速本地迭代、Actuator 生产端点速览
>
> **目标读者**: 刚回归 Java、想快速搭顺手的开发工作流的学习者
>
> **前置知识**: 已完成 [环境搭建](../basics/01-environment-setup.md) 与 [Spring Boot 入门](./01-spring-boot-basics.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐ |
| **标签** | `#Maven` `#Gradle` `#DevTools` `#Actuator` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 在 Maven 与 Gradle 之间做出选型，并掌握日常高频命令
- 用 DevTools + LiveReload 实现"保存即生效"
- 暴露 Actuator 端点并配置健康检查

## 🛠️ 一、构建工具：Maven 与 Gradle

### 选型速查

| 维度 | Maven | Gradle |
|------|-------|--------|
| 配置格式 | `pom.xml`（XML） | `build.gradle(.kts)` |
| 学习曲线 | 平缓、约定优先 | 灵活、需要理解构建模型 |
| 增量构建 | 无 | 有（缓存 + 增量编译，快） |
| 生态 | 最广泛 | Android/Kotlin 领域标配 |

团队没有历史包袱时：**Spring Boot 3.x 两者都一等公民**，追求构建速度选 Gradle Kotlin DSL，追求稳定可读选 Maven。

### Maven 高频命令

```bash
mvn clean verify          # 清理 + 编译 + 测试 + 集成验证（CI 最常用）
mvn test -Dtest=BookServiceTest        # 只跑一个测试类
mvn dependency:tree -Dincludes=org.slf4j   # 排查依赖冲突（谁是传递来源）
mvn versions:display-dependency-updates  # 检查可升级版本
mvn -o package            # 离线模式：CI 里跳过远程仓库检查
```

### Gradle 高频任务

```bash
./gradlew build           # 完整构建（含测试）
./gradlew test --tests "com.devquest.BookServiceTest"   # 过滤测试
./gradlew bootRun         # 直接启动 Spring Boot 应用
./gradlew dependencies --configuration runtimeClasspath # 查看依赖树
```

### 版本对齐：Spring Boot BOM

```xml
<!-- Maven：parent 方式统一管理依赖版本，子依赖无需写版本号 -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.3.5</version>
</parent>
```

```kotlin
// Gradle Kotlin DSL：插件方式等价
plugins {
    java
    id("org.springframework.boot") version "3.3.5"
    id("io.spring.dependency-management") version "1.1.6"
}
```

## 🛠️ 二、DevTools 热重载

### 引入

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
    <optional>true</optional> <!-- 不传递给依赖本模块的项目，不打进 fat jar -->
</dependency>
```

### 工作原理

- **重启（Restart）**：classpath 变化时用"快速重启类加载器"重启应用上下文，比冷启动快数倍
- **自动触发**：IDE 构建（IDEA `Ctrl+F9` / Eclipse 自动编译）即触发
- **LiveReload**：静态资源变化时通知浏览器插件自动刷新
- **禁用缓存**：自动为模板引擎（Thymeleaf 等）关闭生产缓存

```yaml
spring:
  devtools:
    restart:
      additional-paths: src/main/resources   # 额外监听目录
    livereload:
      enabled: true
```

### 手动触发（IDEA 无自动构建时）

```yaml
spring:
  devtools:
    restart:
      trigger-file: .reloadtrigger  # 仅该文件变化才重启，可配合脚本 touch
```

### 边界认知

- DevTools 只做**类加载器级重启**，不是 JRebel 式的真正热替换；大量 Bean 状态会重建
- 生产环境自动失效：fat jar 启动时 DevTools 不加载
- 大项目重启仍需数秒，重度热更需求再考虑商业工具

## 🛠️ 三、Actuator 生产端点

### 引入与暴露

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env,conditions
  endpoint:
    health:
      show-details: when_authorized   # 健康详情不随便暴露
```

### 常用端点

| 端点 | 用途 |
|------|------|
| `/actuator/health` | 存活/就绪探针（K8s liveness/readiness 数据源） |
| `/actuator/metrics` | JVM、HTTP、连接池指标 |
| `/actuator/env` | 环境变量与配置（注意脱敏） |
| `/actuator/conditions` | 自动配置评估报告（排查 Bean 为什么没装配） |

### 自定义健康检查

```java
@Component
public class PaymentChannelHealthIndicator extends AbstractHealthIndicator {

    @Override
    protected void doHealthCheck(Health.Builder builder) {
        boolean reachable = pingPaymentGateway(); // 合成示例：探测第三方依赖
        if (reachable) {
            builder.up().withDetail("channel", "primary");
        } else {
            builder.down().withDetail("channel", "unreachable");
        }
    }
}
```

## 🎨 最佳实践

### ✅ 推荐
- 依赖版本全部交给 BOM 管理，禁止散落的硬编码版本
- CI 统一用 `mvn verify` / `./gradlew build` 单命令完成全链路校验
- Actuator 只暴露必要端点，并叠加 Spring Security 访问控制

### ❌ 陷阱
- DevTools 依赖被打进生产镜像（忘了 `optional` / `developmentOnly`）
- 生产 `show-details: always` 泄露内部拓扑
- Actuator 端点未鉴权：`/env`、`/heapdump` 是常见泄露面

## 🚀 下一步

- 构建产物如何交付 → [Docker 部署](../deployment/01-docker-deployment.md)
- 用本项目工具链跑第一个真实项目 → [TODO API 项目](../projects/01-todo-api.md)

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — Actuator 端点完整条目
- 📖 [标准库与工具链](../reference/library-guides/01-standard-library.md) — 标准库与工具链索引
- 📄 [环境搭建](../basics/01-environment-setup.md) — Maven/Gradle 安装与配置基础
- 📄 [CI/CD 与可观测性](../deployment/03-ci-cd-observability.md) — Actuator 指标接入 Prometheus
