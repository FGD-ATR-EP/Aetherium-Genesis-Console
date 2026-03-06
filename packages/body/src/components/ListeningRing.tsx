import React, { useMemo } from 'react';
import { Canvas, Fill, Shader, useClockValue } from '@shopify/react-native-skia';

interface ListeningRingProps {
  skia: any;
  progress: number; // 0.0 to 1.0 (10s countdown)
  volume: number;   // 0.0 to 1.0 (Audio level)
}

const SHADER_CODE = `
uniform float u_time;
uniform float2 u_resolution;
uniform float u_progress; // 0.0 (Start) -> 1.0 (End)
uniform float u_volume;

float sdRing(float2 p, float r, float w) {
    return abs(length(p) - r) - w;
}

float4 main(float2 pos) {
    float2 uv = (pos - u_resolution * 0.5) / min(u_resolution.x, u_resolution.y);
    float t = u_time / 1000.0;

    // Ring shrinks as progress increases
    float initialRadius = 0.45;
    float finalRadius = 0.1;
    float currentRadius = mix(initialRadius, finalRadius, u_progress);

    // Thickness pulses with volume
    float thickness = 0.005 + (u_volume * 0.02);

    // Jitter/Vibration based on volume
    float jitter = sin(t * 50.0) * u_volume * 0.01;

    float d = sdRing(uv, currentRadius + jitter, thickness);

    // Glow
    float glow = 0.01 / abs(d);

    // Color: Cyan -> Red as time runs out
    float3 color = mix(float3(0.0, 1.0, 1.0), float3(1.0, 0.0, 0.0), u_progress);

    float alpha = smoothstep(0.01, 0.0, d);
    float3 finalColor = color * (alpha + glow);

    return float4(finalColor, 1.0);
}
`;

const ListeningRing: React.FC<ListeningRingProps> = ({ skia, progress, volume }) => {
  // useClockValue handles the animation timer and triggers Skia redraws without React re-renders.
  const time = useClockValue();

  const source = useMemo(() => {
    if (!skia || !skia.RuntimeEffect) return null;
    return skia.RuntimeEffect.Make(SHADER_CODE);
  }, [skia]);

  // Using useMemo to construct the uniforms object ensures we only update the non-clock
  // values when they change, while the u_time SkiaValue automatically drives the shader.
  const uniforms = useMemo(() => ({
    u_time: time,
    u_resolution: [window.innerWidth, window.innerHeight],
    u_progress: progress,
    u_volume: volume
  }), [time, progress, volume]);

  if (!source) return null;

  return (
    // @ts-ignore
    <Canvas style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}>
      <Fill>
        <Shader source={source} uniforms={uniforms} />
      </Fill>
    </Canvas>
  );
};

export default ListeningRing;
