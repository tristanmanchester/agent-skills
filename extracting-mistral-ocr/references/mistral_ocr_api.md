# Mistral OCR contract

Reviewed 2026-09-13. Runtime dependencies: Python >=3.10 and `mistralai>=2.10,<3`.

```python
from mistralai.client import Mistral

with Mistral(api_key=api_key) as client:
    with open("document.pdf", "rb") as stream:
        uploaded = client.files.upload(file={"file_name": "document.pdf", "content": stream}, purpose="ocr")
    try:
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "file", "file_id": uploaded.id},
            table_format="html",
            include_image_base64=False,
            retries=None,
        )
        data = response.model_dump(mode="json", by_alias=True)
    finally:
        client.files.delete(file_id=uploaded.id)
```

Document URLs use `{ "type": "document_url", "document_url": "https://..." }`; images use `image_url` with an HTTPS or data URL. Zero-based page selection is explicit. A private URL requiring browser authentication is not a public document URL.

OCR table objects contain `id`, `content`, and `format` (`html` or `markdown`). SDK `format_` is an internal field name; JSON-mode dumping with aliases preserves the wire shape. Pages also contain Markdown, images, dimensions, optional headers/footers, blocks, and confidence metadata. Keep the complete response rather than flattening away information not used by the export.

Structured annotations use a JSON Schema response format. The SDK dictionary uses `schema_definition` inside `json_schema`; its wire alias is `schema`. The old generic `json_object`/`text` annotation switch is removed. Schema validation does not establish that extracted values are true.

Do not treat upload limits as OCR processing limits. Check current service limits and model capabilities before large jobs. Table/header/footer options need OCR 2512 or newer; structural blocks need OCR 4 or newer. Paid requests are not automatically retried by this helper.

## Primary sources

- [SDK migration guide](https://github.com/mistralai/client-python/blob/main/MIGRATION.md): v2 imports and Python minimum.
- [OCR processor](https://docs.mistral.ai/studio/document-processing/basic_ocr): current capabilities and inputs.
- [SDK OCR implementation](https://github.com/mistralai/client-python/blob/main/src/mistralai/client/ocr.py): supported keyword arguments and annotation schema requirement.
- [File document type](https://github.com/mistralai/client-python/blob/main/src/mistralai/client/models/filechunk.py).
- [Table response model](https://github.com/mistralai/client-python/blob/main/src/mistralai/client/models/ocrtableobject.py).
- [JSON Schema model](https://github.com/mistralai/client-python/blob/main/src/mistralai/client/models/jsonschema.py).
- [Package releases](https://pypi.org/project/mistralai/): 2.10.0 released 2026-09-09.
