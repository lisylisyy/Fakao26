'use client'

import { useRef } from 'react'
import { motion, useInView } from 'framer-motion'

export default function CallToAction() {
  const ref = useRef<HTMLElement>(null)
  const inView = useInView(ref, { once: true, margin: '-10%' })

  return (
    <section ref={ref} className="section relative overflow-hidden">
      {/* Background glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 70% 50% at 50% 50%, rgba(79,158,255,0.06) 0%, transparent 70%)',
        }}
      />

      <div className="max-w-4xl mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        >
          <p
            className="text-xs tracking-widest uppercase mb-8"
            style={{ color: 'rgba(255,255,255,0.3)', fontFamily: 'var(--font-inter)' }}
          >
            Ready to scale globally?
          </p>

          <h2
            className="text-5xl md:text-7xl font-light leading-tight mb-8"
            style={{ fontFamily: 'var(--font-space)' }}
          >
            The world's
            <br />
            <span className="text-gradient">your market.</span>
          </h2>

          <p
            className="text-base mb-12 max-w-md mx-auto leading-relaxed"
            style={{ color: 'rgba(255,255,255,0.4)', fontFamily: 'var(--font-inter)' }}
          >
            Partner with the team that has helped 3,000+ brands achieve their global ambitions.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <a
              href="mailto:contact@linknlatch.com"
              className="group relative inline-flex items-center gap-3 px-10 py-4 rounded-full text-sm text-white overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, rgba(79,158,255,0.35), rgba(122,231,255,0.2))',
                border: '1px solid rgba(79,158,255,0.6)',
                fontFamily: 'var(--font-inter)',
                letterSpacing: '0.06em',
                boxShadow: '0 0 40px rgba(79,158,255,0.15)',
              }}
            >
              <span>Start the conversation</span>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2 12 L12 2 M12 2 H5 M12 2 V9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </a>

            <a
              href="mailto:contact@linknlatch.com"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full text-sm transition-colors duration-300"
              style={{
                color: 'rgba(255,255,255,0.5)',
                border: '1px solid rgba(255,255,255,0.1)',
                fontFamily: 'var(--font-inter)',
                letterSpacing: '0.06em',
              }}
            >
              contact@linknlatch.com
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
