# ios-cepheus 移植状态（iOS 16 → 小米 9）

> 目标：参考 dipa-studio/ios-sweet，把 iOS 16 移植到小米 9（cepheus，骁龙 855 SM8150）。
> 状态更新时间：2026-11-10

## 一、已完成（本地 Windows 环境，无需真机/macOS）

| # | 里程碑 | 产物 | 位置 |
|---|---|---|---|
| 1 | 交叉编译工具链 | zig 0.13.0 (79MB) | `zig-windows-x86_64-0.13.0/` |
| 2 | sweet shim 编译 | Image 208896 字节 | `ios-sweet/shim/out/Image` |
| 3 | 小米9 设备树 | cepheus.adt 10560 字节 | `ios-cepheus/cepheus.adt` |
| 4 | 打包工具 | mkbootimg.py（已 patch gki） | `downloads/mkbootimg.py` |
| 5 | 小米9 专用 shim | Image 208896 字节（SM8150 IMEM 修正） | `ios-cepheus/shim/out/Image` |

### 构建脚本
- `build-shim2.ps1 <shim-dir>` — zig 编译+链接 shim（参数化，可编 sweet 或 cepheus）
- `elf2bin.py` — Python ELF→裸机 Image 转换（替代 objcopy+truncate）

## 二、关键技术结论（已从源码确认）

### SM7150(sweet) vs SM8150(小米9) 引导期地址
| 地址 | SM7150 | SM8150 | 结论 |
|---|---|---|---|
| GICD / GICR | 0x17a00000 / 0x17a60000 | 相同 | 不改 |
| UFS | 0x01d84000 | 相同 | 不改 |
| framebuffer | 0x9c000000 | 相同 | 不改 |
| PSHOLD | 0x0c264000 | 相同 | 不改 |
| 定时器 | 19.2 MHz | 相同 | 不改 |
| **IMEM_RESTART_REASON** | 0x146aa65c | **0x146bf65c** | **已改** |

### mkadt.py 改动（小米9 vs flame 基座）
- FB: 0x9c400000 → 0x9c000000（小米9 cont_splash 在 0x9c000000）
- FB_H: 2280 → 2340（小米9 面板 1080x2340）
- compatible: google,flame → xiaomi,cepheus
- 其余（CPU 1+3+4 频率、kryo485、WCN3990 wlan 节点、mac 地址）全复用 flame

### 小米9 硬件真相（从 MiCode cepheus-q-oss 内核源码确认）
- CPU: 1×A76@2.84G + 3×A76@2.42G + 4×A55@1.78G
- 面板: Samsung EA8076 FHD+ command-mode AMOLED 1080x2340
- 触摸: ST FTS @ qupv3_se17_i2c 0x49（非 Goodix）
- PMIC: PM8150 / PM8150B / PM8150L
- 音频: TI tas2557 + Cirrus cs35l41
- 蓝牙/WiFi: WCN3990
- UFS: ufshc@1d84000

## 三、阻塞项（需外部资源）

1. **XNU 内核构建** — 只能 macOS（blacktop/darwin-xnu-build + GitHub Actions macos-14）
   - 需要：GitHub 账号，fork 仓库后跑 `.github/workflows/xnu.yml`
   - 无法在 Windows 本地绕过（需 Xcode 15 iig + KDK）
2. **boot.img 打包** — 需小米9 原厂 DTB（从真机 boot.img 用 unpack_bootv2.py 解包）
3. **最终验证** — 真机 fastboot boot，或 QEMU（仍需 macOS 内核）

## 四、下一步（一旦有资源）

1. fork ios-sweet（或本 cepheus 仓库）到 GitHub → 跑 macOS CI 构建 XNU 内核
2. 真机解包 DTB → mkbootimg 打包 boot.img
3. `fastboot boot shim-boot.img` 验证 probe（探测 GIC/PSCI/定时器/UFS）
4. 有内核后：mkpayload.py 打包 → 完整引导 → 攻 command-mode 显示 + ST FTS 触摸

## 五、参考
- ios-sweet（基座，SM7150）: E:\dsh\ios-sweet-port\ios-sweet
- ios-flame（同 SM8150，Pixel4）: E:\dsh\ios-sweet-port\ios-flame
- 官方移植指南: https://hackiosx.dev/porting
