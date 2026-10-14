# OKVideoMac 0.8.6（Build 139）发布就绪记录

日期：2026-10-14。用户已授权启用官方 DMG 的崩溃上报、上传匹配调试符号、合成事件验收及更新 GitHub。公开源码的实际服务配置留空，后台令牌只用于构建机上的服务管理/符号上传。

状态：正式发布、安装、最终 App/重启助手后台解析与全部16项公开资产核验通过。实际结果与范围见[正式验证](RELEASE_VALIDATION_0.8.6.md)。

版本固定为 0.8.6 / Build 139，Android Bridge 0.3.48 / 60 与依赖版本保持。macOS 12、其他机器/系统、蓝牙/耳机、连续深睡耗电、完整泄漏普查及第三方依赖完整源码行覆盖仍按既有范围记录，不随本次配置启用自动扩大。

详见[服务配置与发布流程](CRASH_REPORTING_RELEASE_CONFIGURATION.md)和[发布说明](RELEASE_NOTES_0.8.6.md)。0.8.5 作为历史稳定版本保留，既有 tag 与资产不替换。

## Initial locked-desktop validation checkpoint

- Configuration/privacy regressions: 15 passed. Release compilation passed. Full XCTest: 1283 passed, 4 failed, 17 conditional skips; 1304 total.
- All four failures occur before real OpenGL presentation in the fullscreen fixtures. Window Server/loginwindow shielding layers were observed while the Mac was locked; the user deferred unlocking. Failed runs remain retained and are not counted as passed. Original assertions are unchanged; temporary fullscreen diagnostics/Space fixture edits were reverted. Player code is unchanged.
- A separate official release client key was enabled and its 100-errors-per-hour rate limit verified after a fresh page load. The old acceptance key/configuration and existing management-token scopes are unchanged. Actual DSN values stay in an owner-only configuration file outside the checkout.
- At the initial draft checkpoint, final packaging, dSYM upload, synthetic backend symbolication, signing/notarization/Gatekeeper, public asset verification and desktop installation have not run. At that checkpoint GitHub work was a draft PR and 0.8.5 was stable.

## Unlocked desktop revalidation

The user unlocked the Mac and kept the display visible. The unchanged full Release suite passed: **1287 passed, 0 failed, 17 conditional skips, 1304 total**. All four previously blocked fullscreen cases and the crash-upload controller suite passed. A temporary caffeinate assertion kept the display awake only during this run. Earlier locked-screen failures remain recorded above; no assertions were relaxed and no tests were newly skipped.

Final distribution gates passed; see the formal validation record above. Earlier failures and scope limits remain retained. Old release assets are unchanged.
