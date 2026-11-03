#!/usr/bin/env python3
"""Build README.md, README_CN.md, catalog.json and llms.txt from data/catalog.yaml + data/stats.json.

Status and rank are computed mechanically (see RULES). No opinions are added here.
Usage: python3 scripts/build.py
"""
import json
import unicodedata
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REPO = "jeffy-w/awesome-ios-for-agents"
REPO_URL = f"https://github.com/{REPO}"
SKILL_DIR = ROOT / "skills" / "ios-starter"

ACTIVE_DAYS, INACTIVE_DAYS = 365, 730
RANKED = ("active", "slowing")
RULES = {
    "last_activity": "latest GitHub release date; for repos with no GitHub release, the last commit date on the default branch",
    "status": {
        "active": f"last activity less than {ACTIVE_DAYS} days ago",
        "slowing": f"last activity {ACTIVE_DAYS}-{INACTIVE_DAYS - 1} days ago",
        "inactive": f"last activity {INACTIVE_DAYS} or more days ago",
        "archived": "repository is archived on GitHub",
    },
    "rank": ("within a category, entries with status active or slowing that are not add-ons (addon_of) "
             "are sorted by stars, highest first; rank 1 is the top pick. Categories with ranked=false are not ranked."),
}


def age_days(d: str, today: str) -> int:
    return (date.fromisoformat(today) - date.fromisoformat(d)).days


def version_number(v):
    """'15' -> 15.0, '16.4' -> 16.4, None -> None (for numeric comparison by agents)."""
    if not v:
        return None
    parts = (v.split(".") + ["0"])[:2]
    return float(f"{int(parts[0])}.{int(parts[1])}")


def status_of(st: dict, today: str):
    # Status follows releases. Only repos without any GitHub release fall back to the last commit.
    last = st.get("released") or st.get("last_commit")
    if st["archived"]:
        return "archived", last
    if last is None:
        return "inactive", None
    age = age_days(last, today)
    if age < ACTIVE_DAYS:
        return "active", last
    if age < INACTIVE_DAYS:
        return "slowing", last
    return "inactive", last


def load():
    catalog = yaml.safe_load((ROOT / "data" / "catalog.yaml").read_text())
    stats = json.loads((ROOT / "data" / "stats.json").read_text())
    today = stats["refreshed"]
    out = {"generated": today, "source": REPO_URL, "rules": RULES, "sections": []}
    for sec in catalog["sections"]:
        s = {"id": sec["id"], "title": sec["title"], "categories": []}
        for cat in sec["categories"]:
            ranked_cat = cat.get("ranked", True)
            libs = []
            for lib in cat["libs"]:
                if lib["repo"] not in stats["repos"]:
                    raise SystemExit(f"{lib['repo']} is in catalog.yaml but not in stats.json; run scripts/refresh.py")
                st = stats["repos"][lib["repo"]]
                status, last = status_of(st, today)
                libs.append({
                    "repo": lib["repo"], "name": lib["repo"].split("/")[1], "url": st["url"],
                    "does": lib["does"], "note": lib.get("note"), "addon_of": lib.get("addon_of"),
                    "stars": st["stars"], "status": status, "last_activity": last,
                    "latest_release": st.get("release_tag"), "released": st.get("released"),
                    "last_commit": st.get("last_commit"),
                    "spm": st["spm"], "spm_version": st.get("spm_version"), "products": st.get("products", []),
                    "min_ios": version_number(st["min_ios"]), "swift_tools": st["swift_tools"],
                    "package_swift_at": st.get("package_swift_at"),
                    "license": st["license"], "rank": None,
                })
            names = [l["name"] for l in libs]
            for l in libs:
                if names.count(l["name"]) > 1:
                    l["name"] = l["repo"]
            if ranked_cat:
                ranked = sorted((l for l in libs if l["status"] in RANKED and not l["addon_of"]),
                                key=lambda l: -l["stars"])
                for i, l in enumerate(ranked, 1):
                    l["rank"] = i
            libs.sort(key=lambda l: (l["rank"] is None, l["rank"] or 0, -l["stars"]))
            native = [{"api": n["api"], "ios": version_number(n.get("ios")),
                       "xcode": n.get("xcode"), "source": n.get("source")} for n in cat.get("native", [])]
            s["categories"].append({"id": cat["id"], "title": cat["title"], "ranked": ranked_cat,
                                    "native": native, "libs": libs})
        out["sections"].append(s)
    return out


