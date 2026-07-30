import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: "#F5F7F3",
        surface: "#FFFFFF",
        ink: "#12312B",
        "ink-soft": "#4B5F58",
        primary: {
          DEFAULT: "#0E6B5C",
          dark: "#0A4A3F",
          light: "#E4F0EC",
        },
        seal: {
          DEFAULT: "#C98A1B",
          light: "#FBF0DC",
        },
        alert: {
          DEFAULT: "#B23A2E",
          light: "#FBE9E6",
        },
        line: "#D8DED9",
      },
      fontFamily: {
        display: ["Newsreader", '"Noto Sans Devanagari"', "ui-serif", "Georgia", "serif"],
        body: ["Inter", '"Noto Sans Devanagari"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius: {
        card: "14px",
      },
      boxShadow: {
        card: "0 1px 2px rgba(18,49,41,0.06), 0 8px 24px -12px rgba(18,49,41,0.12)",
      },
    },
  },
  plugins: [],
};
export default config;
