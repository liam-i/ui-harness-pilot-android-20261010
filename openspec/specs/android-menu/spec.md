# android-menu Specification

## Purpose

验证获批的 Figma 菜单设计在原生 Android 试点中的消费，覆盖原设计资源、菜单与会话、系统交互，以及两台专用模拟器的呈现和交付证据。

## Requirements

### Requirement: Approved design consumption

消费者 SHALL 恢复获批 D/A 的完整闭包，固定 policy、实际工程 Review、行为分母和允许差异；每次动作使用对应 current 检查，不依赖活动 Figma 或历史 PASS。

#### Scenario: Original engineering entry

- **WHEN** 原工程开始 Propose、开始或恢复 Apply
- **THEN** 分别执行 current propose、start 或 resume；缺包、撤回、UNKNOWN 或缺阶段授权停止依赖动作，保留诊断

#### Scenario: Runtime resources and rendering

- **WHEN** 原生 APK 显示任一受审状态
- **THEN** 实际使用获批两张 PNG 和 tokens、原生文字／按钮／容器；保存源文件→APK 条目→运行加载身份，不把参考整屏图片当实现

### Requirement: Menu and session behavior

App SHALL 遵循 D 的七状态及全部条件流；初始 best=128、无会话。New game 创建新会话，Continue 恢复原会话；静态会话显示 2×2 两个 2、两个空格及 Menu，不实现完整玩法。

#### Scenario: Cold start and disabled Continue

- **WHEN** 新进程冷启动并触点禁用的 Continue
- **THEN** 显示准确文案与 best=128，Continue 禁用，触点不产生会话或状态转移

#### Scenario: New and resumed session

- **WHEN** 任一菜单点击 New game，或有会话菜单点击 Continue，再点击 Menu
- **THEN** New game 的会话身份始终为新值，Continue 保持原身份，Menu 返回 best=128 或 0 对应的有会话菜单

#### Scenario: Reset and cancellation

- **WHEN** 无／有会话、best=128／0 的菜单打开重置框并取消或确认
- **THEN** 取消保留 best、会话及身份；确认只令 best=0；遮罩阻止背景交互，返回后 Continue 的启用状态正确

### Requirement: Android lifecycle and input

App SHALL 保持竖屏，按真实系统 Insets 保护内容与触控区域；存活进程内保留菜单／会话／弹窗与数据，新进程恢复初始值。

#### Scenario: Back hierarchy

- **WHEN** 依次在弹窗、会话、根菜单按真实 Android Back
- **THEN** 取消弹窗、返回菜单、离开前台；不重复派发，不误清除保留数据

#### Scenario: Home and genuine process restart

- **WHEN** 各状态 Home 后返回，或 force-stop 后启动新进程
- **THEN** 前者核实同一进程并保留原状态／数据，后者核实新进程且回 best=128、无会话；不能以 Activity 重建冒充新进程

#### Scenario: Orientation and accessibility

- **WHEN** 请求横屏、检视真实可访问节点或打开弹窗
- **THEN** 产品仍竖屏且数据保留；按钮名称／禁用属性正确，弹窗隐藏背景辅助访问；无键盘输入场景不增加虚构键盘用例

### Requirement: Bounded presentation and evidence

App SHALL 在两设备、1.0／1.3 档完整显示七状态及 best=0 弹窗变体，遵守 D 的颜色、几何、原字号参考与原差异阈值。字号工程解释以本组真实审核为前提；若不成立则停止，不改 D 或降低分母。

#### Scenario: Actual visual checks

- **WHEN** 运行 A14、A15、A16
- **THEN** 对照实际截图、View 几何／文字基线／资源、WindowInsets 与独立预期；触控区域至少 48 dp、不重叠、无裁切，保存未通过断言而非只报告截图存在

#### Scenario: Complete local and CI acceptance

- **WHEN** 判定本平台验证通过
- **THEN** 两设备精确 32 项、真实 CI 正向／平台失败／恢复及共同输入失败／恢复、完整可恢复证据与真人运行验收均须具备；缺失、零项、跳过、取消、超时或失败不能通过
