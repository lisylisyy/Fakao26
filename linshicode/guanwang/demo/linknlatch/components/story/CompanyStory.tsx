'use client'

import { useRef, useEffect } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import type { MotionValue } from 'framer-motion'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const milestones = [
  {
    year: '2019',
    en: 'Founded in Hangzhou with a singular mission: collapse the distance between Chinese innovation and global markets.',
    zh: '创立于杭州，使命明确：消弭中国创新与全球市场之间的距离。',
  },
  {
    year: '2021',
    en: 'Launched the first AI-native TikTok commerce engine. First brand crossed $10M GMV in 90 days.',
    zh: '发布首个 AI 原生 TikTok 电商引擎，首个品牌在 90 天内突破千万美元 GMV。',
  },
  {
    year: '2023',
    en: 'Expanded to 60 countries. Opened operations in North America, Europe and Southeast Asia.',
    zh: '业务拓展至 60 个国家，在北美、欧洲及东南亚全面布局。',
  },
  {
    year: '2025',
    en: 'LinknLatch becomes the operating system for 3,000+ global brands. $2B+ in managed commerce.',
    zh: '淋浪成为 3,000 余个全球品牌的商业操作系统，管理超 200 亿人民币规模的跨境交易。',
  },
]

// Each milestone gets a different parallax depth [startY, endY] in px
const PARALLAX_MAP = [
  [30, -20],
  [10, -45],
  [-15, 35],
  [45, -25],
]

const headlineLines = [
  { text: "We didn't build", cls: 'text-white', extraStyle: {} },
  { text: 'an agency.', cls: 'text-gradient', extraStyle: {} },
  { text: 'We built', cls: 'text-white', extraStyle: {} },
  { text: 'an engine.', cls: '', extraStyle: { color: 'rgba(255,255,255,0.3)' } },
]

function MilestoneItem({
  m,
  i,
  scrollYProgress,
}: {
  m: (typeof milestones)[0]
  i: number
  scrollYProgress: MotionValue<number>
}) {
  const [startY, endY] = PARALLAX_MAP[i]
  const y = useTransform(scrollYProgress, [0, 1], [startY, endY])

  return (
    <motion.div
      style={{ y }}
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true, margin: '-5%' }}
      transition={{ duration: 0.9, delay: 0.1 + i * 0.12 }}
      className={`flex flex-col lg:flex-row gap-8 items-start ${
        i % 2 === 1 ? 'lg:flex-row-reverse' : ''
      }`}
    >
      {/* Year */}
      <div className="lg:w-1/2 flex items-center gap-6">
        {i % 2 === 1 && <div className="hidden lg:block flex-1" />}
        <div className="flex items-center gap-4">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{
              background: 'rgba(79,158,255,0.1)',
              border: '1px solid rgba(79,158,255,0.25)',
            }}
          >
            <div className="w-2 h-2 rounded-full" style={{ background: '#7AE7FF' }} />
          </div>
          <span
            className="text-4xl font-light text-gradient"
            style={{ fontFamily: 'var(--font-space)' }}
          >
            {m.year}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="lg:w-1/2 space-y-3">
        <p
          className="text-base leading-relaxed"
          style={{ color: 'rgba(255,255,255,0.75)', fontFamily: 'var(--font-inter)' }}
        >
          {m.en}
        </p>
        <p
          className="text-sm leading-relaxed"
          style={{ color: 'rgba(255,255,255,0.3)', fontFamily: 'var(--font-inter)' }}
        >
          {m.zh}
        </p>
      </div>
    </motion.div>
  )
}

export default function CompanyStory() {
  const ref = useRef<HTMLElement>(null)
  const headlineRef = useRef<HTMLHeadingElement>(null)

  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  })

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger)
    const el = headlineRef.current
    if (!el) return

    const ctx = gsap.context(() => {
      gsap.from(el.querySelectorAll('.line-inner'), {
        yPercent: 115,
        duration: 0.75,
        stagger: 0.1,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 82%',
          toggleActions: 'play none none none',
        },
      })
    }, el)

    return () => ctx.revert()
  }, [])

  return (
    <section id="story" ref={ref} className="section relative overflow-hidden">
      {/* Vertical timeline line */}
      <div
        className="absolute left-1/2 top-0 bottom-0 w-px hidden lg:block pointer-events-none"
        style={{ background: 'linear-gradient(to bottom, transparent, rgba(79,158,255,0.15), transparent)' }}
      />

      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="mb-24 lg:mb-32">
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-xs tracking-widest uppercase mb-6"
            style={{ color: '#4F9EFF', fontFamily: 'var(--font-inter)' }}
          >
            Our Story
          </motion.p>

          {/* GSAP 逐行遮罩揭示 */}
          <h2
            ref={headlineRef}
            className="text-5xl md:text-7xl font-light leading-none"
            style={{ fontFamily: 'var(--font-space)' }}
          >
            {headlineLines.map((line, li) => (
              <span
                key={li}
                style={{ display: 'block', overflow: 'hidden', paddingBottom: '0.06em' }}
              >
                <span
                  className={`line-inner ${line.cls}`}
                  style={{ display: 'block', ...line.extraStyle }}
                >
                  {line.text}
                </span>
              </span>
            ))}
          </h2>
        </div>

        {/* Milestones — 视差滚动 */}
        <div className="space-y-16 lg:space-y-24">
          {milestones.map((m, i) => (
            <MilestoneItem
              key={m.year}
              m={m}
              i={i}
              scrollYProgress={scrollYProgress}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
