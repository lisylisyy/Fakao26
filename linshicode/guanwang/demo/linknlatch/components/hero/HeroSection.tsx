'use client'

import { useRef, useEffect, Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { motion } from 'framer-motion'
import dynamic from 'next/dynamic'

const ParticleField = dynamic(() => import('./ParticleField'), { ssr: false })

const EASE = [0.16, 1, 0.3, 1] as const

const textVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.9, delay: 2.8 + i * 0.15, ease: EASE },
  }),
}

export default function HeroSection() {
  const mouse = useRef<[number, number]>([0, 0])
  const heroRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      mouse.current = [
        (e.clientX / window.innerWidth) * 2 - 1,
        -((e.clientY / window.innerHeight) * 2 - 1),
      ]
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [])

  const scrollDown = () => {
    const el = document.getElementById('story')
    el?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section ref={heroRef} className="relative w-full h-screen flex items-center justify-center overflow-hidden">
      {/* R3F Canvas — full bleed background */}
      <div className="absolute inset-0">
        <Canvas
          dpr={[1, 1.5]}
          gl={{ antialias: false, alpha: true, powerPreference: 'high-performance' }}
          camera={{ fov: 60, near: 0.1, far: 100 }}
          style={{ background: 'transparent' }}
        >
          <Suspense fallback={null}>
            <ParticleField mouse={mouse} />
          </Suspense>
        </Canvas>
      </div>

      {/* Radial gradient overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 80% 60% at 50% 50%, transparent 0%, rgba(7,11,20,0.4) 60%, #070B14 100%)',
        }}
      />
      <div
        className="absolute bottom-0 left-0 right-0 h-48 pointer-events-none"
        style={{ background: 'linear-gradient(to top, #070B14, transparent)' }}
      />

      {/* Hero content */}
      <div className="relative z-10 text-center px-6 max-w-5xl mx-auto">
        {/* Eyebrow */}
        <motion.div
          custom={0}
          variants={textVariants}
          initial="hidden"
          animate="visible"
          className="inline-flex items-center gap-2 mb-8 px-4 py-2 rounded-full text-xs tracking-widest uppercase"
          style={{
            background: 'rgba(79,158,255,0.08)',
            border: '1px solid rgba(79,158,255,0.25)',
            color: '#7AE7FF',
            fontFamily: 'var(--font-inter)',
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full animate-pulse"
            style={{ background: '#7AE7FF', boxShadow: '0 0 6px #7AE7FF' }}
          />
          杭州淋浪信息技术有限公司
        </motion.div>

        {/* Main headline */}
        <motion.h1
          custom={1}
          variants={textVariants}
          initial="hidden"
          animate="visible"
          className="text-6xl md:text-8xl lg:text-9xl font-light tracking-tight leading-none mb-6"
          style={{ fontFamily: 'var(--font-space)' }}
        >
          <span className="text-white">Linkn</span>
          <span className="text-gradient">Latch</span>
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          custom={2}
          variants={textVariants}
          initial="hidden"
          animate="visible"
          className="text-lg md:text-xl font-light max-w-lg mx-auto mb-12 leading-relaxed"
          style={{ color: 'rgba(255,255,255,0.55)', fontFamily: 'var(--font-inter)' }}
        >
          Empowering Global Commerce Through AI
        </motion.p>

        {/* CTAs */}
        <motion.div
          custom={3}
          variants={textVariants}
          initial="hidden"
          animate="visible"
          className="flex items-center justify-center gap-4 flex-wrap"
        >
          <button
            onClick={scrollDown}
            className="group relative px-8 py-3.5 rounded-full text-sm text-white overflow-hidden transition-all duration-300"
            style={{
              background: 'linear-gradient(135deg, rgba(79,158,255,0.3), rgba(122,231,255,0.15))',
              border: '1px solid rgba(79,158,255,0.5)',
              fontFamily: 'var(--font-inter)',
              letterSpacing: '0.05em',
            }}
          >
            <span className="relative z-10">Explore</span>
            <div
              className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full"
              style={{ background: 'linear-gradient(135deg, rgba(79,158,255,0.5), rgba(122,231,255,0.3))' }}
            />
          </button>

          <a
            href="mailto:contact@linknlatch.com"
            className="px-8 py-3.5 rounded-full text-sm transition-all duration-300 hover:bg-white/5"
            style={{
              color: 'rgba(255,255,255,0.6)',
              border: '1px solid rgba(255,255,255,0.12)',
              fontFamily: 'var(--font-inter)',
              letterSpacing: '0.05em',
            }}
          >
            Contact Us
          </a>
        </motion.div>
      </div>

      {/* Scroll hint */}
      <motion.button
        onClick={scrollDown}
        custom={4}
        variants={textVariants}
        initial="hidden"
        animate="visible"
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 group"
      >
        <span
          className="text-xs tracking-widest uppercase"
          style={{ color: 'rgba(255,255,255,0.3)', fontFamily: 'var(--font-inter)' }}
        >
          Scroll
        </span>
        <div
          className="w-px h-12 relative overflow-hidden"
          style={{ background: 'rgba(255,255,255,0.1)' }}
        >
          <div
            className="absolute top-0 left-0 w-full"
            style={{
              background: 'linear-gradient(to bottom, #7AE7FF, transparent)',
              height: '40%',
              animation: 'scrollDrop 2s ease-in-out infinite',
            }}
          />
        </div>
      </motion.button>

      <style>{`
        @keyframes scrollDrop {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(350%); }
        }
      `}</style>
    </section>
  )
}
