'use client'

import { Suspense, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { motion, useInView } from 'framer-motion'
import dynamic from 'next/dynamic'

const EarthScene = dynamic(() => import('./EarthScene'), { ssr: false })

const stats = [
  { value: '80+', label: 'Countries' },
  { value: '3,000+', label: 'Brand Partners' },
  { value: '$2B+', label: 'GMV Managed' },
  { value: '15', label: 'Global Offices' },
]

export default function GlobalNetwork() {
  const ref = useRef<HTMLElement>(null)
  const inView = useInView(ref, { once: true, margin: '-15%' })

  return (
    <section id="network" ref={ref} className="section relative overflow-hidden">
      {/* Subtle section divider glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-24 pointer-events-none"
        style={{ background: 'linear-gradient(to bottom, transparent, rgba(79,158,255,0.4), transparent)' }}
      />

      <div className="max-w-7xl mx-auto px-6">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="mb-20 max-w-xl"
        >
          <p
            className="text-xs tracking-widest uppercase mb-4"
            style={{ color: '#4F9EFF', fontFamily: 'var(--font-inter)' }}
          >
            Global Reach
          </p>
          <h2
            className="text-4xl md:text-5xl font-light leading-tight"
            style={{ fontFamily: 'var(--font-space)' }}
          >
            Commerce moves
            <br />
            <span className="text-gradient">without borders.</span>
          </h2>
        </motion.div>

        {/* Earth + stats layout */}
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* 3D Earth */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={inView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            className="relative aspect-square max-w-lg mx-auto w-full"
          >
            {/* Outer glow ring */}
            <div
              className="absolute inset-0 rounded-full pointer-events-none"
              style={{
                background: 'radial-gradient(circle at 50% 50%, rgba(79,158,255,0.06) 40%, transparent 70%)',
                boxShadow: '0 0 80px rgba(79,158,255,0.12), inset 0 0 60px rgba(79,158,255,0.04)',
              }}
            />
            <Canvas
              dpr={[1, 1.5]}
              camera={{ fov: 45, position: [0, 0, 4.5] }}
              gl={{ alpha: true, antialias: true, powerPreference: 'high-performance' }}
              style={{ background: 'transparent' }}
            >
              <Suspense fallback={null}>
                <EarthScene />
              </Suspense>
            </Canvas>
          </motion.div>

          {/* Stats + copy */}
          <div className="space-y-12">
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-lg leading-relaxed"
              style={{ color: 'rgba(255,255,255,0.5)', fontFamily: 'var(--font-inter)' }}
            >
              We connect brands to consumers across every continent — powering cross-border commerce with intelligence,
              speed and precision.
            </motion.p>

            <div className="grid grid-cols-2 gap-6">
              {stats.map((s, i) => (
                <motion.div
                  key={s.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={inView ? { opacity: 1, y: 0 } : {}}
                  transition={{ duration: 0.6, delay: 0.4 + i * 0.1 }}
                  className="glass rounded-2xl p-6"
                >
                  <div
                    className="text-3xl md:text-4xl font-light mb-2 text-gradient"
                    style={{ fontFamily: 'var(--font-space)' }}
                  >
                    {s.value}
                  </div>
                  <div
                    className="text-sm"
                    style={{ color: 'rgba(255,255,255,0.4)', fontFamily: 'var(--font-inter)' }}
                  >
                    {s.label}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
