# OKVideoMac 0.8.6（Build 139）正式发布验证记录

日期：2026-10-14。[GitHub v0.8.6](https://github.com/yaolin-dev/OKVideoMac/releases/tag/v0.8.6) 已公开、非 Prerelease、latest；已安装并保持桌面 App 运行供用户测试。

## 固定身份与行为

- Release commit `590a065d93116d341f94b925b46d8fed0d719744`从干净 main 通过 `package-app.sh --mode distribution --notarize --crash-config FILE` 构建；annotated tag `v0.8.6` 固定该提交。商业工作树未参与打包。
- App 0.8.6（139），Android Bridge 0.3.48（60）；arm64 / 最低 macOS 12；构建机 macOS 14.8.9，Xcode 16.2 / SDK 15.2。依赖版本保持。
- 官方 DMG 在签名前从仓库外、所有者专用配置注入公开 HTTPS DSN；源码项目和源码归档保留空服务配置。DSN 可从 App 提取，不赋予后台读取/管理权限。实际管理令牌不进入 App、源码或日志。
- 上传默认关闭；已安装 App 的“设置 → 高级”中 `crash-upload-consent` 可用且为关闭，待发送报告为 0。验收未更改用户授权，未使用真实用户报告。
- 继承 0.8.5 的本机恢复、有限 SDK 文件等待、窗口重开和弹幕填充/Retina 阴影改进；普通字幕轨道未新增改动，PR #9 的作者贡献保持记载。

## 验证结果

| 项目 | 结果 |
| --- | --- |
| 完整 Release XCTest | 1287 通过、0 失败、17 条件跳过；共 1304 |
| 配置/隐私回归 | 15 通过，包含 FIFO 有限读取、权限/符号链接、无效 DSN、源码归档分块边界和令牌扫描 |
| 实际私有值检查 | 两个现有真实服务地址均不在源码/源码归档/日志中；真实管理令牌不在 App、源码或日志中 |
| 签名与公证 | 36 个 Mach-O；Developer ID、Accepted、staple、Gatekeeper、盘内布局、source index、APK 与 SBOM 通过 |
| Hardened Runtime | 最终代码与依赖的隔离身份副本：QuickJS、MPV/FFmpeg、Node/V8 JIT、5 秒 App 运行通过；隔离进程以 SIGTERM 结束，不据此宣称正常 AppKit 退出验收 |
| 安装 | 签名文件字节、链接与执行位一致；独立 strict/deep、staple、Gatekeeper 通过；旧版本正常退出后安装并保留备份 |
| 正式身份启动 | 使用现有用户配置，窗口可见且持续观察 20.0 秒；观察器开始后 6.862 秒首次见窗口，该数字包含 CUA 调度时间，不是纯 App 启动耗时 |
| 公开资产 | 16 项本地 SHA-256、GitHub digest、匿名下载一致；latest feed 字节与 XML/DMG EdDSA 签名通过 |

最初锁屏时完整测试为 1283 通过、4 失败、17 跳过；Window Server/loginwindow 遮挡使真实 OpenGL 呈现不可用。用户解锁后原始完整测试全部复验通过，四项原全屏断言均通过；临时诊断/Space 改动已撤回，未放宽断言或新增跳过。原失败日志保留。

首轮打包在 Apple 提交后因 `HTTPClientError.connectTimeout` 停止；同一任务有限等待仍为 In Progress。按 Apple 官方支持的非加速 S3 端点重传同一字节的签名 DMG，获得 Accepted；从既有 ZIP 恢复同一签名 App，执行原打包脚本未改变的最后核验步骤。没有重建、重签、跳过门禁或使用首轮未知状态充当通过。

## 后台与符号范围

- Apple Accepted `e6f34fba-656a-44e3-b416-e2a898371aae`；Apple log 无 issues。DMG SHA-256 `8deb4d638740f3f3d6358f9789bb28955bc23a2b86bd83a2c93b184d833c3daf`；stable feed/公钥沿用既有配置，Build139 高于138。
- 最终 App UUID `039C19BA-2C64-39CE-8B51-C4B1E0375630`，重启助手 UUID `C7A44C75-9544-3096-8713-AAF0031D9070`，与最终二进制匹配。官方 sentry-cli 处理两个指定 DWARF 成功；未上传源码 bundle，也未上传旧 C 故障夹具。
- 登记 `com.okvideomac.OKVideoMac@0.8.6+139`。最终签名 App 的生产上传进程发送两份合成地址记录，HTTP200；授权网页分别核对事件 ID、0.8.6（139）、`okvideomac-crash-reports`、源码行、Debug ID 和符号文件 Ok：
- app: event `c5d764176d4b4f45b3e8ae2bd5b652b8`, `CrashUploadController.setConsent`, `CrashUploadController.swift:67`, Debug ID `039C19BA-2C64-39CE-8B51-C4B1E0375630`.
- helper: event `033f4af1745d4976af03dad55e027da5`, `RelaunchArguments.init`, `main.swift:11`, Debug ID `C7A44C75-9544-3096-8713-AAF0031D9070`.
- 两份事件网页用户计数、附件、回放均为 0。现有管理令牌读取权限未扩大；这是网页核验加既有 allowlist/授权回归，不是完整后台 JSON 审计。源码上下文未上传。
- 合成记录只检验最终生产上传和后台解析；不是最终二进制的新实际故障触发验收。重试、撤回、禁止未授权发送由本轮完整回归与既有隔离故障证据覆盖，未将旧 Build1377001 的后台解析替代本次结果。
- 36 个 image 中，App/重启助手匹配；34 个既有缺 dSYM 记录含32个原生代码镜像与2个无代码静态 SDK 隐私资源 stub。不声明完整第三方源码行覆盖。
- 发布客户端配置启用且每小时限100条错误；旧验收配置保持。服务端数据清洗、默认清洗、禁止保存IP、移除用户地理字段、禁用 minidump 附件均从授权页面核对，未更改原规则。

## 安装与不可变旧版

桌面入口 `Desktop/OKVideoMac.app` 指向 `Applications/OKVideoMac-0.8.6-build139.app`，旧入口备份 `Desktop/OKVideoMac-backups/OKVideoMac-0.8.5-build138-20261014-131801.app`，旧 App 目标保留。未启用崩溃上传、自动更新或更改用户 SDK/AVD。

v0.8.5 的 Release ID、16项资产 ID/大小/digest 和 annotated tag 保持不变。发布后的文档不改变 v0.8.6 tag、签名资产、构建时源码/notes 快照。

## 公开资产 SHA-256

| 文件 | SHA-256 |
| --- | --- |
| `OKVideoMac-0.8.6-AndroidDexBridge-release.apk` | `08d8d8dfdb704baac6ef83c5d392f1642ff3c25baf84cc539fce0c4d9e165b9c` |
| `OKVideoMac-0.8.6-build139-SHA256SUMS` | `2ffe3565325e224f5ea8e2c2c84fc3b641f58645c911ba2983baef99ef3a6511` |
| `OKVideoMac-0.8.6-build139-SOURCE_RELEASE_INDEX.json` | `741d6428d663640e0a89903e41210ef9120767c39f64d9b2958407d571d6a1e5` |
| `OKVideoMac-0.8.6-build139-SOURCE_RELEASE_MANIFEST.json` | `ae48f8f9b7a005c5a5b913b8a1927e37e55cb65bebd91d581fa691179efef3d2` |
| `OKVideoMac-0.8.6-build139-licenses.tar.gz` | `fb3437484d204240e8df6c1227eba6c53bbca1df31bd90eef2f57d52b1e7dac0` |
| `OKVideoMac-0.8.6-build139-source.tar.gz` | `4aea69d1b780980b76b3620f6d4663300ede343669ca110a4784f91398a1b4a4` |
| `OKVideoMac-0.8.6-build139-third-party-source.tar.gz` | `bcc3528102abc0726a51fc8a6d2baa4b32309a5d8f0143018a8bd555de62f134` |
| `OKVideoMac-0.8.6.dmg` | `8deb4d638740f3f3d6358f9789bb28955bc23a2b86bd83a2c93b184d833c3daf` |
| `OKVideoMac-0.8.6.dmg.sha256` | `5767cec5abddf2cb64717fb8c8ef56e872b91be9dc72eada0f492e1daf3425bc` |
| `OKVideoMac-Android.cdx.json` | `a775ecb616a28d2bc8c77b16f3da9d8f3db711e8bc3ee7d9a24b7bdf8d896ea8` |
| `OKVideoMac-Android.spdx.json` | `d22a3e87b2441fc8b0ae2534d9ca55acbbd2caa11ab4d0a7ffa20d944b21096a` |
| `OKVideoMac-macOS.cdx.json` | `104abaf60a7409e20a62f9fc52df6a3eae11f988b4b87acc5caeaf8381ffbc6f` |
| `OKVideoMac-macOS.spdx.json` | `9189e21d9d953872ab8a5527c19abb61ffc449656c80baf398c84bfbba027990` |
| `RELEASE_NOTES_0.8.6.md` | `18780bc0ccc4908e71acbd77f59f1e452c5964bb4747c0178f2ce3cd4d5b8bde` |
| `THIRD_PARTY_NOTICES.md` | `a9787bb1b1e19456c8ec0ef439c9a2a8de8a4ef32b6fb1d4f21e614b14b2d45e` |
| `appcast.xml` | `0e98444c3062b4fd02adc5a814a4cd168d15dfe1ee4a1d06c7899bd6c34b78fd` |

## 未扩大的验收范围

本轮未重做真实睡眠/唤醒、macOS12/27或其他机器、蓝牙/耳机、外部 Node Contract B 样本、连续深睡耗电、全面泄漏普查或 Sparkle 更新安装全流程。此前实机证据保留其原范围；17项条件跳过未计为通过。原生可复现性例外继续记录，不随配置启用自动消失。
