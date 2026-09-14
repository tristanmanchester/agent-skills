import React, { useCallback, useState } from 'react';
import { Button, Text, View } from 'react-native';
import { Canvas, Group, Image, useImage, type SkImage } from '@shopify/react-native-skia';
import { GestureDetector, usePanGesture, usePinchGesture, useSimultaneousGestures } from 'react-native-gesture-handler';
import { useDerivedValue, useSharedValue } from 'react-native-reanimated';
import { scheduleOnUI } from 'react-native-worklets';
import { makeBounds, moveBy, zoomBetween, type Bounds, type Pose } from './pan-zoom-math';

type Props = {
  source: number | string;
  width?: number;
  height?: number;
  minScale?: number;
  maxScale?: number;
  accessibilityLabel?: string;
};

/** Skia 2.10+, Reanimated 4, RNGH 3. Requires the app's GestureHandlerRootView. */
export function PanZoomImageStage({
  source, width = 320, height = 220, minScale = 1, maxScale = 4,
  accessibilityLabel = 'Image preview',
}: Props) {
  // Check public props before mounting hooks; source/dimension changes start a new view.
  makeBounds(1, 1, width, height, minScale, maxScale);
  return <LoadedStage key={JSON.stringify([source, width, height, minScale, maxScale])}
    source={source} width={width} height={height} minScale={minScale}
    maxScale={maxScale} label={accessibilityLabel} />;
}

function LoadedStage({ source, width, height, minScale, maxScale, label }: {
  source: number | string; width: number; height: number;
  minScale: number; maxScale: number; label: string;
}) {
  const [failed, setFailed] = useState(false);
  const onError = useCallback(() => setFailed(true), []);
  const image = useImage(source, onError);
  if (!image) return <View style={{ width, height }}>
    <Text accessibilityRole={failed ? 'alert' : undefined}>
      {failed ? 'Image could not be loaded.' : 'Loading image…'}
    </Text>
  </View>;
  const bounds = makeBounds(image.width(), image.height(), width, height, minScale, maxScale);
  return <InteractiveStage image={image} bounds={bounds} label={label} />;
}

function InteractiveStage({ image, bounds, label }: { image: SkImage; bounds: Bounds; label: string }) {
  const { width, height, contentWidth, contentHeight, minScale } = bounds;
  const pose = useSharedValue<Pose>({ scale: minScale, x: 0, y: 0 });
  const pinching = useSharedValue(false);
  const panning = useSharedValue(false);
  const panPointers = useSharedValue(0);
  const focal = useSharedValue({ x: 0, y: 0 });

  const pan = usePanGesture({
    averageTouches: true,
    onActivate: event => {
      panning.value = true;
      panPointers.value = event.numberOfPointers;
    },
    onUpdate: event => {
      const previousPointers = panPointers.value;
      panPointers.value = event.numberOfPointers;
      // Pinch owns two-finger translation. Skip pointer-count transitions to avoid jumps.
      if (pinching.value || event.numberOfPointers !== 1 || previousPointers !== 1) return;
      pose.value = moveBy(pose.value, event.changeX, event.changeY, bounds);
    },
    onFinalize: () => { panning.value = false; panPointers.value = 0; },
  });
  const pinch = usePinchGesture({
    onActivate: event => {
      pinching.value = true;
      focal.value = { x: event.focalX - width / 2, y: event.focalY - height / 2 };
    },
    onUpdate: event => {
      const next = { x: event.focalX - width / 2, y: event.focalY - height / 2 };
      if (!Number.isFinite(next.x) || !Number.isFinite(next.y)) return;
      pose.value = zoomBetween(pose.value, event.scaleChange, focal.value, next, bounds);
      focal.value = next;
    },
    // Cancellation keeps the last bounded view. It never requests a business mutation.
    onFinalize: () => { pinching.value = false; },
  });
  const gesture = useSimultaneousGestures(pan, pinch);
  const transform = useDerivedValue(() => [
    { translateX: width / 2 + pose.value.x },
    { translateY: height / 2 + pose.value.y },
    { scale: pose.value.scale },
  ]);

  const control = (action: 'in' | 'out' | 'reset' | 'left' | 'right' | 'up' | 'down') => {
    scheduleOnUI(() => {
      'worklet';
      if (pinching.value || panning.value) return;
      if (action === 'reset') pose.value = { scale: minScale, x: 0, y: 0 };
      else if (action === 'in' || action === 'out') {
        pose.value = zoomBetween(pose.value, action === 'in' ? 1.25 : 0.8,
          { x: 0, y: 0 }, { x: 0, y: 0 }, bounds);
      } else {
        pose.value = moveBy(pose.value,
          action === 'left' ? -width / 4 : action === 'right' ? width / 4 : 0,
          action === 'up' ? -height / 4 : action === 'down' ? height / 4 : 0, bounds);
      }
    });
  };
  return <View style={{ width }}>
    <GestureDetector gesture={gesture}>
      <View collapsable={false} accessible accessibilityRole="image" accessibilityLabel={label}
        accessibilityHint="Use the zoom, move, and reset buttons to change the view."
        style={{ width, height, overflow: 'hidden' }}>
        <Canvas accessible={false} style={{ width, height }}>
          <Group transform={transform}>
            <Image image={image} x={-contentWidth / 2} y={-contentHeight / 2}
              width={contentWidth} height={contentHeight} fit="fill" />
          </Group>
        </Canvas>
      </View>
    </GestureDetector>
    <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
      <Button title="Zoom in" onPress={() => control('in')} />
      <Button title="Zoom out" onPress={() => control('out')} />
      <Button title="Reset" onPress={() => control('reset')} />
      <Button title="Left" accessibilityLabel="Move image left" onPress={() => control('left')} />
      <Button title="Right" accessibilityLabel="Move image right" onPress={() => control('right')} />
      <Button title="Up" accessibilityLabel="Move image up" onPress={() => control('up')} />
      <Button title="Down" accessibilityLabel="Move image down" onPress={() => control('down')} />
    </View>
  </View>;
}
