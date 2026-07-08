import Navigation from '@/components/nav/Navigation'
import HeroSection from '@/components/hero/HeroSection'
import CompanyStory from '@/components/story/CompanyStory'
import ServicesSection from '@/components/services/ServicesSection'
import GlobalNetwork from '@/components/earth/GlobalNetwork'
import AIPlatform from '@/components/ai/AIPlatform'
import CallToAction from '@/components/cta/CallToAction'
import Footer from '@/components/footer/Footer'

export default function Home() {
  return (
    <main>
      <Navigation />
      <HeroSection />
      <CompanyStory />
      <ServicesSection />
      <GlobalNetwork />
      <AIPlatform />
      <CallToAction />
      <Footer />
    </main>
  )
}
