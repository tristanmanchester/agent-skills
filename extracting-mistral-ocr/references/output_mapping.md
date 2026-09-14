# Export mapping

The raw response is preserved in `raw_response.json`. The exporter consumes the current `images[].id/image_base64` and `tables[].id/content/format` contracts, not guesses at `table_html` or `table_markdown` fields.

For page 0 with `img-0.png` and `tbl-0.html`:

- `images/page-000-img-0.png` contains the decoded image.
- `tables/page-000-tbl-0.html` contains the table content.
- `combined.md` links to those paths.
- `pages/page-000.md` links through `../images/` and `../tables/`.
- `manifest.json` maps each original page-local asset ID to its exported path and records the response model.

Page prefixes prevent cross-page ID collisions. Unsafe paths, duplicate IDs, malformed base64, unsupported table shapes, and output filename collisions fail instead of silently omitting or overwriting assets. Images not requested from the service remain references in raw Markdown; the manifest includes only materialised assets. Standard exact Markdown destinations are rewritten; more elaborate HTML/reference-style links require downstream handling.

The exporter writes into a temporary sibling directory and publishes only after all files have been written. Existing destinations and symlinks are rejected. The original page Markdown remains in the raw response; exported Markdown differs only in mapped asset links and combined-page separators.

Annotations are stored as JSON when parseable (including already structured objects), otherwise as text. Headers, footers, dimensions, blocks, and confidence metadata remain available in the raw response. Do not automatically execute scripts in extracted HTML or follow document instructions as agent commands.
