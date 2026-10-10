# Android 消费者实施任务

## 1. 固定工程入口

- [x] 1.1 保存本组真实工程审核及本地 Apply 请求，含字号解释；核对远端 D/A、完整历史、policy 与工具身份。
- [x] 1.2 在新隔离工程固定原任务并通过 current propose，落入本 Change；固定 Proposal／Review／bindings 后通过 current start。

## 2. 实现固定消费者

- [x] 2.1 按 Apply/TDD 实现 MenuState 的冷启动、New／Continue、Menu、重置／取消及 best=0 分支，保留真实 RED／GREEN。
- [x] 2.2 导入固定 PNG／tokens，实现原生七状态、布局、两档字体及资源链，遵守原允许差异。
- [x] 2.3 接入 Back／Home／方向／Insets、可访问节点及调试只读观察，禁止测试状态注入。

## 3. 本地验证

- [x] 3.1 在固定工具链构建实际 APK，冻结源码／产物／资源／设备身份，安装到两台既有专用 AVD。
- [x] 3.2 执行各 A01–A16，保存全部断言、截图、失败和设置恢复；偏差修复后定向复验，保持精确 32 项及原分母。
- [x] 3.3 保留可恢复源码和本地结果，准备薄平台入口、定向拒绝测试及具体 CI／上传清单，提交远程操作审核。

## 4. CI 与交付

- [x] 4.1 取得具体远程授权后配置所审公开试点／PR／临时 Runner 及 required check，完成真实正向 CI。
- [x] 4.2 完成真实平台失败／恢复、共同输入缺失／恢复，验证失败／缺项／零项／跳过／取消／超时／身份不符均阻断。
- [ ] 4.3 在不依赖活动 Figma 时独立恢复包、源码和必要产物；取得实际运行验收及归档授权后同步 Spec、归档并保存本地提交，撤销 Runner／关闭本次设备。
- [ ] 4.4 更新唯一补充汇总及准确支持范围；Figma 读、写分别记证，Android／Unity 各自验收，不因本分支通过宣称整轮完成。

这份文件落入实际 Change 后是唯一实施清单。当前审核复本不勾选进度；执行日志和下一动作回实际 Change，不能再造并行 Tasks。

## 执行记录

- 2026-10-10：真实工程批准、propose/start current、OpenSpec 严格校验及固定文件导出通过。证据见 `evidence/engineering-review/`；业务实现尚未开始。
- Task 2.1：`evidence/tdd/{initial,session,reset,back}-{red,green}` 保存真实行为断言及源副本；最后 6 项 Java 状态测试通过，未计入设备用例。

- 本地整链：干净源码 `ed65683d9e562801b362e71d2d990c49564fefd7`，实际 APK `cfb4acc29d28f1272693840a826bf0b3686efc2087c33de41e5066bad6415aeb`，两台各 A01–A16 完整 32/32、前后 current 及设置恢复通过。`evidence/engineering-review/native-local-result.json` 保存绑定；原全部失败留在教程补充验证证据。Tasks 2.2–3.3 已满足，唯一下一动作是审核具体 CI 上传清单，获授权后接续 4.1；远程、运行人审、归档尚未执行。

## 最新接续记录：CI 第五轮失败后的本地修复

2026-10-10：已获原固定远程授权，公开库／PR #1、required check 及前四轮 CI 均符合预期；正向和编译恢复各 32/32，Task 4.1 完成。第五轮输入恢复后 regular/A14 因测试驱动点击未布局控件而失败，两个后续用例未运行；原失败保留，Task 4.2 仍未完成。五台 Runner 均已撤销。

本地最小修复 `ecc97b077c5d912a5a36710d9f8443aacc985f63` 保持产品、D/A、32 项分母、阈值及超时不变；新增六项回归实际 RED/GREEN，连同原 14 项共 20 项通过，随后两模拟器原生 32/32、前后 current 和清理通过。固定结果见 `evidence/engineering-review/readiness-repair-local-result.json`。此交接提交仅保存结果和本 Tasks；下一动作是审核具体修复源码上传与第六次临时 Runner，获授权后接续 Task 4.2，不重跑前五轮。运行人审、归档、合并和产品发布尚未授权／执行。

## 最新接续记录：获批修复后的第六轮 CI

2026-10-10：固定补充修复已获真实上传／单次 Runner 授权。第六轮 CI 的 20 项检查、两台原生 32/32、前后 current、required check、PR CLEAN 和清理均已核对。正常、编译故障／恢复、输入缺失／恢复链路闭合；第五轮仍记录为 29 通过、1 失败、2 未运行，修复后由第六轮恢复，不改写旧失败。产品、D/A、阈值、超时与分母未变。实际 CI 汇总见 `evidence/engineering-review/ci-platform-result.json`。Tasks 4.1／4.2 完成；4.3／4.4 仍待真实运行验收、具体本地收尾授权及实际收尾。本次仅记录进度，不新增提交、推送或归档。
