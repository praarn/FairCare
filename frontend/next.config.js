/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Emit a self-contained server bundle (.next/standalone) so the Docker
  // runtime image can be small and doesn't need node_modules.
  output: "standalone",
};

module.exports = nextConfig;
