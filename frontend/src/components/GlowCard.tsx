import React from "react";

interface GlowCardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
}

export const GlowCard: React.FC<GlowCardProps> = ({ children, className = "", glow = false }) => {
  return (
    <div
      className={`bg-[#191225] border border-[#30203F] rounded-xl transition-all duration-200 ${
        glow ? "shadow-[0_0_20px_-5px_rgba(168,85,247,0.35)] border-purple-500/50" : "hover:border-purple-500/40 hover:shadow-[0_0_15px_-3px_rgba(168,85,247,0.2)]"
      } ${className}`}
    >
      {children}
    </div>
  );
};
