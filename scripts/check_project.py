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


GROUP_IDS = {
    "about": ["1-1", "1-2", "1-3", "1-4", "1-5"],
    "technology": ["2-1", "2-3", "2-2"],
    "pipeline": ["3-1", "3-2"],
    "science": ["4-1"],
    "contact": ["5-1", "5-2"],
}
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
    groups = dict(GROUP_IDS)
    if page.path.parent.name == "en":
        groups["about"] = ["1-1", "1-3", "1-5"]
    expected_ids = [unit_id for ids in groups.values() for unit_id in ids]
    require(isinstance(value, list) and len(value) == len(expected_ids), f"expected {len(expected_ids)} content units")
    require(all(isinstance(unit, dict) for unit in value), "content units must be objects")
    require(Counter(unit.get("sectionId") for unit in value) == {section: len(ids) for section, ids in groups.items()}, "section counts differ")
    require([unit.get("id") for unit in value] == expected_ids, "content IDs or order differ")
    for section, ids in groups.items():
        require([unit.get("id") for unit in value if unit.get("sectionId") == section] == ids, "section membership differs: " + section)
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
        check(prefix + "content units", lambda: units(page))

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
            if language == "en":
                require('<a id="info-publications" href="mailto:bd@angecon.com">For more details, please contact us: bd@angecon.com</a>' in page.text, "English contact mail link missing")
            else:
                require('<span id="info-publications">查阅更多见公众号</span>' in page.text, "Chinese publication text missing")
        check(prefix + "language routes / hreflang / contact", navigation)

    if len(pages) == 2:
        def bilingual():
            zh, en = ({unit["id"]: unit for unit in units(page)} for page in pages)
            for unit_id, right in en.items():
                left = zh[unit_id]
                require(left.keys() == right.keys(), "unit field sets differ: " + left["id"])
                for key in ("id", "sectionId", "seed", "anchor", "sourceIds"):
                    if unit_id == "1-1" and key == "sourceIds":
                        expected = list(dict.fromkeys(source for old_id in ("1-1", "1-2", "1-4") for source in zh[old_id][key]))
                        require(right[key] == expected, "Company Profile merged source IDs differ")
                        continue
                    require(left[key] == right[key], f"bilingual {left['id']} {key} differs")
            profile = en["1-1"]["body"]
            require("Milestones\n" in profile and "China's first qualified biobank certificate" in profile, "Company Profile milestones missing")
            require("MF 31537" in en["1-5"]["body"], "Anku Biomed DMF number missing")
            for unit in en.values():
                require(not re.search(r"[\u4e00-\u9fff]", unit["body"]), "Chinese text in English body: " + unit["id"])
            require(not any(term in profile for term in ("High-Tech Enterprise", "Certifications & honors", "Postdoctoral")), "Retired local credentials in Company Profile")
            require(pages[0].styles == pages[1].styles, "bilingual CSS differs")
            zh_tags = Counter(tag for tag, _ in pages[0].elements)
            en_tags = Counter(tag for tag, _ in pages[1].elements)
            # Chinese publication hint is plain text; English keeps its mail link.
            zh_tags.subtract({"span": 1})
            en_tags.subtract({"a": 1})
            require(zh_tags == en_tags, "bilingual tag counts differ")
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
