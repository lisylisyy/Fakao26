'use client'

import { Suspense, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { motion, useInView } from 'framer-motion'
import dynamic from 'next/dynamic'

const AICore = dynamic(() => import('./AICore'), { ssr: false })

const capabilities = [
  { label: 'Demand Forecasting', value: '98.2%', desc: 'Accuracy' },
  { label: 'Content Generation', value: '<2s', desc: 'Per creative' },
  { label: 'Market Intelligence', value: '140M+', desc: 'Data points daily' },
  { label: 'Conversion Lift', value: '+340%', desc: 'Avg. client growth' },
]

export default function AIPlatform() {
  const ref = useRef<HTMLElement>(null)
  const inView = useInView(ref, { once: true, margin: '-10%' })

  return (
    <section id="ai" ref={ref} className="section relative overflow-hidden">
      {/* Background accent */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(79,158,255,0.04) 0%, transparent 70%)',
        }}
      />

      <div className="max-w-7xl mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-20 items-center">
          {/* Left: 3D AI Core */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={inView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 1.4, ease: [0.16, 1, 0.3, 1] }}
            className="relative aspect-square max-w-md mx-auto w-full"
          >
            {/* Glow aura */}
            <div
              className="absolute inset-0 rounded-full pointer-events-none"
              style={{
                background: 'radial-gradient(circle, rgba(79,158,255,0.08) 30%, transparent 70%)',
              }}
            />
            <Canvas
              dpr={[1, 1.5]}
              camera={{ fov: 50, position: [0, 0, 5] }}
              gl={{ alpha: true, antialias: true, powerPreference: 'high-performance' }}
              style={{ background: 'transparent' }}
            >
              <Suspense fallback={null}>
                <AICore />
              </Suspense>
            </Canvas>
          </motion.div>

          {/* Right: Copy + metrics */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <p
                className="text-xs tracking-widest uppercase mb-5"
                style={{ color: '#4F9EFF', fontFamily: 'var(--font-inter)' }}
              >
                AI Platform
              </p>
              <h2
                className="text-4xl md:text-5xl font-light leading-tight mb-6"
                style={{ fontFamily: 'var(--font-space)' }}
              >
                Intelligence that
                <br />
                <span className="text-gradient">never sleeps.</span>
              </h2>
              <p
                className="text-base leading-relaxed mb-12"
                style={{ color: 'rgba(255,255,255,0.45)', fontFamily: 'var(--font-inter)' }}
              >
                Our proprietary AI engine runs continuously — ingesting market data, optimizing campaigns,
                predicting shifts, and generating creative assets faster than any human team can react.
              </p>
            </motion.div>

            {/* Capability metrics */}
            <div className="space-y-3">
              {capabilities.map((c, i) => (
                <motion.div
                  key={c.label}
                  initial={{ opacity: 0, x: 30 }}
                  animate={inView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.6, delay: 0.4 + i * 0.1 }}
                  className="flex items-center justify-between rounded-2xl px-6 py-4"
                  style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.06)',
                  }}
                >
                  <span
                    className="text-sm"
                    style={{ color: 'rgba(255,255,255,0.5)', fontFamily: 'var(--font-inter)' }}
                  >
                    {c.label}
                  </span>
                  <div className="text-right">
                    <span
                      className="text-xl font-light text-gradient"
                      style={{ fontFamily: 'var(--font-space)' }}
                    >
                      {c.value}
                    </span>
                    <span
                      className="text-xs ml-2"
                      style={{ color: 'rgba(255,255,255,0.3)', fontFamily: 'var(--font-inter)' }}
                    >
                      {c.desc}
                    </span>
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
