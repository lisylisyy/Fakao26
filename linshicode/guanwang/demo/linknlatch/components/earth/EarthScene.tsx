'use client'

import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { Sphere } from '@react-three/drei'
import * as THREE from 'three'

// Trade route arcs: [lat1, lon1, lat2, lon2]
const ROUTES: [number, number, number, number][] = [
  [31.2, 121.5, 40.7, -74.0],   // Shanghai → New York
  [31.2, 121.5, 51.5, -0.1],    // Shanghai → London
  [22.3, 114.2, 1.3, 103.8],    // HK → Singapore
  [31.2, 121.5, 35.7, 139.7],   // Shanghai → Tokyo
  [31.2, 121.5, 48.9, 2.3],     // Shanghai → Paris
  [22.3, 114.2, 19.1, 72.9],    // HK → Mumbai
  [31.2, 121.5, -33.9, 151.2],  // Shanghai → Sydney
  [30.0, 116.0, 37.8, -122.4],  // China → San Francisco
]

function latLonToVec3(lat: number, lon: number, r = 1.5): [number, number, number] {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lon + 180) * (Math.PI / 180)
  return [
    -r * Math.sin(phi) * Math.cos(theta),
    r * Math.cos(phi),
    r * Math.sin(phi) * Math.sin(theta),
  ]
}

function buildArcPoints(lat1: number, lon1: number, lat2: number, lon2: number, r = 1.5, segments = 80) {
  const start = new THREE.Vector3(...latLonToVec3(lat1, lon1, r))
  const end = new THREE.Vector3(...latLonToVec3(lat2, lon2, r))
  const mid = start.clone().add(end).normalize().multiplyScalar(r * 1.35)

  const curve = new THREE.QuadraticBezierCurve3(start, mid, end)
  return curve.getPoints(segments)
}

function AnimatedArc({ points, delay }: { points: THREE.Vector3[]; delay: number }) {
  const lineObj = useMemo(() => {
    const geo = new THREE.BufferGeometry().setFromPoints(points)
    const mat = new THREE.LineBasicMaterial({
      color: '#7AE7FF',
      transparent: true,
      opacity: 0,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    })
    return new THREE.Line(geo, mat)
  }, [points])

  useFrame(({ clock }) => {
    const t = ((clock.getElapsedTime() + delay) % 4) / 4
    ;(lineObj.material as THREE.LineBasicMaterial).opacity = Math.sin(t * Math.PI) * 0.8
  })

  return <primitive object={lineObj} />
}

function GlobeGrid() {
  const geo = useMemo(() => {
    const pts: THREE.Vector3[] = []
    const r = 1.51

    // Latitude lines
    for (let lat = -80; lat <= 80; lat += 20) {
      for (let lon = 0; lon <= 360; lon += 3) {
        pts.push(new THREE.Vector3(...latLonToVec3(lat, lon, r)))
        pts.push(new THREE.Vector3(...latLonToVec3(lat, lon + 3, r)))
      }
    }
    // Longitude lines
    for (let lon = 0; lon <= 360; lon += 30) {
      for (let lat = -90; lat <= 90; lat += 3) {
        pts.push(new THREE.Vector3(...latLonToVec3(lat, lon, r)))
        pts.push(new THREE.Vector3(...latLonToVec3(lat + 3, lon, r)))
      }
    }
    const g = new THREE.BufferGeometry().setFromPoints(pts)
    return g
  }, [])

  return (
    <lineSegments geometry={geo}>
      <lineBasicMaterial color="#4F9EFF" transparent opacity={0.06} depthWrite={false} />
    </lineSegments>
  )
}

export default function EarthScene() {
  const earthRef = useRef<THREE.Group>(null)

  const arcPoints = useMemo(() => ROUTES.map(([a, b, c, d]) => buildArcPoints(a, b, c, d)), [])

  useFrame(({ clock }) => {
    if (earthRef.current) {
      earthRef.current.rotation.y = clock.getElapsedTime() * 0.08
    }
  })

  return (
    <>
      <ambientLight intensity={0.15} />
      <pointLight color="#4F9EFF" intensity={3} position={[5, 3, 5]} distance={20} />
      <pointLight color="#7AE7FF" intensity={1.5} position={[-5, -2, -5]} distance={15} />

      <group ref={earthRef}>
        {/* Earth sphere */}
        <Sphere args={[1.5, 64, 64]}>
          <meshPhongMaterial
            color="#0a1628"
            emissive="#0d1f3c"
            emissiveIntensity={0.4}
            shininess={30}
          />
        </Sphere>

        {/* Atmosphere glow */}
        <Sphere args={[1.56, 32, 32]}>
          <meshBasicMaterial
            color="#4F9EFF"
            transparent
            opacity={0.04}
            side={THREE.BackSide}
          />
        </Sphere>
        <Sphere args={[1.65, 32, 32]}>
          <meshBasicMaterial
            color="#4F9EFF"
            transparent
            opacity={0.015}
            side={THREE.BackSide}
          />
        </Sphere>

        {/* Grid overlay */}
        <GlobeGrid />

        {/* Trade routes */}
        {arcPoints.map((pts, i) => (
          <AnimatedArc key={i} points={pts} delay={i * 0.5} />
        ))}

        {/* City dots */}
        {ROUTES.flatMap(([lat1, lon1, lat2, lon2], i) => [
          <mesh key={`a${i}`} position={latLonToVec3(lat1, lon1, 1.52)}>
            <sphereGeometry args={[0.015, 8, 8]} />
            <meshBasicMaterial color="#7AE7FF" />
          </mesh>,
          <mesh key={`b${i}`} position={latLonToVec3(lat2, lon2, 1.52)}>
            <sphereGeometry args={[0.015, 8, 8]} />
            <meshBasicMaterial color="#7AE7FF" />
          </mesh>,
        ])}
      </group>
    </>
  )
}
