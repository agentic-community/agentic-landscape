#!/usr/bin/env python3
"""Validate that items within each subcategory in data.yml are alphabetically sorted by name."""

import sys
import yaml


def check_sort_order(path):
    with open(path) as f:
        data = yaml.safe_load(f)

    errors = []

    for category in data.get("categories", []):
        cat_name = category["name"]
        for subcategory in category.get("subcategories", []):
            sub_name = subcategory["name"]
            items = subcategory.get("items", [])
            names = [item["name"] for item in items]
            sorted_names = sorted(names, key=str.casefold)

            if names != sorted_names:
                errors.append(f"  {cat_name} > {sub_name}")
                for actual, expected in zip(names, sorted_names):
                    if actual != expected:
                        errors.append(f"    found '{actual}', expected '{expected}'")
                        break

    if errors:
        print("Items are not in alphabetical order:")
        print("\n".join(errors))
        print("\nRun .github/scripts/sort-data.py to fix automatically.")
        return 1

    print("All items are in alphabetical order.")
    return 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "agentic-landscape/data.yml"
    sys.exit(check_sort_order(path))
