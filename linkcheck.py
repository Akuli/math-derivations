from os.path import relpath, dirname

from bs4 import BeautifulSoup


def _parse_html(path):
    with open(path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    ids = [h2["id"] for h2 in (soup.find_all("h1") + soup.find_all("h2"))]
    links = [
        a["href"]
        for a in soup.find_all("a")
        if not a["href"].startswith(("http://", "https://"))
    ]
    return ids, links


def _check_link(href, ids_by_relative_path):
    if "#" in href:
        path_part, the_id = href.split("#")
    else:
        path_part = href
        the_id = None

    if path_part not in ids_by_relative_path:
        return f"file not found: {path_part}"
    if the_id is not None and the_id not in ids_by_relative_path[path_part]:
        return f"id not found: {the_id}"
    return None


def check_links(path_pairs_as_strings):
    ids_by_path = {}
    links_by_path = {}
    for source_path, html_path in path_pairs_as_strings:
        ids, links = _parse_html(html_path)
        ids_by_path[html_path] = ids
        links_by_path[html_path] = links

    problem_list = []
    for source_path, html_path in path_pairs_as_strings:
        ids_by_relative_path = {
            relpath(p, dirname(html_path)): ids
            for p, ids in ids_by_path.items()
        }
        ids_by_relative_path[""] = ids_by_path[html_path]
        for href in links_by_path[html_path]:
            problem = _check_link(href, ids_by_relative_path)
            if problem is not None:
                with open(source_path, "r", encoding="utf-8") as file:
                    lineno = next(lineno for lineno, line in enumerate(file, start=1) if href in line)
                problem_list.append(f"{source_path}:{lineno}: {problem}")

    return problem_list
