import React, { useEffect, useRef, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { Canvas, Image, RoundedRect, type SkImage, makeImageFromView } from "@shopify/react-native-skia";

/** Captures this text-only card after layout; async assets need their own readiness signal. */
export function SnapshotComposite() {
  const ref = useRef<View>(null);
  const mounted = useRef(false);
  const inFlight = useRef(false);
  const revision = useRef(0);
  const [ready, setReady] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [snapshot, setSnapshot] = useState<SkImage | null>(null);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; revision.current += 1; };
  }, []);

  const capture = async () => {
    if (!mounted.current || !ready || !ref.current || inFlight.current) return;
    const requestedRevision = revision.current;
    inFlight.current = true;
    setPending(true);
    setError(null);
    try {
      const image = await makeImageFromView(ref);
      if (!mounted.current) return;
      if (requestedRevision !== revision.current) {
        setError("The card changed during capture. Capture it again.");
      } else {
        setSnapshot(image);
      }
    } catch {
      if (mounted.current) setError("Capture failed. The previous snapshot is unchanged.");
    } finally {
      inFlight.current = false;
      if (mounted.current) setPending(false);
    }
  };

  return (
    <View>
      <View ref={ref} collapsable={false} style={styles.card}
        onLayout={({ nativeEvent }) => {
          revision.current += 1;
          setReady(nativeEvent.layout.width > 0 && nativeEvent.layout.height > 0);
        }}>
        <Text style={styles.title}>Snapshot this card</Text>
        <Text style={styles.body}>Capture a React Native subtree and reuse it inside Skia.</Text>
      </View>
      <Pressable onPress={capture} disabled={!ready || pending} accessibilityRole="button"
        accessibilityState={{ disabled: !ready || pending, busy: pending }} style={styles.button}>
        <Text style={styles.buttonText}>{pending ? "Capturing…" : "Capture"}</Text>
      </Pressable>
      {error ? <Text accessibilityRole="alert">{error}</Text> : null}
      {snapshot ? (
        <Canvas style={styles.canvas} accessibilityLabel="Captured card preview">
          <RoundedRect x={0} y={0} width={320} height={180} r={28} color="#0F172A" />
          <RoundedRect x={1} y={1} width={318} height={178} r={27}
            style="stroke" strokeWidth={1} color="rgba(255,255,255,0.10)" />
          <Image image={snapshot} x={16} y={16} width={288} height={148} fit="contain" />
        </Canvas>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { borderRadius: 24, padding: 18, backgroundColor: "#0F172A" },
  title: { color: "#F8FAFC", fontSize: 18, fontWeight: "600" },
  body: { color: "#CBD5E1", fontSize: 14, marginTop: 8, lineHeight: 20 },
  button: { marginTop: 12, alignSelf: "flex-start", borderRadius: 16,
    paddingHorizontal: 14, paddingVertical: 10, backgroundColor: "#1D4ED8" },
  buttonText: { color: "#F8FAFC", fontWeight: "600" },
  canvas: { width: 320, height: 180, marginTop: 16 },
});
