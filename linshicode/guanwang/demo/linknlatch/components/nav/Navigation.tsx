'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const links = [
  { label: 'Story', href: '#story' },
  { label: 'Services', href: '#services' },
  { label: 'Network', href: '#network' },
  { label: 'AI Platform', href: '#ai' },
]

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const navRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const scrollTo = (href: string) => {
    setMenuOpen(false)
    const el = document.querySelector(href)
    el?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <>
      <motion.nav
        ref={navRef}
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 2.5, ease: [0.16, 1, 0.3, 1] }}
        className="fixed top-0 left-0 right-0 z-[9000] px-6 py-4"
      >
        <div
          className="max-w-7xl mx-auto flex items-center justify-between rounded-2xl px-6 py-3 transition-all duration-500"
          style={{
            background: scrolled ? 'rgba(7,11,20,0.85)' : 'transparent',
            backdropFilter: scrolled ? 'blur(20px)' : 'none',
            border: scrolled ? '1px solid rgba(255,255,255,0.06)' : '1px solid transparent',
          }}
        >
          {/* Logo */}
          <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: 'rgba(79,158,255,0.15)', border: '1px solid rgba(79,158,255,0.3)' }}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="3" fill="#4F9EFF" />
                <circle cx="8" cy="8" r="7" stroke="#7AE7FF" strokeWidth="0.8" strokeOpacity="0.5" />
              </svg>
            </div>
            <span
              className="text-white text-sm font-medium tracking-widest uppercase"
              style={{ fontFamily: 'var(--font-space)' }}
            >
              LinknLatch
            </span>
          </button>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-8">
            {links.map((l) => (
              <button
                key={l.label}
                onClick={() => scrollTo(l.href)}
                className="text-white/50 hover:text-white text-sm tracking-wider transition-colors duration-300"
                style={{ fontFamily: 'var(--font-inter)' }}
              >
                {l.label}
              </button>
            ))}
          </div>

          {/* CTA */}
          <div className="flex items-center gap-4">
            <a
              href="mailto:contact@linknlatch.com"
              className="hidden md:flex items-center gap-2 text-sm px-5 py-2 rounded-full text-white transition-all duration-300"
              style={{
                background: 'rgba(79,158,255,0.15)',
                border: '1px solid rgba(79,158,255,0.4)',
                fontFamily: 'var(--font-inter)',
              }}
            >
              Contact Us
            </a>

            {/* Mobile hamburger */}
            <button
              className="md:hidden flex flex-col gap-1.5 p-1"
              onClick={() => setMenuOpen((v) => !v)}
              aria-label="Toggle menu"
            >
              <span
                className="block w-5 h-px bg-white transition-all duration-300"
                style={{ transform: menuOpen ? 'rotate(45deg) translate(2px, 2px)' : 'none' }}
              />
              <span
                className="block w-5 h-px bg-white transition-all duration-300"
                style={{ opacity: menuOpen ? 0 : 1 }}
              />
              <span
                className="block w-5 h-px bg-white transition-all duration-300"
                style={{ transform: menuOpen ? 'rotate(-45deg) translate(2px, -2px)' : 'none' }}
              />
            </button>
          </div>
        </div>
      </motion.nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-[8999] flex flex-col items-center justify-center md:hidden"
            style={{ background: 'rgba(7,11,20,0.97)', backdropFilter: 'blur(20px)' }}
          >
            {links.map((l, i) => (
              <motion.button
                key={l.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                onClick={() => scrollTo(l.href)}
                className="text-white text-3xl font-light py-4 tracking-wider"
                style={{ fontFamily: 'var(--font-space)' }}
              >
                {l.label}
              </motion.button>
            ))}
            <motion.a
              href="mailto:contact@linknlatch.com"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-8 text-sm px-8 py-3 rounded-full text-white"
              style={{ background: 'rgba(79,158,255,0.2)', border: '1px solid rgba(79,158,255,0.4)' }}
            >
              Contact Us
            </motion.a>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
