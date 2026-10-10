# Android 工程规划审核

2026-10-10。Figma 设计已获真实批准并发布。本次拟在隔离目录实现原生 Android 菜单，并完成两台既有专用模拟器的 32 项本地验证。**尚未开始 Apply；本次审核不包括新远程仓库、Runner 或运行验收。**

## 本次确认什么

1. 按[已批准的设计及发布记录](../figma-android-design/review/approval/README.md)，使用原生 Java／Android Views 实现七状态菜单、重置弹窗和静态会话预览。
2. 沿现有 Standard 路径执行 current `propose` → 固定原 Change／Review／bindings → current `start` → Apply/TDD；唯一工作清单是下列 Tasks。两设备各 A01–A16，不删减状态、失败恢复或后续 CI 义务。
3. 确认下述**字号解释**：本试点优先保持获批参考中的两组视觉字号；工程显式转换，不能把设计表误读成 Android 默认 `sp` 会线性放大。其他未测字号不作通过声明。

| 固定输入 | 内容 |
| --- | --- |
| 设计 D／批准 A | `0c2b7c404648f448c794769357b7ed3c8abd013f`／`c6f8cb0b1bb9db34cf894a383092dee4d5bdbc8d` |
| 原工程输入 S | `191cd85b86f9ddf3f3ba1e759c9527794afc540d`；[独立预期](../figma-android-design/review/inputs/expected.json)先于实现固定 |
| policy／共同工具 | 已审 policy `03eefa28dc36a22e807a5c8147359ddf0be97d9f`；`ui-check/1` 及 Darwin/arm64、CPython 3.13 锁保持不变 |
| 新工程／Change | `/private/tmp/ui-reconciliation-20261009-kd2a3glf/android-menu`；分支 `codex/android-menu-supplementary`；Change `consume-approved-android-menu` |
| 工具链 | 原生 Android 探针已验 Java 17.0.20.1+1、Gradle 8.13、AGP 8.13.2、compile/target 36、build-tools 35.0.0；不是 Cocos 工具链 |
| 设备 | 既有 `Harness_UI_Small_20261009` 与 `Harness_UI_Regular_20261009`；API 37、ARM64、16 KB 页；精确镜像、尺寸与密度在独立预期中 |

具体职责与步骤分别见 [Proposal](change/proposal.md)、[Spec](change/specs/android-menu/spec.md)、[Design](change/design.md)、[唯一 Tasks](change/tasks.md)及[逐例验证合同](validation.md)。[固定输入](inputs.json)和[审阅摘要清单](review-manifest.json)绑定整组内容；当前是规划审阅副本，没有假称实际工程 Propose／start 已通过。审核后原样落入实际 Change；副本保持原字节，不同步勾选进度。

## 字号解释需要明确确认

原交接表同时写了“sp”和 64 → 83.2 等线性 1.3 倍视觉尺寸；Android 14 起系统 `sp` 使用非线性缩放，不能假设这两个含义天然相同。官方建议用 `TypedValue` 转换，而不是用 `scaledDensity` 推算系统字号。[Android 官方说明](https://developer.android.com/about/versions/14/features#non-linear-font-scaling)

本次提议把两组固定参考及表中数值作为**目标视觉字号**：例如 1.3 档标题的最终文字尺寸为 83.2×设备 density 像素，仍随系统选择的 1.0／1.3 档变化；用明确的像素尺寸设置文字，或逆算对应 Android `sp`，避免再放大一次。这是所选试点的工程解释，不声称等于平台默认 `sp` 行为，不推广为通用 Android 字体适配建议。原设计、参考、阈值及字号可读性义务均不改。

该解释尚待本次工程审核确认，不能自动生效。如果要求完全采用平台默认 `sp` 曲线，则需先制作相应的新设计 D 并取得新 A；不能在实现时偷偷替换字体尺度或放宽已审差异。此处保留明确选择，不把单位冲突藏在代码中。

## 允许修改的位置

| 范围 | 用途 |
| --- | --- |
| 新隔离工程的 `AGENTS.md`、`README.md`、Git 忽略、Gradle 文件、`package.json`／锁、`scripts/openspec.mjs`、`harness/openspec-profile.json`、`openspec/config.yaml`、项目 Skills | 固定原生构建和项目级 OpenSpec 1.12.0／现有适配入口；缓存留在隔离目录 |
| `openspec/changes/consume-approved-android-menu/` | 原 Proposal／Spec／Design／唯一 Tasks、审阅、固定绑定与执行证据 |
| `app/src/main/AndroidManifest.xml`、`java/io/harness/menu/`、`res/values/`、`assets/ui/` | 原生界面、状态、生命周期、可访问节点及实际使用的固定 PNG／tokens |
| `app/src/debug/java/io/harness/menu/RuntimeObservation.java`、对应 release 空实现 | 只读实际 View／状态／资源观察，不提供状态注入或远程命令入口 |
| `tests/menu-state/`、`tests/android-menu/`、`scripts/build-android-menu.py`、`scripts/test-android-menu.py` | 行为 TDD、32 项真实设备测试及固定构建入口 |
| `harness/ui-design/`、`harness/ui-ci/`、`scripts/ui-design-check`、`design-inputs/`、`evidence/` | 沿用完整共同工具及固定输入；必要本地提交用于可恢复引用和交付 |
| 教程 `templates/ui-design/ci/android.py`、`github-android.yml.example`、对应定向测试／现行说明 | 如试点确需复用，新增薄原生 Android 入口；复用 `check_inputs.py`，不改共同规则或扩充运行锁 |

现有 preflight、Cocos／iOS 工程、旧批准、Goal 01–06、已确认方案及主仓库其他改动保留。不开完整 2048 玩法、持久化、后端、Unity 实施或物理真机验证。没有新的业务兼容层、任务系统或设计工具依赖。

## 通过条件和下一停点

本地需取得真实 current 通过、干净源码身份、可安装 APK、两设备各 16 项及资源／截图证据；缺项、失败、跳过或超时均不算通过。字号解释确认后仍需用真实绘制结果证明尺寸、基线和无裁切，不能只看公式。

本地通过后提交具体 CI 源码、工作流和上传清单供审核；既有公开库偏好不等于提前批准尚未形成的新上传内容。随后完成真实 CI 正常／平台失败／恢复、共同输入失败／恢复，再交运行人审和归档。Unity 缺许可仍保留，六项完整目标不结项。

当前设计批准已完成，无需重复确认。用户前次明确限定“Android 工程 Apply 另行审核”；[UI Skill](../../../../../templates/ui-design/skills/ui-design-workflow/SKILL.md)也要求“取包成功不启动 Apply；核对原 Tiny／Standard 路径、当前唯一 Tasks／真实任务和工程授权后再交工程角色。”因此先确认本页整组规划及字号解释，再开始本地 Apply。
