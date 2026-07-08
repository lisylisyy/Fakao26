'use client'

import { useEffect, useRef } from 'react'

export default function ScrollProgress() {
  const lineRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const update = () => {
      const el = lineRef.current
      if (!el) return
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
      el.style.width = `${pct}%`
    }
    window.addEventListener('scroll', update, { passive: true })
    return () => window.removeEventListener('scroll', update)
  }, [])

  return (
    <div className="fixed top-0 left-0 right-0 z-[9998] h-px" style={{ background: 'transparent' }}>
      <div
        ref={lineRef}
        className="h-full"
        style={{
          background: 'linear-gradient(90deg, #4F9EFF, #7AE7FF)',
          boxShadow: '0 0 8px rgba(122,231,255,0.8)',
          transition: 'width 0.05s linear',
          width: '0%',
        }}
      />
    </div>
  )
}