# ---------------------------------------------------------------- README

T = {
    "en": dict(
        file="README.md", other="[中文](README_CN.md)",
        tagline="Pick iOS open-source libraries by data, for people and for AI coding agents.",
        intro=("Every library shows the same facts: stars, latest release, last commit, minimum iOS and Swift tools version. "
               "The top pick in each category comes from a fixed rule. Data refreshed **{date}** and every week by GitHub Actions."),
        agents_h="For agents",
        agents=("Install the `ios-starter` skill, then ask your agent to start a new iOS app. It asks what the app needs, "
                "picks libraries from this catalog by the rule below, creates the project with a verified recipe, "
                "and builds and launches it in the Simulator."),
        agents_raw="Agents can also read the data directly: [`catalog.json`](catalog.json) · [`llms.txt`](llms.txt)",
        rules_h="How the top pick is chosen",
        rules=[
            "**Status is based on releases**: the date of the latest GitHub release. Only repos that have never published a GitHub release use their last commit date instead. Both dates are shown in the tables.",
            "**Status**: 🟢 active (< 1 year) · 🟡 slowing (1–2 years) · ⚪ inactive (≥ 2 years) · 🗄 archived.",
            "**🏆 Top pick** = the most-starred 🟢/🟡 entry in its category. Add-ons of another entry are not ranked. Categories marked *not ranked* list provider-specific SDKs.",
            "**Min iOS** and **Swift tools** are read from `Package.swift` at the latest release tag.",
            "**Apple native** lists the system API for the same job and its minimum OS.",
            "Categories and descriptions are written by hand and only say what a project does. Notes quote a source. Status and rank are computed by [`scripts/build.py`](scripts/build.py).",
        ],
        recipes_h="Start a new project",
        recipes_intro="Four ways an agent can create an iOS app from nothing. Each was run end to end on Xcode 27.2 on 2026-11-03.",
        recipes_cols="| Recipe | Project defined in | Add a package | Verified |",
        recipes=[
            ("XcodeGen", "xcodegen", "`project.yml`", "`packages:` in YAML", "create, add package, build, launch"),
            ("Tuist", "tuist", "`Project.swift`", "`Tuist/Package.swift` + `tuist install`", "create, add package, build, launch"),
            ("MobileBuildMCP", "mobilebuildmcp", "Xcode project + local Swift package", "local `Package.swift`", "create, add package, build, launch"),
            ("Xcode MCP", "xcode-mcp", "Apple's Xcode template", "in Xcode (no MCP tool in 27.2)", "create, build, launch"),
        ],
        contents_h="Contents",
        native="Apple native",
        not_ranked="*Not ranked: provider-specific SDKs.*",
        cols="| | Library | Stars | Release | Last commit | Min iOS | Swift tools | What it does |",
        note="Note", source="source",
        contrib_h="Contributing",
        contrib=("Add an entry to [`data/catalog.yaml`](data/catalog.yaml): the `repo` and a `does` line that says what it does. "
                 "No opinions; a `note` needs a source link. Then run `python3 scripts/refresh.py && python3 scripts/build.py`."),
        star="If this list is useful to you, a ⭐ helps other iOS developers find it.",
    ),
    "zh": dict(
        file="README_CN.md", other="[English](README.md)",
        tagline="用数据挑选 iOS 开源库，给人看，也给 AI 编程 agent 用。",
        intro=("每个库都列出同样的数据：star 数、最近一次 Release、最近一次提交、最低 iOS 版本、Swift tools 版本。"
               "每个分类的首选按固定规则算出。数据更新于 **{date}**，之后由 GitHub Actions 每周刷新。"),
        agents_h="给 agent 用",
        agents=("安装 `ios-starter` skill，然后让 agent 新建一个 iOS 应用。它会先问清楚应用需要什么，"
                "按下面的规则从这份目录里选库，用一套验证过的方案创建项目，再编译并在模拟器里启动。"),
        agents_raw="agent 也可以直接读取数据：[`catalog.json`](catalog.json) · [`llms.txt`](llms.txt)",
        rules_h="首选怎么算出来",
        rules=[
            "**状态按发版计算**：取最近一次 GitHub Release 的日期。只有从未发布过 GitHub Release 的仓库，才改用默认分支最近一次提交的日期。表格里两个日期都会显示。",
            "**状态**：🟢 活跃（< 1 年）· 🟡 放缓（1–2 年）· ⚪ 不活跃（≥ 2 年）· 🗄 已归档。",
            "**🏆 首选** = 分类中 star 最多的 🟢/🟡 条目。依附于其他库的扩展不参与排名。标为“不排名”的分类里是各家服务商自己的 SDK。",
            "**最低 iOS** 和 **Swift tools** 读取自最新 Release 标签下的 `Package.swift`。",
            "**Apple 原生** 列出能完成同样工作的系统 API 及其最低系统版本。",
            "分类和描述是人工编写的，只说明项目做什么；备注引用来源原文。状态和排名由 [`scripts/build.py`](scripts/build.py) 计算。",
        ],
        recipes_h="新建项目",
        recipes_intro="agent 从零创建 iOS 应用的四种方案。每种都于 2026-11-03 在 Xcode 27.2 上完整跑过。",
        recipes_cols="| 方案 | 工程定义方式 | 添加依赖包 | 已验证 |",
        recipes=[
            ("XcodeGen", "xcodegen", "`project.yml`", "YAML 里的 `packages:`", "创建、加依赖、编译、启动"),
            ("Tuist", "tuist", "`Project.swift`", "`Tuist/Package.swift` + `tuist install`", "创建、加依赖、编译、启动"),
            ("MobileBuildMCP", "mobilebuildmcp", "Xcode 工程 + 本地 Swift 包", "本地 `Package.swift`", "创建、加依赖、编译、启动"),
            ("Xcode MCP", "xcode-mcp", "Apple 官方 Xcode 模板", "在 Xcode 里添加（27.2 的 MCP 没有对应工具）", "创建、编译、启动"),
        ],
        contents_h="目录",
        native="Apple 原生",
        not_ranked="*不排名：各家服务商自己的 SDK。*",
        cols="| | 库 | Stars | Release | 最近提交 | 最低 iOS | Swift tools | 用途 |",
        note="备注", source="来源",
        contrib_h="参与贡献",
        contrib=("在 [`data/catalog.yaml`](data/catalog.yaml) 里添加条目：写上 `repo` 和一句说明用途的 `does`。"
                 "不写主观评价；`note` 必须附来源链接。然后运行 `python3 scripts/refresh.py && python3 scripts/build.py`。"),
        star="如果这份列表对你有用，点个 ⭐ 能让更多 iOS 开发者找到它。",
    ),
}

