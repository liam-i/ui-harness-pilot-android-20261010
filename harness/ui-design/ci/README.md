# UI 平台 CI 接入

本目录把项目已审的 UI 输入与原生测试接入一个实际 CI Job；它不改共同 UI 规则，也不替代需求层 G2/G3/G4、人工验收或合并授权。本接入已取得限定 GitHub 公开试点的真实 Job；验证范围是明确的原生工程、设备和受检提交，目标项目仍须完成自己的平台采用验收。

iOS 的限定试点已有真实 CI 与运行人审。新增 [Cocos Android 入口](cocos-android.py)和 [workflow 候选](github-cocos-android.yml.example)已完成限定 GitHub 试点的正向、故障阻断、恢复及最终运行人审，本地归档已完成，PR 尚未合并。下文先说明现有 iOS 接入，Cocos 的差异见末节。

## 接入前固定什么

1. 选择已授权的业务副本、UI 权威、平台账号及专用 Runner／设备。生产源仍按 [文件交付](../adapters/files.md) 或项目已验收的工具导出；CI 不连接活动画稿。
2. 在项目原工程审阅中固定 `harness/ui-ci/context.json`、所引用的 policy／bindings、原批准及本次 UI 分母。`context.json` 只组织已有共同快照的输入，不保存业务状态或替代原 Review。其顶层字段为 `business_repository`、`ui_repository`、`policy_path`、`bindings_path`、`snapshot`。
3. `snapshot` 沿 [共同快照](../snapshot.yaml.example) 填 `schema_version / mode / action / rules / authorities / subject / selections / external_files`；明确 `current` 与 `pre-merge`。省略 `repositories / policy_ref / bindings_ref / subject.head`：CI 从独立宿主 SHA 读取受检提交的 policy／bindings，再填入实际恢复路径与 head。其余固定引用、规则摘要和权威选择必须在审阅时确定，不能在 CI 中自动改成最新值。
4. 在原测试配置 `harness/ui-ci/ios.json` 固定 `project / scheme / test_targets / expected_tests / app_bundle / test_timeout_seconds / xcode_version / runtime / devices / bundled_tokens`。设备填写真实 name／udid；tokens 填产品包相对 path 与获批 sha256。用例选择、数量、超时及平台范围来自独立验收合同，不能由实际结果反推。`expected_basis` 可记录其来源。
5. UI Skill 复制到 `.agents/skills/ui-design-workflow/`；共同工具完整复制到 `harness/ui-design/`，规则锁及 runtime implementation manifest 沿原来源，不把这三个平台文件加入另一套规则注册表。工程 Review／采用记录另固定所用平台脚本及 workflow 的实际身份。

只装本目录没有有效业务输入。缺 policy、绑定、历史、媒体、实际批准或设备时停止；不生成 TEST 决定补足真人资料。

## GitHub 限定试点

将 [workflow](github-ios.yml.example) 合入原项目 CI。示例选择同账号明确授权的试点与临时专用 macOS ARM64 Runner；不自动安装或注册 Runner，不接收 fork 工作负载。`UI_AUTHORITY_URL` 配置实际、无凭据的 UI 仓库地址；必须与已审 policy 的权威一致。共同 observer 的 HTTPS 不使用交互登录，私有源可使用已有只读 SSH 能力和已核实主机身份；凭据、私钥不进入配置或日志。使用 actionlint 时，将[标签声明](actionlint.yaml.example)合入项目 `.github/actionlint.yaml`；它只说明已选 Runner 标签，不创建 Runner。

公开库在注册 Runner 前，必须将所有外部 fork 贡献者的工作流设为需要批准，并回读实际设置；只执行已审、同仓库的本人 PR。Job 内的条件不能替代这个平台设置，外部贡献者可能修改 workflow。临时 Runner 不安装服务，试点结束撤销注册。

原生 Runner 使用已选择的 Xcode，不全局切换工具，不创建或删除设备。对明示专用模拟器验证身份和初始关机状态后运行，恢复原外观／字号并关机。失败不自动重跑，不减少用例。每次保留精确 SHA、命令、源摘要、xcresult、测试数量、截图附件、构建资源和清理结果；结果来自真实 `xcodebuild`，不调用 Node 示例替代原生工程。

公开 Artifact 排除完整模拟器清单 `device-*-before.stdout`，避免发布同机器无关设备信息；`result.json` 仍保存实际选中设备及命令结果，运行方须在 Runner 清理临时目录前，将完整原始清单另存到受限本地诊断目录；本试点由启动包装脚本完成此留存。其余实际测试与构建证据继续留存。

此 UI Job 只证明本次固定 UI 输入和原生范围；采用需求层的项目仍须保留原需求 Gate 义务及相应 CI Job，不能用 `native-ui` 替换；尚未接入需求 CI 时，本 Job 通过也不意味着 G3/G4 准入，接续原[需求阶段指引](../../version-requirements/guidance/README.md)。UI 变化需重评原 Review／E；已归档引用按真实归档路径核对。视觉人审单独绑定受检代码与产物，不因自动测试通过自动生成批准。

