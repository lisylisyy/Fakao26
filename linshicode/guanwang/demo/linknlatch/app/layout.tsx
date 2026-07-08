import type { Metadata } from 'next'
import { Inter, Space_Grotesk } from 'next/font/google'
import './globals.css'
import CustomCursor from '@/components/shared/CustomCursor'
import LoadingScreen from '@/components/shared/LoadingScreen'
import ScrollProgress from '@/components/shared/ScrollProgress'
import LenisProvider from '@/components/shared/LenisProvider'

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
  display: 'swap',
})

const spaceGrotesk = Space_Grotesk({
  variable: '--font-space',
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'LinknLatch — Empowering Global Commerce Through AI',
  description:
    'LinknLatch (杭州淋浪信息技术有限公司) — AI-powered platform for global commerce, TikTok commerce, brand growth and digital infrastructure.',
  keywords: ['AI', 'Global Commerce', 'Cross-border E-commerce', 'TikTok Commerce', 'Brand Growth'],
  openGraph: {
    title: 'LinknLatch — Empowering Global Commerce Through AI',
    description: 'The operating system for global commerce.',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable}`}>
      <body>
        <LenisProvider>
          <LoadingScreen />
          <CustomCursor />
          <ScrollProgress />
          {children}
        </LenisProvider>
      </body>
    </html>
  )
}
