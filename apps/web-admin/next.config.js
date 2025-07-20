/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    transpilePackages: ['@progress-method/shared-types', '@progress-method/database'],
  },
}

module.exports = nextConfig