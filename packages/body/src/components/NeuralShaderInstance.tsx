import React, { useMemo } from 'react';
import { Canvas, Fill, Shader, useClockValue } from '@shopify/react-native-skia';
import { PhysicsParams } from '../types/intent';

interface NeuralShaderInstanceProps {
  physicsParams: PhysicsParams | null;
  skia: any;
}

// ORGANIC FLUID SHADER (The Soul) - Enhanced for PhysicsParams
const SHADER_CODE = `
uniform float u_time;
uniform float2 u_resolution;
uniform float3 u_color_base;
uniform float u_vibe_intensity;
uniform float u_ripple_mode; // 0=calm, 1=sharp, 2=chaotic

// Smooth Union
float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

float noise(float3 p) {
    return fract(sin(dot(p, float3(12.9898, 78.233, 45.164))) * 43758.5453);
}

float fbm(float3 p) {
    float v = 0.0;
    float amp = 0.5;
    for (int i = 0; i < 3; i++) {
        v += amp * noise(p);
        p *= 2.0;
        amp *= 0.5;
    }
    return v;
}

float4 main(float2 pos) {
    float2 uv = (pos - u_resolution * 0.5) / min(u_resolution.x, u_resolution.y);
    float t = u_time / 1000.0; // Assume t is in ms

    // Vibe Intensity modulates speed and scale
    float speed = 1.0 + u_vibe_intensity * 2.0;

    // Base Pulse
    float pulse = sin(t * speed) * 0.5 + 0.5;

    // Core Shape
    float d = length(uv) - 0.3 - (u_vibe_intensity * 0.2);

    // Ripple Logic (Procedural Pattern)
    if (u_ripple_mode > 1.5) {
        // Chaotic (Red)
        d += fbm(float3(uv * 5.0, t)) * 0.5;
    } else if (u_ripple_mode > 0.5) {
        // Sharp (White)
        d += sin(atan(uv.y, uv.x) * 10.0 + t) * 0.05;
    } else {
        // Calm (Blue)
        d += sin(length(uv) * 10.0 - t) * 0.02;
    }

    // Organic Distortion
    float n = fbm(float3(uv * 2.0, t * 0.5));
    d -= n * 0.1;

    // Glow
    float glow = 0.02 / abs(d);

    // Color
    float3 col = u_color_base;

    float alpha = smoothstep(0.01, 0.0, d);
    float3 finalColor = col * (alpha + glow);

    return float4(finalColor, 1.0);
}
`;

const NeuralShaderInstance: React.FC<NeuralShaderInstanceProps> = ({ physicsParams, skia }) => {
  // useClockValue handles the animation timer and triggers Skia redraws without React re-renders.
  const time = useClockValue();

  const source = useMemo(() => {
    if (!skia || !skia.RuntimeEffect) return null;
    return skia.RuntimeEffect.Make(SHADER_CODE);
  }, [skia]);

  const hexToFloat3 = (hex: string) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? [
        parseInt(result[1], 16) / 255,
        parseInt(result[2], 16) / 255,
        parseInt(result[3], 16) / 255
      ] : [0, 0, 1]; // Default Blue
  };

  // Map params
  const colorBase = useMemo(() =>
    hexToFloat3(physicsParams?.neural_shader_params.color_base || "#2323ee"),
  [physicsParams]);

  const intensity = physicsParams?.neural_shader_params.vibe_intensity || 0.0;

  // Ripple Mode Map
  let rippleMode = 0.0;
  const pattern = physicsParams?.neural_shader_params.ripple_pattern;
  if (pattern === "sharp_beams") rippleMode = 1.0;
  if (pattern === "chaotic_noise") rippleMode = 2.0;

  // Using useMemo to construct the uniforms object ensures we only update the non-clock
  // values when they change, while the u_time SkiaValue automatically drives the shader.
  const uniforms = useMemo(() => ({
      u_time: time,
      u_resolution: [window.innerWidth, window.innerHeight],
      u_color_base: colorBase,
      u_vibe_intensity: intensity,
      u_ripple_mode: rippleMode
  }), [time, colorBase, intensity, rippleMode]);

  if (!source) return null;

  return (
    // @ts-ignore
    <Canvas style={{ width: '100%', height: '100%' }}>
      <Fill>
        <Shader source={source} uniforms={uniforms} />
      </Fill>
    </Canvas>
  );
};

export default NeuralShaderInstance;
