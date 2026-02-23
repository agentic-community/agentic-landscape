#!/usr/bin/env python3
"""Validate data.yml entries: check URLs are reachable, don't redirect to a different host,
and that extra.summary_tags exists with a valid value.

When --base is provided, URL checks are scoped to only new or changed items.
Tag/schema checks always run on the full file."""

import argparse
import sys
import yaml
import urllib.request
import urllib.error
from urllib.parse import urlparse
import ssl
import os

VALID_TAGS = {"Open Source", "Open Core", "Commercial"}
TIMEOUT = 15


def parse_items(path):
    """Parse data.yml and return a dict keyed by item name with all item fields."""
    with open(path) as f:
        data = yaml.safe_load(f)

    items = {}
    for cat in data.get("categories", []):
        for sub in cat.get("subcategories", []):
            for item in sub.get("items", []):
                key = item["name"]
                items[key] = {
                    "cat": cat["name"],
                    "sub": sub["name"],
                    **item,
                }
    return items


def diff_items(base_path, head_path):
    """Return the set of item names that are new or changed between base and head."""
    base = parse_items(base_path)
    head = parse_items(head_path)

    changed = set()
    for name, item in head.items():
        if name not in base:
            changed.add(name)
        else:
            # Check if any URL fields changed
            for field in ("homepage_url", "repo_url"):
                if item.get(field) != base[name].get(field):
                    changed.add(name)
    return changed


def check_url(url):
    """Check that a URL is reachable and doesn't redirect to a different host.
    Returns (ok, message)."""
    parsed = urlparse(url)
    original_host = parsed.hostname

    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "agentic-landscape-validator/1.0"})
        resp = urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx)
        final_url = resp.geturl()
        final_host = urlparse(final_url).hostname

        # Same-host redirects are fine (e.g. /path -> /path/), only flag cross-host redirects
        if original_host != final_host:
            return False, f"redirects to different host: {original_host} -> {final_host} ({final_url})"
        return True, "ok"

    except urllib.error.HTTPError as e:
        # 3xx redirects: urllib doesn't always follow them on HEAD requests.
        # Check the Location header — same-host redirects are fine.
        if e.code in (301, 302, 307, 308):
            location = e.headers.get("Location", "")
            if location:
                redirect_host = urlparse(location).hostname
                # Relative redirects or same-host redirects are fine
                if redirect_host is None or redirect_host == original_host:
                    return True, "ok"
                return False, f"redirects to different host: {original_host} -> {redirect_host} ({location})"
            return True, "ok"
        # Some servers reject HEAD, retry with GET
        if e.code in (405, 403):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "agentic-landscape-validator/1.0"})
                resp = urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx)
                final_url = resp.geturl()
                final_host = urlparse(final_url).hostname
                if original_host != final_host:
                    return False, f"redirects to different host: {original_host} -> {final_host} ({final_url})"
                return True, "ok"
            except Exception as e2:
                return False, f"HTTP error: {e2}"
        return False, f"HTTP {e.code}"

    except Exception as e:
        return False, str(e)


def validate(path, check_urls=True, only_items=None):
    """Validate all items in data.yml.

    Args:
        path: Path to data.yml
        check_urls: Whether to check URLs at all
        only_items: If set, only URL-check items whose name is in this set.
                    Tag/schema checks always run on all items.
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    errors = []

    for cat in data.get("categories", []):
        cat_name = cat["name"]
        for sub in cat.get("subcategories", []):
            sub_name = sub["name"]
            for item in sub.get("items", []):
                name = item["name"]
                prefix = f"{cat_name} > {sub_name} > {name}"

                # Tag checks always run on all items
                extra = item.get("extra", {})
                tag = extra.get("summary_tags")
                if not tag:
                    errors.append(f"{prefix}: missing extra.summary_tags")
                elif tag not in VALID_TAGS:
                    errors.append(f"{prefix}: invalid summary_tags '{tag}' (must be one of: {', '.join(sorted(VALID_TAGS))})")

                # URL checks scoped to changed items when only_items is set
                if check_urls and (only_items is None or name in only_items):
                    for field in ("homepage_url", "repo_url"):
                        url = item.get(field)
                        if not url:
                            if field == "homepage_url":
                                errors.append(f"{prefix}: missing {field}")
                            continue
                        ok, msg = check_url(url)
                        if not ok:
                            errors.append(f"{prefix}: {field} ({url}) — {msg}")

    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate data.yml")
    parser.add_argument("path", nargs="?", default="agentic-landscape/data.yml", help="Path to data.yml")
    parser.add_argument("--base", help="Base version of data.yml to diff against (only URL-check new/changed items)")
    args = parser.parse_args()

    skip_urls = os.environ.get("SKIP_URL_CHECKS", "").lower() in ("1", "true", "yes")
    check_urls = not skip_urls

    only_items = None
    if check_urls and args.base:
        only_items = diff_items(args.base, args.path)
        if only_items:
            print(f"URL-checking {len(only_items)} new/changed item(s): {', '.join(sorted(only_items))}")
        else:
            print("No new or changed items — skipping URL checks.")
            check_urls = False

    if check_urls and not args.base:
        print("Validating data.yml (full URL checks)...")
    elif not check_urls:
        print("Validating data.yml (tags/schema only)...")

    errors = validate(args.path, check_urls=check_urls, only_items=only_items)

    for e in errors:
        print(f"  ERROR: {e}")

    if errors:
        print(f"\n{len(errors)} error(s) found.")
        sys.exit(1)
    else:
        print("All checks passed.")
        sys.exit(0)
