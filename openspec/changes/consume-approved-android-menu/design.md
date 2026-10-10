# Android 消费者工程设计

## Context

固定输入及工具身份见工程审核页的 `inputs.json`。D=`0c2b7c404648f448c794769357b7ed3c8abd013f`，A=`c6f8cb0b1bb9db34cf894a383092dee4d5bdbc8d`，已完成远程独立恢复；尚未实施本 Change。

## Goals / Non-Goals

目标是由真实原生 Android 消费包，闭合已审菜单、两设备与失败恢复链。范围沿 D，采用项目已有无需求层 Standard 路径；不增加需求层、设计来源分支、完整玩法、存档或历史业务兼容。

## Decisions

### 原入口与批准

先固定真实工程请求作为 task 身份，恢复 UI 对象并执行 current propose；通过后本组四文件原样进入 `openspec/changes/consume-approved-android-menu/`。固定已有 Proposal、真实工程 Review、A、完整行为覆盖及原允许差异为 bindings，取得 current start 后才实施。恢复用 resume，UI PASS 不授予其他阶段权限。

复用 OpenSpec 1.12.0 的项目级入口、既有 Harness 适配及原 Apply/TDD；行为任务保存实际 RED／GREEN 证据。共同 UI checker 完整复制，规则锁、依赖、历史与角色不变。必要本地提交只在隔离试点，主教程不提交；请求和绑定记账不改变已审语义。

### 状态与原生界面

`MenuState.java` 保存 screen、best、会话身份和模态状态。`MenuApplication` 只持有本进程状态；Activity 重建从它恢复，新进程初始化 128。会话身份用进程标识加递增计数，供只读观察比较；测试不能修改模型。状态转换不依赖观察器存在。

`MainActivity` 处理生命周期、Insets 和 Back；`MenuScreen` 用实际 ViewGroup、TextView、Button／ImageView 组合菜单、棋盘和模态覆盖层。模态阻止背景触点，背景设为不参与辅助访问，保留 Cancel／Reset 正确名称与操作。Continue 的禁用属性、透明度及按钮区域必须同时正确。键盘无业务输入，记为不适用。

根 Activity 在 API 33+ 使用本地 SDK 已确认存在的 `OnBackInvokedDispatcher`；根菜单返回系统前台，其他两层调用同一状态转移，不能再次走旧 Back 回调。低 API 守卫只是保证最低构建声明可链接，本轮只验 API 37，不据此声称低版本运行通过。

### 素材、几何与字号

两张 PNG 原字节及 tokens 放在 `app/src/main/assets/ui/`；避免 Android 自动密度推算与 PNG 重新编码。读取实际 assets，关闭 bitmap 的隐式密度放大，按 24 dp ImageView 绘制。对每个资源记录 D 文件摘要、APK 解压摘要、运行加载摘要与实际使用节点。资源缺失须显式失败，不使用占位图。

布局按 D 的 312 dp 内容宽、24 dp 最小侧边、实际系统 Insets＋12 dp 内容间距；参考 24／32 系统栏只用于对照，不能硬编码为运行 Insets。普通与大屏使用参考弹性空白，小屏 1.3 档使用已审紧凑间距。模态在可用区居中；264 dp 棋盘、56 dp 主按钮、48 dp 最小触控均不缩小。对照 SVG／`reference-geometry.json` 的真实形状，处理大屏导出不足 1 dp 的取整留白。

**字号决定须随工程审核确认。** D 的线性两档视觉数值与 Android 默认非线性 `sp` 存在单位歧义。本试点以已批准的两档视觉尺寸为目标：基准角色值 64／12／16／18／36／26／40，大字号值 83.2／15.6／20.8／23.4／46.8／33.8／52；各值乘当前显示 density 得到最终绘制像素。只以真实系统 fontScale 选择受审档位，不把 `scaledDensity` 当通用系统转换公式。实现可直接设置 PX，或用 `TypedValue.deriveDimension` 逆算等效 SP；两者都不得额外重复缩放。真实 Paint 尺寸、文字完整性和基线仍独立验真。