ICON = {"active": "🟢", "slowing": "🟡", "inactive": "⚪", "archived": "🗄"}
DASH = "—"


def stars(n):
    return f"{n/1000:.1f}k" if n >= 1000 else str(n)


def anchor(text):
    """GitHub heading slug: lowercase, drop punctuation, spaces to hyphens."""
    out = []
    for ch in text.lower():
        if ch == " ":
            out.append("-")
        elif ch in "-_" or unicodedata.category(ch)[0] in "LN":
            out.append(ch)
    return "".join(out)


def native_text(n, lang):
    ver = f"iOS {n['ios']:g}" if n["ios"] is not None else (f"Xcode {n['xcode']}" if n["xcode"] else "")
    s = f"`{n['api']}`" + (f" ({ver})" if ver else "")
    if n["source"]:
        s += f" [{T[lang]['source']}]({n['source']})"
    return s


def readme(data, lang):
    t = T[lang]
    L = ["# Awesome iOS for Agents", "", t["other"], "", f"**{t['tagline']}**", "",
         t["intro"].format(date=data["generated"]), "",
         f"## {t['agents_h']}", "", t["agents"], "", "```bash",
         f"npx skills add {REPO}@ios-starter -g -y", "```", "", t["agents_raw"], "",
         f"## {t['rules_h']}", ""]
    L += [f"- {r}" for r in t["rules"]]
    L += ["", f"## {t['recipes_h']}", "", t["recipes_intro"], "", t["recipes_cols"], "|---|---|---|---|"]
    for name, slug, defined, pkg, ok in t["recipes"]:
        L.append(f"| [{name}](skills/ios-starter/recipes/{slug}.md) | {defined} | {pkg} | {ok} |")
    L += ["", f"## {t['contents_h']}", ""]
    for s in data["sections"]:
        cats = " · ".join(f"[{c['title'][lang]}](#{anchor(c['title'][lang])})" for c in s["categories"])
        L.append(f"- **{s['title'][lang]}**: {cats}")
    for s in data["sections"]:
        L += ["", f"## {s['title'][lang]}"]
        for c in s["categories"]:
            L += ["", f"### {c['title'][lang]}", ""]
            if c["native"]:
                L += [f"{t['native']}: " + " · ".join(native_text(n, lang) for n in c["native"]), ""]
            if not c["ranked"]:
                L += [t["not_ranked"], ""]
            L += [t["cols"], "|:-:|---|--:|---|---|---|---|---|"]
            notes = []
            for l in c["libs"]:
                mark = "🏆" if l["rank"] == 1 else ICON[l["status"]]
                name = f"**[{l['name']}]({l['url']})**" if l["rank"] == 1 else f"[{l['name']}]({l['url']})"
                rel = (l["released"] or "")[:7] or DASH
                com = (l["last_commit"] or "")[:7] or DASH
                ios = f"{l['min_ios']:g}" if l["min_ios"] is not None else DASH
                L.append(f"| {mark} | {name} | {stars(l['stars'])} | {rel} | {com} | {ios} | "
                         f"{l['swift_tools'] or DASH} | {l['does'][lang]} |")
                if l["note"]:
                    notes.append(f"> **{t['note']}** · {l['name']}: {l['note'][lang]} ([{t['source']}]({l['note']['source']}))")
            if notes:
                L += [""] + notes
    L += ["", f"## {t['contrib_h']}", "", t["contrib"], "", "---", "", t["star"], f"[⭐ {REPO}]({REPO_URL})", ""]
    (ROOT / t["file"]).write_text("\n".join(L))