Job 只证明执行时的当前观察。独立 UI 权威在 Job 结束后前进，不会由这个仅监听 PR 的 workflow 自动撤销旧的绿色状态；实际工程动作前仍沿原 current Gate 重查，必要时重评输入／Review／E 并重新运行 CI。本模板不冻结远端或自动合并。

## 平台验收

`native-tests` 在专用 Mac 上执行原生检查；`native-ui` 在托管 Ubuntu 上只判断该依赖 Job 是否实际成功，不读取业务代码。最终检查使用 `always()`，依赖失败、取消或跳过均返回失败，避免 [GitHub 将跳过的 Job 视为成功](https://docs.github.com/en/pull-requests/reference/status-checks) 导致误放行。

取得实际 Job 后，再配置项目要求的 `native-ui` required check，保留原有必需检查。至少核对两个 Job 的 ID／链接、workflow 来源、head SHA、真实执行步骤、非零失败、数量与跳过项、完整产物、分支保护回读；缺 required check、UI 输入缺失／过时或原生失败必须挡住准入。同名外部绿色状态不能充当实际 Job；保护设置固定实际 GitHub Actions 检查来源，人工审阅继续核对受审 workflow 与所运行的原生步骤。

私库保护受账号套餐与平台权限影响。若实际不支持，保留缺口并调整已授权的试点平台；不自动公开仓库、购买套餐或把本地 YAML 校验记为通过。规则与实际 Job 均验证后，按原人工审核与工程授权决定下一动作；本模板不合并、不发布。

## Cocos Android 候选的采用边界

此参考入口对应 Creator 3.8.8 的 Android 菜单试点：两个专用 ARM64 AVD、各 C01–C16，独立 `tests/cocos-menu/expected.json` 固定原 32 项及全部超时。当前已完成实际本地构建／32 项运行、平台结果拒绝测试及五个真实 GitHub 场景：正常和两次恢复各 32/32，编译错误与输入缺失均使必需检查失败并阻断 PR。原生 Job 在专用 macOS ARM64 自托管 Runner 执行，汇总检查在 GitHub 托管 Ubuntu 执行；固定版本已通过真人运行验收，本地归档已完成，PR 尚未合并。其他项目须在原工程 Review 中审阅自己的构建／测试脚本、证据结构与设备合同，不能直接套用此试点结果。

复制共同工具及 `cocos-android.py`，使用项目已有 `scripts/build-cocos-android.py` 和 `scripts/test-cocos-android.py`。工程的 `harness/ui-ci/cocos-android.json` 保存 `expected_path / expected_sha256 / build_script / test_script / toolchain_files`；固定工具文件每项为 `base / relative / sha256`，其中 `base` 对应机器配置里的路径键。独立分母来自设计确认前的验收合同，不根据实际结果生成。项目构建／运行脚本负责 Creator 导出、Gradle 原生构建、实际触控、只读观察，以及专用设备设置恢复；平台入口核对干净宿主 SHA、固定工具身份、真实 APK、精确设备／用例集合、完整截图和清理结果。

物理安装与缓存路径写在仓库外的 JSON，通过 `--host-config` 传入；Runner 启动环境设置 `COCO_ANDROID_HOST_CONFIG` 指向该文件。入口不安装工具、不自动创建 AVD、不切换全局配置。该试点脚本使用独立 ADB 5038 和 AVD 端口 5580／5582，启动前拒绝已占用端口，只关闭本次所有的进程；正常及有界失败均恢复字号、方向。取消信号传递给项目脚本执行清理；若宿主强杀或 Runner 丢失，保留失败并由运行方检查专用进程／设置，不能把清理未知写成成功。

`context.json` 继续使用本页的五字段共同输入合同，CI 前后都执行未修改的 `check_inputs.py`。workflow 的原生 Job 为 `cocos-native-tests`，60 分钟；聚合 `cocos-native-ui` 使用 `always()`，只接纳原生 Job 的实际 `success`。固定 Actions、全部外部 fork 审批、本人同仓库 PR、临时 Runner 和 required check 来源沿本页规则；新增 Cocos 检查不能替换项目原需求 Gate 或 iOS 检查。上传目录只包含此运行的原始日志、源清单、APK 和专用设备证据；不得包含机器配置、凭据、全量 SDK／引擎及无关设备清单。

先审阅准确源码提交和上传清单，再创建所授权远程试点／PR、配置保护并注册临时 Runner。实际验证正常 → 平台失败 → 恢复，以及共同输入缺失 → 恢复；本地结果拒绝测试不能替代这些真实 Job。取得最终运行人审后，回到原 Change 的归档与交付流程。

[交付入口](../README.md) · [固定输入](../data-contract.md)
