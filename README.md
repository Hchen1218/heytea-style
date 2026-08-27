# heytea-style

把生活照片转成手绘图文海报，或生成能在 macOS / Windows 桌面运行的手绘桌宠。

> 这是非官方开源视觉研究与创作工具，与喜茶不存在合作、授权或官方归属关系。

![风味小怪兽桌宠](examples/desktop-pet/pink-green-flavor-monster-v3/preview.png)

## 效果概览

| 海报原图 | 带字海报 | 无字海报 |
|---|---|---|
| ![食物原图](assets/examples/poster/source-food.jpg) | ![歪扭标题海报](assets/examples/poster/typography-poster.png) | ![小人叙事海报](assets/examples/poster/doodle-poster.png) |

| 桌宠原图 | 写实卡通形象 | 动作预览 |
|---|---|---|
| ![饮料原图](assets/examples/desktop-pet/source-drink.png) | ![桌宠母版](assets/examples/desktop-pet/canonical-pet.png) | ![动态预览](assets/examples/desktop-pet/motion-preview.gif) |

![v2 动作审核表](assets/examples/desktop-pet/contact-sheet.png)

![桌面运行尺寸](assets/examples/desktop-pet/runtime-screenshot.png)

## 三种能力

| 模式 | 输入如何参与 | 输出 |
|---|---|---|
| 图文海报 | 保留照片主体的真实质感，增加歪扭文字与微型小人 | 带字海报、无字海报 |
| 写实卡通桌宠 | 原主体直接成为角色，保留轮廓与关键结构 | schema v2 固定动作角色包 |
| 风味小怪兽桌宠 | 提取颜色、配料、材质与动作 DNA，重新设计怪兽 | schema v3 分阶段行为角色包 |

桌宠生成遵循两次确认：先确认角色形象，再确认动作或行为。没有明确桌宠类型时，Skill 会询问选择“写实卡通”或“风味小怪兽”，不会自行决定。

## 安装 Skill

```bash
git clone https://github.com/Hchen1218/heytea-style.git ~/.codex/skills/heytea-doodle-poster
cd ~/.codex/skills/heytea-doodle-poster
python3 -m pip install -r requirements.txt
```

重新打开 Codex，上传图片后直接描述需求：

```text
把这张照片做成图文海报，两套都出。
把这杯饮料做成写实卡通桌宠。
把这杯饮料做成风味小怪兽桌宠。
```

完整工作边界见 [SKILL.md](SKILL.md)。海报与桌宠制作细节位于 [references/](references/)。

## 桌宠快速开始

运行器只需安装一次，之后每只角色通过轻量角色包导入。schema v3 需要运行器 `3.1.0` 或更高版本。

### 1. 环境预检

```bash
python3 scripts/check_desktop_pet_environment.py --json --required-schema 3
python3 scripts/install_desktop_pet_runtime.py --json-plan
```

检查安装计划并明确同意后，再执行：

```bash
python3 scripts/install_desktop_pet_runtime.py --yes
```

升级已有运行器需要额外添加 `--upgrade`。脚本会保留用户目录中的旧版本备份，不会静默替换系统目录应用、绕过系统安全提示或开启登录自启。

### 2. 构建并校验示例

schema v2 写实卡通桌宠：

```bash
python3 scripts/build_desktop_pet_pack.py \
  examples/desktop-pet/pink-green-drink \
  --out generated-pets/pink-green-drink-v2.zip \
  --review-dir generated-pets/pink-green-drink-v2-review

python3 scripts/validate_desktop_pet_pack.py \
  generated-pets/pink-green-drink-v2.zip
```

schema v3 风味小怪兽桌宠：

```bash
python3 scripts/build_desktop_pet_pack.py \
  examples/desktop-pet/pink-green-flavor-monster-v3 \
  --out generated-pets/pink-green-flavor-monster-v3.zip \
  --review-dir generated-pets/pink-green-flavor-monster-v3-review

python3 scripts/validate_desktop_pet_pack.py \
  generated-pets/pink-green-flavor-monster-v3.zip
```

需要生成启动/关闭入口时，为构建命令添加 `--delivery-dir <目录>`。交付目录只包含角色包、预览、使用说明和轻量启动入口，不复制 Electron 应用。

### 3. 本地运行器开发

```bash
cd assets/desktop-pet-runtime
npm ci
npm start
```

不要直接打开 `src/renderer/index.html`；透明置顶、托盘、角色导入和桌面物理依赖 Electron 主进程。

## v2 与 v3

| 能力 | schema v2 | schema v3 |
|---|---|---|
| 角色线 | 写实卡通 | 风味小怪兽 |
| 动作模型 | 固定 12 个动作，可选 `fall` / `touch` | 6–10 个自由行为，每个行为包含一个或多个阶段 |
| 长行为 | 整段动作循环 | enter / loop / exit 与完成事件 |
| 睡眠 | 普通动作 | 持久睡眠状态，可被点击或拖拽唤醒 |
| 交互 | 即时点击与拖拽 | 点击、拖拽互斥手势状态机 |
| 贴地 | 统一角色锚点 | 逐帧贴地；抓取和下落阶段允许悬空 |
| 屏幕底边 | 系统工作区 | 可选择工作区或显示器物理边缘 |

两个版本会编译成统一内部行为模型，共用窗口、物理、托盘和交付链路。已有 v2 角色包无需迁移。

## 开发与验证

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

CI 在 macOS 和 Windows 上运行 Python 测试、Electron 单元测试及对应平台构建。

## 目录结构

```text
.
├── SKILL.md                         # Skill 入口与权限边界
├── references/                      # 风格、工作流与角色包协议
├── scripts/                         # 构建、校验、交付与环境工具
├── tests/                           # Python 工具测试
├── assets/desktop-pet-runtime/      # Electron 通用运行器
├── assets/examples/                 # README 自制示例
├── examples/desktop-pet/            # 可校验的 v2 / v3 角色包
└── private-assets/reference-cutouts # 研究参考素材
```

本地生成结果、`generated-pets/`、`node_modules/`、`dist/`、用户原始素材、安装后的应用和运行缓存不会进入仓库。

## 授权与素材边界

- 代码与运行器采用 [MIT License](LICENSE)。
- 仓库自制示例采用 CC BY 4.0；具体范围见 [ASSET-NOTICE.md](ASSET-NOTICE.md)。
- `private-assets/reference-cutouts/` 是第三方视觉研究参考，不属于 CC BY 授权，也不能视为官方素材。
- 用户应确认自己拥有上传图片及生成结果所需的使用权。
- 请勿在未获授权时加入官方 Logo、吉祥物、包装标识或合作声明。
