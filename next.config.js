/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:57018/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig