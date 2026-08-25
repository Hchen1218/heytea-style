# heytea-style：手绘海报与桌宠 Skill

上传一张生活照片，把真实物件变成歪扭、稚拙、留白充足的图文海报，或一只真正能在 macOS / Windows 桌面运行的手绘桌宠。

> 非官方开源视觉研究与创作工具，不代表品牌合作或官方归属。

## 两种模式

### 1. 图文海报模式

| 原始照片 | 带字海报 | 无字海报 |
|---|---|---|
| ![原始食物照片](assets/examples/poster/source-food.jpg) | ![歪扭中文标题图文海报](assets/examples/poster/typography-poster.png) | ![通过小人动作讲故事的无字海报](assets/examples/poster/doodle-poster.png) |

带字版以歪扭中文标题为主要视觉信号；无字版依靠真实物件、小人动作与少量道具讲故事。两者会分别构图，不是同一张图片简单加字或删字。

### 2. 桌宠模式

| 用户原图 | 生成的桌宠形象 | 动态桌宠 |
|---|---|---|
| ![用户上传的粉绿奶茶原图](assets/examples/desktop-pet/source-drink.png) | ![由奶茶照片生成的最终桌宠母版](assets/examples/desktop-pet/canonical-pet.png) | ![粉绿奶茶桌宠最终动作预览](assets/examples/desktop-pet/motion-preview.gif) |

桌宠模式会把照片主体完整角色化，保留原轮廓、1–3 个识别色和关键结构，再生成透明动作资产、角色包以及启动/关闭入口。

## 能做什么

直接在 Codex 中上传图片并说明你想要的模式，例如：

```text
把这张照片做成图文海报，两套都出。
把这杯饮料做成一个桌宠。
```

- **图文海报模式**：主体保持真实照片质感，手绘人物、标题和附带元素围绕它展开。
- **桌宠模式**：主体本身成为角色，完成形象确认与动作确认后，导出可运行的透明角色包。

## 图文海报模式

海报模式提供 `带字版`、`无字版` 和 `两套都出（推荐）`：

- 带字版先生成无字底图，再根据标题模板构造歪扭字形骨架，最后独立生成标题层；普通电脑字体、整齐网格和圆润可爱字都会被拒绝。
- 无字版不预留标题区，不出现文字、数字或随机字符；叙事由微型小人的动作、真实物件和少量动作道具完成。
- 两种版本共享粗糙线条、纸面留白和真实物件，但使用不同的构图重点和参考模板。

`private-assets/reference-cutouts/` 中的标题、笔画、人物与动作模板用于稳定字形骨架、断笔、坏连接、粗细变化和动作比例。它们是绘图语法参考，不是需要复制到成品中的内容。

## 桌宠模式

```text
上传照片
→ 识别主体
→ 三款角色候选
→ 角色确认
→ 十二动作确认
→ 透明角色包与启动入口
```

没有可识别主体时，Skill 会要求重新上传；出现多个独立主体时，会先编号请用户选择。杯中饮料与碗中食物默认按“容器 + 内容物”整体处理。三款候选必须是角色设计差异，而不是同一角色只换动作。

![十二动作桌宠审核表](assets/examples/desktop-pet/contact-sheet.png)

十二个必需动作：`idle`、`walk`、`rest`、`happy`、`drag`、`land`、`wave`、`signature`、`curious`、`stretch`、`tiptoe`、`play`。还可增加 `fall`（从高处释放后的下落）与 `touch`（鼠标靠近后追一小段、伸手触碰并回到原位）。

![桌宠运行尺寸素材预览](assets/examples/desktop-pet/runtime-screenshot.png)

最终运行素材使用真实 Alpha 透明底；白色或暖白背景只用于候选和审核。角色包采用 schema v2，并校验画布、帧数、透明度、脚底锚点、循环接缝、身份漂移和 ZIP 路径安全。

## 一次安装运行器

