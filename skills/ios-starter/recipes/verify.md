# Build, launch and check in the Simulator

## Pick one simulator by UDID

Do not use `booted` as the device. When several simulators are booted, `simctl io booted screenshot` fails.

```bash
xcrun simctl list devices available
UDID=<udid of an iPhone running an iOS version >= the deployment target>
xcrun simctl boot "$UDID" 2>/dev/null || true   # already booted is fine
```

## Build

Use the build command from the recipe. If `xcbeautify` is not installed, drop `| xcbeautify` and add `-quiet`.
Add `set -o pipefail` before piping so a failed build is not hidden by the formatter.

## Install, launch, screenshot

```bash
BUNDLE_ID=$(/usr/libexec/PlistBuddy -c "Print CFBundleIdentifier" "$APP/Info.plist")
xcrun simctl install "$UDID" "$APP"
xcrun simctl launch "$UDID" "$BUNDLE_ID"
sleep 3
xcrun simctl io "$UDID" screenshot launch.png
```

Look at `launch.png`. The task is done only when the build succeeded and the first screen is visible.
