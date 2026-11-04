#!/usr/bin/env python3
"""Fetch live GitHub facts for every repo in data/catalog.yaml into data/stats.json.

Facts per repo: stars, archived, latest release (tag + date), last commit on the default
branch, latest semantic-version tag, and from Package.swift at that version: swift-tools-version,
minimum iOS and library product names. The Swift language mode of the library targets is read by
`swift package dump-package`, so SwiftPM itself picks the version-specific manifest
(Package@swift-X.Y.swift) and evaluates the settings.

Manifests are Swift code from third parties. Each runs in its own container of the pinned image in
scripts/swift/Dockerfile: no network, no GitHub token, and only its own manifest folder mounted
read-only. On macOS without Docker the local Swift is used instead, inside SwiftPM's sandbox.

Needs the GitHub CLI (`gh`) authenticated, or GH_TOKEN set (as in GitHub Actions).
A value that cannot be read in a run keeps the last value read (swift_mode_checked / issues_checked
say when). `--check` exits 1 when the data needs attention, e.g. a manifest needs a newer Swift.

Usage: python3 scripts/refresh.py            # fetch and write data/stats.json
       python3 scripts/refresh.py --check    # exit 1 if stats.json needs attention
"""
import json
import platform
import shutil
from urllib.parse import quote
import posixpath
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.yaml"
STATS = ROOT / "data" / "stats.json"
SEMVER = re.compile(r"^v?(\d+)\.(\d+)(?:\.(\d+))?$")
MAINTAINER = {"OWNER", "MEMBER", "COLLABORATOR"}
ISSUE_WINDOW, ISSUE_GRACE, ISSUE_MIN = 365, 30, 5
ISSUE_FIELDS = """
  issueCount
  nodes { ... on Issue {
    author { __typename login } authorAssociation
    comments(first: 30) { nodes { author { __typename login } authorAssociation } }
    timelineItems(itemTypes: [CLOSED_EVENT, LABELED_EVENT, ASSIGNED_EVENT], first: 20) { nodes {
      __typename
      ... on ClosedEvent { actor { __typename login } }
      ... on LabeledEvent { actor { __typename login } }
      ... on AssignedEvent { actor { __typename login } }
    } }
  } }
"""
# Swift image (tag@digest) from scripts/swift/Dockerfile, which Dependabot keeps current.
def pinned_image():
    m = re.search(r"^FROM\s+(?:--\S+\s+)*(\S+)", (ROOT / "scripts" / "swift" / "Dockerfile").read_text(), re.M)
    if not m or not re.fullmatch(r"[\w./-]+:[\w.-]+@sha256:[0-9a-f]{64}", m.group(1)):
        raise SystemExit("scripts/swift/Dockerfile: FROM must be image:tag@sha256:<digest>")
    return m.group(1)


SWIFT_IMAGE = pinned_image()
# No network, no host environment, unprivileged user, read-only root, bounded processes and memory.
SANDBOX = ["--network", "none", "--user", "65534:65534", "--cap-drop", "ALL",
           "--security-opt", "no-new-privileges", "--pids-limit", "256", "--memory", "2g",
           "--read-only", "--tmpfs", "/tmp:rw,exec", "-e", "HOME=/tmp"]
MAX_FAILURES = 0.5  # `--check` fails when more repos than this share could not be read this run
MAX_STALE_DAYS = 28  # `--check` fails when a kept value is older than this
NEEDS_SWIFT = re.compile(r"using Swift tools version ([0-9.]+) but the installed version is ([0-9.]+)")

