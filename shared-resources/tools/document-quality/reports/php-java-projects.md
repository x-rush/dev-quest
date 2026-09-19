# PHP / Java 首项目端到端验证

本报告限定于 [PHP CLI 任务管理](../../../../07-php-mastery/basics/08-first-project.md) 与 [Java 控制台图书管理](../../../../08-java-revisited/basics/08-first-project.md) 两篇完整项目，不能推导出 Laravel、Spring 或整模块通过。

验证器：[verify_php_java_projects.py](../verify_php_java_projects.py)。机器证据：[php-java-projects.json](./php-java-projects.json)，保存正文与每个提取文件的 SHA-256、命令、输出、退出码和断言结果。

## 实际结果

2026-09-19 在 Linux 容器以非 root 用户运行，网络禁用、源目录只读、工作目录为临时文件系统。PHP 8.3.6、Composer 2.10.3、Temurin JDK 21.0.12。Java 使用 `javac --release 21` 编译。

| 范围 | 通过 |
|---|---:|
| PHP：Composer 自动加载、重启、删除与幂等完成、参数错误、存储校验、权限、并发 | 19 / 19 |
| Java：编译、重启、借阅状态机、输入校验、存储校验、权限、并发 | 16 / 16 |
| 总计 | **35 / 35** |

这些是场景数量；一个场景可能执行多次真实 CLI 调用。验证器直接从 `project-file` 标记后的正文围栏提取文件，既不补 import，也不注入替代服务实现。PHP 使用真实 Composer 生成 PSR-4 自动加载；Java 使用正文的完整单文件程序。

失败路径比较数据文件前后字节，确认没有覆盖；权限测试在非 root 用户下把目录设为只读；并发场景启动 8 个 CLI 进程，检查所有成功提交都保留。多次 CLI 调用各自创建新进程，用于验证重启读取。

## 复现

在已安装 PHP 8.3+、JDK 21+、Python 3.10+ 的 POSIX 环境，准备 Composer 2 的 phar，以普通用户运行：

```bash
python3 shared-resources/tools/document-quality/verify_php_java_projects.py \
  --composer /absolute/path/composer.phar \
  --report /tmp/php-java-projects.json
```

本次使用的 Composer phar 来自官方 `getcomposer.org`，SHA-256 为 `7a2d379d5b8ffdaa028580ef26494c36d2feef4b178d3dd1473a4dbc5e17c8d6`。项目没有第三方依赖，运行验收不需要联网下载包。

容器复现时需提供已有工具链镜像、只读仓库挂载以及可写证据目录，核心命令如下（镜像标签是本地准备好的工具链，不是公共镜像）：

```bash
docker run --rm --network none --read-only --user 65534:65534 \
  --tmpfs /tmp:rw,exec,nosuid,size=512m --cap-drop ALL \
  --pids-limit 256 --memory 1g --cpus 2 -e HOME=/tmp \
  -v "$PWD:/source:ro" -v "$PWD/../verification-lab:/out:rw" \
  dev-quest-validation:local \
  python3 /source/shared-resources/tools/document-quality/verify_php_java_projects.py \
  --composer /out/composer.phar --report /out/php-java-projects.json
```

## 已修复与边界

- PHP 删除条件原先写反，删除存在的 ID 会抛错，未知 ID 反而保存成功；现已用真实删除与重复删除覆盖。
- PHP 不再静默接收未知优先级、不再将目录或坏 JSON 当成新存储；模型检查字段、日期、控制字符和重复 ID。固定锁覆盖读改写，同目录临时文件写完再替换。
- Java 原文缺少完整类/import、加载实现与保存调用，分号分割会损坏合法标题；现改成完整 Java 21 程序与明确的受限 TSV，所有命令在保存成功后才报告成功。
- 两个程序仅针对受控本地目录；不证明恶意目录竞争、网络文件系统、Windows 文件替换、断电持久性或生产环境容量。Java 原子替换遇到不支持的平台会明确失败，未增加弱化覆盖方式。
- 权限测试在 root 或非 POSIX 主机应失败并说明前置条件，不会跳过后仍宣称全通过。
