#!/usr/bin/env python3
"""Fetch live GitHub facts for every repo in data/catalog.yaml into data/stats.json.

Facts per repo: stars, archived, latest release (tag + date), last commit on the default
branch, latest semantic-version tag, and from Package.swift at that version: swift-tools-version,
minimum iOS and library product names.

Needs the GitHub CLI (`gh`) authenticated, or GH_TOKEN set (as in GitHub Actions).
Usage: python3 scripts/refresh.py
"""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.yaml"
STATS = ROOT / "data" / "stats.json"
SEMVER = re.compile(r"^v?(\d+)\.(\d+)(?:\.(\d+))?$")

FIELDS = """
  nameWithOwner url stargazerCount isArchived
  licenseInfo { spdxId }
  defaultBranchRef { target { ... on Commit { committedDate } } }
  latestRelease { tagName publishedAt }
  refs(refPrefix: "refs/tags/", last: 100, orderBy: {field: TAG_COMMIT_DATE, direction: ASC}) { nodes { name } }
  head: object(expression: "HEAD:Package.swift") { ... on Blob { text } }
"""


def gql(query: str) -> dict:
    for attempt in range(3):
        res = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                             capture_output=True, text=True)
        try:
            data = json.loads(res.stdout or "{}").get("data")
        except json.JSONDecodeError:
            data = None
        if data:  # partial results (one repo renamed) still carry data
            return data
        print(f"gh api graphql failed (attempt {attempt + 1}): {res.stderr.strip()[:300]}", file=sys.stderr)
    raise SystemExit("GitHub API unavailable; stats.json left unchanged")


def semver_key(tag: str):
    m = SEMVER.match(tag)
    return tuple(int(x or 0) for x in m.groups()) if m else None


def best_tag(release_tag, tags):
    """Latest release tag if it is semver, else the highest semver tag."""
    if release_tag and semver_key(release_tag):
        return release_tag
    versions = [t for t in tags if semver_key(t)]
    return max(versions, key=semver_key) if versions else None


def parse_package(text):
    if not text:
        return None, None, []
    tools = re.search(r"swift-tools-version\s*:\s*([0-9.]+)", text)
    ios = re.search(r"\.iOS\(\s*(?:\.v|\")([0-9_.]+)", text)
    products = sorted(set(re.findall(r"\.library\(\s*name:\s*\"([^\"]+)\"", text)))
    return (tools.group(1) if tools else None,
            ios.group(1).replace("_", ".") if ios else None,
            products)


def batched(items, n=20):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def main():
    catalog = yaml.safe_load(CATALOG.read_text())
    repos = sorted({lib["repo"] for s in catalog["sections"] for c in s["categories"] for lib in c["libs"]})
    raw, missing = {}, []
    for chunk in batched(repos):
        parts = [f'r{i}: repository(owner: "{r.split("/")[0]}", name: "{r.split("/")[1]}") {{ {FIELDS} }}'
                 for i, r in enumerate(chunk)]
        data = gql("query {" + "\n".join(parts) + "}")
        for i, repo in enumerate(chunk):
            if data.get(f"r{i}"):
                raw[repo] = data[f"r{i}"]
            else:
                missing.append(repo)
    if missing:
        raise SystemExit("MISSING (renamed or deleted?): " + ", ".join(missing) + "\nstats.json left unchanged")

    # Read Package.swift at the version an agent will install, not at HEAD.
    tags = {r: best_tag((d.get("latestRelease") or {}).get("tagName"),
                        [n["name"] for n in (d.get("refs") or {}).get("nodes") or []])
            for r, d in raw.items()}
    tagged = [r for r in repos if tags[r]]
    pkg_at_tag = {}
    for chunk in batched(tagged):
        parts = [f'r{i}: repository(owner: "{r.split("/")[0]}", name: "{r.split("/")[1]}") '
                 f'{{ object(expression: "{tags[r]}:Package.swift") {{ ... on Blob {{ text }} }} }}'
                 for i, r in enumerate(chunk)]
        data = gql("query {" + "\n".join(parts) + "}")
        for i, r in enumerate(chunk):
            obj = (data.get(f"r{i}") or {}).get("object")
            if obj and obj.get("text"):
                pkg_at_tag[r] = obj["text"]

    stats = {}
    for repo, d in raw.items():
        text = pkg_at_tag.get(repo) or (d.get("head") or {}).get("text")
        tools, min_ios, products = parse_package(text)
        release = d.get("latestRelease") or {}
        commit = ((d.get("defaultBranchRef") or {}).get("target") or {}).get("committedDate")
        stats[repo] = {
            "url": d["url"],
            "stars": d["stargazerCount"],
            "archived": d["isArchived"],
            "license": (d.get("licenseInfo") or {}).get("spdxId"),
            "release_tag": release.get("tagName"),
            "released": (release.get("publishedAt") or "")[:10] or None,
            "last_commit": (commit or "")[:10] or None,
            "spm_version": tags[repo].lstrip("v") if tags[repo] and tools else None,
            "spm": tools is not None,
            "package_swift_at": (tags[repo] if repo in pkg_at_tag else "HEAD") if tools else None,
            "swift_tools": tools,
            "min_ios": min_ios,
            "products": products,
        }

    tmp = STATS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"refreshed": date.today().isoformat(), "repos": stats},
                              indent=1, sort_keys=True) + "\n")
    tmp.replace(STATS)
    print(f"refreshed {len(stats)} repos; Package.swift read at a release tag for {len(pkg_at_tag)}")


if __name__ == "__main__":
    main()
