# Docker 部署 - 容器化 Spring Boot 与分层镜像

> **文档简介**: 把 Spring Boot 应用打包成小、快、安全的容器镜像：分层 JAR 与 Spring Boot 原生分层支持、多阶段构建、JVM 容器感知参数与非 root 运行
>
> **目标读者**: 需要把应用交付为容器镜像的开发者
>
> **前置知识**: 已完成 [开发工具链](../frameworks/04-devtools.md)；容器概念基础见 [第一个项目](../basics/08-first-project.md)

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `08-java-revisited` |
| **象限** | 操作指南 |
| **难度** | ⭐⭐ |
| **标签** | `#Docker` `#分层镜像` `#多阶段构建` |
| **更新日期** | `2026年9月` |

## 🎯 学习目标

完成本文档后，你将能够：
- 用多阶段构建产出只含 JRE 的最小镜像
- 利用分层 JAR 让依赖层充分缓存，重建镜像秒级
- 正确设置容器内存参数与非 root 用户

## 🛠️ 一、为什么需要分层镜像？

传统做法把 fat jar 一整个 COPY 进镜像——改一行代码也要重新上传几十 MB 的依赖层。

Spring Boot 3.3+/4.x 的 fat jar 天生分层：`java -Djarmode=tools -jar app.jar extract` 可把 **依赖 / 应用代码** 解到不同目录，各自成层，代码变更只失效最上层。

## 🛠️ 二、多阶段构建 Dockerfile

```dockerfile
# ---------- 阶段 1：构建 ----------
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
# 先只拷 pom 拉依赖：pom 不变时此层全缓存
RUN mvn -B dependency:go-offline
COPY src ./src
RUN mvn -B package -DskipTests

# ---------- 阶段 2：分层提取 ----------
FROM eclipse-temurin:21-jre AS extractor
WORKDIR /app
COPY --from=build /app/target/app.jar ./app.jar
# Boot 3.3+/4.x：jarmode=tools 解出分层目录
RUN java -Djarmode=tools -jar app.jar extract --layers --destination extracted

# ---------- 阶段 3：运行镜像 ----------
FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S app && adduser -S app -G app    # 非 root 用户
WORKDIR /app
# 按变更频率从低到高 COPY：依赖在前，应用代码最后
COPY --from=extractor /app/extracted/dependencies/ ./
COPY --from=extractor /app/extracted/spring-boot-loader/ ./
COPY --from=extractor /app/extracted/snapshot-dependencies/ ./
COPY --from=extractor /app/extracted/application/ ./
USER app
EXPOSE 8080
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
```

```bash
docker build -t todo-api:1.0.0 .
docker run -p 8080:8080 --memory=512m todo-api:1.0.0
```

> 运行类名以 `java -jar` 启动日志为准；Boot 3.2+/4.x 的 Loader 类为 `org.springframework.boot.loader.launch.JarLauncher`。

## 🛠️ 三、容器中的 JVM 参数

JVM 10+ 默认感知 cgroup 限制（`MaxRAMPercentage` 按容器配额取比例），无需再 `-Xmx` 硬编码：

```bash
java -XX:MaxRAMPercentage=75.0 \
     -XX:+UseG1GC \
     -jar app.jar
# 512m 容器配额 → 堆约 384m，其余留给元空间/线程栈/直接内存
```

调优依据与 GC 选型见 [JVM 调优与 GC 基础](../advanced-topics/performance/01-jvm-tuning.md)。

## 🛠️ 四、本地编排：docker-compose

```yaml
# docker-compose.yml —— 本地一键起全套依赖
services:
  app:
    build: .
    ports: ["8080:8080"]
    environment:
      DB_URL: jdbc:postgresql://db:5432/demo   # 服务名即主机名
      REDIS_HOST: cache
    depends_on:
      db: { condition: service_healthy }
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: localdev              # 仅本地，生产走 Secret
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
  cache:
    image: redis:7-alpine
```

```bash
docker compose up -d --build   # 修改代码后重建应用层，依赖容器复用
```

## ❓ 常见问题

### Q1: 镜像里能看到分层效果吗？

`docker history todo-api:1.0.0`：依赖层在前且大小稳定，`application` 层只有百 KB 级——代码变更推送镜像只传输这一层。

### Q2: 要不要用 Spring Boot Buildpacks？

`mvn spring-boot:build-image` 零 Dockerfile、自动处理分层与安全补丁；代价是构建较慢、定制性弱。需要精细控制用本文 Dockerfile，追求省心用 Buildpacks。

### Q3: 时区/字符集问题？

alpine 镜像默认 UTC：`ENV TZ=Asia/Shanghai` + `apk add tzdata`；`-Dfile.encoding=UTF-8` 显式指定。

## 🎨 最佳实践

### ✅ 推荐
- 镜像 tag 用语义化版本 + commit SHA，禁止只打 `latest`
- `.dockerignore` 排除 `target/`、`.git`，加速构建上下文
- 运行镜像不含 Maven/JDK 编译链（多阶段构建隔离）

### ❌ 陷阱
- 容器里 `-Xmx` 硬编码超过配额 → OOMKilled
- 用 root 跑应用：容器逃逸攻击面变大
- `COPY . .` 一步到位：任何文件变动都击穿全部缓存层

## 🚀 下一步

- 多副本编排与自愈 → [K8s 部署](./02-kubernetes-deployment.md)
- 镜像推送与流水线 → [CI/CD 与可观测性](./03-ci-cd-observability.md)

## 🔗 相关文档

### 本模块
- 📖 [Spring Boot 核心速查](../reference/framework-essentials/01-spring-boot-essentials.md) — fat jar 与启动机制
- 📖 [标准库与工具链](../reference/library-guides/01-standard-library.md) — JDK 工具索引
- 📄 [开发工具链](../frameworks/04-devtools.md) — Maven 打包基础
- 📄 [K8s 部署](./02-kubernetes-deployment.md) — 下一篇：编排
- 📄 [生产级 Spring Boot 应用](../projects/04-production-spring-app.md) — 容器化只是起点
