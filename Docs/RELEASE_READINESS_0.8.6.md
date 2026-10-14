# OKVideoMac 0.8.6（Build 139）发布就绪记录

日期：2026-10-14。用户已授权启用官方 DMG 的崩溃上报、上传匹配调试符号、合成事件验收及更新 GitHub。公开源码的实际服务配置留空，后台令牌只用于构建机上的服务管理/符号上传。

当前为发布候选。15 项私有配置/隐私回归已通过；完整 Release XCTest、最终符号与合成事件后台解析、Developer ID、Apple Accepted、staple、Gatekeeper、最终 DMG/安装、签名 appcast 及 16 项公开资产核验须逐项通过后，才公开新版本并替换桌面入口。不会把旧 Build1377001 的服务验收当作新 Build139 的证据。

版本固定为 0.8.6 / Build 139，Android Bridge 0.3.48 / 60 与依赖版本保持。macOS 12、其他机器/系统、蓝牙/耳机、连续深睡耗电、完整泄漏普查及第三方依赖完整源码行覆盖仍按既有范围记录，不随本次配置启用自动扩大。

详见[服务配置与发布流程](CRASH_REPORTING_RELEASE_CONFIGURATION.md)和[发布说明](RELEASE_NOTES_0.8.6.md)。正式公开前 0.8.5 继续作为稳定版本，既有 tag 与资产不替换。

## 2026-10-14 validation status

- Configuration/privacy regressions: 15 passed. Release compilation passed. Full XCTest: 1283 passed, 4 failed, 17 conditional skips; 1304 total.
- All four failures occur before real OpenGL presentation in the fullscreen fixtures. Window Server/loginwindow shielding layers were observed while the Mac was locked; the user deferred unlocking. Failed runs remain retained and are not counted as passed. Original assertions are unchanged; temporary fullscreen diagnostics/Space fixture edits were reverted. Player code is unchanged.
- A separate official release client key was enabled and its 100-errors-per-hour rate limit verified after a fresh page load. The old acceptance key/configuration and existing management-token scopes are unchanged. Actual DSN values stay in an owner-only configuration file outside the checkout.
- Final packaging, dSYM upload, synthetic backend symbolication, signing/notarization/Gatekeeper, public asset verification and desktop installation have not run. GitHub work is a draft PR; 0.8.5 remains the stable release.

Next gate: unlock the Mac and keep the desktop visible, rerun the original graphics checks and full Release suite, then complete the remaining distribution gates from a clean main exact commit. Do not overwrite old release assets.
