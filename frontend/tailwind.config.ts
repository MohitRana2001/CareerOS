import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111318",
        paper: "#f7f3ea",
        ember: "#d8572a",
        moss: "#2f5d50",
        sky: "#4d86c9",
      },
      fontFamily: {
        sans: ["'Space Grotesk'", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
};

export default config;
