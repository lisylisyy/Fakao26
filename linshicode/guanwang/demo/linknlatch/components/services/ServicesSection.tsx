'use client'

import { useRef } from 'react'
import { motion } from 'framer-motion'

const services = [
  {
    id: '01',
    title: 'TikTok Commerce',
    subtitle: 'Content-driven sales at scale',
    description:
      'We architect full-funnel TikTok strategies — from influencer ecosystems to live commerce operations — converting attention into revenue.',
    accent: '#4F9EFF',
    size: 'large',
  },
  {
    id: '02',
    title: 'AI Brand Growth',
    subtitle: 'Intelligence-first marketing',
    description:
      'Proprietary AI models analyze market signals, optimize creatives, and predict consumer behavior across every channel.',
    accent: '#7AE7FF',
    size: 'small',
  },
  {
    id: '03',
    title: 'Cross-border Logistics',
    subtitle: 'Borderless fulfillment',
    description:
      'End-to-end supply chain intelligence — customs clearance, last-mile delivery, and real-time inventory across 80+ countries.',
    accent: '#8B5CF6',
    size: 'small',
  },
  {
    id: '04',
    title: 'Digital Infrastructure',
    subtitle: 'Built to scale globally',
    description:
      'Enterprise-grade technology stack — from ERP integrations to custom commerce platforms — engineered for hypergrowth.',
    accent: '#4F9EFF',
    size: 'large',
  },
]

const cardVariants = {
  hidden: { opacity: 0, y: 60 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] as const },
  },
}

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.12 },
  },
}

function ServiceCard({ service }: { service: (typeof services)[0] }) {
  const cardRef = useRef<HTMLDivElement>(null)

  const onMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current
    if (!card) return
    const rect = card.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const cx = rect.width / 2
    const cy = rect.height / 2
    const rx = ((y - cy) / cy) * -8
    const ry = ((x - cx) / cx) * 8
    card.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg) scale(1.02)`
    card.style.setProperty('--mx', `${x}px`)
    card.style.setProperty('--my', `${y}px`)
  }

  const onMouseLeave = () => {
    if (cardRef.current) {
      cardRef.current.style.transform = 'perspective(800px) rotateX(0) rotateY(0) scale(1)'
    }
  }

  return (
    <motion.div
      variants={cardVariants}
      className={service.size === 'large' ? 'md:col-span-2' : ''}
    >
      <div
        ref={cardRef}
        onMouseMove={onMouseMove}
        onMouseLeave={onMouseLeave}
        className="relative h-full rounded-3xl p-8 md:p-10 overflow-hidden group cursor-none"
        style={{
          background: 'rgba(255,255,255,0.03)',
          border: '1px solid rgba(255,255,255,0.07)',
          transition: 'transform 0.2s ease',
          minHeight: service.size === 'large' ? '240px' : '300px',
        }}
      >
        {/* Spotlight on hover */}
        <div
          className="absolute inset-0 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-500 rounded-3xl"
          style={{
            background: `radial-gradient(300px circle at var(--mx, 50%) var(--my, 50%), rgba(79,158,255,0.06), transparent 60%)`,
          }}
        />

        {/* Corner accent line */}
        <div
          className="absolute top-0 left-8 right-8 h-px"
          style={{
            background: `linear-gradient(90deg, transparent, ${service.accent}40, transparent)`,
          }}
        />

        <div className={`flex ${service.size === 'large' ? 'items-center gap-12' : 'flex-col'} h-full`}>
          <div className="flex-shrink-0">
            <span
              className="text-xs tracking-widest mb-4 block"
              style={{ color: 'rgba(255,255,255,0.2)', fontFamily: 'var(--font-mono)' }}
            >
              {service.id}
            </span>
            <h3
              className="text-2xl md:text-3xl font-light mb-2 leading-tight"
              style={{ fontFamily: 'var(--font-space)', color: '#fff' }}
            >
              {service.title}
            </h3>
            <p className="text-sm mb-4" style={{ color: service.accent, fontFamily: 'var(--font-inter)' }}>
              {service.subtitle}
            </p>
          </div>

          <p
            className="text-sm leading-relaxed flex-1"
            style={{ color: 'rgba(255,255,255,0.45)', fontFamily: 'var(--font-inter)' }}
          >
            {service.description}
          </p>
        </div>

        {/* Bottom right arrow */}
        <div
          className="absolute bottom-8 right-8 w-8 h-8 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-2 group-hover:translate-x-0"
          style={{ border: `1px solid ${service.accent}60`, color: service.accent }}
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M2 10 L10 2 M10 2 H4 M10 2 V8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </div>
      </div>
    </motion.div>
  )
}

export default function ServicesSection() {
  return (
    <section id="services" className="section relative">
      <div className="max-w-7xl mx-auto px-6">
        {/* Heading — deliberately asymmetric */}
        <div className="flex justify-end mb-20">
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: '-15%' }}
            transition={{ duration: 0.8 }}
            className="max-w-md text-right"
          >
            <p
              className="text-xs tracking-widest uppercase mb-4"
              style={{ color: '#4F9EFF', fontFamily: 'var(--font-inter)' }}
            >
              What We Do
            </p>
            <h2
              className="text-4xl md:text-5xl font-light leading-tight"
              style={{ fontFamily: 'var(--font-space)' }}
            >
              Every layer of
              <br />
              <span className="text-gradient">global commerce.</span>
            </h2>
          </motion.div>
        </div>

        {/* Bento grid — stagger入场 */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-15%' }}
        >
          {services.map((s) => (
            <ServiceCard key={s.id} service={s} />
          ))}
        </motion.div>
      </div>
    </section>
  )
}
