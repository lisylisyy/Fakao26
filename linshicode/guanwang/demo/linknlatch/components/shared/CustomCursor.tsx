'use client'

import { useEffect, useRef } from 'react'

export default function CustomCursor() {
  const dotRef = useRef<HTMLDivElement>(null)
  const ringRef = useRef<HTMLDivElement>(null)
  const pos = useRef({ x: 0, y: 0 })
  const ring = useRef({ x: 0, y: 0 })
  const rafId = useRef<number>(0)

  useEffect(() => {
    const dot = dotRef.current
    const ringEl = ringRef.current
    if (!dot || !ringEl) return

    const onMove = (e: MouseEvent) => {
      pos.current = { x: e.clientX, y: e.clientY }
    }

    const onEnter = () => {
      dot.style.transform = 'translate(-50%,-50%) scale(2.5)'
      ringEl.style.transform = 'translate(-50%,-50%) scale(1.5)'
      ringEl.style.opacity = '0.4'
    }

    const onLeave = () => {
      dot.style.transform = 'translate(-50%,-50%) scale(1)'
      ringEl.style.transform = 'translate(-50%,-50%) scale(1)'
      ringEl.style.opacity = '1'
    }

    const addListeners = () => {
      document.querySelectorAll('a, button, [data-cursor]').forEach((el) => {
        el.addEventListener('mouseenter', onEnter)
        el.addEventListener('mouseleave', onLeave)
      })
    }

    const animate = () => {
      ring.current.x += (pos.current.x - ring.current.x) * 0.12
      ring.current.y += (pos.current.y - ring.current.y) * 0.12

      dot.style.left = pos.current.x + 'px'
      dot.style.top = pos.current.y + 'px'
      ringEl.style.left = ring.current.x + 'px'
      ringEl.style.top = ring.current.y + 'px'

      rafId.current = requestAnimationFrame(animate)
    }

    window.addEventListener('mousemove', onMove)
    addListeners()
    rafId.current = requestAnimationFrame(animate)

    const observer = new MutationObserver(addListeners)
    observer.observe(document.body, { childList: true, subtree: true })

    return () => {
      window.removeEventListener('mousemove', onMove)
      cancelAnimationFrame(rafId.current)
      observer.disconnect()
    }
  }, [])

  return (
    <>
      <div
        ref={dotRef}
        className="fixed pointer-events-none z-[99999] w-2 h-2 rounded-full bg-white"
        style={{ transform: 'translate(-50%,-50%)', transition: 'transform 0.15s ease', mixBlendMode: 'difference' }}
      />
      <div
        ref={ringRef}
        className="fixed pointer-events-none z-[99998] w-8 h-8 rounded-full border border-white/40"
        style={{ transform: 'translate(-50%,-50%)', transition: 'transform 0.3s ease, opacity 0.3s ease' }}
      />
    </>
  )
}
