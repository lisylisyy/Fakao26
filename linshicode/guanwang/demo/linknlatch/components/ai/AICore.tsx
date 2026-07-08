'use client'

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Sphere } from '@react-three/drei'
import * as THREE from 'three'

const coreVertexShader = `
  uniform float uTime;
  varying vec3 vNormal;
  varying vec3 vPosition;

  void main() {
    vNormal = normal;
    vPosition = position;

    // Displacement breathing
    float noise = sin(position.x * 4.0 + uTime) * cos(position.y * 4.0 + uTime * 0.7) * sin(position.z * 4.0 + uTime * 0.5);
    vec3 displaced = position + normal * noise * 0.08;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(displaced, 1.0);
  }
`

const coreFragmentShader = `
  uniform float uTime;
  varying vec3 vNormal;
  varying vec3 vPosition;

  void main() {
    float fresnel = pow(1.0 - dot(normalize(vNormal), vec3(0.0, 0.0, 1.0)), 2.0);
    float pulse = sin(uTime * 2.0) * 0.15 + 0.85;

    vec3 innerCol = vec3(0.12, 0.5, 1.0);
    vec3 outerCol = vec3(0.48, 0.9, 1.0);
    vec3 col = mix(innerCol, outerCol, fresnel) * pulse;

    gl_FragColor = vec4(col, fresnel * 0.9 + 0.1);
  }
`

function OrbitalRing({ radius, tilt, speed }: { radius: number; tilt: number; speed: number }) {
  const ref = useRef<THREE.Mesh>(null)

  const geo = useMemo(() => {
    const g = new THREE.TorusGeometry(radius, 0.004, 8, 120)
    return g
  }, [radius])

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.z = clock.getElapsedTime() * speed
    }
  })

  return (
    <mesh ref={ref} rotation={[tilt, 0, 0]} geometry={geo}>
      <meshBasicMaterial color="#4F9EFF" transparent opacity={0.25} />
    </mesh>
  )
}

function StreamParticles() {
  const ref = useRef<THREE.Points>(null)
  const COUNT = 300

  const geo = useMemo(() => {
    const pos = new Float32Array(COUNT * 3)
    const phase = new Float32Array(COUNT)
    for (let i = 0; i < COUNT; i++) {
      const theta = Math.random() * Math.PI * 2
      const r = 0.8 + Math.random() * 2.5
      pos[i * 3] = r * Math.cos(theta)
      pos[i * 3 + 1] = (Math.random() - 0.5) * 2
      pos[i * 3 + 2] = r * Math.sin(theta)
      phase[i] = Math.random() * Math.PI * 2
    }
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3))
    g.setAttribute('aPhase', new THREE.Float32BufferAttribute(phase, 1))
    return g
  }, [])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    const pos = geo.attributes.position.array as Float32Array
    const phase = geo.attributes.aPhase.array as Float32Array

    for (let i = 0; i < COUNT; i++) {
      const p = phase[i]
      const r = 0.8 + Math.sin(t * 0.5 + p) * 0.3 + 2.0 * (1 - ((t * 0.3 + p) % 1))
      const theta = p + t * 0.2
      pos[i * 3] = r * Math.cos(theta)
      pos[i * 3 + 1] = Math.sin(t + p) * 0.5
      pos[i * 3 + 2] = r * Math.sin(theta)
    }
    geo.attributes.position.needsUpdate = true
  })

  return (
    <points geometry={geo}>
      <pointsMaterial
        color="#7AE7FF"
        size={0.025}
        transparent
        opacity={0.6}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  )
}

export default function AICore() {
  const coreRef = useRef<THREE.Mesh>(null)

  const coreMat = useMemo(
    () =>
      new THREE.ShaderMaterial({
        vertexShader: coreVertexShader,
        fragmentShader: coreFragmentShader,
        uniforms: { uTime: { value: 0 } },
        transparent: true,
        side: THREE.FrontSide,
      }),
    []
  )

  useFrame(({ clock }) => {
    coreMat.uniforms.uTime.value = clock.getElapsedTime()
    if (coreRef.current) {
      coreRef.current.rotation.y = clock.getElapsedTime() * 0.2
    }
  })

  return (
    <>
      <ambientLight intensity={0.1} />
      <pointLight color="#4F9EFF" intensity={4} distance={8} />
      <pointLight color="#7AE7FF" intensity={2} position={[3, 2, 3]} distance={10} />

      {/* Core sphere */}
      <mesh ref={coreRef} material={coreMat}>
        <sphereGeometry args={[0.7, 64, 64]} />
      </mesh>

      {/* Inner glow */}
      <Sphere args={[0.65, 16, 16]}>
        <meshBasicMaterial color="#4F9EFF" transparent opacity={0.08} />
      </Sphere>

      {/* Orbital rings */}
      <OrbitalRing radius={1.3} tilt={0.3} speed={0.4} />
      <OrbitalRing radius={1.8} tilt={1.1} speed={-0.25} />
      <OrbitalRing radius={2.2} tilt={0.7} speed={0.18} />

      {/* Streaming particles */}
      <StreamParticles />
    </>
  )
}
