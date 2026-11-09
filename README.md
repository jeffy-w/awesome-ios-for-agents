# Awesome iOS for Agents

[中文](README_CN.md)

**Pick iOS open-source libraries by data, for people and for AI coding agents.**

Every library shows the same facts: stars, latest release, last commit, minimum iOS, Swift tools version, Swift language mode and issue reply rate. The top pick in each category comes from a fixed rule. Data refreshed **2026-11-09** and every week by GitHub Actions.

## For agents

Install the `ios-starter` skill, then ask your agent to start a new iOS app. It asks what the app needs, picks libraries from this catalog by the rule below, creates the project with a verified recipe, and builds and launches it in the Simulator.

```bash
npx skills add jeffy-w/awesome-ios-for-agents@ios-starter -g -y
```

Agents can also read the data directly: [`catalog.json`](catalog.json) · [`llms.txt`](llms.txt)

## How the top pick is chosen

- **Status is based on releases**: the date of the latest GitHub release. Only repos that have never published a GitHub release use their last commit date instead. Both dates are shown in the tables.
- **Status**: 🟢 active (< 1 year) · 🟡 slowing (1–2 years) · ⚪ inactive (≥ 2 years) · 🗄 archived.
- **🏆 Top pick** = the most-starred 🟢/🟡 entry in its category. Add-ons of another entry are not ranked. Categories of provider SDKs (backend, payments, analytics, crash reporting, sign-in) are *not ranked*: pick by service.
- **Min iOS** and **Swift tools** come from `Package.swift` at the latest release tag (or the highest version tag when the release tag is not a version number; otherwise the default branch).
- **Swift mode** is the language mode the library's own targets build in, read with `swift package dump-package` (Swift 6.4.2): `6` · `5` · `6/5` (some targets each) · `strict` = Swift 5 mode with complete concurrency checking. Only targets with Swift sources count, so ObjC/C-only libraries show `ObjC/C`; `—` = not a Swift package or not readable. It does not change your app's mode; `6` means the library's API was checked for data races, so Swift 6 code that uses it needs fewer `@preconcurrency` workarounds.
- **Issue replies** = share of issues from outside the project, opened 2025-10-10 to 2026-10-10, that a maintainer answered or closed (latest 100 per repo; bots do not count). Fewer than 5 issues shows the raw count, e.g. `0/2`; `off` = issues disabled. Shown for information, not used for the top pick.
- `*` after a Swift mode or issue value = it could not be read this time, so the last value read is kept; `swift_mode_checked` and `issues_checked` in catalog.json give its date.
- **Apple native** lists the system API for the same job and its minimum OS.
- Categories and descriptions are written by hand and only say what a project does. Notes quote a source. Status and rank are computed by [`scripts/build.py`](scripts/build.py).

## Start a new project

Four ways an agent can create an iOS app from nothing. Each was run end to end on Xcode 27.2 on 2026-11-03.

| Recipe | Project defined in | Add a package | Verified |
|---|---|---|---|
| [XcodeGen](skills/ios-starter/recipes/xcodegen.md) | `project.yml` | `packages:` in YAML | create, add package, build, launch |
| [Tuist](skills/ios-starter/recipes/tuist.md) | `Project.swift` | `Tuist/Package.swift` + `tuist install` | create, add package, build, launch |
| [MobileBuildMCP](skills/ios-starter/recipes/mobilebuildmcp.md) | Xcode project + local Swift package | local `Package.swift` | create, add package, build, launch |
| [Xcode MCP](skills/ios-starter/recipes/xcode-mcp.md) | Apple's Xcode template | in Xcode (no MCP tool in 27.2) | create, build, launch |

## Contents

