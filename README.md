# objc4-debug

基于 Apple 官方 [objc4-951.7](https://github.com/apple-oss-distributions/objc4/tree/objc4-951.7) 的 macOS 源码调试工程。源码和依赖通过 submodule 固定版本，本地适配通过 patch 维护。

已验证：Apple Silicon、macOS 27.0.1、Xcode 27.2，Debug / arm64e。

## 使用

需要 Xcode、Python 3 和 xcbeautify。在项目根目录执行：

```sh
python3 support/bootstrap.py
./support/build.sh
./support/run.sh
```

也可以打开 `objc.xcodeproj`，选择 **objcDebug → My Mac → ⌘R**。

在 `objcDebug/main.mm` 中编写实验，在 `runtime/` 中下断点。可从 `objc_setAssociatedObject`、`lookUpImpOrForward`、`weak_register_no_lock` 开始。

命令行调试运行 `./support/debug.sh`，进入 LLDB 后输入 `run`。程序会打印实际加载的 libobjc 路径，确认使用本地编译的库。

## 目录

- `upstream/`：Apple 官方源码 submodule。
- `patches/`：runtime 和 SDK 头文件适配，按 `series` 顺序应用。
- `runtime/`、`dependency/`：自动生成的工作副本，不入库。
- `objcDebug/`：测试入口。
- `support/`：构建和调试脚本。

构建日志位于 `.build/logs/build.log`。

## 更新版本

将 `<新标签>` 替换为目标版本：

```sh
git -C upstream/objc4 fetch --depth=1 origin tag <新标签>
git -C upstream/objc4 checkout --detach <新标签>
python3 support/prepare.py
./support/build.sh
./support/run.sh
```

验证后，将 submodule 指针和调整后的 patch 一起提交。其他依赖可按相同方式更新。

patch 冲突会中止生成，未保存的源码改动也不会被覆盖。`bootstrap.py` 用于恢复仓库固定的版本，升级时使用 `prepare.py`。

本工程用于 macOS 本地实验，包含公开 SDK 和系统 ABI 适配；未验证 iOS、Intel 或 Release。源码许可证见各 submodule 和 [LICENSES](LICENSES/APPLE_LICENSE)。
