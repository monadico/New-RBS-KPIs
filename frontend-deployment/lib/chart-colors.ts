// lib/chart-colors.ts
// RBS Brand-Consistent Chart Colors with High Contrast

export const CHART_COLORS = {
  // Primary data series colors (high contrast against dark background)
  primary: "#D0FF12",      // Arctic Lime - Main brand color
  secondary: "#50F895",    // Over Green - High contrast green
  tertiary: "#9FFDFE",     // Focused Cyan - Bright cyan
  quaternary: "#FFB627",   // Under Orange - Warning orange
  quinary: "#EC305D",      // Boxing Pink - Bright pink
  
  // Extended palette for multi-series charts
  extended: [
    "#D0FF12", // Arctic Lime
    "#50F895", // Over Green  
    "#9FFDFE", // Focused Cyan
    "#FFB627", // Under Orange
    "#EC305D", // Boxing Pink
    "#5DD070", // Soccer Green
    "#F07632", // Basketball Orange
    "#1E90FF", // Baseball Blue
    "#8F65F7", // Purple
    "#FF6B35", // Accent Orange
  ],
  
  // Specific use cases
  volume: {
    mon: "#D0FF12",        // Arctic Lime for $MON
    jerry: "#EC305D",      // Boxing Pink for $JERRY
  },
  
  activity: {
    submissions: "#D0FF12", // Arctic Lime for submissions
    bettors: "#50F895",     // Over Green for active bettors
    newBettors: "#9FFDFE",  // Focused Cyan for new bettors
  },
  
  cards: {
    total: "#D0FF12",       // Arctic Lime for total cards
    average: "#1E90FF",     // Baseball Blue for averages
  },
  
  // Card count stacked chart colors (ensuring good contrast)
  cardCounts: [
    "#D0FF12", // 1 card - Arctic Lime
    "#50F895", // 2 cards - Over Green
    "#9FFDFE", // 3 cards - Focused Cyan
    "#FFB627", // 4 cards - Under Orange
    "#EC305D", // 5 cards - Boxing Pink
    "#5DD070", // 6 cards - Soccer Green
    "#F07632", // 7 cards - Basketball Orange
    "#1E90FF", // 8 cards - Baseball Blue
    "#8F65F7", // 9 cards - Purple
    "#FF6B35", // 10+ cards - Accent Orange
  ],
  
  // Gradient definitions for area charts
  gradients: {
    primary: {
      start: "rgba(208, 255, 18, 0.4)",
      end: "rgba(208, 255, 18, 0.05)",
    },
    secondary: {
      start: "rgba(80, 248, 149, 0.4)",
      end: "rgba(80, 248, 149, 0.05)",
    },
    volume: {
      mon: {
        start: "rgba(208, 255, 18, 0.4)",
        end: "rgba(208, 255, 18, 0.05)",
      },
      jerry: {
        start: "rgba(236, 48, 93, 0.4)",
        end: "rgba(236, 48, 93, 0.05)",
      },
    },
  },
  
  // Muted/background colors
  muted: {
    light: "rgba(248, 250, 252, 0.3)",
    medium: "rgba(248, 250, 252, 0.2)",
    dark: "rgba(248, 250, 252, 0.1)",
  },
  
  // Axis and grid colors
  axis: {
    text: "rgba(248, 250, 252, 0.4)",
    line: "rgba(248, 250, 252, 0.1)",
    grid: "rgba(248, 250, 252, 0.05)",
  },
  
  // Cursor and hover colors
  cursor: "rgba(255, 255, 255, 0.02)",
  activeDot: {
    stroke: "#1A1D24",
    glow: "0 0 8px rgba(208, 255, 18, 0.8)",
  },
}

// Helper function to get colors for card count data
export const getCardCountColors = (numCards: number): string[] => {
  return CHART_COLORS.cardCounts.slice(0, numCards)
}

// Helper function to create gradient definitions for Recharts
export const createGradientDefs = () => {
  return [
    {
      id: "primaryGradient",
      stops: [
        { offset: "5%", stopColor: CHART_COLORS.gradients.primary.start },
        { offset: "95%", stopColor: CHART_COLORS.gradients.primary.end },
      ],
    },
    {
      id: "secondaryGradient", 
      stops: [
        { offset: "5%", stopColor: CHART_COLORS.gradients.secondary.start },
        { offset: "95%", stopColor: CHART_COLORS.gradients.secondary.end },
      ],
    },
    {
      id: "monVolumeGradient",
      stops: [
        { offset: "5%", stopColor: CHART_COLORS.gradients.volume.mon.start },
        { offset: "95%", stopColor: CHART_COLORS.gradients.volume.mon.end },
      ],
    },
    {
      id: "jerryVolumeGradient",
      stops: [
        { offset: "5%", stopColor: CHART_COLORS.gradients.volume.jerry.start },
        { offset: "95%", stopColor: CHART_COLORS.gradients.volume.jerry.end },
      ],
    },
  ]
}

export default CHART_COLORS 