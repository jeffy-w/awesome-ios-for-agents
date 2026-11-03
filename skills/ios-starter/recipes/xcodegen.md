# Recipe: XcodeGen

The project is described in `project.yml`. To change targets, settings or packages, edit the YAML and run `xcodegen generate` again. Never edit `project.pbxproj` by hand.

Verified on Xcode 27.2, XcodeGen 2.46.0 (2026-11-03): generate, add a Swift package, build, launch in the Simulator.

## Requirements

```bash
brew install xcodegen      # check: xcodegen --version
brew install xcbeautify    # optional, shorter build logs
```

## 1. Create the files

Replace `MyApp`, `com.example` and the iOS version with the user's answers.

`project.yml`

```yaml
name: MyApp
options:
  bundleIdPrefix: com.example
  deploymentTarget:
    iOS: "18.0"
packages: {}            # filled in step 3
targets:
  MyApp:
    type: application
    platform: iOS
    sources: [Sources]
    dependencies: []    # filled in step 3
    settings:
      base:
        GENERATE_INFOPLIST_FILE: YES
        MARKETING_VERSION: "1.0"
        CURRENT_PROJECT_VERSION: "1"
        INFOPLIST_KEY_UILaunchScreen_Generation: YES
        SWIFT_VERSION: "6.0"
```

`Sources/MyAppApp.swift`

```swift
import SwiftUI

@main
struct MyAppApp: App {
    var body: some Scene {
        WindowGroup { Text("Hello") }
    }
}
```

## 2. Generate

```bash
xcodegen generate
```

Add `*.xcodeproj` to `.gitignore` if the team agrees to always regenerate.

## 3. Add Swift packages

For each library chosen from the catalog, use its `url`, `spm_version` and a name from `products`:

```yaml
packages:
  Kingfisher:
    url: https://github.com/onevcat/Kingfisher
    from: 8.0.0
targets:
  MyApp:
    dependencies:
      - package: Kingfisher
```

If the product name differs from the package key, add `product: <ProductName>` under the dependency. Run `xcodegen generate` again.

## 4. Build and run

See [verify.md](verify.md). Build command for this recipe:

```bash
xcodebuild -project MyApp.xcodeproj -scheme MyApp \
  -destination "id=$UDID" -derivedDataPath build build | xcbeautify
APP=build/Build/Products/Debug-iphonesimulator/MyApp.app
```
