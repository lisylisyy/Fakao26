'use client'

const links = {
  Company: ['About', 'Careers', 'Press', 'Contact'],
  Services: ['TikTok Commerce', 'AI Platform', 'Cross-border Logistics', 'Brand Strategy'],
  Resources: ['Case Studies', 'Blog', 'Documentation', 'API'],
}

export default function Footer() {
  return (
    <footer
      className="relative border-t py-16"
      style={{ borderColor: 'rgba(255,255,255,0.06)', background: '#070B14' }}
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-16">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-3 mb-6">
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
            </div>
            <p className="text-xs leading-relaxed mb-2" style={{ color: 'rgba(255,255,255,0.3)', fontFamily: 'var(--font-inter)' }}>
              Empowering global commerce through AI, content, technology and data.
            </p>
            <p className="text-xs" style={{ color: 'rgba(255,255,255,0.2)', fontFamily: 'var(--font-inter)' }}>
              杭州凌浪信息技术有限公司
            </p>
          </div>

          {/* Link columns */}
          {Object.entries(links).map(([group, items]) => (
            <div key={group}>
              <p
                className="text-xs tracking-widest uppercase mb-5"
                style={{ color: 'rgba(255,255,255,0.25)', fontFamily: 'var(--font-inter)' }}
              >
                {group}
              </p>
              <ul className="space-y-3">
                {items.map((item) => (
                  <li key={item}>
                    <a
                      href="#"
                      className="text-sm transition-colors duration-200 hover:text-white"
                      style={{ color: 'rgba(255,255,255,0.35)', fontFamily: 'var(--font-inter)' }}
                    >
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div
          className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8 border-t"
          style={{ borderColor: 'rgba(255,255,255,0.05)' }}
        >
          <p className="text-xs" style={{ color: 'rgba(255,255,255,0.2)', fontFamily: 'var(--font-inter)' }}>
            © 2025 LinknLatch. All rights reserved. 杭州凌浪信息技术有限公司
          </p>
          <div className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: '#7AE7FF' }} />
            <span className="text-xs ml-1" style={{ color: 'rgba(255,255,255,0.2)', fontFamily: 'var(--font-inter)' }}>
              Systems operational
            </span>
          </div>
        </div>
      </div>
    </footer>
  )
}
