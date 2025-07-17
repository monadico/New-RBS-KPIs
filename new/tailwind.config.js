const { fontFamily } = require("tailwindcss/defaultTheme")

module.exports = {
  darkMode: ["class"],
  content: ["app/**/*.{ts,tsx}", "components/**/*.{ts,tsx}", "lib/**/*.{ts,tsx}", "*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // RareBetSports Official Brand Colors
        // Main Colors
        "rbs-lime": "#D0FF12", // ARCTIC LIME - Primary brand color
        "rbs-black": "#04070D", // BLACK MAIN
        "rbs-white": "#FFFFFF", // JUST WHITE
        
        // Secondary Colors
        "rbs-spring-morn": "#E3FAD4", // SPRING MORN
        "rbs-davys-grey": "#7C8716", // DAVY'S GREY
        "rbs-davys-grey-dark": "#36393A", // DAVY'S GREY DARK
        "rbs-washed-black": "#1E1E29", // WASHED BLACK
        "rbs-washed-black-dark": "#141C1C", // WASHED BLACK DARK
        "rbs-selected-lime": "rgba(208, 255, 18, 0.08)", // SELECTED LIME GRADIENT (8% opacity)
        "rbs-selected-white": "rgba(255, 255, 255, 0.08)", // SELECTED WHITE GRADIENT (8% opacity)
        "rbs-dark-lime": "#9EF909", // DARK LIME
        
        // Service Colors (for alerts, states, feedback)
        "rbs-alert": "#F66660", // ALERT - Error states
        "rbs-over": "#50F895", // OVER - Success states
        "rbs-under": "#FFB627", // UNDER - Warning states
        "rbs-focused": "#9FFDFE", // FOCUSED - Focus states
        "rbs-accent": "#FF6B35", // ACCENT - General accent
        
        // Sport Colors (for data visualization)
        "rbs-soccer": "#5DD070", // SOCCER
        "rbs-basketball": "#F07632", // BASKETBALL
        "rbs-boxing": "#EC305D", // BOXING
        "rbs-baseball": "#1E90FF", // BASEBALL
        
        // Background Colors (using official brand colors)
        "bg-base": "#04070D", // BLACK MAIN
        "bg-alt": "#1E1E29", // WASHED BLACK
        "bg-elevated": "#141C1C", // WASHED BLACK DARK
        "bg-deep": "#04070D", // BLACK MAIN
        "surface": "#1E1E29",
        "surface-elevated": "#141C1C",
        
        // Text Colors
        "text-primary": "#FFFFFF", // JUST WHITE
        "text-secondary": "rgba(255, 255, 255, 0.7)", // 70% opacity
        "text-tertiary": "rgba(255, 255, 255, 0.6)", // 60% opacity
        "text-brand": "#D0FF12", // ARCTIC LIME for highlights
        "text-mono": "#E3FAD4", // SPRING MORN for monospace
        
        // Border Colors
        "border-subtle": "rgba(208, 255, 18, 0.1)",
        "border-medium": "rgba(208, 255, 18, 0.2)",
        "border-brand": "rgba(208, 255, 18, 0.3)",
        
        // Legacy accent colors (keeping for compatibility)
        "accent-primary": "#D0FF12",
        "accent-secondary": "#9EF909",
        "accent-muted": "rgba(208, 255, 18, 0.15)",
        "accent-glow": "rgba(208, 255, 18, 0.25)",

        // Chart Colors (using brand palette)
        "rbs-blue": "#D0FF12", // ARCTIC LIME
        "rbs-orange": "#FF6B35", // ACCENT
        "rbs-green": "#9EF909", // DARK LIME
        "rbs-purple": "#8F65F7", // Purple for variety
        "rbs-red": "#EF4444", // Red for alerts/negative

        // Shadcn/ui colors (kept for compatibility)
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      fontFamily: {
        sans: ["Red Hat Display", ...fontFamily.sans],
        display: ["Sacco", ...fontFamily.sans],
        mono: ["JetBrains Mono", ...fontFamily.mono],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem" }],
        xs: ["0.75rem", { lineHeight: "1.125rem" }],
        sm: ["0.875rem", { lineHeight: "1.375rem" }],
        base: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.125rem", { lineHeight: "1.75rem" }],
        xl: ["1.25rem", { lineHeight: "1.875rem" }],
        "2xl": ["1.5rem", { lineHeight: "2rem" }],
        "3xl": ["1.875rem", { lineHeight: "2.375rem" }],
        "4xl": ["2.25rem", { lineHeight: "2.75rem" }],
        "5xl": ["3rem", { lineHeight: "1" }], // For large metrics
      },
      spacing: {
        4.5: "1.125rem",
        5.5: "1.375rem",
        6.5: "1.625rem",
        7.5: "1.875rem",
        8.5: "2.125rem",
        9.5: "2.375rem",
        15: "3.75rem",
        18: "4.5rem",
        22: "5.5rem",
      },
      borderRadius: {
        "4xl": "2rem",
        "5xl": "2.5rem",
      },
      boxShadow: {
        "card-subtle": "0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2)",
        "card-medium": "0 4px 6px rgba(0, 0, 0, 0.4), 0 2px 4px rgba(0, 0, 0, 0.3)",
        "card-elevated": "0 10px 15px rgba(0, 0, 0, 0.5), 0 4px 6px rgba(0, 0, 0, 0.4)",
        "glow-subtle": "0 0 20px rgba(208, 255, 18, 0.1)",
        "glow-medium": "0 0 30px rgba(208, 255, 18, 0.2)",
        "inner-glow": "inset 0 1px 0 rgba(255, 255, 255, 0.05)",
      },
      animation: {
        "fade-in-up": "fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
        "fade-in-delayed": "fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both",
        "scale-in": "scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
        "glow-pulse": "glowPulse 3s ease-in-out infinite",
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 2s linear infinite",
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        glowPulse: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(208, 255, 18, 0.1)" },
          "50%": { boxShadow: "0 0 40px rgba(208, 255, 18, 0.2)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-4px)" },
        },
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
