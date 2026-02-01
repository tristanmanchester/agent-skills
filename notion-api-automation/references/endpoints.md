# Notion API endpoints (practical map)

Base URL: `https://api.notion.com/v1`

Headers (always):
- `Authorization: Bearer <token>`
- `Notion-Version: 2025-09-03`
- `Content-Type: application/json` (POST/PATCH with JSON)

## Auth / identity
- `GET /users/me` — verify token, get bot user

## Search
- `POST /search` — find pages/databases by title + filters (paginated)

## Pages (properties + metadata)
- `POST /pages` — create a page (child page or data source row)
- `GET /pages/{page_id}` — retrieve page properties (NOT content)
- `GET /pages/{page_id}/properties/{property_id}` — retrieve a single property item (needed for large relation/rollup lists)
- `PATCH /pages/{page_id}` — update properties, icon/cover, lock/unlock, archive/trash, apply template
- `POST /pages/{page_id}/move` — move (re-parent) a page

## Blocks (page body/content)
- `GET /blocks/{block_id}` — retrieve a block
- `PATCH /blocks/{block_id}` — update a block (supported block types only)
- `GET /blocks/{block_id}/children` — list child blocks (paginated)
- `PATCH /blocks/{block_id}/children` — append child blocks
- `DELETE /blocks/{block_id}` — trash a block (includes page blocks)

Tip: To fetch a page’s content, use the page ID as `block_id` in `/blocks/{block_id}/children`.

## Databases + data sources (2025-09-03 model)
- `GET /databases/{database_id}` — retrieve a database container (includes `data_sources`)
- `GET /data_sources/{data_source_id}` — retrieve schema/properties for the data source
- `POST /data_sources/{data_source_id}/query` — query rows (pages) in the data source (paginated)
- `GET /data_sources/{data_source_id}/templates` — list templates for that data source
- `PATCH /data_sources/{data_source_id}` — update the data source schema (columns)

Notes:
- Older endpoint `POST /databases/{database_id}/query` is deprecated under the newer API version.
- “Rows” are pages: create/update them via `/pages` endpoints.

## Errors (common)
- 400 `missing_version`
- 400 `validation_error`
- 401 `unauthorized`
- 403 `restricted_resource`
- 404 `object_not_found`
- 429 `rate_limited`
- 409 `conflict_error`
