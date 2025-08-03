"use client"

import React from "react"

type StarBorderProps<T extends React.ElementType> =
  React.ComponentPropsWithoutRef<T> & {
    as?: T
    className?: string
    children?: React.ReactNode
    color?: string
    speed?: React.CSSProperties['animationDuration']
    thickness?: number
  }

const StarBorder = <T extends React.ElementType = "div">({
  as,
  className = "",
  color = "#D0FF12", // Using your brand color
  speed = "6s",
  thickness = 1,
  children,
  ...rest
}: StarBorderProps<T>) => {
  const Component = as || "div"

  return (
    <Component 
      className={`relative inline-block overflow-hidden rounded-lg ${className}`} 
      {...(rest as any)}
      style={{
        padding: `${thickness}px 0`,
        ...(rest as any).style,
      }}
    >
      <div
        className="absolute w-[400%] h-[60%] opacity-90 bottom-[-15px] right-[-300%] rounded-full animate-star-movement-bottom z-0"
        style={{
          background: `radial-gradient(circle, ${color}, transparent 15%)`,
          animationDuration: speed,
          filter: `drop-shadow(0 0 8px ${color})`,
        }}
      ></div>
      <div
        className="absolute w-[400%] h-[60%] opacity-90 top-[-15px] left-[-300%] rounded-full animate-star-movement-top z-0"
        style={{
          background: `radial-gradient(circle, ${color}, transparent 15%)`,
          animationDuration: speed,
          filter: `drop-shadow(0 0 8px ${color})`,
        }}
      ></div>
      <div className="relative z-10">
        {children}
      </div>
    </Component>
  )
}

export default StarBorder 