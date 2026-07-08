'use client'

import { useRef, useMemo, useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'

const PARTICLE_COUNT = 6000
const CONNECTION_COUNT = 120

const vertexShader = `
  attribute float aSize;
  attribute float aAlpha;
  uniform float uTime;
  uniform vec2 uMouse;
  varying float vAlpha;

  void main() {
    vAlpha = aAlpha;
    vec3 pos = position;

    // Gentle drift
    float drift = sin(uTime * 0.3 + pos.x * 0.5) * 0.15;
    pos.y += drift;
    pos.x += cos(uTime * 0.2 + pos.z * 0.4) * 0.1;

    // Mouse repulsion (mild)
    vec2 mouseWorld = uMouse * 8.0;
    float dist = length(pos.xy - mouseWorld);
    if (dist < 2.0) {
      vec2 dir = normalize(pos.xy - mouseWorld);
      pos.xy += dir * (2.0 - dist) * 0.3;
    }

    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    gl_PointSize = aSize * (300.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
  }
`

const fragmentShader = `
  uniform float uTime;
  varying float vAlpha;

  void main() {
    vec2 uv = gl_PointCoord - 0.5;
    float dist = length(uv);
    if (dist > 0.5) discard;

    float alpha = (1.0 - dist * 2.0) * vAlpha;
    float pulse = sin(uTime * 2.0) * 0.1 + 0.9;

    vec3 col = mix(vec3(0.31, 0.62, 1.0), vec3(0.48, 0.9, 1.0), dist * 2.0);
    gl_FragColor = vec4(col, alpha * pulse);
  }
`

export default function ParticleField({ mouse }: { mouse: React.MutableRefObject<[number, number]> }) {
  const pointsRef = useRef<THREE.Points>(null)
  const linesRef = useRef<THREE.LineSegments>(null)
  const { camera } = useThree()

  const { positions, sizes, alphas } = useMemo(() => {
    const positions = new Float32Array(PARTICLE_COUNT * 3)
    const sizes = new Float32Array(PARTICLE_COUNT)
    const alphas = new Float32Array(PARTICLE_COUNT)

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      // Spherical shell distribution for depth
      const r = 4 + Math.random() * 12
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)

      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta)
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta)
      positions[i * 3 + 2] = r * Math.cos(phi)

      sizes[i] = Math.random() * 1.8 + 0.4
      alphas[i] = Math.random() * 0.6 + 0.2
    }
    return { positions, sizes, alphas }
  }, [])

  // Neural network connection lines
  const lineGeometry = useMemo(() => {
    const pts: number[] = []
    const nodes: [number, number, number][] = []

    // Pick a subset of particles as nodes
    for (let i = 0; i < CONNECTION_COUNT; i++) {
      const idx = Math.floor(Math.random() * PARTICLE_COUNT)
      nodes.push([positions[idx * 3], positions[idx * 3 + 1], positions[idx * 3 + 2]])
    }

    // Connect nearby nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[i][0] - nodes[j][0]
        const dy = nodes[i][1] - nodes[j][1]
        const dz = nodes[i][2] - nodes[j][2]
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz)
        if (dist < 3.5) {
          pts.push(...nodes[i], ...nodes[j])
        }
      }
    }

    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3))
    return geo
  }, [positions])

  useEffect(() => {
    camera.position.set(0, 0, 18)
  }, [camera])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    const pts = pointsRef.current
    if (!pts) return

    const mat = pts.material as THREE.ShaderMaterial
    mat.uniforms.uTime.value = t
    mat.uniforms.uMouse.value = new THREE.Vector2(mouse.current[0], mouse.current[1])

    // Slow rotation
    pts.rotation.y = t * 0.03
    pts.rotation.x = Math.sin(t * 0.015) * 0.1

    if (linesRef.current) {
      linesRef.current.rotation.y = t * 0.03
      linesRef.current.rotation.x = Math.sin(t * 0.015) * 0.1
    }
  })

  const material = useMemo(
    () =>
      new THREE.ShaderMaterial({
        vertexShader,
        fragmentShader,
        uniforms: {
          uTime: { value: 0 },
          uMouse: { value: new THREE.Vector2(0, 0) },
        },
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      }),
    []
  )

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry()
    geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    geo.setAttribute('aSize', new THREE.Float32BufferAttribute(sizes, 1))
    geo.setAttribute('aAlpha', new THREE.Float32BufferAttribute(alphas, 1))
    return geo
  }, [positions, sizes, alphas])

  return (
    <>
      <points ref={pointsRef} geometry={geometry} material={material} />
      <lineSegments ref={linesRef} geometry={lineGeometry}>
        <lineBasicMaterial
          color="#4F9EFF"
          transparent
          opacity={0.15}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </lineSegments>
      {/* Central glow sphere */}
      <mesh>
        <sphereGeometry args={[0.6, 32, 32]} />
        <meshBasicMaterial color="#7AE7FF" transparent opacity={0.06} />
      </mesh>
      <pointLight color="#4F9EFF" intensity={2} distance={20} />
      <pointLight color="#7AE7FF" intensity={1} distance={15} position={[5, 5, 5]} />
      <ambientLight intensity={0.1} />
    </>
  )
}
