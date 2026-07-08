/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['three', '@react-three/fiber', '@react-three/drei', '@react-three/postprocessing'],
  images: {
    formats: ['image/avif', 'image/webp'],
  },
}

export default nextConfig
