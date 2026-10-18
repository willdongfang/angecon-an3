"""Offline AN3 checks. Read-only: Python stdlib + Node, no network or reports written."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import unquote, urlsplit


GROUPS = {"about": 5, "technology": 4, "pipeline": 5, "science": 4, "contact": 2}
IMPORTS = re.compile(r'''(?:\bfrom\s*|\bimport\s*\(\s*|\bimport\s*)["']([^"']+)["']''')
IMAGES = re.compile(r'''["']((?:\.\.?/)?assets/[^"'\s]+\.(?:png|jpe?g|svg|webp))["']''')


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self.ids = []
        self.elements = []
        self.scripts = []
        self.styles = []
        self.active = None
        self.feed(self.text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag in ("script", "style"):
            self.active = (tag, attrs, [])

    def handle_data(self, data):
        if self.active:
            self.active[2].append(data)

    def handle_endtag(self, tag):
        if self.active and self.active[0] == tag:
            _, attrs, parts = self.active
            (self.scripts if tag == "script" else self.styles).append((attrs, "".join(parts)))
            self.active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def units(page):
    match = re.search(r"\bconst\s+CONTENT_UNITS\s*=\s*", page.text)
    require(match is not None, "CONTENT_UNITS declaration missing")
    value, _ = json.JSONDecoder().raw_decode(page.text[match.end():])
    require(isinstance(value, list) and len(value) == 20, "expected 20 content units")
    require(all(isinstance(unit, dict) for unit in value), "content units must be objects")
    require(Counter(unit.get("sectionId") for unit in value) == GROUPS, "section counts differ")
    expected_ids = {f"{i}-{n}" for i, count in enumerate(GROUPS.values(), 1) for n in range(1, count + 1)}
    require({unit.get("id") for unit in value} == expected_ids, "missing/duplicate content IDs")
    for unit in value:
        require(set(("id", "sectionId", "title", "body", "sourceIds", "seed", "anchor")) <= unit.keys(), "unit fields missing")
        require(all(isinstance(unit[k], str) and unit[k].strip() for k in ("title", "body")), "empty title/body")
        require(isinstance(unit["seed"], int), "seed must be integer")
        anchor = unit["anchor"]
        require(isinstance(anchor, list) and len(anchor) == 3 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in anchor), "invalid anchor")
        require(isinstance(unit["sourceIds"], list) and bool(unit["sourceIds"]) and all(isinstance(x, str) for x in unit["sourceIds"]), "source IDs missing")
    return value


def check_project(root):
    root = root.resolve()
    results = []

    def check(name, action):
        try:
            action()
            results.append({"name": name, "status": "pass"})
        except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
            results.append({"name": name, "status": "fail", "detail": str(exc)})

    def local_target(origin, reference):
        url = urlsplit(reference)
        require(not url.scheme and not url.netloc, "external runtime resource: " + reference)
        path = unquote(url.path)
        target = (root / path.lstrip("/") if path.startswith("/") else origin.parent / path).resolve() if path else origin
        require(target == root or root in target.parents, "reference leaves project: " + reference)
        require(target.exists(), "missing resource: " + reference)
        return target, unquote(url.fragment)

    pages = []
    for relative, language, other in (("index.html", "zh-CN", "./en/"), ("en/index.html", "en", "../")):
        try:
            page = Page(root / relative)
        except (OSError, ValueError) as exc:
            results.append({"name": relative + " HTML", "status": "fail", "detail": str(exc)})
            continue
        pages.append(page)
        prefix = relative + " "

        def structure():
            require(not [key for key, count in Counter(page.ids).items() if count > 1], "duplicate HTML IDs")
            require(any(tag == "html" and attrs.get("lang") == language for tag, attrs in page.elements), "wrong html lang")
            require({"network", "info-dialog", "info-qr", "language-toggle"} <= set(page.ids), "required interaction element missing")
        check(prefix + "HTML / language / IDs", structure)
        check(prefix + "20 content units", lambda: units(page))

        def javascript():
            require(shutil.which("node") is not None, "Node.js 18+ required")
            scripts = [(attrs, body) for attrs, body in page.scripts if attrs.get("type", "") in ("", "module", "text/javascript") and "src" not in attrs]
            require(len(scripts) >= 2, "inline page scripts missing")
            for number, (attrs, body) in enumerate(scripts, 1):
                mode = "module" if attrs.get("type") == "module" else "commonjs"
                run = subprocess.run(["node", "--check", "--input-type=" + mode], input=body, text=True, encoding="utf-8", capture_output=True, timeout=20)
                require(run.returncode == 0, f"script {number}: {run.stderr[-1200:]}")
        check(prefix + "JavaScript syntax", javascript)

        def resources():
            for tag, attrs in page.elements:
                require(tag != "base", "base tag changes fragment and module resolution")
                for key in ("src", "href", "poster"):
                    if key not in attrs:
                        continue
                    ref = attrs[key]
                    parsed = urlsplit(ref)
                    if parsed.scheme == "data":
                        continue
                    if tag == "a" and (parsed.scheme in ("mailto", "https", "http", "tel") or parsed.netloc):
                        continue
                    target, fragment = local_target(page.path, ref)
                    if target.is_dir():
                        target = target / "index.html"
                        require(target.is_file(), "missing route index: " + ref)
                    if fragment:
                        require(fragment in Page(target).ids, "missing anchor: " + ref)
            css_refs = re.findall(r"url\(\s*['\"]?([^'\"\s)]+)", "\n".join(body for _, body in page.styles))
            for ref in [*IMAGES.findall(page.text), *css_refs]:
                if not ref.startswith("data:"):
                    target, _ = local_target(page.path, ref)
                    require(target.is_file(), "asset is not a file: " + ref)
            for name in ("qr-angecon.jpg", "qr-anku.png"):
                require(name in page.text and (root / "assets" / name).is_file(), "QR asset missing: " + name)

            maps = [json.loads(body).get("imports", {}) for attrs, body in page.scripts if attrs.get("type") == "importmap"]
            require(len(maps) == 1 and "three" in maps[0], "Three.js import map missing")
            imports = maps[0]
            for ref in imports.values():
                local_target(page.path, ref)
            visited = set()

            def inspect_imports(origin, source):
                for specifier in IMPORTS.findall(source):
                    if specifier.startswith((".", "/")) or urlsplit(specifier).scheme:
                        target, _ = local_target(origin, specifier)
                    else:
                        keys = sorted((k for k in imports if k == specifier or k.endswith("/") and specifier.startswith(k)), key=len, reverse=True)
                        require(bool(keys), "unmapped module: " + specifier)
                        key = keys[0]
                        target, _ = local_target(page.path, imports[key] + specifier[len(key):])
                    require(target.is_file(), "module is not a file: " + specifier)
                    if target not in visited:
                        visited.add(target)
                        inspect_imports(target, target.read_text(encoding="utf-8"))
            for attrs, body in page.scripts:
                if attrs.get("type") != "importmap":
                    inspect_imports(page.path, body)
        check(prefix + "local resources / imports / anchors", resources)

        def navigation():
            require(re.search(r"location\.href\s*=\s*['\"]" + re.escape(other) + r"['\"]", page.text) is not None, "wrong language switch target")
            target, _ = local_target(page.path, other)
            require((target / "index.html").is_file(), "language destination missing")
            alternates = {attrs.get("hreflang"): attrs.get("href") for tag, attrs in page.elements if tag == "link" and attrs.get("rel") == "alternate"}
            require(set(alternates) == {"zh-Hans", "en"}, "hreflang pair missing")
            for lang, expected in (("zh-Hans", root / "index.html"), ("en", root / "en" / "index.html")):
                target, _ = local_target(page.path, alternates[lang])
                require((target / "index.html" if target.is_dir() else target) == expected, "wrong hreflang destination")
            require(any(tag == "a" and attrs.get("href") == "mailto:bd@angecon.com" for tag, attrs in page.elements), "contact mail link missing")
        check(prefix + "language routes / hreflang / contact", navigation)

    if len(pages) == 2:
        def bilingual():
            zh, en = (sorted(units(page), key=lambda unit: unit["id"]) for page in pages)
            for left, right in zip(zh, en):
                require(left.keys() == right.keys(), "unit field sets differ: " + left["id"])
                for key in ("id", "sectionId", "seed", "anchor", "sourceIds"):
                    require(left[key] == right[key], f"bilingual {left['id']} {key} differs")
            require(pages[0].styles == pages[1].styles, "bilingual CSS differs")
            require(Counter(tag for tag, _ in pages[0].elements) == Counter(tag for tag, _ in pages[1].elements), "bilingual tag counts differ")
        check("bilingual data / styles / structure", bilingual)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", help="print JSON to stdout; no report file is written")
    args = parser.parse_args()
    results = check_project(args.root)
    passed = sum(item["status"] == "pass" for item in results)
    if args.json:
        print(json.dumps({"passed": passed, "total": len(results), "checks": results}, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(f"{item['status'].upper()}: {item['name']}" + (": " + item["detail"] if "detail" in item else ""))
        print(f"{passed}/{len(results)} static checks passed. Browser/translation/GPU checks are separate.")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
