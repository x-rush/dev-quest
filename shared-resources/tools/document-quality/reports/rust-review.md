# Rust `NEEDS_REVIEW` 复核

范围：`verification-lab/rust-final` 的标准 manifest/results/commands 产物；基线为 Rust 1.98.1，edition 由验证器配置决定。本次未运行主机代码、未全库扫描。

20 项中 16 项为历史 short-hash adjudicated 基线，4 项为新项。没有把缺 crate、缺项目模块、或命令行示例缺参数视为通过；它们仍需要在相应 Cargo 项目、依赖锁定和运行参数下验证。借用、生命周期、对象安全、const-generic 的编译失败是有意反例，应保留反例并由正文说明预期诊断。

| 文件：行 | SHA-256 | 结果／结论 |
|---|---|---|
| `projects/01-cli-tool.md:262` | `14be61b0c22328c1c144e886f464bf33e38beac2423a182de127ebe4f03a1b5f` | 缺 `Cli`：同项目 CLI 定义上下文。 |
| `projects/02-tauri-notes-app.md:297` | `2a0556375b501e96abbdc48a55f0a2cc7a03345e5bd997efdfd97b34e9ae07a2` | 缺 `rustnotes_lib`：Tauri crate 模块上下文。 |
| `projects/04-websocket-realtime.md:169` | `4628a2c14aeebbe8f283ca27e6dad7d6e665f1b8702147edf7a264607f7e331d` | 离线缺 axum crate，未判通过。 |
| `projects/04-websocket-realtime.md:206` | `3affa0ee1781b756e6f8aad11413b2d0c997bb7271172e83b274ee3ac8330825` | 未闭合分隔符；需与相邻 WebSocket 片段组合审查。 |
| `projects/04-websocket-realtime.md:303` | `797a0accd65f91cd0b17e18547184dad67652d707dfd0b8b11b80bae0c0e5e07` | 多余 `}`；需与相邻片段组合审查。 |
| `reference/language-concepts/01-ownership-dictionary.md:259` | `2e0442ee9df85695b8c26de9ddb7eea3ef98a853770a6dc2219bce7228b5b579` | E0382 有意 move 后借用反例。 |
| `reference/language-concepts/01-ownership-dictionary.md:271` | `73a5c360fce177ad056f5cc9a603e1c14f746e09b8819cd10e7ac3b5363ee66d` | E0502 有意可变/不可变借用冲突反例。 |
| `reference/language-concepts/02-trait-objects.md:344` | `04a97a8b34c590c4e74fbacd2572e2e2c394754e1507a3fd9e7e19830523febd` | E0038 有意非 dyn-compatible trait 反例。 |
| `reference/language-concepts/03-const-generics.md:265` | `527bbdb320fc660c1f60b52148f1b7737852e21126910457aad43c840d5ec2fd` | E0308 const-generic 类型反例。 |
| `reference/language-concepts/03-const-generics.md:280` | `38060c906f531c14dbafcac3cfd8ee230525bc906feb9c74199fb3c27107bf81` | 泛型 const operation 限制反例。 |
| `reference/language-concepts/04-advanced-lifetimes.md:283` | `68f64ca42546bfcb8a94bdd1b238dec8bed5b9520276dd16a2e106acaa3bc5fb` | E0597 生命周期反例。 |
| `reference/language-concepts/04-advanced-lifetimes.md:302` | `c0f232004af1396dd4f8d77bd66d9accd9b7bf105c56491fa4f1f7277dda9f5b` | E0106 缺生命周期标注反例。 |
| `reference/library-guides/15-standard-library-map.md:30` | `f1a765dc525b091ac63047e792f2ccba33a7ed253f71a3e7137b3560d7a6587d` | 运行缺 `counter <path>` 参数，未判通过。 |
| `basics/05-error-handling.md:310` | `77d58ff46b15472727504a054eddf332671fccf886d350395c076ce68d85c5ca` | 离线缺 axum crate，未判通过。 |
| `basics/09-concurrency-async.md:219` | `59ccfa1d136dcb7a729aeb8315f5dabbfec85640bd2bbb813336ea4a54550ddc` | 离线缺 axum crate，未判通过。 |
| `deployment/04-containerized-services.md:199` | `33d4d4f35721de237f29b4aa5346418fb947a5689b80614b219213199e8a6c60` | 离线缺 axum crate，未判通过。 |
| `deployment/04-containerized-services.md:264` | `a8cd6f55ad8fb23fcadca06e1f9866a56a9979fb84b606a3a64b42731ef94c37` | 运行缺 `app [health]` 参数，未判通过。 |
| `frameworks/02-tauri-plugins.md:329` | `e1f48ebe46fe142d50e6e853a37499042ad4c43a1a9ebf3797b2183577009410` | 缺 tauri plugin crate/module。 |
| `frameworks/04-axum-web-stack.md:180` | `b982b35fe32d31afba4c48ed8db576676a27a8802689ba32e34f0db39d504362` | 离线缺 axum crate，未判通过。 |
| `frameworks/04-axum-web-stack.md:216` | `296731e54811d32f2aece931da2f9ee79e33654ab2f2744845d9fa8ec4fdf224` | 离线缺 axum crate，未判通过。 |

本轮未对片段作内容修改，因此没有生成 `rust-recheck`；只有在修复后才需要按内容合并的标准 manifest/results 产物。