FIELDS = """
  nameWithOwner url stargazerCount isArchived hasIssuesEnabled
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
        time.sleep(2 ** attempt * 5)
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
    """Return (tools, min_ios, ios_platform, products).

    ios_platform: "declared" (minimum iOS found), "not-declared" (no platforms list),
    "ios-not-listed" (platforms list names other OSes but not iOS),
    "unparsed" (a platforms list exists but no literal .iOS(...) or other OS was found).
    Products are literal `.library(name: "...")` names, skipping internal ones that start with "_".
    """
    if not text:
        return None, None, None, []
    tools = re.search(r"swift-tools-version\s*:\s*([0-9.]+)", text)
    ios = re.search(r"\.iOS\(\s*(?:\.v|\")([0-9_.]+)", text)
    if ios:
        platform = "declared"
    else:
        # a Package-level `platforms:` argument, not `.when(platforms: ...)` in conditions
        top_level = any(not re.search(r"when\(\s*$", text[:m.start()])
                        for m in re.finditer(r"\bplatforms\s*:", text))
        if not top_level:
            platform = "not-declared"
        elif re.search(r"\.(macOS|tvOS|watchOS|visionOS|macCatalyst)\(", text):
            platform = "ios-not-listed"
        else:
            platform = "unparsed"
    products = sorted({p for p in re.findall(r"\.library\(\s*name:\s*\"([^\"]+)\"", text)
                       if not p.startswith("_")})
    return (tools.group(1) if tools else None,
            ios.group(1).replace("_", ".") if ios else None,
            platform, products)


def setting_applies(s, strict=False):
    """A target setting counts unless its condition limits it to platforms other than iOS.
    For strict concurrency, settings that only apply to one build configuration or trait do not count."""
    cond = s.get("condition") or {}
    names = cond.get("platformNames") or []
    if names and "ios" not in names:
        return False
    return not (strict and (cond.get("config") or cond.get("traits")))


SOURCE_DIRS = ("Sources", "Source", "src", "srcs")


def norm(path):
    """Repo-relative folder; "" for the package root."""
    p = posixpath.normpath(path).strip("/")
    return "" if p == "." else p


def under(f, base):
    return f.startswith(base + "/") if base else True


def target_dirs(t):
    """Folders SwiftPM would read a target's sources from."""
    return [norm(t["path"])] if t.get("path") else [f"{d}/{t['name']}" for d in SOURCE_DIRS]


def has_swift(t, files, all_dirs):
    """Does target t compile any of the .swift `files`? A file belongs to the deepest target folder
    that holds it (nested targets exclude each other's folders); `exclude` and `sources` apply."""
    exclude = [norm(e) for e in t.get("exclude") or []]
    sources = [norm(x) for x in t.get("sources") or []]
    for base in target_dirs(t):
        deeper = [d for d in all_dirs if d != base and d and under(d, base)]
        for f in files:
            if not under(f, base) or any(under(f, d) for d in deeper):
                continue
            rel = f[len(base) + 1:] if base else f
            if any(rel == e or rel.startswith(e + "/") for e in exclude):
                continue
            if sources and not any(rel == x or rel.startswith(x + "/") for x in sources):
                continue
            return True
    return False


def linked_targets(dump):
    """Targets an app links: those of library products and the package targets they depend on.
    Without a library product (a tool), every regular and executable target."""
    by_name = {t["name"]: t for t in dump["targets"]}
    roots = [n for p in dump["products"] if "library" in p["type"] for n in p["targets"]]
    if not roots:
        roots = [t["name"] for t in dump["targets"] if t["type"] in ("regular", "executable")]
    seen, todo = set(), list(roots)
    while todo:
        name = todo.pop()
        if name in seen or name not in by_name:
            continue
        seen.add(name)
        for dep in by_name[name].get("dependencies") or []:
            for key in ("byName", "target"):
                if key in dep and dep[key] and dep[key][0] in by_name:
                    todo.append(dep[key][0])
    return [by_name[n] for n in sorted(seen) if by_name[n]["type"] in ("regular", "executable")]


