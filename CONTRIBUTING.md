# 贡献指南

感谢你对 Dev Quest 的关注！本项目是个人学习路径仓库，欢迎通过 Issue 反馈问题或提交内容改进。

## 贡献流程

1. **反馈问题**: 发现文档错误、失效链接或内容过时，请提交 Issue 并注明具体文件与位置
2. **内容贡献**: Fork 仓库 → 创建分支 → 修改内容 → 提交 Pull Request
3. **PR 要求**: 描述改动范围与动机，确保不引入新的失效引用

## 提交信息规范

使用以下前缀（与现有提交历史保持一致）：

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat:` | 新增内容/功能 | `feat: 完成02-nextjs-frontend模块现代化重构` |
| `refactor:` | 结构调整/重构 | `refactor: 模块编号 04-12 重排为 03-11` |
| `fix:` | 修复错误 | `fix: 修复重构归档中的相对路径引用` |
| `docs:` | 文档修正 | `docs: 修复全部陈旧引用并对齐新模块布局` |
| `chore:` | 杂项维护 | `chore: 清理冗余文件` |

## 写作规范

新增或修改文档前，请阅读以下规范文件：

- [文档规范指南](shared-resources/standards/documentation-guidelines.md) — 写作风格与质量标准
- [标准文档模板](shared-resources/templates/document-template.md) — 文档骨架
- [模块结构指南](shared-resources/standards/module-structure-guide.md) — 目录结构标准
- [交叉引用系统](shared-resources/standards/cross-reference-system.md) — 链接与引用规范

### 必做检查

- [ ] 新文档使用标准模板骨架
- [ ] 交叉引用使用相对路径且目标文件存在
- [ ] 已同步更新 [文档索引](shared-resources/tools/document-index.md)
- [ ] 已同步更新 [学习进度](shared-resources/progress/learning-progress.md)

## 模块结构

每个技术模块遵循统一结构（README + basics/advanced-topics/knowledge-points/frameworks/projects/testing/deployment），详见[模块结构指南](shared-resources/standards/module-structure-guide.md)。

## 许可证

提交内容即表示你同意该贡献按 [MIT License](LICENSE) 授权。
