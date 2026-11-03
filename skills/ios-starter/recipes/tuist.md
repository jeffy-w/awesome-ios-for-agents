# Recipe: Tuist

The project is described in Swift (`Project.swift`). External packages go in `Tuist/Package.swift`. Run `tuist generate` after every change. Never edit the generated `.xcodeproj`.

Verified on Xcode 27.2, Tuist 4.175.0 (2026-11-03): generate, add a Swift package, build, launch in the Simulator.

## Requirements

```bash
brew install tuist         # or: mise use tuist ; check: tuist version
brew install xcbeautify    # optional
```

## 1. Create the files

`Tuist.swift`

```swift
import ProjectDescription

let tuist = Tuist(project: .tuist())
```

`Project.swift`

```swift
import ProjectDescription

let project = Project(
    name: "MyApp",
    targets: [
        .target(
            name: "MyApp",
            destinations: .iOS,
            product: .app,
            bundleId: "com.example.MyApp",
            deploymentTargets: .iOS("18.0"),
            infoPlist: .extendingDefault(with: ["UILaunchScreen": [:]]),
            sources: ["Sources/**"],
            dependencies: []   // filled in step 3
        )
    ]
)
```

`Sources/MyAppApp.swift`: same SwiftUI `@main` app as in the XcodeGen recipe.

## 2. Generate

```bash
tuist generate --no-open
```

## 3. Add Swift packages

`Tuist/Package.swift`

```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "MyAppDependencies",
    dependencies: [
        .package(url: "https://github.com/onevcat/Kingfisher", from: "8.0.0"),
    ]
)
```

Use the catalog's `url` and `spm_version`. In `Project.swift`, add `.external(name: "<product>")` to the target's `dependencies`, using a name from `products`. Then:

```bash
tuist install
tuist generate --no-open
```

## 4. Build and run

See [verify.md](verify.md). Build command for this recipe:

```bash
xcodebuild -workspace MyApp.xcworkspace -scheme MyApp \
  -destination "id=$UDID" -derivedDataPath build build | xcbeautify
APP=build/Build/Products/Debug-iphonesimulator/MyApp.app
```