def swift_mode(dump, has_swift):
    """Language mode of the Swift targets an app links, from `swift package dump-package` JSON.

    has_swift(target) tells whether the target's folder holds .swift files (ObjC/C targets have no
    language mode). Returns (mode, strict): "6" when every such target builds in Swift 6 mode, "5"
    when none does, "6/5" when mixed; strict is True when every target left in Swift 5 mode turns on
    complete strict concurrency checking. ("none", None) when no linked target has Swift sources.
    """
    tools = semver_key(dump["toolsVersion"]["_version"]) or (0, 0, 0)
    listed = [float(v) for v in dump.get("swiftLanguageVersions") or []
              if re.fullmatch(r"\d+(\.\d+)?", v) and float(v) <= 6]
    package_mode = max(listed) if listed else (6 if tools >= (6, 0, 0) else 5)
    targets = [t for t in linked_targets(dump) if has_swift(t)]
    if not targets:
        return "none", None
    modes, strict = [], []
    for t in targets:
        mode, complete = package_mode, False
        for s in t.get("settings") or []:
            if s["tool"] != "swift" or not setting_applies(s):
                continue
            kind = s["kind"]
            flags = (kind.get("unsafeFlags") or {}).get("_0") or []
            if "swiftLanguageMode" in kind:
                mode = float(kind["swiftLanguageMode"]["_0"])
            if "-swift-version" in flags[:-1]:
                v = flags[flags.index("-swift-version") + 1]
                if re.fullmatch(r"\d+(\.\d+)?", v):
                    mode = float(v)
            if not setting_applies(s, strict=True):
                continue
            for key in ("enableUpcomingFeature", "enableExperimentalFeature"):
                if (kind.get(key) or {}).get("_0") in ("StrictConcurrency", "StrictConcurrency=complete"):
                    complete = True
            if "-strict-concurrency=complete" in flags:
                complete = True
        modes.append(mode >= 6)
        if mode < 6:
            strict.append(complete)
    mode = "6" if all(modes) else ("5" if not any(modes) else "6/5")
    return mode, (all(strict) if strict else None)


def rest(path):
    """GET a REST path; None (and a note on stderr) on any failure."""
    try:
        res = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=120)
        if res.returncode == 0:
            return json.loads(res.stdout)
        err = res.stderr.strip()[:200]
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        err = str(e)[:200]
    print(f"gh api {path} failed: {err}", file=sys.stderr)
    return None


def swift_files(repo, ref, dump):
    """Paths of .swift files at ref inside the folders of the targets an app links, or None if unknown."""
    dirs = {d for t in linked_targets(dump) for d in target_dirs(t)}
    inside = lambda f: f.endswith(".swift") and any(under(f, d) for d in dirs)
    tree = rest(f"repos/{repo}/git/trees/{ref}?recursive=1")
    if tree is None:
        return None
    if not tree.get("truncated"):
        return [e["path"] for e in tree["tree"] if e["type"] == "blob" and inside(e["path"])]
    # Large repo (truncated listing): list each target folder's own tree.
    names = {e["path"] for e in tree["tree"] if e["type"] == "tree"}  # top levels are listed even when truncated
    files = []
    for d in dirs:
        if not d or d.split("/")[0] not in names:
            if not d:
                return None  # root target in a huge repo: cannot list it
            continue
        sub = rest(f"repos/{repo}/git/trees/{quote(ref + ':' + d, safe='')}?recursive=1")
        if sub is None:
            continue  # folder does not exist at ref (one of the default source folders)
        if sub.get("truncated"):
            return None
        files += [f"{d}/{e['path']}" for e in sub["tree"] if e["type"] == "blob" and e["path"].endswith(".swift")]
    return sorted(set(files))  # nested target folders are listed more than once


def use_container():
    """The pinned image everywhere Docker runs, so local and CI results match. Without Docker,
    macOS falls back to the local Swift (SwiftPM sandbox); other systems have no safe fallback."""
    try:
        if shutil.which("docker") and subprocess.run(["docker", "info"], capture_output=True, timeout=30).returncode == 0:
            return True
    except subprocess.TimeoutExpired:
        pass
    if platform.system() == "Darwin" and shutil.which("swift"):
        print("Docker not running: reading Package.swift with the local Swift, results may differ from CI",
              file=sys.stderr)
        return False
    return None


