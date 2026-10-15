# Figma Android 菜单交接候选

范围和责任见同包 `brief.md`；业务预期来自先于工程实现固定的 `expected-copy.json`。本包候选尚无真人批准，不能据此开始 Apply。

## 状态与交互

| 状态 | best／会话 | 参考及变化 | 行为 |
| --- | --- | --- | --- |
| menu/default | 128／无 | `small-f100-menu-default` | Continue 禁用；New game 新建会话 |
| menu/resumable | 128／有 | `small-f100-menu-resumable` | Continue 恢复同一次会话；New game 新建会话 |
| menu/zero-empty | 0／无 | `small-f100-menu-zero-empty` | Continue 禁用，New game 可用 |
| menu/zero-resumable | 0／有 | `small-f100-menu-zero-resumable` | Continue 恢复原会话 |
| dialog/reset-empty | 保留当前分数／无 | `small-f100-dialog-reset-empty` | Cancel／Back 不变；Reset → menu/zero-empty |
| dialog/reset-resumable | 保留当前分数／有 | `small-f100-dialog-reset-resumable` | Cancel／Back 不变；Reset → menu/zero-resumable |
| session/active | 保留当前分数／有 | `small-f100-session-active` | 静态 2×2 预览；Menu／Back 回对应有会话菜单 |

上述名字对应 `references/` 下同名 PNG 和 SVG。`references.html` 直接展示固定图片，不执行伪造的 Android 交互。模态层阻止背景点击与辅助访问；取消、返回必须恢复 best=128 或 0 对应的菜单，不能无条件回 default。会话身份可由后续受审只读观察证明，不允许测试直接注入成功状态。

完整参考包含七个小屏普通字号状态，加上小屏大字号、大屏普通字号、大屏大字号的菜单／弹窗／会话三个家族，共 16 张画面。其余尺寸／字号的菜单变体保持相同家族布局，只替换 best 文本及 Continue 启用、描边和文字／图标透明度；弹窗背景取当时菜单。静态参考没有 Figma prototype 连线，交互事实以这里及固定 scope/expected 为准。

## 单位、安全区与排布

Figma 1 单位映射 Android 1 dp；文字字号映射 sp。像素换算为 dp×densityDpi/160。两台目标显示分别为 360×640 dp 和 411.428571×914.285714 dp；Figma 大屏外框是 411.43×914.29，其 PNG/SVG 导出外框向上取整为 412×915。导出的不足 1 dp 边缘是格式留白，不能把整幅参考拉伸到设备尺寸后倒推控件。

参考顶栏 24 dp、底栏 32 dp；内容额外上下各 12 dp，标题从 y=36 开始。系统实际 WindowInsets 才决定运行安全区，参考导航横条由 Android 系统提供，不导入产品资源。内容最大宽 312 dp，水平居中；小屏侧边 24 dp，大屏约 49.715 dp。实际系统栏若使内容不可容纳，回报设计冲突后修订，不自行缩小字号、截断内容或冒用旧截图。

普通字号以及大屏使用参考所示的弹性纵向留白；小屏 1.3 字号用紧凑布局：菜单分区间距 12 dp、动作间距 8 dp，会话分区间距 8 dp。必需文字全部随 1.3 放大，控件保留 56 dp 高、重置文字按钮保留 48 dp 触控高。不能统一缩放整页。独立状态切换不改变排布规则；字号只测试 1.0 和 1.3，不声称覆盖全部系统最大字号。

会话棋盘为 264×264 dp、内边距 12、格距 12，每格 114×114，两个 2 和两个空格；它只是会话预览。弹窗宽 312、圆角 28、内边距 24，居中于系统栏之间的可用区；普通／大字号高 203／258 dp。遮罩为 ink 的 40%。具体矢量参考及 `reference-geometry.json` 保留实际几何值，描边居中半像素不能误当控件外框缩小。

## 字体与组件

`tokens.json` 固定颜色、字号和尺寸。Roboto Regular 用于正文，Medium 用于标签、按钮和数字，Bold 用于主标题及弹窗标题；不嵌入外部字体。所有产品文字字间距为零；源属性中的错误百分比已在候选修订中归零，不能从早期诊断 SVG 复制 `-2.6em`。引用的是修订后的原生 `.fig` 及固定参考。

| 文本角色 | 普通字号 | 1.3 字号 |
| --- | --- | --- |
| 菜单／会话标题 | 64 sp | 83.2 sp |
| 顶部标签／分数标签 | 12 sp | 15.6 sp |
| 正文／底部提示 | 16 sp | 20.8 sp |
| 按钮 | 18 sp | 23.4 sp |
| 最佳分数 | 36 sp | 46.8 sp |
| 弹窗标题 | 26 sp | 33.8 sp |
| 预览格数字 | 40 sp | 52 sp |

源文件包含 14 个本地组件，即七个组件的普通／1.3 字号版本；组件名称为 Cancel、Continue disabled、Continue enabled、Primary、Reset、Text reset、Reset best score。原生工程实现用可访问的容器、文字、按钮及模态表达这些意图，具体类与资源落点由工程 Design 决定，不生成第二套 Tasks。

## 素材与运行使用

| 文件 | 源与用途 | 后续工程约束 |
| --- | --- | --- |
| `assets/asset-arrow.png` | Figma 原创矢量导出，透明 72×72，即 24 dp 的 3×资源 | Continue 右箭头，禁用时与文字同样降透明度 |
| `assets/asset-reset.png` | 同上 | Reset best score 左侧图标 |
| `assets/asset-arrow.svg`、`assets/asset-reset.svg` | 同源 24×24 矢量 | 保留可编辑几何；选用转换时须记录输入／参数／输出摘要 |
| `references/*.png`、`references/*.svg` | Figma 实际全画面导出 | 仅作设计对照，不把整屏图片当原生实现 |
| `source/native-source.fig` | 固定源版本本地副本 | 可编辑恢复；运行及 CI 不依赖活动 Figma |

优先把两张 PNG 原字节放入 Android 无自动密度推算的资源位置，按明确 24 dp 布局绘制；工程 Review 固定确切路径。bitmap 缩放的边缘取样是平台渲染差异，图标形状、颜色和尺寸不改变。所有视觉资源来自本次新草稿，不引用原 AST/DAS，不引入第三方图像、字体或账户文件。

## 允许差异、验收与回退

- 字体的系统栅格化／抗锯齿可不同；文字、字号、字重、换行、可读性及控件必须一致，文字基线偏差最多 2 dp，不允许裁字或缺动作。
- 密度取整允许至多 1 个物理像素的非文字边缘误差；SVG 对大屏外框的向上取整按前述规则处理。
- 系统状态栏／导航栏的图标和实际 Insets 由固定 OS 决定；产品内容不得占用它们。系统栏差异不能解释产品排布、颜色或行为错误。

独立 expected 为 A01–A16×两台设备，共 32 项。进入工程前仍需完整 Review/Apply；之后实际保存源码和 APK 身份、逐例断言／截图、资源使用、失败证据及真实 CI 正向、平台失败阻断／恢复、共同输入拒绝。运行结果再交真人验收。任何 skipped、零测试、缺件、超时、取消或失败均不能算通过。

制作工具额度不足、MCP 不可用或原稿变动时，可按已经固定的完整包恢复，不换 latest。当前 Figma 路径是浏览器／原生 Agent＋人工 UI 操作，未验证 Figma MCP。Unity 尚无许可、物理真机未测；这些均不能用本包覆盖。设计内容需要改动时另建 D/A，只有工程偏差则回原 Change 返修。
