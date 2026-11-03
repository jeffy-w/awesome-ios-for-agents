# Recipe: Xcode MCP (Apple template)

Creates the same project as Xcode's *File › New › Project › App*, through the MCP server that ships with Xcode.

Verified on Xcode 27.2 (2026-11-03): create and build, launch in the Simulator.
**Limitation:** Xcode 27.2's MCP server has no tool to add Swift packages. The user adds packages in Xcode (*File › Add Package Dependencies…*), or pick another recipe when the app needs libraries.

## Requirements

Xcode 26.3 or later, with the MCP server connected to the agent, for example:

```bash
claude mcp add --transport stdio xcode -- xcrun mcpbridge
```

## 1. Find the template

Call `XcodeListTemplates` with `kind: "project"`, `platformFilter: ["ios"]`, `categoryFilter: ["Application"]`.
On Xcode 27.2 the SwiftUI app template is `com.apple.dt.unit.multiPlatform.app` with options `storageType` (None / SwiftData / Core Data) and `testingSystem` (None / XCTest / Swift Testing).

## 2. Create

Call `XcodeNewProject`:

```json
{
  "templateIdentifier": "com.apple.dt.unit.multiPlatform.app",
  "productName": "MyApp",
  "destinationPath": "/path/to/parent",
  "organizationIdentifier": "com.example",
  "options": { "storageType": "None", "testingSystem": "Swift Testing" }
}
```

It creates `MyApp/MyApp.xcodeproj` with the app, unit test and UI test targets. Files added to the app folder later are picked up automatically (synchronized folders).

## 3. Add packages

Ask the user to add each chosen package in Xcode with its `url` from the catalog, then continue.

## 4. Build and run

See [verify.md](verify.md). Build command for this recipe:

```bash
xcodebuild -project MyApp/MyApp.xcodeproj -scheme MyApp \
  -destination "id=$UDID" -derivedDataPath build build | xcbeautify
APP=build/Build/Products/Debug-iphonesimulator/MyApp.app
```
