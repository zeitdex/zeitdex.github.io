"""Generate the "Find a specialist" directory page at build time.

Reads the compiled specialist records from the Zeitdex resources repo
(``entities.json``) and writes a Markdown directory. This keeps the page
data-driven: add or correct an entry in https://github.com/zeitdex/resources
and the directory regenerates on the next build of this site.

Data source order:
1. ``resources-src/entities.json`` if a local checkout is present (CI), else
2. fetched from the raw GitHub copy (also works for local ``mkdocs serve``).
"""

import json
import os
import re
import urllib.request

import mkdocs_gen_files

# entities.json is generated (gitignored on main) and published on the
# resources repo's "built" branch. CI checks that out to resources-src/.
LOCAL = "resources-src/entities.json"
RAW_URL = "https://raw.githubusercontent.com/zeitdex/resources/built/entities.json"
OUT = "find-a-specialist.md"


def load_records():
    try:
        if os.path.exists(LOCAL):
            with open(LOCAL, encoding="utf-8") as handle:
                data = json.load(handle)
        else:
            with urllib.request.urlopen(RAW_URL, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as exc:
        # No data checkout (e.g. offline local preview): degrade gracefully.
        print(f"gen_directory: could not load specialist data ({exc})")
        return []
    return data.get("specialist", {}).get("records", [])


def tel_href(tel):
    return "tel:" + re.sub(r"[^0-9+]", "", tel)


def render(rec):
    name = (rec.get("name") or {}).get("value") or "Unnamed"
    lines = [f"## {name}", ""]

    meta = []
    if rec.get("specialist_type"):
        meta.append(str(rec["specialist_type"]).capitalize())
    if (rec.get("description") or "").strip():
        meta.append(rec["description"].strip())
    if meta:
        lines += [" — ".join(meta), ""]

    links = []
    if rec.get("url"):
        links.append(f"[Website]({rec['url']})")
    if rec.get("booking_url"):
        links.append(f"[Book an appointment]({rec['booking_url']})")
    if rec.get("registration_url"):
        links.append(f"[Register as a patient]({rec['registration_url']})")
    if links:
        lines += [" · ".join(links), ""]

    for loc in rec.get("locations") or []:
        bits = []
        if loc.get("name"):
            bits.append(f"**{loc['name']}**")
        addr_parts = [p.strip().rstrip(",").strip() for p in (loc.get("address") or "").split("\n")]
        addr = ", ".join(p for p in addr_parts if p)
        if addr:
            bits.append(addr)
        if loc.get("tel"):
            bits.append(f"Phone: [{loc['tel']}]({tel_href(loc['tel'])})")
        if bits:
            lines += ["*Location:* " + " — ".join(bits), ""]

    forms = [f for f in (rec.get("forms") or []) if f.get("url")]
    if forms:
        lines += ["**Sleep diary templates:**", ""]
        for form in forms:
            label = form.get("short_name") or form.get("name") or "Sleep diary"
            lines.append(f"- [{label}]({form['url']})")
        lines.append("")

    return lines


def main():
    records = load_records()
    records.sort(key=lambda r: ((r.get("name") or {}).get("value") or "").lower())

    lines = [
        "# Find a specialist",
        "",
        "Sleep specialists and clinics that publish sleep-diary resources. This "
        "directory is generated from community-maintained data in "
        "[zeitdex/resources](https://github.com/zeitdex/resources) — "
        "[add or correct an entry]"
        "(https://github.com/zeitdex/resources/issues/new/choose).",
        "",
        '!!! warning "Not medical advice"',
        "    A listing here is not an endorsement or a recommendation. Always "
        "consult a qualified clinician about your own care.",
        "",
        "See also the [Circadian Sleep Disorders Network's list of doctors]"
        "(https://www.circadiansleepdisorders.org/doctors.php), which includes "
        "many specialists not yet listed here.",
        "",
    ]
    if not records:
        lines += ["_The specialist directory could not be loaded for this build._", ""]
    for rec in records:
        lines += render(rec)

    with mkdocs_gen_files.open(OUT, "w") as handle:
        handle.write("\n".join(lines))


main()
