"""
Export Chrome bookmarks to markdown
"""

import json
import sys


def get_folder(folder, inc):
    if isinstance(folder, dict):
        if "children" in folder:
            inc += 1
            print(f"{'#' * inc} {folder['name']}")
            get_folder(folder["children"], inc)
        if "url" in folder:
            print(f"* [{folder['name']}]({folder['url']})")
    if isinstance(folder, list):
        for key in folder:
            get_folder(key, inc)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <chrome-profile-path>")
        sys.exit(1)

    chrome_profile_path = sys.argv[1]
    chrome_bookmark_file = f"{chrome_profile_path}/Bookmarks"
    with open(chrome_bookmark_file) as file:
        bookmarks = json.load(file)["roots"]

    print("# Bookmarks")
    get_folder(bookmarks["bookmark_bar"], 1)
    get_folder(bookmarks["other"], 1)


if __name__ == "__main__":
    main()
