# Resource contracts and recovery

The following endpoint map is inherited from the repository's previous OpenAPI
snapshot. It is a navigation aid, not a current complete schema. Confirm the exact
operation in the current official API reference or installed SDK before execution.
The SDK/authentication surface was rechecked on 2026-09-13; not every endpoint was.

| Intent | Inherited HTTP route | What to resolve |
| --- | --- | --- |
| Identify account | GET /v2/user/me | Actual credential/account context |
| Find roots | GET /v2/resource-roots | Inbox/bin folder IDs in the selected workspace |
| Retrieve item | GET /v2/resources/{resourceId} | Kind, identity, content representation |
| Browse children | POST /v2/resources/filter | Parent UUID, order, limit, pagination |
| Search | POST /v2/search | Query modes, filters, returned snippets and pages |
| Create note | POST /v2/notepads | Parent and text/structured content |
| Create folder/bookmark | POST /v2/folders or /v2/bookmarks | Parent, name, bookmark URL |
| Upload/create file | GET /v2/upload then POST /v2/files | Transfer instructions and attachment contract |
| Tags | GET/POST /v2/tags | Existing names/IDs and write intent |
| Delete/recover | POST /v2/resource/delete or /v2/resource/recover | Exact IDs, bin versus permanent deletion semantics |

## Preserve the useful distinctions

The inspected snapshot models notes as `notepad`, not a guessed `/v2/notes` route.
For creation it uses `name` rather than `title`, `parentId`, and either Markdown
`text` or structured `ydoc`. Do not construct Yjs data by guessing its encoding.
Its tags are objects such as `{"name":"reading"}` or `{"id":"TAG_UUID"}`, not an
array of strings. Confirm these fields in the current contract when implementing.

Root aliases are operation-specific: the old create schemas accept
`@alias::inbox` and `@alias::bin`, while child filtering requires a UUID. Resolve
roots rather than assuming aliases work everywhere. Keep Inbox as the default
only for an authorised create with no destination constraint; never substitute
it for a named folder that could not be resolved.

An illustrative notepad payload from that contract is:

```json
{"name":"Research notes","parentId":"DESTINATION_UUID","text":"# Findings\n\nVerified notes."}
```

Resolve IDs, validate the schema, and inspect intent before using it. A 400 can
mean an invalid field, not a reason to repeatedly create slightly different notes.
On an ambiguous outcome, search/retrieve to reconcile. Search indexing delay can
make absence from results inconclusive; prefer an acknowledged resource ID.

## Files

The old workflow obtains presigned upload instructions, transfers bytes, then
creates a file resource referencing that upload. Preserve all returned metadata
needed for finalisation. Use the current documented attachment path or object key;
do not derive it by stripping a URL unless the live contract explicitly requires
that exact transformation. Query parameters and path encoding can carry semantics.

Check local file identity and size before upload. Treat signed URLs as secrets,
validate destination/protocol, do not follow a redirect automatically, and never
forward Fabric credentials. Check both transfer and finalisation status and the
created resource's extraction/availability state. Retain partial outcomes instead
of blindly uploading again. Do not delete remote orphaned uploads without a
supported, authorised cleanup operation.

## Search and evidence

A search result can be a bookmark, note, uploaded file, or a connected item. Keep
those types and source URLs separate. Preserve query, filters, workspace/base,
page boundaries, and any retrieval failures. Retrieve the original relevant
content before quoting or summarising beyond the returned excerpt. Connected
resource permissions may differ from workspace membership.

## Error handling

Use a bounded timeout and explicit response-size policy. For read-only operations,
respect documented throttling and backoff. For mutations, an SDK's retry default
needs inspection as well as any application retry wrapper. Report auth, permission,
not-found, rate-limit, schema, and unknown transport outcomes distinctly. Do not
interpret all 404s as proof that a private resource does not exist.

Current entry points: [developer guide](https://developers.fabric.so/),
[TypeScript SDK](https://developers.fabric.so/sdks/typescript-sdk),
[API reference](https://developers.fabric.so/api-reference).
