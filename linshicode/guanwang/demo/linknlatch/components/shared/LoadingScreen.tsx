'use client'

import { useEffect, useRef, useState } from 'react'

export default function LoadingScreen() {
  const [visible, setVisible] = useState(true)
  const [progress, setProgress] = useState(0)
  const barRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let p = 0
    const timer = setInterval(() => {
      p += Math.random() * 18 + 4
      if (p >= 100) {
        p = 100
        clearInterval(timer)
        setTimeout(() => setVisible(false), 600)
      }
      setProgress(Math.min(p, 100))
    }, 80)
    return () => clearInterval(timer)
  }, [])

  if (!visible) return null

  return (
    <div
      className="fixed inset-0 z-[99997] flex flex-col items-center justify-center"
      style={{
        background: '#070B14',
        opacity: progress >= 100 ? 0 : 1,
        transition: 'opacity 0.6s ease',
        pointerEvents: progress >= 100 ? 'none' : 'all',
      }}
    >
      {/* Logo mark */}
      <div className="mb-10 flex items-center gap-3">
        <div
          className="w-10 h-10 rounded-xl border border-white/20 flex items-center justify-center"
          style={{ background: 'rgba(79,158,255,0.1)' }}
        >
          <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
            <circle cx="11" cy="11" r="4" fill="#4F9EFF" />
            <circle cx="11" cy="11" r="9" stroke="#4F9EFF" strokeWidth="1" strokeOpacity="0.4" />
            <line x1="11" y1="2" x2="11" y2="0" stroke="#7AE7FF" strokeWidth="1.5" />
            <line x1="20" y1="11" x2="22" y2="11" stroke="#7AE7FF" strokeWidth="1.5" />
            <line x1="11" y1="20" x2="11" y2="22" stroke="#7AE7FF" strokeWidth="1.5" />
            <line x1="2" y1="11" x2="0" y2="11" stroke="#7AE7FF" strokeWidth="1.5" />
          </svg>
        </div>
        <span
          className="text-white tracking-[0.2em] text-sm font-light uppercase"
          style={{ fontFamily: 'var(--font-space)' }}
        >
          LinknLatch
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-48 h-px bg-white/10 relative overflow-hidden rounded-full">
        <div
          ref={barRef}
          className="absolute left-0 top-0 h-full rounded-full"
          style={{
            width: `${progress}%`,
            background: 'linear-gradient(90deg, #4F9EFF, #7AE7FF)',
            transition: 'width 0.1s ease',
            boxShadow: '0 0 10px rgba(79,158,255,0.8)',
          }}
        />
      </div>

      <p className="mt-4 text-white/30 text-xs tracking-widest uppercase" style={{ fontFamily: 'var(--font-inter)' }}>
        {Math.round(progress)}%
      </p>
    </div>
  )
}
