import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#08060D",
          secondary: "#100B18",
          sidebar: "#120D1C",
          card: "#191225",
        },
        purple: {
          primary: "#8B5CF6",
          neon: "#A855F7",
          bright: "#C084FC",
          light: "#D8B4FE",
        },
        border: {
          DEFAULT: "#30203F",
          glow: "rgba(168, 85, 247, 0.4)",
        },
        text: {
          main: "#FFFFFF",
          secondary: "#A1A1AA",
        },
      },
      boxShadow: {
        glow: "0 0 20px -5px rgba(168, 85, 247, 0.35)",
        "glow-lg": "0 0 35px -5px rgba(168, 85, 247, 0.5)",
        "glow-purple": "0 0 15px rgba(139, 92, 246, 0.4)",
        card: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "purple-glass": "linear-gradient(135deg, rgba(25, 18, 37, 0.75) 0%, rgba(16, 11, 24, 0.85) 100%)",
      },
    },
  },
  plugins: [],
};
export default config;
