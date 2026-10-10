# Change：consume-approved-android-menu

## Why

Figma 已完成真实制作、反馈、读取、固定设计批准及发布；需要一个实际原生 Android 消费者验证交接是否成立。现有空白 APK 只证明工具链可用，不能替代菜单、设备用例和 CI。

## What Changes

- 在隔离原生 Android 工程实现获批七状态菜单、重置弹窗和静态会话预览。
- 接入固定 D/A、原 current 检查、行为 TDD、两设备 A01–A16、资源身份和实际可访问节点。
- 按原流程保留失败、恢复、真实 CI、运行人审和归档；CI 远程操作待完整内容另审。

## Capabilities

### New Capabilities

- `android-menu`：固定设计消费、菜单状态、Android 系统交互和模拟器验收。

### Modified Capabilities

无；原需求层、共同 UI 合同、iOS／Cocos 与旧批准不变。

## Impact

修改位置限工程审核页。没有完整游戏、跨进程存档、网络服务或产品发布。D 管视觉与交互，A 管真实设计批准，Spec 管本轮可观察行为，Design 管工程实现，`tasks.md` 是唯一实施任务源；没有第二套业务状态账本。

当前规划审阅副本在实际 current propose 通过后原样落入 Change；实际请求、工程确认、bindings 与 source SHA 另以固定引用关联，不用候选占位哈希冒充已发生事实。
