# Java 第一轮 NEEDS_REVIEW 复核

范围是第一轮容器 `results.jsonl` 中模块默认 Java 21 的 Java 块；没有执行主机代码或全库扫描。共 140 项，116 项为 manifest 的历史 adjudicated 短哈希基线，24 项为非 legacy。历史标记不等于通过：非 legacy 的 Spring/JUnit/Jakarta 失败仅说明该容器缺少依赖，仍需在对应构建中验证。

逐项查看非 legacy 后，修复了一个确定的 Java 语法结构问题：AOP 示例原先把 `audit` 方法置于类外；现已放入 `TimingAspect`。Spring、RestClient、JUnit、Jakarta 与虚拟线程示例未被判 PASS：它们需要相应依赖、项目类型、导入或 Java 21/可选 Java 25 的编译环境。涉及 JDK API 的条目保留为 NEEDS_REVIEW，后续应以官方 Java 21 API 文档和实际 target release 验证。

| 路径：起始行 | 快照 SHA-256 | 第一轮原因 | 复核状态／所需上下文 |
|---|---|---|---|
+| `08-java-revisited/projects/01-todo-api.md:29` | `5785b8bea53acfe6f4544121e36b932fdd61ad11c6f2778ef0146623c88cbc51` | Error: package jakarta.validation does not exist | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/projects/01-todo-api.md:221` | `6116b52bae4b1f6467478f20f35790cfbe8bd67871d8086740acf2264eabe5d3` | Error: package org.junit.jupiter.api does not exist | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/projects/02-library-management.md:47` | `eb25e4f27c2ceb0a61c17f3aa6cf7e1b85392e9daea61855b3b2641ac048b84a` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/02-library-management.md:124` | `5c776c80127e93913a1a45557d07e6fac26229c560982524d9324df629e6cb8f` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/02-library-management.md:174` | `b1a7dedfda75fb1222d019abf6941ccba607876eb9014be1b4a463ec801287c5` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/02-library-management.md:196` | `2a41b7ac83744cb97108be08b94b33960d38172b7228ad2f0f285e07ba71ab97` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/03-order-system.md:53` | `9b64cd26510535497f1bfc870162531cab18c8556864256041bafedb51824c2d` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/03-order-system.md:90` | `24299bb69d7cc52831aaeec523b69f7c932131d8f3f984365b3ec2efc428b9db` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/03-order-system.md:127` | `31b39f1f5f6e12cf2e1344e9e8afafa46a59a875d1e908505546e4f7ec160163` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/03-order-system.md:172` | `78c285e62e779a120b09832b49ccf034744e92646c3c7d645b3387a3e600bd95` | Exception in thread "main" java.lang.InternalError: Exception during analyze - java.lang.AssertionError at jdk.jshell/jdk.jshell.TaskFactory$AnalyzeTask.analyze(TaskFactory.java:415) | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/04-production-spring-app.md:82` | `a831755211f5dfc5d2e3e944e5beb308ffc87ff070930d3fa95db9bf0759237c` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/projects/04-production-spring-app.md:90` | `15ebd34baf6fbdb4b32b3810d9080ed619af157e14e6b983cdf9a7ba177ac893` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/01-java-keywords.md:54` | `dbded6fd228b2fd3c7794aeb2c6d8c24648922912bf46116e0afd1216349ca61` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/01-java-keywords.md:91` | `d7245b68108b7ff4bbd3a6fa814fea0a59f52c24dca08ef33b6b36528366004c` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/01-java-keywords.md:106` | `4a31d966c6c1c58bd37c314878fb71de5f806800c293affd84dab55c2a88ffb3` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/01-java-keywords.md:120` | `dd5d4c1d60db10191adf9036e2f50b25d94c2767f9668f454ac5c0c0025a1440` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/01-java-keywords.md:132` | `4d223219e3c2b39ad10807292ea4bc6fa00e8f81d849c1ba95cb8e7076e4f7d0` | Error: Modifier 'synchronized' not permitted | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/01-java-keywords.md:157` | `2057f0c74d3e21866d9c2d76a4cd876db471c35f783edcadd5c908142f25a430` | Error: ';' expected | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/02-collections-generics.md:60` | `07817df41cbaee6078d2aef18ef8fcb7fa87b942f416b94fd10e7712129f56c9` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/02-collections-generics.md:75` | `7a6855d285828bb829fa89e744784a95f8023801ccaef7d4496248d5965253b6` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/02-collections-generics.md:90` | `8903640f28b6a292d6221f68c1e8c13ef76a22b486a7facd44396a596f8a23e4` | Error: illegal start of expression | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/03-streams-optional.md:34` | `63cc3ff91977e9f2346ad381febf4d0b4baa24d0bc34c6a5a6dc7cc6f55844fa` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/03-streams-optional.md:74` | `b328334ca5324a4a5d0327421986b3c243973732aeec30852d4fae6c1f668ed8` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/03-streams-optional.md:86` | `3ac9c2be1f389ac0d918f507bf09ec7901e067995871d587b0adc67a3d777b80` | Error: illegal start of expression | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/03-streams-optional.md:101` | `0d452f4a004761775ec25f59490f69ce707e7c80372fec53561d120fed00ce45` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/03-streams-optional.md:120` | `82d665fb22de3a877b15b334244a83193fb0dcd0a869261f601569dd3ec707df` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/03-streams-optional.md:139` | `1395a4eb04e102d2567c9940f88226937126c1b5ef140c99eb1e7d3d80bc1976` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/04-concurrency-api.md:26` | `a7a32b5f05097c1bc32502919db9b8e9ac2dde8595a532d0e645cd4e1bd5b0f7` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/04-concurrency-api.md:48` | `3f27b1579032ac75aa1d1377a166688c0c28cb3c642b9100e78d579b4b270dce` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/04-concurrency-api.md:62` | `948c947b10c064d6ec25cfcae15907462c377aa60508eb9693038708a88c1232` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/04-concurrency-api.md:74` | `7496f0bb6d8d28ec93aa1179175629cdb44fbf327c21aca35320dc6e416156a6` | Error: java.lang.ScopedValue is a preview API and is disabled by default. | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/04-concurrency-api.md:117` | `203d4c30a978e41575fe75fb7fe2b83b2472e8681252a8f0c312c158b41b6cb4` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/05-records-sealed-patterns.md:98` | `a2e333b4500badaea5657644567a5eec1011dc54021c14c7147545529a477f09` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/05-records-sealed-patterns.md:106` | `be72e941f3117147a20e75d6a75483acde6a34bda3689e9b743a9eacb47a85a4` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/05-records-sealed-patterns.md:122` | `8371e16c7366452d895aea34a7f27f76e22970c272346aeba85317d8f464ec17` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/06-exceptions-resources.md:37` | `1a9083120df97fb0ec229497679828066c8653e49ddc7b824f217cc311c064d9` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/06-exceptions-resources.md:69` | `3c2903163a7aa7bdc45a9ef4432e509093fcc3739062cff499ef94cb0a197ed1` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/07-string-immutability-pool.md:100` | `e4ca4469dff4251436980c76ddd197e5ba378b0b33d598d040cf616f9f0f47ea` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/language-concepts/10-interface-semantics.md:78` | `f9f2de0bd881097402808170616498da72f71a78b847d5a67f8d4d85aec71fb8` | Error: illegal start of type | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:26` | `328ecb3e3162219bed0eeecb81c7491a5177d908b19eed930b07626ae75d2a25` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:42` | `95222e58154ace130521925f51dc78025aa5a161c88794008c12d26ac71fdf8d` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:58` | `7e9be6ac7a17c92e757496f5a045a4eff429ed3589f98cb2c4ca75fc7c4c58f7` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:73` | `4c7b2f7be16a18d1af263e6306ce6431cdf435e1c9104520cd400873d6987ebb` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:84` | `dd21a5fbb1a8b7c24f201b352abd4922ebaca64d5800f7c294df981c11963abf` | Error: unnamed variables are a preview feature and are disabled by default. | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:98` | `d7bc6a85a0653654e8fc01e7092fb8dd95badfa0a6354bdf5ed1d2d72e115bb8` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:114` | `1d10e6ced877dfa98d30949022c0ebf9948b7077d0ed29e29f4cf291d5944120` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:127` | `d96914932ec1e28c28c54dcdde6a7b07c83781087a7ab9f9aa4446bdcb07d7bd` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/quick-references/01-java-cheatsheet.md:145` | `31976a3c01f2c590324e8b816d94d556da9a3a0c25d0e9a8b144853effcc35e7` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/quick-references/02-troubleshooting.md:31` | `5948debb4b3e09708b1aeed4bd44d7f23444de209693cf54749a07593d245da0` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/quick-references/02-troubleshooting.md:59` | `7821286c547426b78af2c141dffc7364dbe053314651911184c8f36883b253cd` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/quick-references/02-troubleshooting.md:75` | `7b9cc0a8cdfac2246f7e3cb0d0d090fd42f49263c10f12741eba8dc8c6894ad7` | Error: illegal start of expression | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/quick-references/02-troubleshooting.md:105` | `35c6800706a5223d318775b338fa4786cd3c1152e189ed480b1558a6f47b8c21` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/quick-references/03-spring-boot4-migration.md:62` | `8b48356ea62c6f5be26a602f17a5913f969601d7ea477ef563dafc4d0919edd8` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/01-spring-boot-essentials.md:55` | `0c592664ad00163762b9039a89c99713fe41501da49a179a31ce7437d3612d42` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/01-spring-boot-essentials.md:69` | `b9268d90417f3b9dcc1684b9684b9f8ab41efb05a3907b404dd2dfd5efcb5909` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/01-spring-boot-essentials.md:99` | `b192163173b6617547cbd6741cfa57450e689d93a3ede173338178e691893e27` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/01-spring-boot-essentials.md:109` | `cb072eb5c1e7b1336dbb92422feca89c0164b1002fb6154ad91ce57ec30f1c12` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/01-spring-boot-essentials.md:135` | `8004507bd7878a2d0dd485289967791c26e8a33d514505af450f0eeef3cd4939` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/02-jpa-essentials.md:26` | `0a02871b824d058f8f2bc1063b24a43470bca80367672442ab142265b95d9913` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/02-jpa-essentials.md:86` | `d8a4af311c07f062df1af887e001cb5acdc141cb556317fccae0e2c82f18267e` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/02-jpa-essentials.md:92` | `f97850b7cff8a1833e58676cbbb644af24980ec8611bde4b97cc2539c022600d` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/02-jpa-essentials.md:119` | `5750a73756983628a427f23ae6e821ac5ed18910303e04c03dc4f2896f252c53` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/03-ioc-di-essentials.md:35` | `ce960867eb8cbac00586308b9b4b4ac296810cd7c6e85a0d3e0b485e72ae01c8` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/03-ioc-di-essentials.md:55` | `bb6307c1315a34e6e7a34485a93dd998e108a540a86afb6dba1fe410a48414f0` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/03-ioc-di-essentials.md:71` | `f6de8e1c0c5646241fc0682d0c8b71e7de592556d9de288e0bf49e8ad988bce4` | Error: illegal start of type | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/framework-essentials/04-aop-essentials.md:61` | `f9b01ee78c6e70063d4c8834b1d161d710a04ef7dfc6a647f39c70613ed057d6` | Error: illegal start of type | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/framework-essentials/05-transaction-essentials.md:69` | `d82ae8fffe24fcce168a591c03285408572852597e53edfb90ce6227f50194c6` | Error: illegal start of expression | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/06-spring-security-essentials.md:33` | `e08bdf71e8b64ece442704cc67609fa7c7e3ce0520da96950c2d19af0af7e7cf` | Error: illegal start of type | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/framework-essentials/06-spring-security-essentials.md:64` | `fef022490bbb5faf761a1da15a039410777d310d8c2d9105550f29403278b431` | Error: illegal start of expression | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/framework-essentials/07-rest-client-essentials.md:37` | `477a82703bde709e2d63b3919f6479bc5fd228181156d80aa6319feefb5f98af` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/framework-essentials/07-rest-client-essentials.md:62` | `be89dd9b467956f3bff58dd4cda01d634bbb4a08ca47ed246b185d9ff3a78b25` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/framework-essentials/07-rest-client-essentials.md:87` | `0b5494f35be52a50215cac5aa6095aba21ce735966e35d86641940a1395fce8e` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/library-guides/01-standard-library.md:49` | `a64579d5a16f20d3319e90da2e41f037f656c0791988b011d31103e2996ba0e8` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/01-standard-library.md:79` | `6e39c51fd173e4c261fddd1bcd9f7d53a54db3518f1c5c3c7fea89f6ae5bbd21` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/01-standard-library.md:104` | `88eae817657f319e11ba237e706a6b6ee9a640f86c2bbded50d16d6d65ebca9d` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/01-standard-library.md:122` | `7484b759d6169e48d27bb9c6b37faac0b252a27c45ba2119cbbc43c79bc7bcbc` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/01-standard-library.md:130` | `29a879c0eaee096850d3eaf0354fa0221ede3fc430a5d36d7cb5ba84b8b03ccc` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/01-standard-library.md:147` | `e399cf314b09f1b91d3c85b01fb10a9db850e9a95d64d62cca9850cc6ed93700` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/02-third-party-libs.md:36` | `53a51e244e71f0284c4c64e60552241698aac675cd371c4714664335c2fe1518` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/02-third-party-libs.md:58` | `920d89784d16ae7917e509cea0c1a37088a69c8588b83ebb03c901d3bb24d826` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/03-java-lang.md:57` | `ab6756ba292d080a8b4f7bb3d00e7c5e52eb24babf0ab90f38d231506ae1642d` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/library-guides/03-java-lang.md:72` | `7f2e453a82868d325f402b2dcb2a05ffd07e7c2fdcf864e3974d8890dae56eca` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/library-guides/04-java-io.md:43` | `6410e1c568dcd164f4bb43581161f210ebc81851a181864b4af54011b2d54fb1` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/reference/library-guides/04-java-io.md:79` | `d93d56e5dfe862b4f65eb657b7e802cfce4df3954b6abb91c451bce332996275` | Error: illegal start of expression | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/library-guides/05-java-util-function.md:47` | `cd4d3ac5d168b99f9e519b89f8f87ac6d1446d04a5897299654781d60976bdac` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/library-guides/06-java-math.md:82` | `68c5974a68d4eaa244b373a3b01bf2b0985c193a2ab6b5ea19b212f3bc6f55db` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/library-guides/07-java-text-and-time-format.md:48` | `48e02f35f254e4909abdc8f5df1570e2a5b413618b3045a44a58d29001e9b783` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/library-guides/07-java-text-and-time-format.md:69` | `74b3ae792b059495526167459352406431c866fdde9cfb886846eaf625479a9b` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/reference/library-guides/09-jdk-package-map.md:81` | `4903b35d58f497a4e830cfe23ae53ad165cd39cf1750c3d35fb26e790761d440` | Error: ';' expected | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/advanced-topics/security/01-security-practices.md:58` | `fcedf9c50537378f0f16d5ea6ffddadc126dfd3e10d00a1518dfbfca8a9759fc` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/advanced-topics/security/01-security-practices.md:89` | `80d46eb1d5cacc521e70798a18808f0b1f98614e9b7318d14e42caab21e770ba` | Error: illegal start of expression | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/advanced-topics/architecture/01-layered-architecture.md:68` | `b95367c2b68fd2c1fa6861cba664b34d95d06788109bd0272cb45eb1a33c1550` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/advanced-topics/performance/02-virtual-threads.md:60` | `2f7f3e126249b514d1c102649acd67abdf9290bf7a79b410ae8ded63ba9bffad` | Error: cannot find symbol | 非 legacy；已判为依赖缺失、局部示例或见报告修复项 |
| `08-java-revisited/advanced-topics/performance/02-virtual-threads.md:94` | `9791d48da0984d98b28defaf34fafd1e7df1221fca91c191859e225b88732793` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/advanced-topics/performance/02-virtual-threads.md:108` | `30fcdc5ef71aa5b2cbaf4da6ff3bc70316097ac6b6fc0a80617f1951e446272f` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/advanced-topics/performance/02-virtual-threads.md:117` | `cf367d472bee10eb96519974ab84d7a4312c7e99cc6e4f3fe295aaba01f159eb` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/03-variables-types.md:84` | `8407638756160da4dacd2f9c9f6b32b9882fbb19402a9df1ddae2651212e8447` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/04-classes-records.md:98` | `6fc7ee3a7f2c20ad21e4605166792234a3a66569d4327731e0246070ae9e958b` | Error: call to super must be first statement in constructor | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/04-classes-records.md:137` | `e8555cb6ccca6ee5bce6f5140affdcec75b2c7920757cbdb09cdca0c1d3c22e4` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/05-control-flow.md:49` | `b1208c59ab15fadddfefffecde13f4989ff7c4abb2a189aaac27d0a15adfd2a0` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/05-control-flow.md:69` | `609ded8d6bd827c2b3d0a434b2e36a75caf34c7f7db2a5b241517f77c3f2042d` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/05-control-flow.md:86` | `11440edf3a14fe62c00a77f9fb9c85298a3aa757640d61f494fa231fb3f84d97` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/05-control-flow.md:145` | `67a67ff75eb38901c3e1ee8f8feaa44a47e728489c42c5014afe7390f842618d` | Error: illegal start of expression | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/06-exceptions.md:63` | `0c4d54b2a815e2b158d8d8821edbc5be98748a45abb7e765af5f7b6ed67dbbba` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/06-exceptions.md:73` | `039c11a5229b66fbfcbcac5c52d9ae7779c4b88624caa5935d42f2e57f9232a8` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/06-exceptions.md:82` | `cd45e6006c7b2ef25493561bcf80e9afed29b15f12d13de2bed2e2723ec81f49` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/06-exceptions.md:101` | `8e755c328b6b04b72a8c286c304af4dae91c627af7ccc5d0090cf83f9bac899f` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/06-exceptions.md:110` | `c869b45c7295cf085e7f5217aefb740341c5e6e908a0c09ad7c1d4b47ec0ea89` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/06-exceptions.md:125` | `8db11168fd6cc0708d2c5264c701cbc8d0d70d6d2060fd9d0463080bd0b3e08e` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/07-modern-features.md:81` | `c65d230abd40968417f5ab62814e12b623b8bf49cc232618cf7597a1284baa5e` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/07-modern-features.md:102` | `a8e5e3438180620b0e8ce4613f1582260f9a3b9fc57aa61bb038143a0749cccb` | Error: illegal start of expression | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/07-modern-features.md:110` | `88ffbc3b1aff43b12017ae1740647067fa3d7baa156864001f1273bfcc63e555` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/basics/07-modern-features.md:127` | `628800f08eb14b5b61e260d080a79f71fa977ab9e0bf9bc8740af440167e9dfe` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/01-unit-testing.md:33` | `84a8aa22e66459ee08ba6982afaa6fca0bd9e7ac517ef8c33b3fc74d9e71051f` | Error: package org.junit.jupiter.api does not exist | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/01-unit-testing.md:78` | `6589d6cecce942d926d38677e7a11c61eea1ef8475e4b982db39e5990fcff614` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/01-unit-testing.md:130` | `897a52000fc7ab388a528a0f96a4d1ef3023fd8a1e2a750aec923a0ebc727ec5` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/01-unit-testing.md:147` | `d2405eec79933d5e5f633efd709dac4952f74164031d1b9e20ce86a1ccbd6980` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/02-integration-testing.md:44` | `23bc473514922997ce2ed607144f3e0203a213ace96807947751504086182bf2` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/02-integration-testing.md:86` | `6f959bf6d834860f672a515456784c330a95d21410375c8e640c27ab254b6f32` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/02-integration-testing.md:127` | `8b29230f93f0d379468dc2a013de2627d016f61c606d26deb328d7d332fb7687` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/03-api-testing.md:103` | `f82e9f0c623b8b91762a794e1792c595af4a198102985a36b77dc7b681c5510e` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/testing/03-api-testing.md:144` | `22882aeca3c8e33308dc5a28f72ef861a7c32dc93eeff150db4962ed82c35c0b` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/01-spring-boot-basics.md:65` | `a50f7c8826744120095e0d485cc0d03d3b4ad88fced24368f60424603499abcb` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/01-spring-boot-basics.md:107` | `7f07b3143695de9f74e8d7b319b6a259f572dff5f523eb53e1030f0cde70140e` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/01-spring-boot-basics.md:120` | `dd08cf9c31467f64a79ed05645a8db57b9906910220065ec7afe72dce540197c` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/01-spring-boot-basics.md:134` | `70c8da5212d2124ffbec36b7b0d40c608422cee83a83c01b51b08727044da94b` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/01-spring-boot-basics.md:160` | `a853384325907d2f8cf14de8b3b6ba99dcd544aab852a0f46da3832e310a00f2` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/01-spring-boot-basics.md:198` | `f8a83f29faef728b980afe5ae7554ee82580f67a31a86a2d72755013b72be725` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/02-spring-boot-advanced.md:68` | `25b397fc866a3b684d8b099e0c4d2354b3e2e9dd222d8f8f681ffe14edaf52fd` | Error: package jakarta.persistence does not exist | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/02-spring-boot-advanced.md:112` | `75ad0be17343445e5d92c3fb82e87e61d712f4718b290d2c8e5bca1435822333` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/02-spring-boot-advanced.md:145` | `74e022f71d872c8e6df9235f645fce7a5bd8164b68e2fabf5a7e05057797d104` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/02-spring-boot-advanced.md:171` | `47a1603e253da9b17ed23d0662b0d684e8642205a68deaa74453277e01e5cd9c` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/03-ecosystem-integration.md:43` | `24e1a8c5b2c3b86978212d1553dcbea621d2e303503baf043a698d1cae55ebb4` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/03-ecosystem-integration.md:69` | `ce0cd77a186c17773c1a5283a6209c942fdaa2cffe351217f427c6dced8900c5` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/03-ecosystem-integration.md:84` | `7f26c0ac2f64e0f0abbc7e11276d7310c488035dd2a754fcda4fc6925536d97d` | Error: cannot find symbol | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/03-ecosystem-integration.md:102` | `e91f0604ececb8bb0ef748add5ea4e7add91cddf320398d397767bcc12578341` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/03-ecosystem-integration.md:122` | `77d852d67cd993a3ee49566e74f2c2d90ce37b0bb2c8a2d25fd8f597b71fd478` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/03-ecosystem-integration.md:151` | `233989d77b81f51119bae9f774b4c3ce7dee44418a9e4672dddbd762f2701b18` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/03-ecosystem-integration.md:177` | `6d714afdb63459c79eb2470ccf040369d0dbab7311ea16e73512fef8fd558035` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
| `08-java-revisited/frameworks/04-devtools.md:168` | `1e792d032bf2994c33e6b47b9c0b7c44ae87e4b99c0eb929f8a5c7c2a04d75d5` | Error: illegal start of type | 历史 adjudicated 基线；仍需按片段上下文判读 |
