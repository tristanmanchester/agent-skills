# Recipes (multi-step workflows)

## 1) Move pages into another page or database
Goal: re-parent existing pages.

Checklist:
- [ ] Identify the page(s) to move (page_id list)
- [ ] Identify destination:
  - another page: parent.type=page_id
  - a database: parent.type=data_source_id (discover via GET /databases/{database_id})
- [ ] For each page:
  - POST /pages/{page_id}/move
- [ ] Validate:
  - GET /pages/{page_id} and confirm parent changed
- [ ] Throttle to avoid 429

JS (SDK):
```js
await notion.pages.move({
  page_id,
  parent: { type: "data_source_id", data_source_id },
})
```

Raw HTTP:
POST `https://api.notion.com/v1/pages/{page_id}/move`
```json
{
  "parent": { "type": "page_id", "page_id": "<target_page_id>" }
}
```

## 2) Bulk archive/trash pages in a data source (dangerous)
- Query the data source with a filter to target pages
- Iterate pages and PATCH /pages/{page_id} with { archived: true }
- Validate by re-querying with a “archived/in_trash” filter (if available) or retrieving page status

## 3) Upsert rows by a unique key property
Pattern:
1) Query data source for existing row(s) matching unique key
2) If found: PATCH /pages/{page_id}
3) If not found: POST /pages (parent=data_source_id)
Always re-fetch and confirm.

## 4) Create pages from templates (fast scaffolding)
1) List templates:
   GET /data_sources/{data_source_id}/templates
2) Create page with template:
   POST /pages with parent.type=data_source_id and template.type=default|template_id
3) Wait:
   Template application is async; poll block children or use webhooks to detect content ready.

## 5) Export page content (best-effort)
- Retrieve blocks with recursion
- Convert block tree to Markdown/HTML in your app
Notes:
- Not all block types are trivially representable as Markdown.
- File uploads and embeds may require additional file handling.