def dump_one(d: Path, container: bool):
    """Run `swift package dump-package` on one manifest folder; return (stdout, stderr).

    Container: one per manifest, no network, no environment from this process (so no GitHub
    token), unprivileged, and only this folder mounted, read-only. Native: SwiftPM's macOS sandbox.
    """
    if container:
        cmd = ["docker", "run", "--rm", "--name", f"dump-{d.parent.name}-{d.name}", *SANDBOX,
               "-v", f"{d}:/w:ro", SWIFT_IMAGE, "swift", "package", "dump-package", "--package-path", "/w"]
    else:
        cmd = ["swift", "package", "dump-package", "--package-path", str(d)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        if container:
            subprocess.run(["docker", "kill", cmd[4]], capture_output=True)
        return "", "timed out after 300s"
    return res.stdout, res.stderr


def dump_packages(manifests):
    """{repo: {filename: text}} -> ({repo: JSON or None}, {repo: error}, Swift version or None).
    Never raises: when Swift cannot run at all, every repo gets the same error. The third value is
    the Swift version actually used, the fourth the image (or "local") it came from."""
    container = use_container()
    if container is None:
        return {r: None for r in manifests}, {r: "no Docker or Swift to read manifests" for r in manifests}, None, None
    if container and subprocess.run(["docker", "pull", "-q", SWIFT_IMAGE], capture_output=True).returncode != 0:
        return {r: None for r in manifests}, {r: f"cannot pull {SWIFT_IMAGE}" for r in manifests}, None, None
    out, errors = {}, {}
    with tempfile.TemporaryDirectory() as root:
        dirs = {}
        for i, (repo, files) in enumerate(sorted(manifests.items())):
            d = Path(root) / f"p{i}"
            d.mkdir()
            for name, text in files.items():
                (d / name).write_text(text)
            dirs[repo] = d
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = dict(zip(dirs, pool.map(lambda d: dump_one(d, container), dirs.values())))
    for repo, (stdout, stderr) in results.items():
        try:
            out[repo] = json.loads(stdout)
        except json.JSONDecodeError:
            out[repo] = None
            m = NEEDS_SWIFT.search(stderr)
            lines = stderr.strip().splitlines()
            line = next((x for x in lines if "error:" in x.lower()), lines[-1] if lines else "no output")
            errors[repo] = f"needs Swift {m.group(1)}" if m else line[:200]
            print(f"dump-package failed for {repo}: {errors[repo]}", file=sys.stderr)
    version = subprocess.run(["docker", "run", "--rm", *SANDBOX, SWIFT_IMAGE, "swift", "--version"] if container
                             else ["swift", "--version"], capture_output=True, text=True).stdout
    m = re.search(r"Swift version ([0-9.]+)", version)
    return out, errors, (m.group(1) if m else None), (SWIFT_IMAGE.split("@")[0] if container else "local")


def issue_window(today: date):
    """Issues opened in the 12 months that end ISSUE_GRACE days ago, so each had time to get a reply."""
    end = today - timedelta(days=ISSUE_GRACE)
    return (end - timedelta(days=ISSUE_WINDOW)).isoformat(), end.isoformat()


def is_person(actor):
    return bool(actor) and actor.get("__typename") != "Bot" and not actor.get("login", "").endswith("[bot]")


def issue_response(nodes):
    """(issues, answered) for issues opened by people outside the project.

    Maintainers = people GitHub marks OWNER, MEMBER or COLLABORATOR, plus people who closed, labeled
    or assigned someone else's issue (that needs triage access; it also catches org members whose
    membership is private, whom GitHub marks CONTRIBUTOR). Answered = a maintainer other than the
    author commented, or a person other than the author closed it. Bots (e.g. stale bots) never count.
    """
    nodes = [n for n in nodes if n and is_person(n.get("author"))]
    events = lambda n: [e for e in (n.get("timelineItems") or {}).get("nodes") or [] if e]
    comments = lambda n: (n.get("comments") or {}).get("nodes") or []
    maintainers = {n["author"]["login"] for n in nodes if n.get("authorAssociation") in MAINTAINER}
    for n in nodes:
        maintainers |= {c["author"]["login"] for c in comments(n)
                        if is_person(c.get("author")) and c.get("authorAssociation") in MAINTAINER}
        maintainers |= {e["actor"]["login"] for e in events(n)
                        if is_person(e.get("actor")) and e["actor"]["login"] != n["author"]["login"]}
    issues = answered = 0
    for n in nodes:
        author = n["author"]["login"]
        if author in maintainers:
            continue
        issues += 1
        replied = any(is_person(c.get("author")) and c["author"]["login"] in maintainers
                      and c["author"]["login"] != author for c in comments(n))
        closed = any(e.get("__typename") == "ClosedEvent" and is_person(e.get("actor"))
                     and e["actor"]["login"] != author for e in events(n))
        answered += replied or closed
    return issues, answered


def issue_search(repo, since, until, want=100):
    """Latest `want` issues of one repo in the window, or None.

    Pages of 50, halved to 25 when GitHub reports errors (e.g. RESOURCE_LIMITS_EXCEEDED): partial
    data would undercount replies, so a page with errors is never used.
    """
    nodes, after, total, size, err = [], None, 0, 50, ""
    while len(nodes) < want:
        cursor = f', after: "{after}"' if after else ""
        query = (f'query {{ x: search(type: ISSUE, first: {min(size, want - len(nodes))}{cursor}, '
                 f'query: "repo:{repo} is:issue created:{since}..{until} sort:created-desc") '
                 f'{{ pageInfo {{ hasNextPage endCursor }} {ISSUE_FIELDS} }} }}')
        try:
            res = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                                 capture_output=True, text=True, timeout=120)
            body = json.loads(res.stdout or "{}")
            x = (body.get("data") or {}).get("x")
            err = json.dumps(body["errors"])[:200] if body.get("errors") else res.stderr.strip()[:200]
            bad = x is None or bool(body.get("errors"))
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            bad, err = True, str(e)[:200]
        if bad:
            if size > 25:
                size = 25
                continue
            print(f"issue search failed for {repo}: {err}", file=sys.stderr)
            return None
        nodes += x["nodes"]
        total = x["issueCount"]
        if not x["pageInfo"]["hasNextPage"]:
            break
        after = x["pageInfo"]["endCursor"]
    return {"issueCount": total, "nodes": nodes}


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
    pkg_at_tag, variants, root_files = {}, {}, {}
    for chunk in batched(repos):
        parts = [f'r{i}: repository(owner: "{r.split("/")[0]}", name: "{r.split("/")[1]}") {{ '
                 f'object(expression: "{tags[r] or "HEAD"}:Package.swift") {{ ... on Blob {{ text }} }} '
                 f'tree: object(expression: "{tags[r] or "HEAD"}:") {{ ... on Tree {{ entries {{ name }} }} }} '
                 f'headTree: object(expression: "HEAD:") {{ ... on Tree {{ entries {{ name }} }} }} }}'
                 for i, r in enumerate(chunk)]
        data = gql("query {" + "\n".join(parts) + "}")
        for i, r in enumerate(chunk):
            d = data.get(f"r{i}") or {}
            obj = d.get("object")
            if tags[r] and obj and obj.get("text"):
                pkg_at_tag[r] = obj["text"]
            tree = d.get("tree") if r in pkg_at_tag else d.get("headTree")
            names = [e["name"] for e in ((tree or {}).get("entries") or [])]
            root_files[r] = set(names) if names else None  # None = listing not fetched
            variants[r] = [n for n in names if re.fullmatch(r"Package@swift-[0-9.]+\.swift", n)]

    # Every manifest at the ref, so dump-package picks the one the current Swift would use.
    manifests = {}
    for repo, d in raw.items():
        text = pkg_at_tag.get(repo) or (d.get("head") or {}).get("text")
        if text:
            manifests[repo] = {"Package.swift": text}
    with_variants = [r for r in repos if variants[r] and r in manifests]
    for chunk in batched(with_variants, 10):
        parts = []
        for i, r in enumerate(chunk):
            ref = tags[r] if r in pkg_at_tag else "HEAD"
            fields = " ".join(f'v{j}: object(expression: "{ref}:{n}") {{ ... on Blob {{ text }} }}'
                              for j, n in enumerate(variants[r]))
            parts.append(f'r{i}: repository(owner: "{r.split("/")[0]}", name: "{r.split("/")[1]}") {{ {fields} }}')
        data = gql("query {" + "\n".join(parts) + "}")
        for i, r in enumerate(chunk):
            for j, n in enumerate(variants[r]):
                obj = (data.get(f"r{i}") or {}).get(f"v{j}")
                if obj and obj.get("text"):
                    manifests[r][n] = obj["text"]
    dumps, mode_errors, swift_version, swift_image = dump_packages(manifests)
    refs = {r: tags[r] if r in pkg_at_tag else "HEAD" for r in manifests}
    with ThreadPoolExecutor(max_workers=4) as pool:
        swift_src = dict(zip(dumps, pool.map(lambda r: swift_files(r, refs[r], dumps[r]) if dumps[r] else None,
                                             list(dumps))))
    for r in dumps:
        if dumps[r] is not None and swift_src[r] is None:
            mode_errors[r] = "cannot list source files"

    # Issue responses: the latest issues (up to 100, not PRs) in the window, per repo with issues enabled.
    since, until = issue_window(date.today())
    open_issues = [r for r in repos if raw[r].get("hasIssuesEnabled")]
    issue_data = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for r, x in zip(open_issues, pool.map(lambda r: issue_search(r, since, until), open_issues)):
            if x is not None:
                issue_data[r] = x

    # A value that cannot be read this run keeps the last one read; *_checked says when that was.
    today = date.today().isoformat()
    try:
        old = json.loads(STATS.read_text())
    except (OSError, json.JSONDecodeError):
        old = {}
    prev = old.get("repos", {})
    lost = "Package.swift not found or not fetched"
    for r in repos:
        p = prev.get(r) or {}
        gone = root_files.get(r) is not None and "Package.swift" not in root_files[r]
        if r not in manifests and not gone and (p.get("spm") or p.get("swift_mode_error") == lost):
            # Was a Swift package and the root listing did not load: a failed fetch, not a removed file.
            # Keep the old Package.swift facts and report it.
            mode_errors[r] = lost
    old_date = old.get("refreshed")
    checked = lambda r, key: (prev.get(r) or {}).get(key, old_date if r in prev else None)

    stats = {}
    for repo, d in raw.items():
        text = pkg_at_tag.get(repo) or (d.get("head") or {}).get("text")
        tools, min_ios, ios_platform, products = parse_package(text)
        files = swift_src.get(repo)
        if dumps.get(repo) and files is not None:
            all_dirs = {d for t in dumps[repo]["targets"] for d in target_dirs(t)}
            mode, strict = swift_mode(dumps[repo], lambda t: has_swift(t, files, all_dirs))
            swift = {"swift_language_mode": mode, "strict_concurrency": strict,
                     "swift_mode_checked": today, "swift_mode_error": None}
        elif repo in mode_errors:
            p = prev.get(repo) or {}
            swift = {"swift_language_mode": p.get("swift_language_mode"),
                     "strict_concurrency": p.get("strict_concurrency"),
                     "swift_mode_checked": checked(repo, "swift_mode_checked") if p.get("swift_language_mode") else None,
                     "swift_mode_error": mode_errors[repo]}
        else:  # no Package.swift: not a Swift package, nothing to read
            swift = {"swift_language_mode": None, "strict_concurrency": None,
                     "swift_mode_checked": today, "swift_mode_error": None}
        keys = ("issues_sampled", "issues_answered", "issue_response")
        if not d.get("hasIssuesEnabled"):
            issues = {"issues_enabled": False, **dict.fromkeys(keys), "issues_checked": today, "issues_error": None}
        elif repo in issue_data:
            n, a = issue_response(issue_data[repo]["nodes"])
            issues = {"issues_enabled": True, "issues_sampled": n, "issues_answered": a,
                      "issue_response": round(a / n, 2) if n >= ISSUE_MIN else None,
                      "issues_checked": today, "issues_error": None}
        else:
            p = prev.get(repo) or {}
            issues = {"issues_enabled": True, **{k: p.get(k) for k in keys},
                      "issues_checked": checked(repo, "issues_checked") if p.get("issues_sampled") is not None else None,
                      "issues_error": "issue search failed"}
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
            "ios_platform": ios_platform if tools else None,
            "products": products,
            **swift,
            **issues,
        }
        if mode_errors.get(repo) == lost:
            for key in ("spm", "spm_version", "swift_tools", "min_ios", "ios_platform", "products", "package_swift_at"):
                stats[repo][key] = (prev.get(repo) or {}).get(key)

    tmp = STATS.with_suffix(".json.tmp")
    if not any(dumps.values()):  # Swift did not run: every mode is a kept value, so keep what produced them
        swift_version, swift_image = old.get("swift_version"), old.get("swift_image")
    tmp.write_text(json.dumps({"refreshed": today, "swift_version": swift_version, "swift_image": swift_image,
                               "issue_window": [since, until],
                               "repos": stats},
                              indent=1, sort_keys=True) + "\n")
    tmp.replace(STATS)
    print(f"refreshed {len(stats)} repos; Package.swift read at a release tag for {len(pkg_at_tag)}; "
          f"language mode read for {sum(1 for r in manifests if r not in mode_errors)} of {len(manifests)} "
          f"with Swift {swift_version}; issues read for {len(issue_data)} of {len(open_issues)}")


