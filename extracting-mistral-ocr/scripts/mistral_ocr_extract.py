#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mistralai>=2.10,<3"]
# ///
"""OCR with Mistral SDK v2; export auditable, self-contained Markdown assets."""
from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any
from urllib.parse import urlsplit


class CLIError(RuntimeError):
    pass


@dataclass
class Source:
    payload: dict[str, Any]
    uploaded_file_id: str | None = None


def parse_pages_spec(spec: str | None) -> list[int] | None:
    if spec is None:
        return None
    pages: set[int] = set()
    for part in spec.split(","):
        match = re.fullmatch(r"\s*(\d+)(?:\s*-\s*(\d+))?\s*", part)
        if not match:
            raise CLIError("Use zero-based pages such as 0,2-4; empty segments are invalid")
        start, end = int(match[1]), int(match[2] or match[1])
        if end < start or end > 10000:
            raise CLIError("Invalid page range (helper limit: page 10000)")
        pages.update(range(start, end + 1))
    return sorted(pages)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path)
    source.add_argument("--url")
    parser.add_argument("--url-type", choices=("document", "image"), default="document")
    parser.add_argument("--out", type=Path, required=True, help="New output directory; existing directories are never overwritten")
    parser.add_argument("--model", default="mistral-ocr-latest")
    parser.add_argument("--table-format", choices=("inline", "markdown", "html"), default="inline")
    parser.add_argument("--pages")
    parser.add_argument("--include-image-base64", action="store_true")
    parser.add_argument("--include-blocks", action="store_true")
    parser.add_argument("--confidence", choices=("page", "word", "block"))
    parser.add_argument("--extract-header", action="store_true")
    parser.add_argument("--extract-footer", action="store_true")
    parser.add_argument("--image-limit", type=int)
    parser.add_argument("--image-min-size", type=int)
    parser.add_argument("--annotation-schema", type=Path, help="JSON Schema document for structured annotations")
    parser.add_argument("--annotation-prompt")
    parser.add_argument("--keep-upload", action="store_true", help="Retain this run's uploaded PDF instead of deleting it in finally")
    return parser


