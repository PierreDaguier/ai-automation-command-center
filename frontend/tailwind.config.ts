import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        glow: "0 0 0 1px rgba(120,255,214,0.18), 0 12px 40px rgba(4,12,26,0.45)",
      },
      colors: {
        ink: "#0a0f1a",
        panel: "#12192a",
        edge: "#25314a",
        accent: "#78ffd6",
        signal: "#6ca8ff",
        warning: "#ffcc66",
        danger: "#ff6f6f",
      },
    },
  },
  plugins: [],
};

export default config;