Electron 通用运行器只安装一次。之后每只角色只需要携带角色包、预览图以及启动/关闭入口。

- `启动桌宠.command` / `关闭桌宠.command`：macOS 入口。
- `启动桌宠.cmd` / `关闭桌宠.cmd`：Windows 入口。
- 这些入口位于角色交付文件夹，不是 HTML 页面中的按钮。
- 右键桌宠可以退出；系统托盘是桌宠隐藏后的备用入口。

Skill 在启用桌宠功能前会先做只读环境预检。缺少运行器或构建环境时，它会列出将安装的内容与位置；只有用户明确同意后才自动补齐。

## 快速开始

### 安装 Skill

```bash
git clone <repository-url> ~/.codex/skills/heytea-doodle-poster
cd ~/.codex/skills/heytea-doodle-poster
python3 -m pip install -r requirements.txt
```

重新打开 Codex 后，上传图片并使用上面的自然语言示例即可触发对应模式。

### 环境预检与运行器安装

```bash
python3 scripts/check_desktop_pet_environment.py --json
python3 scripts/install_desktop_pet_runtime.py --json-plan
```

确认安装计划后：

```bash
python3 scripts/install_desktop_pet_runtime.py --yes
```

如果 Node.js / npm 也缺失，并且 macOS 已有 Homebrew 或 Windows 已有 winget，可在同一次明确授权后运行：

```bash
python3 scripts/install_desktop_pet_runtime.py --yes --install-toolchain
```

默认安装到 macOS 的 `~/Applications/Doodle Desktop Pet.app`，或 Windows 的 `%LOCALAPPDATA%\\Programs\\Doodle Desktop Pet`。不会自动开启开机启动，也不会绕过 Gatekeeper、SmartScreen 或系统权限提示。

### 本地启动运行器

```bash
cd assets/desktop-pet-runtime
npm install
npm start
```

不要直接打开 `src/renderer/index.html`：透明置顶、托盘、角色包读取和桌面交互依赖 Electron 主进程与 preload。

### 构建与校验角色包

```bash
python3 scripts/build_desktop_pet_pack.py \\
  examples/desktop-pet/pink-green-drink \\
  --out generated-pets/pink-green-drink-v2.zip \\
  --review-dir generated-pets/pink-green-drink-review

python3 scripts/validate_desktop_pet_pack.py \\
  generated-pets/pink-green-drink-v2.zip
```

角色确认前不生成动作，动作确认前不构建最终 ZIP。构建器同时输出 contact sheet、动态 GIF 和跨平台角色交付目录。

## 开发与测试

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m json.tool evals/evals.json >/dev/null
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/*.py

cd assets/desktop-pet-runtime
npm ci
npm test
npm run pack:mac   # macOS
npm run pack:win   # Windows
```

CI 在 macOS 与 Windows 上运行 Python 测试、Electron 单元测试和当前平台构建。模板完整性测试会拒绝缺失的核心参考板、失效路径、不可读图片、绝对本机路径，以及被错误标记为反例的主模板。

## 目录结构

```text
.
├── SKILL.md
├── references/
├── scripts/
├── tests/
├── evals/evals.json
├── assets/
│   ├── examples/
│   └── desktop-pet-runtime/
├── examples/desktop-pet/pink-green-drink/
└── private-assets/reference-cutouts/
```

`node_modules/`、`dist/`、用户原始素材、运行缓存、重复 ZIP 和安装后的应用不会进入仓库。

## 边界与授权

- 本项目是非官方开源视觉研究与创作工具，不声称品牌合作或官方归属。
- 用户应确认自己对上传图片拥有必要的使用权。
- 代码与运行器采用 [MIT License](LICENSE)。自制示例与第三方参考资产的授权边界见 [ASSET-NOTICE.md](ASSET-NOTICE.md)。
- 首版不包含聊天、声音、抢鼠标、恶作剧、多宠同屏、Linux、自动更新或云端角色市场。
