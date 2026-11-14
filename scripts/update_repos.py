#!/usr/bin/env python3
"""Rewrite the repository list in profile/README.md from the org's public repos."""
import json
import os
import re
import sys
import urllib.request

README = "profile/README.md"
START, END = "<!-- REPOS:START -->", "<!-- REPOS:END -->"


def fetch_repos(org, token):
    repos, page = [], 1
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/orgs/{org}/repos?type=public&per_page=100&page={page}",
            headers={
                "Accept": "application/vnd.github+json",
                **({"Authorization": f"Bearer {token}"} if token else {}),
            },
        )
        with urllib.request.urlopen(req) as resp:
            batch = json.load(resp)
        if not batch:
            return repos
        repos += batch
        page += 1


def render(repos):
    shown = sorted(
        (r for r in repos if r["name"] != ".github" and not r["archived"] and not r["fork"]),
        key=lambda r: r["name"].lower(),
    )
    if not shown:
        return "_No public repositories yet._"
    rows = ["| Repository | Description |", "| --- | --- |"]
    for r in shown:
        desc = " ".join((r["description"] or "").split()).replace("|", "\\|")
        rows.append(f"| [{r['name']}]({r['html_url']}) | {desc} |")
    return "\n".join(rows)


def main():
    org = os.environ.get("ORG") or os.environ["GITHUB_REPOSITORY_OWNER"]
    with open(README, encoding="utf-8") as f:
        text = f.read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(text):
        sys.exit(f"Markers {START} / {END} not found in {README}")
    block = f"{START}\n{render(fetch_repos(org, os.environ.get('GITHUB_TOKEN')))}\n{END}"
    with open(README, "w", encoding="utf-8") as f:
        f.write(pattern.sub(lambda _: block, text))


if __name__ == "__main__":
    main()
