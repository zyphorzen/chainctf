import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#0b0f19",
          card: "#111827",
          border: "#1f2937",
          accent: "#10b981",
          cyan: "#06b6d4",
        },
      },
    },
  },
  plugins: [],
};

export default config;
