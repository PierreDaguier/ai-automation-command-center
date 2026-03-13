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
        glow: "0 0 0 1px rgba(98,255,155,0.2), 0 12px 40px rgba(3,10,8,0.56)",
      },
      colors: {
        ink: "#050b08",
        panel: "#0f1713",
        edge: "#26382f",
        accent: "#62ff9b",
        signal: "#ffd47a",
        warning: "#ffbf66",
        danger: "#ff7a88",
      },
    },
  },
  plugins: [],
};

export default config;
