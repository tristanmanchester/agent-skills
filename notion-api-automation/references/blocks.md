# Blocks: reading and writing page content

## Read page content
- Call `GET /blocks/{block_id}/children`
- Use the **page_id as block_id** to read top-level page blocks.
- Recurse when a returned block has `has_children: true`.

## Append blocks
Use `PATCH /blocks/{block_id}/children` with `children: [...]`

### Minimal paragraph
```json
{
  "children": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          { "type": "text", "text": { "content": "Hello from the API" } }
        ]
      }
    }
  ]
}
```

### Heading + bullet list
```json
{
  "children": [
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [{ "type": "text", "text": { "content": "Notes" } }]
      }
    },
    {
      "object": "block",
      "type": "bulleted_list_item",
      "bulleted_list_item": {
        "rich_text": [{ "type": "text", "text": { "content": "Item one" } }]
      }
    }
  ]
}
```

### Insert not-at-end (append after a specific block)
```json
{
  "after": "<existing_block_id>",
  "children": [
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [{ "type": "text", "text": { "content": "Inserted here" } }]
      }
    }
  ]
}
```

## Update a block
Use `PATCH /blocks/{block_id}` (supported types only).
Children cannot be edited via this endpoint; append new children instead.

## Delete/trash a block
Use `DELETE /blocks/{block_id}`.
This sets `archived: true` and moves the block to Trash in the Notion UI.
