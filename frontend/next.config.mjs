/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // ⚠ Cho phép build dù còn ESLint errors
    ignoreDuringBuilds: true,
  },
  typescript: {
    // ⚠ Cho phép build dù còn TypeScript errors
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
