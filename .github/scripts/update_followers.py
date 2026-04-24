import json
import os
import urllib.request


GRAPHQL_URL = "https://api.github.com/graphql"
LOGIN = "SudoNils42"
COUNT = 12
ROW_SIZE = 6
AVATAR_SIZE = 64
README_PATH = "README.md"
START = "<!-- FOLLOWERS_START -->"
END = "<!-- FOLLOWERS_END -->"

QUERY = """
query($login: String!, $count: Int!) {
  user(login: $login) {
    followers(first: $count) {
      nodes {
        login
        avatarUrl
        url
      }
    }
  }
}
"""


def fetch_followers():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required")

    body = json.dumps(
        {
            "query": QUERY,
            "variables": {"login": LOGIN, "count": COUNT},
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "SudoNils42-followers-updater",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if payload.get("errors"):
        raise RuntimeError(json.dumps(payload["errors"]))

    user = payload.get("data", {}).get("user")
    if not user:
        raise RuntimeError("user not found")

    nodes = user["followers"]["nodes"] or []
    out = []
    for n in nodes:
        out.append(
            {
                "login": n["login"],
                "avatar_url": n["avatarUrl"],
                "html_url": n["url"],
            }
        )
    return out


def build_cell(follower):
    login = follower["login"]
    avatar = follower["avatar_url"]
    profile = follower["html_url"]
    src = f'{avatar}&s={AVATAR_SIZE * 2}'
    return (
        f'<td align="center" width="{AVATAR_SIZE + 8}" height="{AVATAR_SIZE + 8}">'
        f'<a href="{profile}">'
        f'<img src="{src}" width="{AVATAR_SIZE}" height="{AVATAR_SIZE}" alt="{login}" />'
        f'</a></td>'
    )


def build_row(chunk):
    cells = "".join(build_cell(f) for f in chunk)
    return f'<tr>{cells}</tr>'


def build_block(followers):
    rows = [
        build_row(followers[i:i + ROW_SIZE])
        for i in range(0, len(followers), ROW_SIZE)
    ]
    return (
        f'<table align="center" cellpadding="2" cellspacing="0" border="0">'
        f'{"".join(rows)}'
        f'</table>'
    )


def patch_readme(block):
    with open(README_PATH, "r", encoding="utf-8") as file:
        content = file.read()

    start_idx = content.find(START)
    end_idx = content.find(END)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise RuntimeError("followers markers not found")

    insert_start = start_idx + len(START)
    new_content = content[:insert_start] + block + content[end_idx:]

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(new_content)


def main():
    followers = fetch_followers()
    block = build_block(followers)
    patch_readme(block)


if __name__ == "__main__":
    main()
