# Versioning + databases vs data sources

## Versioning
- Every REST request MUST include `Notion-Version: <date>` (e.g. `2025-09-03`).
- Pin a version in your integration (env var: `NOTION_VERSION`) to avoid accidental breakage.

## Data model (2025-09-03+)
- A **database** is a container that can hold one or more **data sources**.
- A **data source** is what you traditionally think of as the “table”: it defines properties (columns) and contains pages (rows).
- A **page** can be:
  - a standalone page under another page, OR
  - a data source row (database item)

## Practical implications
1) To query “rows in a database”, you must query the **data source**:
   - `POST /data_sources/{data_source_id}/query`

2) If all you have is a `database_id`, discover its `data_source_id` first:
   - `GET /databases/{database_id}`
   - choose one entry from `data_sources[]`

3) Moving a page into a database requires a **data_source_id**:
   - `POST /pages/{page_id}/move` with `parent.type=data_source_id`

4) Creating a page:
   - Child of a page: `parent.type=page_id`
   - Row in a data source: `parent.type=data_source_id`

## “Not found” that isn’t actually not found
A 404 `object_not_found` often means:
- the page/database exists, but
- it is NOT shared/connected to the integration

Fix: Share the page/database with the integration via Notion UI “Connections”.
