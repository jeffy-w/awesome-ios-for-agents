# Recipe: MobileBuildMCP scaffold

One command creates an Xcode workspace with a thin app target and a local Swift package (`<Name>Package/`) that holds all app code. It also writes `CLAUDE.md`, Cursor rules and Copilot instructions. Packages are added in the local `Package.swift`, so the agent never touches `project.pbxproj`.

Verified on Xcode 27.2, MobileBuildMCP 2.7.1 (2026-11-03): scaffold, add a Swift package, build, launch in the Simulator.

## Requirements

Node.js 18+ (for `npx`), or `brew tap getsentry/xcodebuildmcp && brew install mobilebuildmcp`.
If the MobileBuildMCP MCP server is already connected, its tools can replace the CLI commands below.

## 1. Scaffold

```bash
npx -y mobilebuildmcp@latest project-scaffolding scaffold-ios \
  --project-name MyApp --output-path ./MyApp \
  --bundle-identifier com.example.MyApp --deployment-target 18.0
```

Read the generated `README.md` and `CLAUDE.md` before editing. App code lives in `MyAppPackage/Sources/MyAppFeature/`.

## 2. Add Swift packages

Edit `MyAppPackage/Package.swift`, using the catalog's `url`, `spm_version` and a name from `products`:

```swift
    dependencies: [
        .package(url: "https://github.com/onevcat/Kingfisher", from: "8.0.0"),
    ],
    targets: [
        .target(
            name: "MyAppFeature",
            dependencies: [.product(name: "Kingfisher", package: "Kingfisher")]
        ),
```

## 3. Build and run

```bash
npx -y mobilebuildmcp@latest simulator build-and-run \
  --workspace-path ./MyApp/MyApp.xcworkspace --scheme MyApp --simulator-id "$UDID"
```

The command prints the app path and log files. Take the screenshot as described in [verify.md](verify.md).
