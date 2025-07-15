declare module 'react-heatmap-grid' {
  import React from 'react';
  
  interface HeatMapProps {
    xLabels: string[];
    yLabels: string[];
    data: number[][];
    cellStyle?: (background: string, value: number, min: number, max: number, data: any, x: number, y: number) => React.CSSProperties;
    cellRender?: (value: number, x: number, y: number) => string;
    height?: number;
    width?: number;
  }
  
  const HeatMap: React.FC<HeatMapProps>;
  export default HeatMap;
} 