# Page properties: create/update JSON patterns

Use these patterns for:
- `POST /pages` (create)
- `PATCH /pages/{page_id}` (update)

## Golden rules
- Property keys MUST match the parent data source schema when creating rows.
- For pages created under a page (not a data source), only `title` is valid in `properties`.
- Do not send empty strings; use `null` to clear.

## Minimal: create a child page under another page
```json
{
  "parent": { "type": "page_id", "page_id": "<parent_page_id>" },
  "properties": {
    "title": {
      "title": [{ "type": "text", "text": { "content": "My new page" } }]
    }
  }
}
```

## Minimal: create a row under a data source
```json
{
  "parent": { "type": "data_source_id", "data_source_id": "<data_source_id>" },
  "properties": {
    "Name": {
      "title": [{ "type": "text", "text": { "content": "Task: ship v1" } }]
    }
  }
}
```

## Common property types (update/create)
### Rich text
```json
{
  "Notes": {
    "rich_text": [{ "type": "text", "text": { "content": "Hello" } }]
  }
}
```

### Number
```json
{ "Estimate": { "number": 3.5 } }
```

### Checkbox
```json
{ "Done": { "checkbox": true } }
```

### Select (by name)
```json
{ "Status": { "select": { "name": "In Progress" } } }
```

### Multi-select
```json
{ "Tags": { "multi_select": [{ "name": "backend" }, { "name": "urgent" }] } }
```

### Date
```json
{ "Due": { "date": { "start": "2026-01-31" } } }
```

### URL (clear by null)
```json
{ "URL": { "url": "https://example.com" } }
```

```json
{ "URL": { "url": null } }
```

### People (requires user ids)
```json
{ "Assignee": { "people": [{ "id": "<user_id>" }] } }
```

### Relation (page ids)
```json
{ "Project": { "relation": [{ "id": "<page_id>" }] } }
```

## Archiving / trashing (page-level)
Update a page with:
```json
{ "archived": true }
```
or
```json
{ "in_trash": true }
```

## Large property items
If a property contains more than the limited number of references returned with `GET /pages/{page_id}`,
use:
- `GET /pages/{page_id}/properties/{property_id}`