这是一项固定试点视觉实现选择，不是 Android 通用辅助字体方案。未测档位不宣称合格，不修改系统字体设置来伪装通过；工程审核若不接受这项解释，先停止并另审设计修订。其他允许差异仍只有原 SYSTEM-GLYPHS／PIXEL-ROUNDING／OS-CHROME，不能加新豁免。

### 驱动与只读观察

真实触点和按键由专用 ADB 驱动，控件位置从实际 UI 层级读取并记录；状态前提通过正常操作形成。调试 `RuntimeObservation` 在布局／绘制后保存实际 View 的 bounds、text、Paint 字号／baseline、enabled、可访问属性、颜色／资源使用、模型身份、Insets 与帧序号到 app 私有文件。主机仅用 `run-as` 读取，release 变体为空实现；没有注入状态、任意代码执行或自报 PASS 的接口。

主机断言来自固定预期和本组验证合同，观察值只是实际值。点击前后需新的帧序号与状态／系统结果，避免旧观察文件误判。使用实际 `uiautomator dump`、设备截图核对原生节点；调试文件不能替代系统可访问节点或截图。TalkBack 真人体验和物理设备性能不在本轮通过声明内。

### 构建、用例与失败

复用已实测 Java／Gradle／AGP／SDK，不增加 UI 框架或更改全局 JDK。行为状态先做独立 Java 测试，保留真实失败与最小修复顺序；之后构建 debug APK，并记录干净 source SHA、APK SHA、资源、工具、设备和 suite 身份。

逐项驱动、分母及有限超时在工程审核的 `validation.md`；不从运行结果生成预期。两台设备全部跑 A01–A16，明确 best=0 弹窗与 New game 替换已有会话。截图与结构比较通过后仍交人审。若出现不可同时满足的系统约束和 D，记录冲突及最小修正候选，不自行降标准。

### 平台 CI

实际本地源码和测试完成后准备具体 GitHub 公开试点／同仓库 PR／临时 Mac ARM64 Runner 审核；此时不创建远程资源。新的薄 Android 平台入口复用共同 `check_inputs.py`，调用项目构建和设备脚本，核对精确 device/case 集合与 clean host SHA。固定 Actions、全部外部 fork 审批、required check 来源及临时 Runner 沿原 CI 合同。

真实链必须先共同输入检查，再原生构建／设备测试，最后再观察权威；托管聚合 `android-native-ui` 用 `always()`，仅接受原生 Job 真正成功。至少实际正常→平台编译失败→恢复、共同输入缺失→恢复五轮；两次恢复回到受审树。缺结果、零项、跳过、取消、超时、身份不符另以定向平台测试拒绝，不能取代真实故障 Job。

## Risks / Trade-offs

- 字号单位问题已显式交工程审核；没有得到确认前不能实现一种解释并宣称自动符合 D。
- Android Insets、Roboto 字形与 Figma 可能不同；依原阈值验证实际视图与截图，只允许已审差异。
- 观察字段可能遗漏或滞后；缺帧、缺字段和系统节点不符失败，不相信观察器自述成功。
- UI 权威可能前进；动作及 CI 前后重新观察，不冻结远端、不强推或以历史模式绕过。

## Migration Plan

创建独立消费者，不迁移旧业务。失败保留原始日志、受检源码与唯一 Tasks，修正实现后定向复验；退出恢复本次设备设置，只关闭本次所有的 AVD／ADB。包、源码、构建与 CI 证据独立恢复后再做真实运行人审与获授权归档。

## Open Questions

本次工程规划／字号解释及本地 Apply 待真实确认。新工程公开内容与 CI 操作待本地候选形成后审核；运行验收及归档在实际结果就绪后按原流程确认。Unity 仍缺许可，不由 Android 结果覆盖。
