# Contributing

Zeitdex is built from Markdown files plus a community-maintained data backend, and **anyone can contribute** — no setup required for most edits.

## Edit a page

=== "In the browser (easiest)"

    1. Open the page you want to improve.
    2. Click the **edit** (:material-pencil:) icon at the top right.
    3. Make your change — GitHub forks the repo and opens a **pull request** for you.

=== "Locally"

    ```bash
    git clone https://github.com/zeitdex/zeitdex.github.io
    cd zeitdex.github.io
    pip install -r requirements.txt
    mkdocs serve   # preview at http://127.0.0.1:8000
    ```

    Add or edit pages under `docs/`, and update `nav:` in `mkdocs.yml` if you add a page.

## Add a specialist or software entry

The [specialist directory](find-a-specialist.md) and [software directory](create/software.md) are generated from data in **[zeitdex/resources](https://github.com/zeitdex/resources)** — add an entry there (via its issue template or a JSON file) and the page regenerates automatically on the next build.

[:material-database-plus: Add a resource entry](https://github.com/zeitdex/resources/issues/new/choose){ .md-button }

## What we're looking for

- Clear, plain-language explanations of circadian concepts and disorders.
- Practical tracking and self-management tips (marked as lived experience where relevant).
- Accurate links to reputable organisations, research, and communities.

!!! warning "Ground rules"
    - **Not medical advice.** Frame clinical topics carefully and cite sources; don't present personal anecdotes as universal medical guidance.
    - Be accurate, and cite authoritative sources where you can.
    - Be respectful — many readers are managing difficult conditions.
