# Awesome iOS for Agents

[English](README.md)

**用数据挑选 iOS 开源库，给人看，也给 AI 编程 agent 用。**

每个库都列出同样的数据：star 数、最近一次 Release、最近一次提交、最低 iOS 版本、Swift tools 版本、Swift 语言模式和 issue 回复率。每个分类的首选按固定规则算出。数据更新于 **2026-11-09**，之后由 GitHub Actions 每周刷新。

## 给 agent 用

安装 `ios-starter` skill，然后让 agent 新建一个 iOS 应用。它会先问清楚应用需要什么，按下面的规则从这份目录里选库，用一套验证过的方案创建项目，再编译并在模拟器里启动。

```bash
npx skills add jeffy-w/awesome-ios-for-agents@ios-starter -g -y
```

agent 也可以直接读取数据：[`catalog.json`](catalog.json) · [`llms.txt`](llms.txt)

## 首选怎么算出来

- **状态按发版计算**：取最近一次 GitHub Release 的日期。只有从未发布过 GitHub Release 的仓库，才改用默认分支最近一次提交的日期。表格里两个日期都会显示。
- **状态**：🟢 活跃（< 1 年）· 🟡 放缓（1–2 年）· ⚪ 不活跃（≥ 2 年）· 🗄 已归档。
- **🏆 首选** = 分类中 star 最多的 🟢/🟡 条目。依附于其他库的扩展不参与排名。服务商 SDK 的分类（后端、付费、数据分析、崩溃监控、第三方登录）*不排名*，按服务本身选择。
- **最低 iOS** 和 **Swift tools** 读取自最新 Release 标签下的 `Package.swift`（Release 标签不是版本号时，用最高的版本号标签；都没有时用默认分支）。
- **Swift 模式** 是库自己的 target 用哪种语言模式编译，用 `swift package dump-package`（Swift 6.4.2）读取：`6` · `5` · `6/5`（各有一部分 target）· `strict` = Swift 5 模式但开了完整并发检查。只统计含 Swift 源码的 target，纯 ObjC/C 库显示 `ObjC/C`；`—` = 不是 Swift 包或读取失败。它不会改变你的 App 的语言模式；`6` 表示库的 API 做过数据竞争检查，你的 Swift 6 代码用它时较少需要 `@preconcurrency` 之类的绕行。
- **Issue 回复** = 2025-10-10 至 2026-10-10 期间项目外部人员提的 issue 中，被维护者回复或关闭的比例（每个仓库取最近 100 个；bot 不算）。不足 5 个时显示原始数量，如 `0/2`；`off` = 仓库关闭了 issue。仅供参考，不参与首选计算。
- Swift 模式或 issue 回复后面带 `*` = 这次没读到，沿用上次读到的值；日期见 catalog.json 的 `swift_mode_checked` 和 `issues_checked`。
- **Apple 原生** 列出能完成同样工作的系统 API 及其最低系统版本。
- 分类和描述是人工编写的，只说明项目做什么；备注引用来源原文。状态和排名由 [`scripts/build.py`](scripts/build.py) 计算。

## 新建项目

agent 从零创建 iOS 应用的四种方案。每种都于 2026-11-03 在 Xcode 27.2 上完整跑过。

| 方案 | 工程定义方式 | 添加依赖包 | 已验证 |
|---|---|---|---|
| [XcodeGen](skills/ios-starter/recipes/xcodegen.md) | `project.yml` | YAML 里的 `packages:` | 创建、加依赖、编译、启动 |
| [Tuist](skills/ios-starter/recipes/tuist.md) | `Project.swift` | `Tuist/Package.swift` + `tuist install` | 创建、加依赖、编译、启动 |
| [MobileBuildMCP](skills/ios-starter/recipes/mobilebuildmcp.md) | Xcode 工程 + 本地 Swift 包 | 本地 `Package.swift` | 创建、加依赖、编译、启动 |
| [Xcode MCP](skills/ios-starter/recipes/xcode-mcp.md) | Apple 官方 Xcode 模板 | 在 Xcode 里添加（27.2 的 MCP 没有对应工具） | 创建、编译、启动 |

## 目录

