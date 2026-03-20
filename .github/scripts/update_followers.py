import json
import urllib.request


API_URL = "https://api.github.com/users/SudoNils42/followers?per_page=12"
README_PATH = "README.md"
START = "<!-- FOLLOWERS_START -->"
END = "<!-- FOLLOWERS_END -->"


def fetch_followers():
    req = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "SudoNils42-followers-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def build_block(followers):
    parts = []
    for f in followers:
        login = f["login"]
        avatar = f["avatar_url"]
        profile = f["html_url"]
        parts.append(
            f'<a href="{profile}"><img src="{avatar}" width="56" height="56" alt="{login}" /></a>'
        )
    return "\n".join(parts)


def patch_readme(block):
    with open(README_PATH, "r", encoding="utf-8") as file:
        content = file.read()

    start_idx = content.find(START)
    end_idx = content.find(END)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise RuntimeError("followers markers not found")

    insert_start = start_idx + len(START)
    new_content = content[:insert_start] + "\n" + block + "\n" + content[end_idx:]

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(new_content)


def main():
    followers = fetch_followers()
    block = build_block(followers)
    patch_readme(block)


if __name__ == "__main__":
    main()
