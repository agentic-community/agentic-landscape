#!/usr/bin/env python3
"""Sort items within each subcategory in data.yml alphabetically by name."""

import sys
import yaml


class IndentDumper(yaml.Dumper):
    """Custom dumper that indents list items properly."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def str_representer(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    if any(c in data for c in ":#{}[]&*?|->!%@`,"):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


IndentDumper.add_representer(str, str_representer)


def sort_data(path):
    with open(path) as f:
        data = yaml.safe_load(f)

    changed = False
    for category in data.get("categories", []):
        for subcategory in category.get("subcategories", []):
            items = subcategory.get("items", [])
            sorted_items = sorted(items, key=lambda x: x["name"].casefold())
            if items != sorted_items:
                subcategory["items"] = sorted_items
                changed = True
                print(f"  Sorted: {category['name']} > {subcategory['name']}")

    if changed:
        with open(path, "w") as f:
            yaml.dump(data, f, Dumper=IndentDumper, default_flow_style=False,
                      sort_keys=False, allow_unicode=True, width=120)
        print(f"\nSorted and wrote {path}")
    else:
        print("Already sorted, no changes needed.")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "agentic-landscape/data.yml"
    sort_data(path)
