# Lists, images, and media

Reviewed 2026-09-13. Measure the actual list before replacing its library. Distinguish row rendering, recycling state, image decoding, network fetches, and native compositing.

## FlatList

Use stable item identities, pure rows, targeted memoisation, and a render window appropriate to the device. A smaller window reduces memory but can expose blank space during fast scrolling. Validate clipping with transformed and absolutely positioned content.

`getItemLayout` is a FlatList optimisation when geometry is genuinely known. Include separator height in offsets and do not pretend dynamic text, font scaling, or heterogeneous rows have fixed heights.

```tsx
const ROW_HEIGHT = 72;
const SEPARATOR_HEIGHT = 1;
<FlatList
  data={data}
  keyExtractor={(item) => item.id}
  renderItem={renderItem}
  getItemLayout={(_, index) => ({
    length: ROW_HEIGHT,
    offset: (ROW_HEIGHT + SEPARATOR_HEIGHT) * index,
    index,
  })}
/>
```

Use that example only when the rendered separator and row dimensions match. Test large text and localisation before accepting fixed geometry.

## FlashList v2

FlashList v2 requires React Native's New Architecture and performs its own sizing. Its baseline contains no estimated-size props:

```tsx
import { FlashList } from '@shopify/flash-list';

<FlashList
  data={data}
  keyExtractor={(item) => item.id}
  renderItem={renderItem}
  getItemType={(item) => item.type}
/>
```

Use `FlashListRef<T>` for refs. `overrideItemLayout` can set spans, not item-size estimates. Masonry uses the `masonry` prop. The v1-only size-estimate and blank-area callbacks are not current v2 APIs; do not preserve compatibility branches in new examples.

Inspect local state inside recycled rows: a component instance can receive a different item. Reset item-specific state through the library's supported recycling patterns, and avoid keys inside recycled item subtrees that defeat reuse. Test reorder, insertion, filtering, dynamic heights, horizontal lists, accessibility focus, and scroll restoration. `maintainVisibleContentPosition` is enabled by default in v2, so verify its effect instead of silently changing scroll behaviour.

## Images

Use an image pipeline such as `expo-image` when its caching, placeholder, and decoding behaviour fits the app. Serve dimensions appropriate to the rendered size and device scale; reserving layout space prevents avoidable relayout. Measure memory as well as cache hit rate. Prefetch bounded next-screen content rather than entire feeds, and ensure recycled cells do not briefly show the previous item's image.

```tsx
import { Image } from 'expo-image';
<Image source={{ uri: url }} style={{ width: 96, height: 96 }}
  contentFit="cover" placeholder={{ blurhash }} transition={150} />
```

Treat private media cache retention as a product/privacy decision, especially across account switches.

## Video

Use the current `expo-video` integration for new Expo video work. Manage player lifetime, visibility, audio focus, and release; a feed should not leave every offscreen player running. Cache only content likely to be replayed and respect disk budgets. Check platform/source constraints such as iOS HLS and DRM before enabling caching; a cache flag is not a promise that every stream is cached.

## Verification and sources

Compare release builds on the same device and dataset. Exercise fast scroll, slow network, memory pressure, font scaling, rotation, and navigation away/back. Record frame-time distributions, retained memory, and visible recycling errors, not just average FPS.

- [FlashList v2 migration](https://shopify.github.io/flash-list/docs/v2-migration/)
- [FlatList configuration](https://reactnative.dev/docs/optimizing-flatlist-configuration)
- [Expo Image](https://docs.expo.dev/versions/latest/sdk/image/)
- [Expo Video](https://docs.expo.dev/versions/latest/sdk/video/)
