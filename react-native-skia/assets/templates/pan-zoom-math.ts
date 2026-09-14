/** Pure geometry for pan-zoom-image-stage. Coordinates are viewport-centred points. */
export type Point = { x: number; y: number };
export type Pose = Point & { scale: number };
export type Bounds = {
  width: number; height: number;
  contentWidth: number; contentHeight: number;
  minScale: number; maxScale: number;
};

export function makeBounds(
  imageWidth: number, imageHeight: number, width: number, height: number,
  minScale = 1, maxScale = 4,
): Bounds {
  if (![imageWidth, imageHeight, width, height, minScale, maxScale]
    .every(value => Number.isFinite(value) && value > 0)
    || minScale < 1 || maxScale < minScale) {
    throw new RangeError('Positive finite dimensions and 1 <= minScale <= maxScale are required');
  }
  const fit = Math.min(width / imageWidth, height / imageHeight);
  const contentWidth = imageWidth * fit;
  const contentHeight = imageHeight * fit;
  if (![contentWidth, contentHeight, contentWidth * maxScale, contentHeight * maxScale]
    .every(value => Number.isFinite(value) && value > 0)) {
    throw new RangeError('Image dimensions and zoom range cannot be represented safely');
  }
  return { width, height, contentWidth, contentHeight, minScale, maxScale };
}

export function constrain(pose: Pose, bounds: Bounds): Pose {
  'worklet';
  const scale = Math.min(bounds.maxScale, Math.max(bounds.minScale, pose.scale));
  const maxX = Math.max(0, (bounds.contentWidth * scale - bounds.width) / 2);
  const maxY = Math.max(0, (bounds.contentHeight * scale - bounds.height) / 2);
  return { scale, x: maxX === 0 ? 0 : Math.min(maxX, Math.max(-maxX, pose.x)),
    y: maxY === 0 ? 0 : Math.min(maxY, Math.max(-maxY, pose.y)) };
}

export function moveBy(pose: Pose, dx: number, dy: number, bounds: Bounds): Pose {
  'worklet';
  if (![dx, dy, pose.x + dx, pose.y + dy].every(Number.isFinite)) return pose;
  return constrain({ ...pose, x: pose.x + dx, y: pose.y + dy }, bounds);
}

/** Preserve the image point under the moving focal point, except where bounds clamp. */
export function zoomBetween(
  pose: Pose, factor: number, previous: Point, next: Point, bounds: Bounds,
): Pose {
  'worklet';
  if (![factor, previous.x, previous.y, next.x, next.y].every(Number.isFinite) || factor <= 0) return pose;
  const scale = Math.min(bounds.maxScale, Math.max(bounds.minScale, pose.scale * factor));
  const ratio = scale / pose.scale;
  const x = next.x - (previous.x - pose.x) * ratio;
  const y = next.y - (previous.y - pose.y) * ratio;
  if (![scale, x, y].every(Number.isFinite)) return pose;
  return constrain({ scale, x, y }, bounds);
}