def llms(data):
    def v(x):
        return "unknown" if x is None else (f"{x:g}" if isinstance(x, float) else x)
    L = ["# Awesome iOS for Agents", "",
         "> Catalog of iOS open-source libraries with objective data (stars, release, last commit, min iOS, "
         "Swift tools version) and a computed top pick per category.", "",
         f"Data date: {data['generated']}. Machine-readable data: {REPO_URL}/raw/main/catalog.json", "",
         f"Rules: last activity = {RULES['last_activity']}. Status: active < {ACTIVE_DAYS} days, "
         f"slowing < {INACTIVE_DAYS} days, inactive otherwise, or archived. Rank: {RULES['rank']}", "",
         "## Recipes", ""]
    for slug in ("xcodegen", "tuist", "mobilebuildmcp", "xcode-mcp", "verify"):
        L.append(f"- [{slug}]({REPO_URL}/blob/main/skills/ios-starter/recipes/{slug}.md)")
    for s in data["sections"]:
        for c in s["categories"]:
            L += ["", f"## {c['title']['en']}" + ("" if c["ranked"] else " (not ranked)")]
            if c["native"]:
                L.append("Native: " + "; ".join(
                    n["api"] + (f" (iOS {n['ios']:g})" if n["ios"] is not None else (f" (Xcode {n['xcode']})" if n["xcode"] else ""))
                    for n in c["native"]))
            for l in c["libs"]:
                top = " TOP" if l["rank"] == 1 else ""
                L.append(f"- {l['repo']} [{l['status']}{top}] stars={l['stars']} last_activity={v(l['last_activity'])} "
                         f"min_ios={v(l['min_ios'])} spm_version={v(l['spm_version'])} — {l['does']['en']}")
    (ROOT / "llms.txt").write_text("\n".join(L) + "\n")


def main():
    data = load()
    js = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    (ROOT / "catalog.json").write_text(js)
    (SKILL_DIR / "catalog.json").write_text(js)
    for lang in T:
        readme(data, lang)
    llms(data)
    n = sum(len(c["libs"]) for s in data["sections"] for c in s["categories"])
    print(f"built {n} entries, {sum(len(s['categories']) for s in data['sections'])} categories, data {data['generated']}")


if __name__ == "__main__":
    main()