- **Foundation**: [HTTP client](#http-client) · [OpenAPI client generation](#openapi-client-generation) · [WebSocket](#websocket) · [Network reachability](#network-reachability) · [Image loading & caching](#image-loading--caching) · [Local database](#local-database) · [Keychain](#keychain) · [Preferences (UserDefaults)](#preferences-userdefaults)
- **Architecture**: [Dependency injection](#dependency-injection) · [App architecture frameworks](#app-architecture-frameworks) · [Navigation](#navigation) · [URL routing](#url-routing)
- **Observability**: [Logging](#logging) · [Network & log inspector](#network--log-inspector) · [Crash reporting](#crash-reporting) · [Product analytics](#product-analytics)
- **Accounts & payments**: [In-app purchases & subscriptions](#in-app-purchases--subscriptions) · [Third-party sign-in](#third-party-sign-in) · [Backend as a service](#backend-as-a-service)
- **User interface**: [UIKit Auto Layout DSL](#uikit-auto-layout-dsl) · [SwiftUI component collections](#swiftui-component-collections) · [SwiftUI introspection](#swiftui-introspection) · [Popups & toasts](#popups--toasts) · [Animation playback](#animation-playback) · [Charts](#charts) · [Markdown rendering](#markdown-rendering) · [HTML parsing](#html-parsing) · [Markdown parsing](#markdown-parsing)
- **Swift language & data**: [Reactive frameworks](#reactive-frameworks) · [AsyncSequence operators](#asyncsequence-operators) · [Data structures](#data-structures) · [Sequence algorithms](#sequence-algorithms) · [JSON](#json) · [Cryptography](#cryptography) · [Protocol Buffers](#protocol-buffers)
- **Testing**: [BDD test frameworks](#bdd-test-frameworks) · [Test matchers](#test-matchers) · [Snapshot testing](#snapshot-testing) · [Value dumps & diffs](#value-dumps--diffs) · [Concurrency testing](#concurrency-testing)
- **Tooling**: [Linting](#linting) · [Formatting](#formatting) · [Project generation](#project-generation) · [Build log formatting](#build-log-formatting) · [View debugging](#view-debugging) · [Resource code generation](#resource-code-generation) · [Release & App Store Connect](#release--app-store-connect)
- **AI agent tooling**: [Build & run MCP servers](#build--run-mcp-servers) · [Simulator & device UI automation](#simulator--device-ui-automation) · [Apple docs for agents](#apple-docs-for-agents) · [SwiftUI skills](#swiftui-skills) · [Swift Concurrency skills](#swift-concurrency-skills) · [Simulator skills](#simulator-skills) · [Release skills](#release-skills) · [Skill indexes](#skill-indexes) · [AGENTS.md templates](#agentsmd-templates)

## Foundation

### HTTP client

Apple native: `URLSession async/await` (iOS 15)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Alamofire](https://github.com/Alamofire/Alamofire)** | 42.4k | 2026-09 | 2026-10 | 15 | 6.4 | 5 | 88% | HTTP client with request interceptors, retry, multipart upload and progress. |
| ⚪ | [Moya](https://github.com/Moya/Moya) | 15.4k | 2022-08 | 2026-07 | 10 | 5.3 | 5 | 0/2 | Network abstraction layer built on Alamofire. |
| ⚪ | [Get](https://github.com/kean/Get) | 988 | 2024-10 | 2024-10 | 13 | 5.5 | 5 | 0/0 | Typed API client built on URLSession. |

### OpenAPI client generation

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-openapi-generator](https://github.com/apple/swift-openapi-generator)** | 2.0k | 2026-11 | 2026-11 | 13 | 6.2 | 6 | 89% | Generates a Swift client and server from an OpenAPI document at build time. |

> **Note** · swift-openapi-generator: README: a Swift package plugin and CLI. Generated code uses apple/swift-openapi-runtime and a ClientTransport such as apple/swift-openapi-urlsession. ([source](https://github.com/apple/swift-openapi-generator#package-ecosystem))

### WebSocket

Apple native: `URLSessionWebSocketTask` (iOS 13)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [Starscream](https://github.com/daltoniam/Starscream) | 8.6k | 2024-03 | 2024-03 | — | 5.3 | 5 | 0/2 | WebSocket client. |

### Network reachability

Apple native: `NWPathMonitor (Network framework)` (iOS 12)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [Reachability.swift](https://github.com/ashleymills/Reachability.swift) | 8.0k | 2024-10 | 2024-10 | — | 5.3 | 5 | 0/1 | Network reachability notifications. |

### Image loading & caching

Apple native: `AsyncImage` (iOS 15)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SDWebImage](https://github.com/SDWebImage/SDWebImage)** | 25.6k | 2026-02 | 2026-04 | 9 | 5.3 | ObjC/C | 38% | Image downloader and cache, with coders for animated WebP, AVIF and HEIC. |
| 🟢 | [Kingfisher](https://github.com/onevcat/Kingfisher) | 24.4k | 2026-11 | 2026-11 | 15 | 6.2 | 5 | 87% | Downloads and caches remote images for UIKit and SwiftUI. |
| 🟢 | [Nuke](https://github.com/kean/Nuke) | 8.7k | 2026-11 | 2026-11 | 15 | 6.0 | 6 | 100% | Image loading pipeline with caching, prefetching and progressive decoding. |
| 🟡 | [SDWebImageSwiftUI](https://github.com/SDWebImage/SDWebImageSwiftUI) | 2.6k | 2025-11 | 2026-02 | 14 | 5.3 | 5 | 1/3 | SwiftUI views for SDWebImage. |

### Local database

Apple native: `SwiftData` (iOS 17) · `Core Data` (iOS 3)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[realm-swift](https://github.com/realm/realm-swift)** | 16.6k | 2026-09 | 2026-09 | 12 | 6.2.1 | 6 | 29% | Object database for mobile. |
| 🟢 | [SQLite.swift](https://github.com/stephencelis/SQLite.swift) | 10.2k | 2026-10 | 2026-10 | 15 | 6.1 | 6 | 89% | Swift layer over SQLite3 with typed query expressions. |
| 🟢 | [GRDB.swift](https://github.com/groue/GRDB.swift) | 8.7k | 2026-11 | 2026-11 | 13 | 6.1 | 6 | 100% | SQLite toolkit with migrations, record types and database observation. |
| 🟢 | [sqlite-data](https://github.com/pointfreeco/sqlite-data) | 2.0k | 2026-10 | 2026-11 | 16 | 6.4 | 6 | 77% | SwiftData-style models and queries on SQLite (GRDB), with CloudKit synchronization. |

> **Note** · realm-swift: MongoDB: Atlas Device SDKs reached end-of-life and were removed on 2025-09-30; the on-device database continues to exist as an open source project. ([source](https://www.mongodb.com/docs/device-sdks-deprecation/))

### Keychain

Apple native: `Keychain Services (Security framework)` (iOS 2)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Valet](https://github.com/square/Valet)** | 4.2k | 2026-09 | 2026-07 | 12 | 6.0 | 6 | 3/4 | Keychain wrapper with iCloud keychain and Secure Enclave support. |
| 🟡 | [SimpleKeychain](https://github.com/auth0/SimpleKeychain) | 728 | 2025-03 | 2026-11 | 14 | 5.9 | 5 | 0/0 | Keychain wrapper. |
| ⚪ | [KeychainAccess](https://github.com/kishikawakatsumi/KeychainAccess) | 8.3k | 2021-03 | 2023-11 | 8 | 5.0 | 5 | 0/2 | Keychain wrapper. |
| ⚪ | [keychain-swift](https://github.com/evgenyneu/keychain-swift) | 3.0k | — | 2024-04 | — | 5.7.1 | 5 | 0/0 | Keychain wrapper. |

### Preferences (UserDefaults)

Apple native: `UserDefaults` (iOS 2) · `@AppStorage` (iOS 14)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Defaults](https://github.com/sindresorhus/Defaults)** | 2.5k | 2026-06 | 2026-06 | 14 | 6.2 | 6/5 | 4/4 | Typed, observable UserDefaults keys with Codable support. |

## Architecture

### Dependency injection

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Swinject](https://github.com/Swinject/Swinject)** | 6.7k | 2025-09 | 2025-09 | 12 | 6.0.0 | 6 | 0/2 | Dependency injection container. |
| 🟢 | [Factory](https://github.com/hmlongco/Factory) | 2.9k | 2026-11 | 2026-11 | 15 | 6.1 | 6 | 86% | Container-based dependency injection. |
| 🟢 | [swift-dependencies](https://github.com/pointfreeco/swift-dependencies) | 2.2k | 2026-10 | 2026-10 | 15 | 6.4 | 6 | 88% | Dependency management modelled on SwiftUI's environment. |
| ⚪ | [needle](https://github.com/uber/needle) | 2.0k | 2024-09 | 2026-04 | — | 5.10 | 5 | 0/1 | Compile-time checked dependency injection with a hierarchical component tree. |

> **Note** · needle: README: needs both the NeedleFoundation framework and the needle code generator executable (installable with Homebrew). ([source](https://github.com/uber/needle#installation))

### App architecture frameworks

Apple native: `Observation (@Observable)` (iOS 17)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-composable-architecture](https://github.com/pointfreeco/swift-composable-architecture)** | 15.0k | 2026-08 | 2026-11 | 16 | 6.4 | 6 | 81% | Unidirectional architecture for state, actions, effects and testing. |
| 🟢 | [RIBs-iOS](https://github.com/uber/RIBs-iOS) | 194 | 2026-07 | 2026-07 | 15 | 5.5 | 5 | 0/3 | Router-Interactor-Builder architecture that composes an app from a tree of modules (RIBs). |

> **Note** · RIBs-iOS: Package.swift: the RIBs library depends on RxSwift and RxRelay. The Android implementation lives in uber/RIBs. ([source](https://github.com/uber/RIBs-iOS/blob/main/Package.swift))

### Navigation

Apple native: `NavigationStack` (iOS 16)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-navigation](https://github.com/pointfreeco/swift-navigation)** | 2.3k | 2026-08 | 2026-08 | 15 | 6.4 | 6 | 43% | State-driven navigation tools for SwiftUI, UIKit and AppKit. |
| 🟡 | [FlowStacks](https://github.com/johnpatrickmorgan/FlowStacks) | 971 | 2025-08 | 2025-10 | 14 | 5.10 | 5 | 0% | Coordinator-style SwiftUI navigation: push and present state hoisted into a routes array. |
| ⚪ | [XCoordinator](https://github.com/QuickBirdEng/XCoordinator) | 2.4k | 2023-02 | 2023-02 | 9 | 5.1 | 5 | 0/0 | Coordinator-pattern navigation for UIKit, with typed routes per coordinator. |

### URL routing

Apple native: `onOpenURL (SwiftUI)` (iOS 14) · `UISceneDelegate scene(_:openURLContexts:)` (iOS 13)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [URLNavigator](https://github.com/devxoul/URLNavigator) | 3.3k | 2023-07 | 2023-07 | 11 | 5.8 | 5 | 0/0 | Maps URL patterns to view controllers or handlers, for deep links and in-app navigation. |

## Observability

### Logging

Apple native: `os.Logger` (iOS 14)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[CocoaLumberjack](https://github.com/CocoaLumberjack/CocoaLumberjack)** | 13.3k | 2026-09 | 2026-11 | 15 | 6.4 | 6 | 100% | Logging framework with file logging and rotation. |
| 🟡 | [SwiftyBeaver](https://github.com/SwiftyBeaver/SwiftyBeaver) | 6.0k | — | 2024-11 | — | 5.0 | 5 | 2/2 | Logging with console, file and cloud destinations. |
| 🟢 | [swift-log](https://github.com/apple/swift-log) | 4.1k | 2026-11 | 2026-11 | — | 6.2 | 6 | 88% | Logging API package for Swift on all platforms. |

### Network & log inspector

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Pulse](https://github.com/kean/Pulse)** | 7.3k | 2026-06 | 2026-10 | 15 | 5.10 | 5 | 45% | In-app viewer for network requests and logs. |

### Crash reporting

Apple native: `MetricKit MXCrashDiagnostic` (iOS 14) · `Xcode Organizer crash reports`

*Not ranked: provider SDKs, pick by service.*

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [firebase-ios-sdk](https://github.com/firebase/firebase-ios-sdk) | 7.0k | 2026-10 | 2026-11 | 15 | 6.2 | 6/5 | 92% | Firebase SDK; includes Crashlytics. |
| 🟢 | [sentry-cocoa](https://github.com/getsentry/sentry-cocoa) | 1.1k | 2026-11 | 2026-11 | 15 | 6.0 | 5 | 92% | Sentry SDK: crash reporting, error tracking and performance tracing. |

### Product analytics

*Not ranked: provider SDKs, pick by service.*

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [firebase-ios-sdk](https://github.com/firebase/firebase-ios-sdk) | 7.0k | 2026-10 | 2026-11 | 15 | 6.2 | 6/5 | 92% | Firebase SDK; includes Google Analytics for Firebase. |
| 🟢 | [SwiftSDK](https://github.com/TelemetryDeck/SwiftSDK) | 229 | 2026-08 | 2026-08 | 12 | 5.9 | 5 strict | 81% | TelemetryDeck analytics SDK. |
| 🟢 | [posthog-ios](https://github.com/PostHog/posthog-ios) | 120 | 2026-11 | 2026-11 | 13 | 5.3 | 5 | 86% | PostHog SDK: product analytics, feature flags and session replay. |

## Accounts & payments

### In-app purchases & subscriptions

Apple native: `StoreKit 2` (iOS 15)

*Not ranked: provider SDKs, pick by service.*

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [purchases-ios](https://github.com/RevenueCat/purchases-ios) | 3.1k | 2026-11 | 2026-11 | 13 | 5.9 | 5 | 81% | RevenueCat SDK: purchases and subscriptions with server-side receipt validation and paywalls. |
| 🟢 | [AdaptySDK-iOS](https://github.com/adaptyteam/AdaptySDK-iOS) | 493 | 2026-11 | 2026-11 | 15 | 6.2 | 6 | 93% | Adapty SDK: purchases and subscriptions with paywall A/B testing. |

### Third-party sign-in

Apple native: `Sign in with Apple (AuthenticationServices)` (iOS 13) · `Passkeys (AuthenticationServices)` (iOS 16)

*Not ranked: provider SDKs, pick by service.*

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [GoogleSignIn-iOS](https://github.com/google/GoogleSignIn-iOS) | 759 | 2026-10 | 2026-11 | 15 | 6.0 | 6 | 62% | Sign in with Google. |
| 🟢 | [Auth0.swift](https://github.com/auth0/Auth0.swift) | 467 | 2026-11 | 2026-11 | 15 | 6.0 | 6 | 85% | Auth0 authentication SDK. |

### Backend as a service

*Not ranked: provider SDKs, pick by service.*

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [firebase-ios-sdk](https://github.com/firebase/firebase-ios-sdk) | 7.0k | 2026-10 | 2026-11 | 15 | 6.2 | 6/5 | 92% | Firebase SDK: Firestore, Auth, Storage, Functions and more. |
| 🟢 | [supabase-swift](https://github.com/supabase/supabase-swift) | 1.3k | 2026-10 | 2026-11 | 16 | 6.1 | 6/5 | 80% | Supabase SDK: Postgres database, auth, storage and realtime. |

## User interface

### UIKit Auto Layout DSL

Apple native: `NSLayoutAnchor` (iOS 9)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SnapKit](https://github.com/SnapKit/SnapKit)** | 20.3k | 2026-05 | 2026-07 | 14 | 6.0 | 5 | 62% | DSL for Auto Layout constraints in code. |

### SwiftUI component collections

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftUIX](https://github.com/SwiftUIX/SwiftUIX)** | 8.2k | 2026-09 | 2026-08 | 13 | 5.10 | 5 | 60% | Collection of additional SwiftUI views and modifiers. |

### SwiftUI introspection

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swiftui-introspect](https://github.com/siteline/swiftui-introspect)** | 6.6k | 2026-10 | 2026-10 | 13 | 6.2 | 6 | 1/2 | Access the UIKit/AppKit view underneath a SwiftUI view. |

### Popups & toasts

Apple native: `fullScreenCover` (iOS 14)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[PopupView](https://github.com/exyte/PopupView)** | 4.1k | — | 2026-11 | 17 | 6.0 | 6 | 100% | Toasts, popups and floating sheets for SwiftUI. |

### Animation playback

Apple native: `PhaseAnimator / KeyframeAnimator` (iOS 17)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[lottie-ios](https://github.com/airbnb/lottie-ios)** | 26.9k | 2026-06 | 2026-10 | 13 | 6.0 | 5 | 46% | Plays Lottie (After Effects) animations. |
| 🟢 | [rive-ios](https://github.com/rive-app/rive-ios) | 860 | 2026-10 | 2026-11 | 14 | 5.10 | ObjC/C | 80% | Plays Rive animations with state machines. |

### Charts

Apple native: `Swift Charts` (iOS 16)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [Charts](https://github.com/ChartsOrg/Charts) | 28.0k | 2024-02 | 2026-03 | 12 | 5.3 | 5 | 0/3 | Chart library for UIKit (DGCharts). |

### Markdown rendering

Apple native: `AttributedString(markdown:)` (iOS 15)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[textual](https://github.com/gonzalezreal/textual)** | 919 | 2026-06 | 2026-06 | 18 | 6.0 | 6 | 32% | Renders Markdown and rich text in SwiftUI. |
| ⚪ | [swift-markdown-ui](https://github.com/gonzalezreal/swift-markdown-ui) | 3.9k | 2024-10 | 2025-12 | 15 | 5.6 | 5 | 0% | Renders Markdown in SwiftUI. |

> **Note** · swift-markdown-ui: README: "MarkdownUI is in maintenance mode. New development is happening in Textual." ([source](https://github.com/gonzalezreal/swift-markdown-ui#readme))

### HTML parsing

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftSoup](https://github.com/scinfu/SwiftSoup)** | 5.1k | 2026-10 | 2026-10 | 13 | 6.0 | 6 | 93% | Parses and cleans HTML. |

### Markdown parsing

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-markdown](https://github.com/swiftlang/swift-markdown)** | 3.5k | 2026-09 | 2026-11 | — | 6.2 | 5 | 67% | Parses Markdown into a syntax tree. |

## Swift language & data

### Reactive frameworks

Apple native: `Combine` (iOS 13)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[RxSwift](https://github.com/ReactiveX/RxSwift)** | 24.6k | 2026-03 | 2026-09 | 9 | 5.5 | 5 | 43% | Reactive programming with observables. |

### AsyncSequence operators

Apple native: `AsyncSequence / AsyncStream (back-deployed to iOS 13 with Xcode 13.2+)` (iOS 13)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-async-algorithms](https://github.com/apple/swift-async-algorithms)** | 3.7k | 2026-09 | 2026-10 | — | 6.2 | 6 | 43% | Operators for AsyncSequence: debounce, throttle, merge, zip and more. |

### Data structures

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-collections](https://github.com/apple/swift-collections)** | 4.5k | 2026-10 | 2026-11 | — | 6.4 | 6/5 | 90% | Deque, OrderedSet, OrderedDictionary, Heap and more. |

### Sequence algorithms

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-algorithms](https://github.com/apple/swift-algorithms)** | 6.3k | 2025-02 | 2026-07 | — | 5.7 | 5 | 57% | Sequence and collection algorithms (chunks, windows, uniqued, ...). |

### JSON

Apple native: `Codable + JSONDecoder (Swift 4)`

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [SwiftyJSON](https://github.com/SwiftyJSON/SwiftyJSON) | 22.9k | 2024-03 | 2026-08 | — | 5.3 | 5 | 1/4 | JSON access with subscripts. |

### Cryptography

Apple native: `CryptoKit` (iOS 13)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[CryptoSwift](https://github.com/krzyzanowskim/CryptoSwift)** | 10.6k | 2026-04 | 2026-08 | 11 | 5.6 | 5 | off | Crypto algorithms implemented in Swift. |
| 🟢 | [swift-crypto](https://github.com/apple/swift-crypto) | 1.7k | 2026-11 | 2026-11 | — | 6.2 | 6 | 100% | Open-source implementation of the CryptoKit API, including Linux. |

### Protocol Buffers

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-protobuf](https://github.com/apple/swift-protobuf)** | 5.0k | 2026-10 | 2026-11 | — | 6.2 | 6 | 100% | Protocol Buffers runtime and code generator for Swift. |

## Testing

### BDD test frameworks

Apple native: `Swift Testing` (Xcode 16) · `XCTest`

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [Quick](https://github.com/Quick/Quick) | 9.8k | 2024-07 | 2026-03 | 13 | 5.7 | 5 | 1/2 | BDD-style test framework. |

### Test matchers

Apple native: `Swift Testing #expect / #require` (Xcode 16)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Nimble](https://github.com/Quick/Nimble)** | 4.8k | 2025-11 | 2026-05 | 13 | 6.0 | 5 | 1/1 | Matcher library for tests. |

### Snapshot testing

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-snapshot-testing](https://github.com/pointfreeco/swift-snapshot-testing)** | 4.4k | 2026-10 | 2026-10 | 13 | 6.0 | 5 | 20% | Snapshot testing for views and values. |

### Value dumps & diffs

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-custom-dump](https://github.com/pointfreeco/swift-custom-dump)** | 894 | 2026-08 | 2026-08 | 15 | 6.4 | 6 | 3/3 | Dumps and diffs Swift values, for test failure messages. |

### Concurrency testing

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-concurrency-extras](https://github.com/pointfreeco/swift-concurrency-extras)** | 492 | 2026-10 | 2026-10 | 13 | 6.0 | 6 | 0/0 | Utilities for testing Swift concurrency code. |

## Tooling

### Linting

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftLint](https://github.com/realm/SwiftLint)** | 19.8k | 2026-08 | 2026-11 | — | 5.9 | 5 | 71% | Enforces Swift style and conventions. |

### Formatting

Apple native: `xcrun swift-format (bundled with Xcode)` (Xcode 16)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftFormat](https://github.com/nicklockwood/SwiftFormat)** | 9.0k | 2026-11 | 2026-11 | — | 5.7 | 5 | 86% | Swift code formatter. |
| 🟢 | [swift-format](https://github.com/swiftlang/swift-format) | 3.0k | 2026-09 | 2026-11 | 16 | 6.0 | 5 | 65% | Swift code formatter from the Swift project. |

### Project generation

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[XcodeGen](https://github.com/yonaskolb/XcodeGen)** | 8.9k | 2026-07 | 2026-10 | — | 5.9 | 5 | 48% | Generates an Xcode project from project.yml. |
| 🟢 | [tuist](https://github.com/tuist/tuist) | 5.9k | 2026-11 | 2026-11 | — | 6.1 | 6/5 | 65% | Generates Xcode projects from Project.swift; also caching and build insights. |

### Build log formatting

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[xcbeautify](https://github.com/cpisciotta/xcbeautify)** | 1.6k | 2026-04 | 2026-08 | — | 6.1 | 6 | 11% | Formatter for xcodebuild output. |

### View debugging

Apple native: `Xcode View Debugger (Debug View Hierarchy)`

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[LookInside](https://github.com/LookInsideApp/LookInside)** | 397 | 2026-10 | 2026-11 | 15 | 5.10 | 5 | 60% | Mac app to inspect views, layers, frames and properties of a running iOS or macOS app. |
| ⚪ | [LookinServer](https://github.com/QMUI/LookinServer) | 2.9k | 2024-04 | 2024-06 | 9 | 5.3 | 5 | 0/3 | iOS framework for the Lookin macOS app: inspect and modify views in a running app. |
| 🟢 | [LookInside-Release](https://github.com/LookInsideApp/LookInside-Release) | 9 | 2026-10 | 2026-10 | 15 | 5.9 | ObjC/C | 0/0 | LookInside server package for iOS apps (Swift Package Manager or CocoaPods). |

> **Note** · LookInside: README: LookInside continues the work of Lookin; version 2.3.11 and later include a local MCP server for AI agents. The iOS side is integrated with the LookInside-Release package. ([source](https://github.com/LookInsideApp/LookInside#readme))

### Resource code generation

Apple native: `Generated asset symbols (ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS)` (Xcode 15) · `String Catalog symbols (STRING_CATALOG_GENERATE_SYMBOLS)` (Xcode 26) [source](https://wwdcnotes.com/documentation/wwdc25-225-codealong-explore-localization-with-xcode/)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [R.swift](https://github.com/mac-cain13/R.swift) | 9.5k | 2024-11 | 2025-03 | 11 | 5.6 | 5 | 0/1 | Generates typed resource accessors. |
| ⚪ | [SwiftGen](https://github.com/SwiftGen/SwiftGen) | 9.5k | 2024-03 | 2022-02 | — | 5.6 | 5 | 0/3 | Generates Swift code for strings, images, fonts and other resources. |

### Release & App Store Connect

Apple native: `xcodebuild archive / -exportArchive` · `Xcode Cloud`

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[fastlane](https://github.com/fastlane/fastlane)** | 42.4k | 2026-10 | 2026-11 | — | 4.0 | 5 | 90% | Automates signing, screenshots, builds and releases. |
| 🟢 | [App-Store-Connect-CLI](https://github.com/rorkai/App-Store-Connect-CLI) | 8.3k | 2026-11 | 2026-11 | — | — | — | 100% | CLI for App Store Connect: builds, TestFlight, metadata, submissions. |

## AI agent tooling

### Build & run MCP servers

Apple native: `xcrun mcpbridge (Xcode MCP server)` (Xcode 26.3) [source](https://infoq.com/news/2026/02/xcode-26-3-agentic-coding)

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[MobileBuildMCP](https://github.com/getsentry/MobileBuildMCP)** | 6.6k | 2026-09 | 2026-10 | — | — | — | 53% | MCP server and CLI to build, run, test, debug and scaffold iOS/macOS projects (formerly XcodeBuildMCP). |

### Simulator & device UI automation

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[mobile-mcp](https://github.com/mobile-next/mobile-mcp)** | 10.4k | 2026-11 | 2026-11 | — | — | — | 79% | MCP server to drive iOS and Android simulators and devices. |
| 🟢 | [agent-device](https://github.com/callstack/agent-device) | 5.3k | 2026-11 | 2026-11 | — | — | — | 100% | CLI, MCP server and Node.js API to control mobile, web, TV and desktop apps on devices and simulators. |
| 🟢 | [AXe](https://github.com/cameroncooke/AXe) | 2.3k | 2026-07 | 2026-07 | — | 5.10 | 5 | 50% | CLI for Simulator UI automation through accessibility APIs. |
| 🟢 | [ios-simulator-mcp](https://github.com/joshuayoes/ios-simulator-mcp) | 2.2k | 2026-10 | 2026-10 | — | — | — | 75% | MCP server to tap, type and inspect UI in the iOS Simulator. |
| 🟢 | [sim-use](https://github.com/lycorp-jp/sim-use) | 1.5k | 2026-10 | 2026-10 | — | 5.10 | 5 | 77% | CLI for AI agents to read and act on iOS Simulator, Android emulator/device and physical iPhone screens. |

### Apple docs for agents

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[apple-docs-mcp](https://github.com/kimsungwhee/apple-docs-mcp)** | 1.4k | 2025-09 | 2026-03 | — | — | — | 0% | MCP server to search Apple developer documentation. |
| 🟢 | [sosumi.ai](https://github.com/NSHipster/sosumi.ai) | 483 | 2026-11 | 2026-11 | — | — | — | 96% | Serves Apple developer docs as Markdown for AI tools. |

### SwiftUI skills

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill)** | 6.5k | 2026-10 | 2026-10 | — | — | — | 50% | SwiftUI agent skill. |
| 🟢 | [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) | 3.9k | 2026-11 | 2026-11 | — | — | — | 87% | SwiftUI agent skill. |

### Swift Concurrency skills

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Swift-Concurrency-Agent-Skill](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill)** | 1.7k | 2026-11 | 2026-11 | — | — | — | 50% | Swift Concurrency agent skill. |

### Simulator skills

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[ios-simulator-skill](https://github.com/conorluddy/ios-simulator-skill)** | 1.3k | 2026-11 | 2026-11 | — | — | — | 75% | Agent skill for building, running and inspecting apps in the Simulator. |

### Release skills

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[app-store-connect-cli-skills](https://github.com/rorkai/app-store-connect-cli-skills)** | 1.1k | — | 2026-11 | — | — | — | 100% | Agent skills for releasing with the asc CLI. |

### Skill indexes

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Swift-Agent-Skills](https://github.com/twostraws/Swift-Agent-Skills)** | 3.0k | — | 2026-09 | — | — | — | 0/2 | Index of Swift agent skills, grouped by framework. |

### AGENTS.md templates

| | Library | Stars | Release | Last commit | Min iOS | Swift tools | Swift mode | Issue replies | What it does |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftAgents](https://github.com/twostraws/SwiftAgents)** | 1.5k | — | 2026-03 | — | — | — | 1/2 | AGENTS.md file for Swift and SwiftUI projects. |

## Contributing

Add an entry to [`data/catalog.yaml`](data/catalog.yaml): the `repo` and a `does` line that says what it does. No opinions; a `note` needs a source link. Then run `python3 scripts/refresh.py && python3 scripts/build.py`.

---

If this list is useful to you, a ⭐ helps other iOS developers find it.
[⭐ jeffy-w/awesome-ios-for-agents](https://github.com/jeffy-w/awesome-ios-for-agents)
