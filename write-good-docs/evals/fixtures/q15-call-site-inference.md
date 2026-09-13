File `delivery.ts` contains this complete caller:

```ts
export function onFailure(message: Message) {
  retry(message);
}
```

No implementation of `retry`, wrapper policy, queue configuration, or runtime evidence is supplied. A discussion note proposes moving a message to a failure queue after six failed attempts; this proposal is unapproved.