def check():
    """Exit 1 when stats.json needs attention: a manifest needs a newer Swift than the pinned image,
    or more than MAX_FAILURES of the repos could not be read this run. Run after the data is committed."""
    data = json.loads(STATS.read_text())
    repos = data["repos"].values()
    newer = sorted({v["swift_mode_error"] for v in repos if (v.get("swift_mode_error") or "").startswith("needs Swift")})
    spm = [v for v in repos if v.get("spm") or v.get("swift_mode_error")]
    mode_failed = sum(1 for v in spm if v.get("swift_mode_error"))
    enabled = [v for v in repos if v.get("issues_enabled")]
    issue_failed = sum(1 for v in enabled if v.get("issues_error"))
    refreshed = date.fromisoformat(data["refreshed"])
    old_values = sorted(f"{r} ({key} {v[key]})" for r, v in data["repos"].items()
                        for key in ("swift_mode_checked", "issues_checked")
                        if v.get(key) and (refreshed - date.fromisoformat(v[key])).days > MAX_STALE_DAYS)
    problems = []
    if newer:
        problems.append(f"Package.swift files need a newer Swift than {data.get('swift_image')} "
                        f"({', '.join(newer)}): merge the Dependabot PR for scripts/swift/Dockerfile, "
                        "or update its FROM line (tag and digest). If no Swift image of that version is "
                        "published yet (e.g. a beta tools version), wait for it")
    if data.get("swift_image") == "local":
        problems.append("language modes were read with the local Swift, not the pinned image; "
                        "rerun scripts/refresh.py with Docker running before committing")
    never = sorted(f"{r} ({v.get('swift_mode_error') or v.get('issues_error')})" for r, v in data["repos"].items()
                   if (v.get("swift_mode_error") and not v.get("swift_mode_checked"))
                   or (v.get("issues_error") and not v.get("issues_checked")))
    if never:
        problems.append(f"never read successfully: {', '.join(never[:20])}" + (" ..." if len(never) > 20 else ""))
    if old_values:
        problems.append(f"values not read for over {MAX_STALE_DAYS} days: {', '.join(old_values[:20])}"
                        + (" ..." if len(old_values) > 20 else ""))
    if mode_failed > MAX_FAILURES * len(spm):
        problems.append(f"language mode could not be read for {mode_failed} of {len(spm)} repos")
    if issue_failed > MAX_FAILURES * len(enabled):
        problems.append(f"issue search failed for {issue_failed} of {len(enabled)} repos")
    for p in problems:
        print(f"::error::{p}")
    print(f"check: Swift {data.get('swift_version')}; mode errors {mode_failed}/{len(spm)}; "
          f"issue errors {issue_failed}/{len(enabled)}")
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    check() if sys.argv[1:] == ["--check"] else main()
