# 原生 Android 菜单工程约定

本工程采用 Standard、无需求层、已采用 UI 输入。真实请求及完整审核材料在 evidence/engineering-review/；用户已批准本地 Apply 与其中的字号解释，新远程操作及运行验收另审。

- 只修改本次已审范围；实际业务义务在当前 Spec、视觉在固定 D、设计批准在 A，工程技术选择在 Design，唯一实施进度在当前 Change 的 tasks.md。
- 先检查状态、实际用户输入、Artifact、固定设计与当前权威；保留既有工作。只读调查和工具准备不伪称业务 Propose。
- UI 动作前读取 harness/ui-design/no-requirements.md、current-check.md、实际 bindings；使用锁定 runtime 分别执行 current propose/start/resume。非零或 UNKNOWN 停止依赖实施，不改 historical，不换 latest，不重签设计。
- 原 Propose 后审阅，再 Apply；当前完整规划已经用户确认，原样落入实际 Change 后继续，不重新设计架构。实质设计、范围或必要验收改变时准备完整受影响 Artifact 差异，按原 Update 整体审核后接续。
- Apply 行为任务自动读取 .agents/skills/test-driven-development/SKILL.md；先独立行为测试，确认有效 RED 后最小实现至 GREEN。缺包、编译／路径错误不计行为 RED；不要删除正确实现制造失败。
- 仅 TDD 自动使用。Debugging、Receiving Review、Verification 等可选 Skill 由用户显式选择；日常排错和完成核查仍必须执行，不声称已加载可选方法。
- 普通执行错误在授权内诊断、修正、定向复验；同一未解决执行故障最多两轮，不改分母／阈值或无限重试。真实目标行为 RED/GREEN 不计执行恢复轮次，保留实际归因。缺权限或范围冲突时停依赖工作，先做好可审阅候选；已有授权不重复请求。
- 源码在 app/src/，行为测试在 tests/menu-state/，实际设备测试在 tests/android-menu/。测试用真实触点／按键，仅允许调试只读观察；无状态注入、整屏图片替代或自报 PASS。
- 固定设备、源码、APK、资产、独立预期与超时；测试失败、缺结果、零项、跳过、取消和清理未知不能通过。设置和专用进程按原验证合同恢复，仅操作本次明确设备。
- 工具、缓存和构建在隔离目录，不改全局安装／配置。现有 iOS/Cocos 工程及权威旧决定不变，不创建历史兼容机制。
- 原生构建／设备脚本准备完成后按真实入口执行；独立 Java 状态测试不代表设备或 CI 通过。每项勾选必须有本 Task 实际证据；详细日志保留在 evidence，下一动作写回原 Tasks。
- npm run spec -- <args> 使用项目固定 OpenSpec 1.12.0 和现有受控包装器；缺包／错来源停止，不绕过包装器。初始化生成的 apply 入口遵循 Harness 局部恢复约定。
- 完成时核对四项 Requirement、十个 Scenario 和 32 项设备合同；实际 CI、真实运行人审和获授权归档仍独立。Archive 在功能分支、同步正确 Spec 后单独提交，不能自行合并或发布。
