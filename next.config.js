/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:57019/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