def prepare_source(client: Any, args: argparse.Namespace) -> Source:
    if args.url:
        parsed = urlsplit(args.url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise CLIError("Provide a public HTTPS URL without embedded credentials")
        kind = args.url_type + "_url"
        return Source({"type": kind, kind: args.url})
    path = args.input.expanduser()
    if not path.is_file():
        raise CLIError("Input file does not exist")
    if path.suffix.lower() == ".pdf":
        with path.open("rb") as stream:
            uploaded = client.files.upload(file={"file_name": path.name, "content": stream}, purpose="ocr")
        return Source({"type": "file", "file_id": uploaded.id}, uploaded.id)
    media = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif"}
    mime = media.get(path.suffix.lower())
    if not mime:
        raise CLIError("Local input must be PDF, PNG, JPEG, WebP, or AVIF")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return Source({"type": "image_url", "image_url": f"data:{mime};base64,{data}"})


def request_options(args: argparse.Namespace) -> dict[str, Any]:
    options: dict[str, Any] = {
        "model": args.model,
        "table_format": None if args.table_format == "inline" else args.table_format,
        "include_image_base64": args.include_image_base64,
        "include_blocks": args.include_blocks,
        "extract_header": args.extract_header,
        "extract_footer": args.extract_footer,
        "retries": None,
    }
    pages = parse_pages_spec(args.pages)
    if pages is not None:
        options["pages"] = pages
    for field in ("image_limit", "image_min_size"):
        value = getattr(args, field)
        if value is not None:
            if value <= 0:
                raise CLIError(f"{field} must be positive")
            options[field] = value
    if args.confidence:
        if args.confidence == "block" and not args.include_blocks:
            raise CLIError("Block confidence requires --include-blocks")
        options["confidence_scores_granularity"] = args.confidence
    if args.annotation_prompt and not args.annotation_schema:
        raise CLIError("--annotation-prompt requires --annotation-schema")
    if args.annotation_schema:
        schema = json.loads(args.annotation_schema.read_text(encoding="utf-8"))
        if not isinstance(schema, dict):
            raise CLIError("Annotation schema must be a JSON object")
        options["document_annotation_format"] = {"type": "json_schema", "json_schema": {
            "name": "document_annotation", "schema_definition": schema, "strict": True,
        }}
        if args.annotation_prompt:
            options["document_annotation_prompt"] = args.annotation_prompt
    return options


def asset_id(value: Any) -> str:
    # Provider responses are untrusted filenames; do not resolve or sanitise paths.
    if not isinstance(value, str) or len(value) > 200 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
        raise CLIError("Unsafe image/table identifier in OCR response")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def render_links(markdown: str, assets: dict[str, str], prefix: str = "") -> str:
    # Rewrite only exact Markdown destinations, not occurrences in prose.
    for original, relative in assets.items():
        markdown = markdown.replace(f"]({original})", f"]({prefix}{relative})")
    return markdown


def write_outputs(out: Path, response: dict[str, Any]) -> None:
    if out.exists() or out.is_symlink():
        raise CLIError("Output path already exists; choose a new directory")
    pages = response.get("pages")
    if not isinstance(pages, list) or not pages:
        raise CLIError("OCR response has no pages")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".mistral-ocr-", dir=out.parent) as temporary:
        root = Path(temporary)
        for name in ("pages", "images", "tables"):
            (root / name).mkdir()
        write_json(root / "raw_response.json", response)
        combined, manifest, seen = [], [], set()
        for page in pages:
            if not isinstance(page, dict) or isinstance(page.get("index"), bool) or not isinstance(page.get("index"), int) or page["index"] < 0:
                raise CLIError("OCR response contains an invalid page index")
            index = page["index"]
            if index in seen:
                raise CLIError("OCR response contains duplicate page indices")
            seen.add(index)
            markdown = page.get("markdown")
            if not isinstance(markdown, str):
                raise CLIError("OCR page is missing Markdown")
            mapping: dict[str, str] = {}
            for image in page.get("images") or []:
                identifier = asset_id(image.get("id"))
                encoded = image.get("image_base64")
                if encoded is None:
                    continue
                if not isinstance(encoded, str):
                    raise CLIError("Invalid image data")
                if encoded.startswith("data:"):
                    encoded = encoded.split(",", 1)[1]
                data = base64.b64decode(encoded, validate=True)
                relative = f"images/page-{index:03d}-{identifier}"
                if identifier in mapping:
                    raise CLIError("Duplicate asset ID within a page")
                (root / relative).write_bytes(data)
                mapping[identifier] = relative
            for table in page.get("tables") or []:
                identifier = asset_id(table.get("id"))
                content, format_ = table.get("content"), table.get("format")
                if not isinstance(content, str) or format_ not in ("html", "markdown"):
                    raise CLIError("Unsupported table shape; expected content and format")
                if identifier in mapping:
                    raise CLIError("Duplicate asset ID within a page")
                extension = "html" if format_ == "html" else "md"
                relative = f"tables/page-{index:03d}-{identifier}"
                if not relative.endswith("." + extension):
                    relative += "." + extension
                if relative in mapping.values():
                    raise CLIError("Asset filename collision")
                (root / relative).write_text(content, encoding="utf-8")
                mapping[identifier] = relative
            (root / "pages" / f"page-{index:03d}.md").write_text(render_links(markdown, mapping, "../"), encoding="utf-8")
            combined.append(f"<!-- page {index} -->\n\n" + render_links(markdown, mapping))
            manifest.append({"page": index, "assets": mapping})
        (root / "combined.md").write_text("\n\n---\n\n".join(combined), encoding="utf-8")
        annotation = response.get("document_annotation")
        if annotation is not None:
            if isinstance(annotation, str):
                try:
                    annotation = json.loads(annotation)
                except ValueError:
                    (root / "document_annotation.txt").write_text(annotation, encoding="utf-8")
            if not isinstance(annotation, str):
                write_json(root / "document_annotation.json", annotation)
        write_json(root / "manifest.json", {"model": response.get("model"), "pages": manifest})
        root.rename(out)


def execute(client: Any, args: argparse.Namespace) -> None:
    options = request_options(args)
    if args.out.exists() or args.out.is_symlink():
        raise CLIError("Output already exists; no request was sent")
    source = prepare_source(client, args)
    try:
        response = client.ocr.process(document=source.payload, **options)
        write_outputs(args.out, response.model_dump(mode="json", by_alias=True))
    finally:
        if source.uploaded_file_id and not args.keep_upload:
            # Cleanup failure is an error, not a silent claim that data was deleted.
            try:
                client.files.delete(file_id=source.uploaded_file_id)
            except Exception as exc:
                raise CLIError(f"Uploaded file cleanup failed: {source.uploaded_file_id}. Check remote retention; local output may already exist.") from exc


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    os.umask(0o077)
    try:
        key = os.environ.get("MISTRAL_API_KEY")
        if not key:
            raise CLIError("MISTRAL_API_KEY is not set")
        # Lazy v2-only import keeps --help and offline export tests usable without SDK/network.
        from mistralai.client import Mistral
        with Mistral(api_key=key) as client:
            execute(client, args)
        print(str(args.out.resolve()))
        return 0
    except ImportError:
        print("Install dependencies from this skill's scripts/requirements.txt with Python 3.10+", file=sys.stderr)
        return 2
    except CLIError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        # SDK exceptions can contain document URLs or response content.
        print(f"OCR/export failed ({type(exc).__name__}); inspect locally without exposing secrets", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
