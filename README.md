# 幸运转盘抽奖工具（Lucky Wheel）

一款轻量级幸运转盘抽奖桌面小工具，支持启动抽奖并展示中奖结果，附带图标资源与一键启动脚本，开箱即用。

## 功能特性

- 转盘抽奖交互
- 图标与视觉资源内置（images）
- 一键启动脚本（启动抽奖.bat）
- 轻量纯 Python 实现

## 技术栈

Python 3.x（lucky_wheel.py）；桌面 GUI（如 tkinter / PySide）；资源以 images 组织。

## 目录结构

```
lucky_wheel/
├── .gitignore
├── BUILD.md
├── CHANGELOG.md
├── images/
├── LICENSE
├── lucky_wheel.py
├── 启动抽奖.bat
```

## 安装与运行

详见仓库根目录 `BUILD.md`（含依赖版本、虚拟环境、启动与打包方式）。

通用步骤：

```bash
# 进入项目目录后，按 BUILD.md 配置依赖并运行
```

## 合规说明

本项目已按统一合规基线完成改造：可见版权头、LICENSE、全局异常与日志脱敏、安全模式审计。详情见 `CHANGELOG.md`。

## 版权与许可

© 中哥  All Rights Reserved

- 本仓库代码仅限项目内部使用，未经授权禁止转载、二次分发或商用。
- 开源许可与版权归属详见仓库根目录 `LICENSE`。
- 合规改造说明见 `CHANGELOG.md`，构建与运行说明见 `BUILD.md`。
