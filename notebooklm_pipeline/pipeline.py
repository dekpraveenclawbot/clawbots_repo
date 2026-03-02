#!/usr/bin/env python3
import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

from notebooklm_client import NotebookLMClient

ARXIV_API = "https://export.arxiv.org/api/query"

KEYWORDS = {
    "humanoid": ["humanoid", "biped", "whole-body", "legged", "anthropomorphic"],
    "video_models": ["video model", "vision-language-action", "vla", "world model", "video prediction"],
    "simulation": ["simulation", "sim2real", "sim-to-real", "simulator", "mujoco", "isaac"],
    "robotic_arms": ["robot arm", "manipulation", "grasp", "pick-and-place", "dexterous"],
    "autonomous_driving": ["autonomous driving", "self-driving", "vehicle", "driving dataset", "adas"],
}


def fetch_recent_csro(max_results=100):
    params = {
        "search_query": "cat:cs.RO",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    r = requests.get(ARXIV_API, params=params, timeout=60)
    r.raise_for_status()
    return r.text


def parse_atom(xml_text):
    entries = re.findall(r"<entry>(.*?)</entry>", xml_text, re.S)
    papers = []
    for e in entries:
        aid = re.search(r"<id>https?://arxiv.org/abs/([^<]+)</id>", e)
        title = re.search(r"<title>(.*?)</title>", e, re.S)
        summary = re.search(r"<summary>(.*?)</summary>", e, re.S)
        if not aid or not title:
            continue
        papers.append(
            {
                "id": aid.group(1).strip(),
                "title": " ".join(title.group(1).split()),
                "summary": " ".join((summary.group(1) if summary else "").split()),
                "abs_url": f"https://arxiv.org/abs/{aid.group(1).strip()}",
                "pdf_url": f"https://arxiv.org/pdf/{aid.group(1).strip()}.pdf",
            }
        )
    return papers


def tag_and_score(paper):
    txt = (paper["title"] + " " + paper["summary"]).lower()
    tags = []
    score = 0
    for tag, keys in KEYWORDS.items():
        if any(k in txt for k in keys):
            tags.append(tag)
            score += 1
    return tags, score


def filter_papers(papers, max_papers=5):
    selected = []
    for p in papers:
        tags, score = tag_and_score(p)
        if score > 0:
            p["tags"] = tags
            p["score"] = score
            selected.append(p)
    selected.sort(key=lambda x: (x["score"], x["id"]), reverse=True)
    return selected[:max_papers]


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def main():
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--max-papers", type=int, default=int(os.getenv("MAX_PAPERS", "5")))
    ap.add_argument("--dry-run", action="store_true", default=os.getenv("DRY_RUN", "true").lower() == "true")
    args = ap.parse_args()

    output_dir = os.getenv("OUTPUT_DIR", "./out")
    ensure_dir(output_dir)

    raw = fetch_recent_csro(100)
    papers = parse_atom(raw)
    selected = filter_papers(papers, args.max_papers)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = Path(output_dir) / f"selected_{ts}.json"
    md_path = Path(output_dir) / f"selected_{ts}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(selected, f, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Daily Robotics Selection ({datetime.now(timezone.utc).isoformat()} UTC)\n\n")
        if not selected:
            f.write("No matches found today.\n")
        for i, p in enumerate(selected, 1):
            f.write(f"## {i}. {p['title']}\n")
            f.write(f"- Tags: {', '.join(p['tags'])}\n")
            f.write(f"- Abs: {p['abs_url']}\n")
            f.write(f"- PDF: {p['pdf_url']}\n\n")

    print(f"Selected {len(selected)} papers")
    print(f"Report: {md_path}")

    if args.dry_run:
        print("DRY RUN enabled; skipping NotebookLM API calls.")
        return

    project_number = os.getenv("GOOGLE_PROJECT_NUMBER", "").strip()
    notebook_id = os.getenv("NOTEBOOKLM_NOTEBOOK_ID", "").strip()
    notebook_title = os.getenv("NOTEBOOKLM_NOTEBOOK_TITLE", "Praveen Daily Robotics Podcast").strip()
    location = os.getenv("NOTEBOOKLM_LOCATION", "global").strip()
    episode_focus = os.getenv("NOTEBOOKLM_EPISODE_FOCUS", "Daily robotics podcast")

    if not project_number:
        raise SystemExit("Missing GOOGLE_PROJECT_NUMBER in .env")

    client = NotebookLMClient(project_number=project_number, location=location)

    if not notebook_id:
        nresp = client.create_notebook(title=notebook_title)
        if not nresp.ok:
            raise SystemExit(f"Notebook creation failed: {nresp.status_code} {nresp.text[:400]}")
        ndata = nresp.json()
        # May be direct notebook resource or operation wrapper.
        notebook_name = ndata.get("name", "")
        if "/operations/" in notebook_name:
            notebook_name = (
                ndata.get("response", {})
                .get("notebook", {})
                .get("name", "")
            )
        notebook_id = notebook_name.split("/")[-1] if notebook_name and "/notebooks/" in notebook_name else ""
        if not notebook_id:
            raise SystemExit(f"Notebook created but ID not found in response: {ndata}")
        print(f"Auto-created notebook: {notebook_id}")
        print("Tip: save this in .env as NOTEBOOKLM_NOTEBOOK_ID for reuse.")

    source_ids = []
    for p in selected:
        resp = client.add_source_url(notebook_id, p["abs_url"])
        if resp.ok:
            data = resp.json()
            sid = data.get("source", {}).get("name", "").split("/")[-1]
            if sid:
                source_ids.append(sid)
        else:
            print(f"WARN: source add failed for {p['id']}: {resp.status_code} {resp.text[:200]}")

    aresp = client.create_audio_overview(
        notebook_id=notebook_id,
        source_ids=source_ids or None,
        episode_focus=episode_focus,
        language_code="en-US",
    )
    print("Audio overview create status:", aresp.status_code)
    print(aresp.text[:500])


if __name__ == "__main__":
    main()
