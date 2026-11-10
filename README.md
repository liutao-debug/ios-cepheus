# ios-cepheus

**Apple's iOS 16 running on a Xiaomi Mi 9.**

A port of [ios-sweet](https://github.com/dipa-studio/ios-sweet) to the Xiaomi Mi 9 (`cepheus`, Qualcomm
SM8150 / Snapdragon 855). Apple's open-source XNU kernel (xnu-8796, the iOS 16 generation), with ios-sweet's
patches, runs the **unmodified iOS 16.7.16 (20H392) userland of the iPhone X**.

> Work in progress — bring-up stage. Nothing boots on hardware yet. See STATUS.md.

## Why this is a small port

The Mi 9's SM8150 shares the Redmi Note 10 Pro's (SM7150) boot-time hardware addresses almost exactly:

| Hardware | SM7150 (sweet) | SM8150 (cepheus) |
|---|---|---|
| GICD / GICR | 0x17a00000 / 0x17a60000 | same |
| UFS | 0x01d84000 | same |
| framebuffer (cont_splash) | 0x9c000000 | same |
| PSHOLD | 0x0c264000 | same |
| timer | 19.2 MHz | same |
| IMEM restart reason | 0x146aa65c | **0x146bf65c** |

Only the IMEM address differs in the shim; the kernel patches (0001-0081) are boot-compatible. Board drivers
(touch = ST FTS over I2C, display = Samsung EA8076 command-mode AMOLED, PMIC = PM8150) come in later stages.

## Status

- ✅ Build toolchain (zig 0.13.0) — cross-compiles the shim on Windows
- ✅ cepheus shim (SM8150 IMEM fix) — builds to a raw arm64 Image
- ✅ cepheus ADT (tools/mkadt.py) — generates the Apple device tree
- ⏳ XNU kernel — needs macOS CI (fork this repo, run .github/workflows/xnu.yml)
- ⏳ boot.img — needs the Mi 9's stock DTB
- ⏳ hardware bring-up — needs the physical device

See `STATUS.md` for the full detail, and `GET-PAT.md` for the CI setup.

## Build the shim (Windows)

```powershell
# 1. get zig from https://ziglang.org/download/0.13.0/zig-windows-x86_64-0.13.0.zip
# 2. build
powershell -ExecutionPolicy Bypass -File build-shim2.ps1 E:\dsh\ios-sweet-port\ios-cepheus\shim
```

## Build the kernel (macOS CI)

1. Fork this repo to your GitHub account.
2. Actions -> xnu -> Run workflow (defaults: macOS 13.5, DEVELOPMENT, SWEET).
3. Download the `xnu-kernel` artifact.

## Credits

Built on ios-sweet (dipa-studio), apple's open-source XNU, [blacktop/darwin-xnu-build](https://github.com/blacktop/darwin-xnu-build),
and the SM8150 reference from [ios-flame](https://github.com/NWylynko/ios-flame). iOS itself is Apple's and is not
distributed here.
