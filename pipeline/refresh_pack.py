"""Rebuild the client pack's working version (and reports/<slug>/current.html) from the current
database, intake answers and wiki research. Use after editing research or other wiki sources.

    uv run python -m pipeline.refresh_pack [slug]"""
import sys

from .config import CLIENT_SLUG
from . import report, wiki_render
from .db import client_by_slug, connect, user_id


def run(slug: str = CLIENT_SLUG):
    with connect() as conn:
        cid = client_by_slug(conn, slug)["id"]
        v = report.refresh_working(conn, cid, user_id(conn, "Pipeline (AI)"), edited=False)
    wiki_render.log(f"report | {slug} — v{v['version_no']} refreshed from wiki + intake")
    print(f"refreshed v{v['version_no']} ({v['state']}) -> reports/{slug}/current.html")


if __name__ == "__main__":
    run(*sys.argv[1:2])