- **基础能力**: [HTTP 客户端](#http-客户端) · [OpenAPI 客户端生成](#openapi-客户端生成) · [WebSocket](#websocket) · [网络状态监测](#网络状态监测) · [图片加载与缓存](#图片加载与缓存) · [本地数据库](#本地数据库) · [钥匙串](#钥匙串) · [偏好设置（UserDefaults）](#偏好设置userdefaults)
- **架构**: [依赖注入](#依赖注入) · [应用架构框架](#应用架构框架) · [导航](#导航) · [URL 路由](#url-路由)
- **日志与监控**: [日志](#日志) · [网络与日志查看器](#网络与日志查看器) · [崩溃监控](#崩溃监控) · [产品数据分析](#产品数据分析)
- **账号与付费**: [应用内购买与订阅](#应用内购买与订阅) · [第三方登录](#第三方登录) · [后端即服务](#后端即服务)
- **界面**: [UIKit 自动布局 DSL](#uikit-自动布局-dsl) · [SwiftUI 组件合集](#swiftui-组件合集) · [SwiftUI 底层视图访问](#swiftui-底层视图访问) · [弹窗与 Toast](#弹窗与-toast) · [动画播放](#动画播放) · [图表](#图表) · [Markdown 渲染](#markdown-渲染) · [HTML 解析](#html-解析) · [Markdown 解析](#markdown-解析)
- **Swift 语言与数据**: [响应式框架](#响应式框架) · [AsyncSequence 操作符](#asyncsequence-操作符) · [数据结构](#数据结构) · [序列算法](#序列算法) · [JSON](#json) · [加密](#加密) · [Protocol Buffers](#protocol-buffers)
- **测试**: [BDD 测试框架](#bdd-测试框架) · [测试断言库](#测试断言库) · [快照测试](#快照测试) · [数据输出与差异对比](#数据输出与差异对比) · [并发代码测试](#并发代码测试)
- **工具链**: [代码检查](#代码检查) · [代码格式化](#代码格式化) · [工程生成](#工程生成) · [构建日志格式化](#构建日志格式化) · [界面调试](#界面调试) · [资源代码生成](#资源代码生成) · [发布与 App Store Connect](#发布与-app-store-connect)
- **AI agent 工具**: [编译运行 MCP](#编译运行-mcp) · [模拟器与真机界面自动化](#模拟器与真机界面自动化) · [给 agent 读的 Apple 文档](#给-agent-读的-apple-文档) · [SwiftUI skills](#swiftui-skills) · [Swift Concurrency skills](#swift-concurrency-skills) · [模拟器 skills](#模拟器-skills) · [发布 skills](#发布-skills) · [Skill 索引](#skill-索引) · [AGENTS.md 模板](#agentsmd-模板)

## 基础能力

### HTTP 客户端

Apple 原生: `URLSession async/await` (iOS 15)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Alamofire](https://github.com/Alamofire/Alamofire)** | 42.4k | 2026-09 | 2026-10 | 15 | 6.4 | 5 | 88% | HTTP 客户端，支持请求拦截、重试、multipart 上传和进度回调。 |
| ⚪ | [Moya](https://github.com/Moya/Moya) | 15.4k | 2022-08 | 2026-07 | 10 | 5.3 | 5 | 0/2 | 构建在 Alamofire 之上的网络抽象层。 |
| ⚪ | [Get](https://github.com/kean/Get) | 988 | 2024-10 | 2024-10 | 13 | 5.5 | 5 | 0/0 | 基于 URLSession 的强类型 API 客户端。 |

### OpenAPI 客户端生成

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-openapi-generator](https://github.com/apple/swift-openapi-generator)** | 2.0k | 2026-11 | 2026-11 | 13 | 6.2 | 6 | 89% | 构建时根据 OpenAPI 文档生成 Swift 客户端和服务端代码。 |

> **备注** · swift-openapi-generator: README：这是 Swift 包插件和命令行工具。生成的代码依赖 apple/swift-openapi-runtime，以及一个 ClientTransport 实现，例如 apple/swift-openapi-urlsession。 ([来源](https://github.com/apple/swift-openapi-generator#package-ecosystem))

### WebSocket

Apple 原生: `URLSessionWebSocketTask` (iOS 13)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [Starscream](https://github.com/daltoniam/Starscream) | 8.6k | 2024-03 | 2024-03 | — | 5.3 | 5 | 0/2 | WebSocket 客户端。 |

### 网络状态监测

Apple 原生: `NWPathMonitor (Network framework)` (iOS 12)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [Reachability.swift](https://github.com/ashleymills/Reachability.swift) | 8.0k | 2024-10 | 2024-10 | — | 5.3 | 5 | 0/1 | 网络可达性变化通知。 |

### 图片加载与缓存

Apple 原生: `AsyncImage` (iOS 15)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SDWebImage](https://github.com/SDWebImage/SDWebImage)** | 25.6k | 2026-02 | 2026-04 | 9 | 5.3 | ObjC/C | 38% | 图片下载与缓存，带动图 WebP、AVIF、HEIC 解码器。 |
| 🟢 | [Kingfisher](https://github.com/onevcat/Kingfisher) | 24.4k | 2026-11 | 2026-11 | 15 | 6.2 | 5 | 87% | 下载并缓存网络图片，支持 UIKit 和 SwiftUI。 |
| 🟢 | [Nuke](https://github.com/kean/Nuke) | 8.7k | 2026-11 | 2026-11 | 15 | 6.0 | 6 | 100% | 图片加载管线，支持缓存、预加载和渐进式解码。 |
| 🟡 | [SDWebImageSwiftUI](https://github.com/SDWebImage/SDWebImageSwiftUI) | 2.6k | 2025-11 | 2026-02 | 14 | 5.3 | 5 | 1/3 | SDWebImage 的 SwiftUI 视图组件。 |

### 本地数据库

Apple 原生: `SwiftData` (iOS 17) · `Core Data` (iOS 3)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[realm-swift](https://github.com/realm/realm-swift)** | 16.6k | 2026-09 | 2026-09 | 12 | 6.2.1 | 6 | 29% | 面向移动端的对象数据库。 |
| 🟢 | [SQLite.swift](https://github.com/stephencelis/SQLite.swift) | 10.2k | 2026-10 | 2026-10 | 15 | 6.1 | 6 | 89% | SQLite3 的 Swift 封装，用类型化表达式写查询。 |
| 🟢 | [GRDB.swift](https://github.com/groue/GRDB.swift) | 8.7k | 2026-11 | 2026-11 | 13 | 6.1 | 6 | 100% | SQLite 工具集，提供迁移、记录类型和数据库变化监听。 |
| 🟢 | [sqlite-data](https://github.com/pointfreeco/sqlite-data) | 2.0k | 2026-10 | 2026-11 | 16 | 6.4 | 6 | 77% | 在 SQLite（GRDB）上提供类似 SwiftData 的模型和查询，支持 CloudKit 同步。 |

> **备注** · realm-swift: MongoDB：Atlas Device SDKs 已于 2025-09-30 终止并下线；设备端数据库继续作为开源项目存在。 ([来源](https://www.mongodb.com/docs/device-sdks-deprecation/))

### 钥匙串

Apple 原生: `Keychain Services (Security framework)` (iOS 2)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Valet](https://github.com/square/Valet)** | 4.2k | 2026-09 | 2026-07 | 12 | 6.0 | 6 | 3/4 | 钥匙串封装，支持 iCloud 钥匙串和 Secure Enclave。 |
| 🟡 | [SimpleKeychain](https://github.com/auth0/SimpleKeychain) | 728 | 2025-03 | 2026-11 | 14 | 5.9 | 5 | 0/0 | 钥匙串封装。 |
| ⚪ | [KeychainAccess](https://github.com/kishikawakatsumi/KeychainAccess) | 8.3k | 2021-03 | 2023-11 | 8 | 5.0 | 5 | 0/2 | 钥匙串封装。 |
| ⚪ | [keychain-swift](https://github.com/evgenyneu/keychain-swift) | 3.0k | — | 2024-04 | — | 5.7.1 | 5 | 0/0 | 钥匙串封装。 |

### 偏好设置（UserDefaults）

Apple 原生: `UserDefaults` (iOS 2) · `@AppStorage` (iOS 14)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Defaults](https://github.com/sindresorhus/Defaults)** | 2.5k | 2026-06 | 2026-06 | 14 | 6.2 | 6/5 | 4/4 | 强类型、可监听的 UserDefaults，支持 Codable。 |

## 架构

### 依赖注入

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Swinject](https://github.com/Swinject/Swinject)** | 6.7k | 2025-09 | 2025-09 | 12 | 6.0.0 | 6 | 0/2 | 依赖注入容器。 |
| 🟢 | [Factory](https://github.com/hmlongco/Factory) | 2.9k | 2026-11 | 2026-11 | 15 | 6.1 | 6 | 86% | 基于容器的依赖注入。 |
| 🟢 | [swift-dependencies](https://github.com/pointfreeco/swift-dependencies) | 2.2k | 2026-10 | 2026-10 | 15 | 6.4 | 6 | 88% | 参照 SwiftUI Environment 设计的依赖管理。 |
| ⚪ | [needle](https://github.com/uber/needle) | 2.0k | 2024-09 | 2026-04 | — | 5.10 | 5 | 0/1 | 编译期校验的依赖注入，按组件树分层组织依赖。 |

> **备注** · needle: README：需要同时集成 NeedleFoundation 框架和 needle 代码生成器可执行文件（可用 Homebrew 安装）。 ([来源](https://github.com/uber/needle#installation))

### 应用架构框架

Apple 原生: `Observation (@Observable)` (iOS 17)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-composable-architecture](https://github.com/pointfreeco/swift-composable-architecture)** | 15.0k | 2026-08 | 2026-11 | 16 | 6.4 | 6 | 81% | 单向数据流架构，管理状态、动作、副作用和测试。 |
| 🟢 | [RIBs-iOS](https://github.com/uber/RIBs-iOS) | 194 | 2026-07 | 2026-07 | 15 | 5.5 | 5 | 0/3 | Router-Interactor-Builder 架构，把应用组织成一棵模块（RIB）树。 |

> **备注** · RIBs-iOS: Package.swift：RIBs 库依赖 RxSwift 和 RxRelay。Android 版本在 uber/RIBs 仓库。 ([来源](https://github.com/uber/RIBs-iOS/blob/main/Package.swift))

### 导航

Apple 原生: `NavigationStack` (iOS 16)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-navigation](https://github.com/pointfreeco/swift-navigation)** | 2.3k | 2026-08 | 2026-08 | 15 | 6.4 | 6 | 43% | 由状态驱动的导航工具，支持 SwiftUI、UIKit、AppKit。 |
| 🟡 | [FlowStacks](https://github.com/johnpatrickmorgan/FlowStacks) | 971 | 2025-08 | 2025-10 | 14 | 5.10 | 5 | 0% | Coordinator 风格的 SwiftUI 导航，把 push 和 present 状态提升到一个路由数组中。 |
| ⚪ | [XCoordinator](https://github.com/QuickBirdEng/XCoordinator) | 2.4k | 2023-02 | 2023-02 | 9 | 5.1 | 5 | 0/0 | 基于 Coordinator 模式的 UIKit 导航，每个 Coordinator 使用强类型路由。 |

### URL 路由

Apple 原生: `onOpenURL (SwiftUI)` (iOS 14) · `UISceneDelegate scene(_:openURLContexts:)` (iOS 13)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [URLNavigator](https://github.com/devxoul/URLNavigator) | 3.3k | 2023-07 | 2023-07 | 11 | 5.8 | 5 | 0/0 | 把 URL 模式映射到视图控制器或处理闭包，用于 deeplink 和应用内跳转。 |

## 日志与监控

### 日志

Apple 原生: `os.Logger` (iOS 14)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[CocoaLumberjack](https://github.com/CocoaLumberjack/CocoaLumberjack)** | 13.3k | 2026-09 | 2026-11 | 15 | 6.4 | 6 | 100% | 日志框架，支持写文件和日志轮转。 |
| 🟡 | [SwiftyBeaver](https://github.com/SwiftyBeaver/SwiftyBeaver) | 6.0k | — | 2024-11 | — | 5.0 | 5 | 2/2 | 日志库，可输出到控制台、文件和云端。 |
| 🟢 | [swift-log](https://github.com/apple/swift-log) | 4.1k | 2026-11 | 2026-11 | — | 6.2 | 6 | 88% | 跨平台的 Swift 日志接口包。 |

### 网络与日志查看器

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Pulse](https://github.com/kean/Pulse)** | 7.3k | 2026-06 | 2026-10 | 15 | 5.10 | 5 | 45% | 在 App 内查看网络请求和日志。 |

### 崩溃监控

Apple 原生: `MetricKit MXCrashDiagnostic` (iOS 14) · `Xcode Organizer crash reports`

*不排名：服务商 SDK，按服务本身选择。*

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [firebase-ios-sdk](https://github.com/firebase/firebase-ios-sdk) | 7.0k | 2026-10 | 2026-11 | 15 | 6.2 | 6/5 | 92% | Firebase SDK，包含 Crashlytics。 |
| 🟢 | [sentry-cocoa](https://github.com/getsentry/sentry-cocoa) | 1.1k | 2026-11 | 2026-11 | 15 | 6.0 | 5 | 92% | Sentry SDK：崩溃上报、错误追踪和性能追踪。 |

### 产品数据分析

*不排名：服务商 SDK，按服务本身选择。*

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [firebase-ios-sdk](https://github.com/firebase/firebase-ios-sdk) | 7.0k | 2026-10 | 2026-11 | 15 | 6.2 | 6/5 | 92% | Firebase SDK，包含 Google Analytics for Firebase。 |
| 🟢 | [SwiftSDK](https://github.com/TelemetryDeck/SwiftSDK) | 229 | 2026-08 | 2026-08 | 12 | 5.9 | 5 strict | 81% | TelemetryDeck 数据分析 SDK。 |
| 🟢 | [posthog-ios](https://github.com/PostHog/posthog-ios) | 120 | 2026-11 | 2026-11 | 13 | 5.3 | 5 | 86% | PostHog SDK：产品分析、功能开关和会话回放。 |

## 账号与付费

### 应用内购买与订阅

Apple 原生: `StoreKit 2` (iOS 15)

*不排名：服务商 SDK，按服务本身选择。*

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [purchases-ios](https://github.com/RevenueCat/purchases-ios) | 3.1k | 2026-11 | 2026-11 | 13 | 5.9 | 5 | 81% | RevenueCat SDK：购买与订阅，提供服务端收据校验和付费墙。 |
| 🟢 | [AdaptySDK-iOS](https://github.com/adaptyteam/AdaptySDK-iOS) | 493 | 2026-11 | 2026-11 | 15 | 6.2 | 6 | 93% | Adapty SDK：购买与订阅，提供付费墙 A/B 测试。 |

### 第三方登录

Apple 原生: `Sign in with Apple (AuthenticationServices)` (iOS 13) · `Passkeys (AuthenticationServices)` (iOS 16)

*不排名：服务商 SDK，按服务本身选择。*

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [GoogleSignIn-iOS](https://github.com/google/GoogleSignIn-iOS) | 759 | 2026-10 | 2026-11 | 15 | 6.0 | 6 | 62% | Google 账号登录。 |
| 🟢 | [Auth0.swift](https://github.com/auth0/Auth0.swift) | 467 | 2026-11 | 2026-11 | 15 | 6.0 | 6 | 85% | Auth0 身份认证 SDK。 |

### 后端即服务

*不排名：服务商 SDK，按服务本身选择。*

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🟢 | [firebase-ios-sdk](https://github.com/firebase/firebase-ios-sdk) | 7.0k | 2026-10 | 2026-11 | 15 | 6.2 | 6/5 | 92% | Firebase SDK：Firestore、Auth、Storage、Functions 等。 |
| 🟢 | [supabase-swift](https://github.com/supabase/supabase-swift) | 1.3k | 2026-10 | 2026-11 | 16 | 6.1 | 6/5 | 80% | Supabase SDK：Postgres 数据库、登录、存储和实时订阅。 |

## 界面

### UIKit 自动布局 DSL

Apple 原生: `NSLayoutAnchor` (iOS 9)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SnapKit](https://github.com/SnapKit/SnapKit)** | 20.3k | 2026-05 | 2026-07 | 14 | 6.0 | 5 | 62% | 用代码写 Auto Layout 约束的 DSL。 |

### SwiftUI 组件合集

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftUIX](https://github.com/SwiftUIX/SwiftUIX)** | 8.2k | 2026-09 | 2026-08 | 13 | 5.10 | 5 | 60% | 额外的 SwiftUI 视图和修饰符合集。 |

### SwiftUI 底层视图访问

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swiftui-introspect](https://github.com/siteline/swiftui-introspect)** | 6.6k | 2026-10 | 2026-10 | 13 | 6.2 | 6 | 1/2 | 获取 SwiftUI 视图底层对应的 UIKit/AppKit 视图。 |

### 弹窗与 Toast

Apple 原生: `fullScreenCover` (iOS 14)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[PopupView](https://github.com/exyte/PopupView)** | 4.1k | — | 2026-11 | 17 | 6.0 | 6 | 100% | SwiftUI 的 Toast、弹窗和浮动面板。 |

### 动画播放

Apple 原生: `PhaseAnimator / KeyframeAnimator` (iOS 17)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[lottie-ios](https://github.com/airbnb/lottie-ios)** | 26.9k | 2026-06 | 2026-10 | 13 | 6.0 | 5 | 46% | 播放 Lottie（After Effects 导出）动画。 |
| 🟢 | [rive-ios](https://github.com/rive-app/rive-ios) | 860 | 2026-10 | 2026-11 | 14 | 5.10 | ObjC/C | 80% | 播放带状态机的 Rive 动画。 |

### 图表

Apple 原生: `Swift Charts` (iOS 16)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [Charts](https://github.com/ChartsOrg/Charts) | 28.0k | 2024-02 | 2026-03 | 12 | 5.3 | 5 | 0/3 | UIKit 图表库（DGCharts）。 |

### Markdown 渲染

Apple 原生: `AttributedString(markdown:)` (iOS 15)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[textual](https://github.com/gonzalezreal/textual)** | 919 | 2026-06 | 2026-06 | 18 | 6.0 | 6 | 32% | 在 SwiftUI 中渲染 Markdown 和富文本。 |
| ⚪ | [swift-markdown-ui](https://github.com/gonzalezreal/swift-markdown-ui) | 3.9k | 2024-10 | 2025-12 | 15 | 5.6 | 5 | 0% | 在 SwiftUI 中渲染 Markdown。 |

> **备注** · swift-markdown-ui: README 原文：MarkdownUI 已进入维护模式，新开发在 Textual 中进行。 ([来源](https://github.com/gonzalezreal/swift-markdown-ui#readme))

### HTML 解析

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftSoup](https://github.com/scinfu/SwiftSoup)** | 5.1k | 2026-10 | 2026-10 | 13 | 6.0 | 6 | 93% | 解析和清洗 HTML。 |

### Markdown 解析

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-markdown](https://github.com/swiftlang/swift-markdown)** | 3.5k | 2026-09 | 2026-11 | — | 6.2 | 5 | 67% | 把 Markdown 解析成语法树。 |

## Swift 语言与数据

### 响应式框架

Apple 原生: `Combine` (iOS 13)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[RxSwift](https://github.com/ReactiveX/RxSwift)** | 24.6k | 2026-03 | 2026-09 | 9 | 5.5 | 5 | 43% | 基于 Observable 的响应式编程。 |

### AsyncSequence 操作符

Apple 原生: `AsyncSequence / AsyncStream (back-deployed to iOS 13 with Xcode 13.2+)` (iOS 13)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-async-algorithms](https://github.com/apple/swift-async-algorithms)** | 3.7k | 2026-09 | 2026-10 | — | 6.2 | 6 | 43% | AsyncSequence 操作符：debounce、throttle、merge、zip 等。 |

### 数据结构

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-collections](https://github.com/apple/swift-collections)** | 4.5k | 2026-10 | 2026-11 | — | 6.4 | 6/5 | 90% | Deque、OrderedSet、OrderedDictionary、Heap 等数据结构。 |

### 序列算法

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-algorithms](https://github.com/apple/swift-algorithms)** | 6.3k | 2025-02 | 2026-07 | — | 5.7 | 5 | 57% | 序列与集合算法（chunks、windows、uniqued 等）。 |

### JSON

Apple 原生: `Codable + JSONDecoder (Swift 4)`

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [SwiftyJSON](https://github.com/SwiftyJSON/SwiftyJSON) | 22.9k | 2024-03 | 2026-08 | — | 5.3 | 5 | 1/4 | 用下标访问 JSON。 |

### 加密

Apple 原生: `CryptoKit` (iOS 13)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[CryptoSwift](https://github.com/krzyzanowskim/CryptoSwift)** | 10.6k | 2026-04 | 2026-08 | 11 | 5.6 | 5 | off | 用 Swift 实现的加密算法。 |
| 🟢 | [swift-crypto](https://github.com/apple/swift-crypto) | 1.7k | 2026-11 | 2026-11 | — | 6.2 | 6 | 100% | CryptoKit 接口的开源实现，也支持 Linux。 |

### Protocol Buffers

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-protobuf](https://github.com/apple/swift-protobuf)** | 5.0k | 2026-10 | 2026-11 | — | 6.2 | 6 | 100% | Swift 的 Protocol Buffers 运行时和代码生成器。 |

## 测试

### BDD 测试框架

Apple 原生: `Swift Testing` (Xcode 16) · `XCTest`

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [Quick](https://github.com/Quick/Quick) | 9.8k | 2024-07 | 2026-03 | 13 | 5.7 | 5 | 1/2 | BDD 风格的测试框架。 |

### 测试断言库

Apple 原生: `Swift Testing #expect / #require` (Xcode 16)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Nimble](https://github.com/Quick/Nimble)** | 4.8k | 2025-11 | 2026-05 | 13 | 6.0 | 5 | 1/1 | 测试断言匹配库。 |

### 快照测试

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-snapshot-testing](https://github.com/pointfreeco/swift-snapshot-testing)** | 4.4k | 2026-10 | 2026-10 | 13 | 6.0 | 5 | 20% | 对视图和数据做快照测试。 |

### 数据输出与差异对比

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-custom-dump](https://github.com/pointfreeco/swift-custom-dump)** | 894 | 2026-08 | 2026-08 | 15 | 6.4 | 6 | 3/3 | 输出 Swift 数据并对比差异，用于测试失败信息。 |

### 并发代码测试

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[swift-concurrency-extras](https://github.com/pointfreeco/swift-concurrency-extras)** | 492 | 2026-10 | 2026-10 | 13 | 6.0 | 6 | 0/0 | 测试 Swift 并发代码的工具。 |

## 工具链

### 代码检查

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftLint](https://github.com/realm/SwiftLint)** | 19.8k | 2026-08 | 2026-11 | — | 5.9 | 5 | 71% | 检查 Swift 代码风格和约定。 |

### 代码格式化

Apple 原生: `xcrun swift-format (bundled with Xcode)` (Xcode 16)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftFormat](https://github.com/nicklockwood/SwiftFormat)** | 9.0k | 2026-11 | 2026-11 | — | 5.7 | 5 | 86% | Swift 代码格式化工具。 |
| 🟢 | [swift-format](https://github.com/swiftlang/swift-format) | 3.0k | 2026-09 | 2026-11 | 16 | 6.0 | 5 | 65% | Swift 项目维护的代码格式化工具。 |

### 工程生成

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[XcodeGen](https://github.com/yonaskolb/XcodeGen)** | 8.9k | 2026-07 | 2026-10 | — | 5.9 | 5 | 48% | 根据 project.yml 生成 Xcode 工程。 |
| 🟢 | [tuist](https://github.com/tuist/tuist) | 5.9k | 2026-11 | 2026-11 | — | 6.1 | 6/5 | 65% | 根据 Project.swift 生成 Xcode 工程，另有缓存和构建分析。 |

### 构建日志格式化

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[xcbeautify](https://github.com/cpisciotta/xcbeautify)** | 1.6k | 2026-04 | 2026-08 | — | 6.1 | 6 | 11% | xcodebuild 输出格式化工具。 |

### 界面调试

Apple 原生: `Xcode View Debugger (Debug View Hierarchy)`

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[LookInside](https://github.com/LookInsideApp/LookInside)** | 397 | 2026-10 | 2026-11 | 15 | 5.10 | 5 | 60% | Mac 应用，查看运行中 iOS 或 macOS App 的视图、图层、frame 和属性。 |
| ⚪ | [LookinServer](https://github.com/QMUI/LookinServer) | 2.9k | 2024-04 | 2024-06 | 9 | 5.3 | 5 | 0/3 | 配合 Lookin macOS 应用的 iOS 框架：查看和修改运行中 App 的视图。 |
| 🟢 | [LookInside-Release](https://github.com/LookInsideApp/LookInside-Release) | 9 | 2026-10 | 2026-10 | 15 | 5.9 | ObjC/C | 0/0 | LookInside 的 iOS 端 server 包（支持 Swift Package Manager 和 CocoaPods）。 |

> **备注** · LookInside: README：LookInside 延续 Lookin 的工作；2.3.11 及以后的版本自带本地 MCP 服务，供 AI agent 使用。iOS 端通过 LookInside-Release 包接入。 ([来源](https://github.com/LookInsideApp/LookInside#readme))

### 资源代码生成

Apple 原生: `Generated asset symbols (ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS)` (Xcode 15) · `String Catalog symbols (STRING_CATALOG_GENERATE_SYMBOLS)` (Xcode 26) [来源](https://wwdcnotes.com/documentation/wwdc25-225-codealong-explore-localization-with-xcode/)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| ⚪ | [R.swift](https://github.com/mac-cain13/R.swift) | 9.5k | 2024-11 | 2025-03 | 11 | 5.6 | 5 | 0/1 | 生成强类型资源访问代码。 |
| ⚪ | [SwiftGen](https://github.com/SwiftGen/SwiftGen) | 9.5k | 2024-03 | 2022-02 | — | 5.6 | 5 | 0/3 | 为字符串、图片、字体等资源生成 Swift 代码。 |

### 发布与 App Store Connect

Apple 原生: `xcodebuild archive / -exportArchive` · `Xcode Cloud`

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[fastlane](https://github.com/fastlane/fastlane)** | 42.4k | 2026-10 | 2026-11 | — | 4.0 | 5 | 90% | 自动化签名、截图、构建和发布。 |
| 🟢 | [App-Store-Connect-CLI](https://github.com/rorkai/App-Store-Connect-CLI) | 8.3k | 2026-11 | 2026-11 | — | — | — | 100% | App Store Connect 命令行：构建、TestFlight、元数据、提交审核。 |

## AI agent 工具

### 编译运行 MCP

Apple 原生: `xcrun mcpbridge (Xcode MCP server)` (Xcode 26.3) [来源](https://infoq.com/news/2026/02/xcode-26-3-agentic-coding)

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[MobileBuildMCP](https://github.com/getsentry/MobileBuildMCP)** | 6.6k | 2026-09 | 2026-10 | — | — | — | 53% | MCP 服务和命令行：编译、运行、测试、调试、创建 iOS/macOS 项目（原名 XcodeBuildMCP）。 |

### 模拟器与真机界面自动化

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[mobile-mcp](https://github.com/mobile-next/mobile-mcp)** | 10.4k | 2026-11 | 2026-11 | — | — | — | 79% | 操作 iOS 和 Android 模拟器及真机的 MCP 服务。 |
| 🟢 | [agent-device](https://github.com/callstack/agent-device) | 5.3k | 2026-11 | 2026-11 | — | — | — | 100% | 命令行、MCP 服务和 Node.js API，用于在真机和模拟器上操作移动、Web、电视和桌面应用。 |
| 🟢 | [AXe](https://github.com/cameroncooke/AXe) | 2.3k | 2026-07 | 2026-07 | — | 5.10 | 5 | 50% | 通过辅助功能接口自动操作模拟器的命令行工具。 |
| 🟢 | [ios-simulator-mcp](https://github.com/joshuayoes/ios-simulator-mcp) | 2.2k | 2026-10 | 2026-10 | — | — | — | 75% | 在 iOS 模拟器里点击、输入、查看界面的 MCP 服务。 |
| 🟢 | [sim-use](https://github.com/lycorp-jp/sim-use) | 1.5k | 2026-10 | 2026-10 | — | 5.10 | 5 | 77% | 供 AI agent 读取和操作 iOS 模拟器、Android 模拟器/真机和 iPhone 真机屏幕的命令行工具。 |

### 给 agent 读的 Apple 文档

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[apple-docs-mcp](https://github.com/kimsungwhee/apple-docs-mcp)** | 1.4k | 2025-09 | 2026-03 | — | — | — | 0% | 搜索 Apple 开发者文档的 MCP 服务。 |
| 🟢 | [sosumi.ai](https://github.com/NSHipster/sosumi.ai) | 483 | 2026-11 | 2026-11 | — | — | — | 96% | 把 Apple 开发者文档转成 Markdown 供 AI 读取。 |

### SwiftUI skills

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill)** | 6.5k | 2026-10 | 2026-10 | — | — | — | 50% | SwiftUI agent skill。 |
| 🟢 | [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) | 3.9k | 2026-11 | 2026-11 | — | — | — | 87% | SwiftUI agent skill。 |

### Swift Concurrency skills

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Swift-Concurrency-Agent-Skill](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill)** | 1.7k | 2026-11 | 2026-11 | — | — | — | 50% | Swift Concurrency agent skill。 |

### 模拟器 skills

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[ios-simulator-skill](https://github.com/conorluddy/ios-simulator-skill)** | 1.3k | 2026-11 | 2026-11 | — | — | — | 75% | 在模拟器里编译、运行、检查 App 的 agent skill。 |

### 发布 skills

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[app-store-connect-cli-skills](https://github.com/rorkai/app-store-connect-cli-skills)** | 1.1k | — | 2026-11 | — | — | — | 100% | 配合 asc 命令行发布的 agent skills。 |

### Skill 索引

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[Swift-Agent-Skills](https://github.com/twostraws/Swift-Agent-Skills)** | 3.0k | — | 2026-09 | — | — | — | 0/2 | 按框架整理的 Swift agent skills 索引。 |

### AGENTS.md 模板

| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | Swift 模式 | Issue 回复 | 用途 |
|:-:|---|--:|---|---|---|---|---|--:|---|
| 🏆 | **[SwiftAgents](https://github.com/twostraws/SwiftAgents)** | 1.5k | — | 2026-03 | — | — | — | 1/2 | Swift / SwiftUI 项目的 AGENTS.md 文件。 |

## 参与贡献

在 [`data/catalog.yaml`](data/catalog.yaml) 里添加条目：写上 `repo` 和一句说明用途的 `does`。不写主观评价；`note` 必须附来源链接。然后运行 `python3 scripts/refresh.py && python3 scripts/build.py`。

---

如果这份列表对你有用，点个 ⭐ 能让更多 iOS 开发者找到它。
[⭐ jeffy-w/awesome-ios-for-agents](https://github.com/jeffy-w/awesome-ios-for-agents)
