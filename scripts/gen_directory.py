"""Generate the data-driven directory pages at build time.

Reads the compiled records from the Zeitdex resources repo (``entities.json``)
and writes:

* ``find-a-specialist.md`` — the specialist / physician directory
* ``create/software.md``   — the sleep-tracking software directory

This keeps both pages data-driven: add or correct an entry in
https://github.com/zeitdex/resources and the pages regenerate on the next build.

Data source order:
1. ``resources-src/entities.json`` if a local checkout is present (CI), else
2. fetched from the resources repo's ``built`` branch (also works locally).
"""

import json
import os
import re
import urllib.request

import mkdocs_gen_files

LOCAL = "resources-src/entities.json"
RAW_URL = "https://raw.githubusercontent.com/zeitdex/resources/built/entities.json"

PLATFORM_ICONS = {
    "watch": ":material-watch:",
    "website": ":material-web:",
    "web": ":material-web:",
    "ios": ":material-apple:",
    "macos": ":material-apple:",
    "mac": ":material-apple:",
    "android": ":material-android:",
    "windows": ":material-microsoft-windows:",
    "linux": ":material-linux:",
}
TYPE_ICONS = {"physician": ":material-stethoscope:", "researcher": ":material-school:"}


def load_data():
    try:
        if os.path.exists(LOCAL):
            with open(LOCAL, encoding="utf-8") as handle:
                return json.load(handle)
        with urllib.request.urlopen(RAW_URL, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError) as exc:
        print(f"gen_directory: could not load resources data ({exc})")
        return {}


def name_of(rec):
    name = rec.get("name")
    if isinstance(name, dict):
        return name.get("value") or "Unnamed"
    return name or "Unnamed"


def tel_href(tel):
    return "tel:" + re.sub(r"[^0-9+]", "", tel)


def clean_address(address):
    parts = [p.strip().rstrip(",").strip() for p in (address or "").split("\n")]
    return ", ".join(p for p in parts if p)


def render_specialist(rec):
    lines = [f"## {name_of(rec)}", ""]

    stype = rec.get("specialist_type")
    if stype:
        icon = TYPE_ICONS.get(stype, ":material-account:")
        lines += [f"{icon} **{stype.capitalize()}**", ""]
    if (rec.get("description") or "").strip():
        lines += [rec["description"].strip(), ""]

    links = []
    if rec.get("url"):
        links.append(f"[:material-web: Website]({rec['url']})")
    if rec.get("booking_url"):
        links.append(f"[:material-calendar-check: Book an appointment]({rec['booking_url']})")
    if rec.get("registration_url"):
        links.append(f"[:material-clipboard-account: Register]({rec['registration_url']})")
    if links:
        lines += [" · ".join(links), ""]

    for loc in rec.get("locations") or []:
        title = loc.get("name") or "Location"
        lines.append(f'??? note ":material-map-marker: {title}"')
        addr = clean_address(loc.get("address"))
        if addr:
            lines.append(f"    {addr}")
            lines.append("")
        if loc.get("tel"):
            lines.append(f"    :material-phone: [{loc['tel']}]({tel_href(loc['tel'])})")
            lines.append("")

    forms = [f for f in (rec.get("forms") or []) if f.get("url")]
    if forms:
        lines += ["**Sleep diary templates**", ""]
        for form in forms:
            label = form.get("short_name") or form.get("name") or "Sleep diary"
            lines.append(f"- :material-file-document-outline: [{label}]({form['url']})")
        lines.append("")

    return lines


def render_software(rec):
    lines = [f"## {name_of(rec)}", ""]

    if (rec.get("business_model") or "").strip():
        lines += [f"*{rec['business_model'].strip()}*", ""]
    if (rec.get("description") or "").strip():
        lines += [rec["description"].strip(), ""]

    platforms = rec.get("platforms") or []
    if platforms:
        badges = [f"{PLATFORM_ICONS.get(p.lower(), ':material-cellphone:')} {p}" for p in platforms]
        lines += ["**Platforms:** " + " · ".join(badges), ""]

    if rec.get("url"):
        lines += [f"[:material-web: Website]({rec['url']})", ""]

    procedure = (rec.get("procedure") or "").strip()
    if procedure:
        lines.append('??? note "How to get started"')
        for pline in procedure.split("\n"):
            lines.append(f"    {pline}" if pline.strip() else "")
        lines.append("")

    return lines


def write_page(out, title, intro_lines, records, render):
    records = sorted(records, key=lambda r: name_of(r).lower())
    lines = [f"# {title}", ""] + intro_lines + [""]
    if not records:
        lines += ["_This directory could not be loaded for this build._", ""]
    for rec in records:
        lines += render(rec)
    with mkdocs_gen_files.open(out, "w") as handle:
        handle.write("\n".join(lines))


def main():
    data = load_data()

    write_page(
        "find-a-specialist.md",
        "Find a specialist",
        [
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
        ],
        (data.get("specialist") or {}).get("records") or [],
        render_specialist,
    )

    write_page(
        "create/software.md",
        "Sleep-tracking software",
        [
            "Apps and devices that can record a sleep diary. This directory is "
            "generated from community-maintained data in "
            "[zeitdex/resources](https://github.com/zeitdex/resources) — "
            "[add or correct an entry]"
            "(https://github.com/zeitdex/resources/issues/new/choose). Many of these "
            "export files that [the Zeitlog dashboard](https://zeitlog.github.io/) can "
            "import — see [supported formats](formats.md).",
        ],
        (data.get("software") or {}).get("records") or [],
        render_software,
    )


main()
