'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Sparkles, Eye, ShieldCheck } from 'lucide-react';

interface ImageComparisonSliderProps {
  originalUrl: string;
  cleanedUrl: string;
  watermarkFound?: boolean;
}

export function ImageComparisonSlider({
  originalUrl,
  cleanedUrl,
  watermarkFound = true,
}: ImageComparisonSliderProps) {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      let percentage = (x / rect.width) * 100;
      if (percentage < 0) percentage = 0;
      if (percentage > 100) percentage = 100;
      setSliderPosition(percentage);
    },
    []
  );

  const handleTouchMove = (e: React.TouchEvent) => {
    if (isDragging) {
      handleMove(e.touches[0].clientX);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      handleMove(e.clientX);
    }
  };

  return (
    <div className="w-full flex flex-col gap-4">
      <div
        ref={containerRef}
        className="relative w-full h-[400px] sm:h-[480px] rounded-2xl overflow-hidden glass-card border border-white/10 select-none cursor-ew-resize"
        onMouseDown={() => setIsDragging(true)}
        onMouseUp={() => setIsDragging(false)}
        onMouseLeave={() => setIsDragging(false)}
        onMouseMove={handleMouseMove}
        onTouchStart={() => setIsDragging(true)}
        onTouchEnd={() => setIsDragging(false)}
        onTouchMove={handleTouchMove}
      >
        {/* Cleaned Image (Base Layer - Right Side) */}
        <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-black/40">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={cleanedUrl}
            alt="Cleaned watermark removed"
            className="w-full h-full object-contain"
          />
          <div className="absolute top-4 right-4 bg-emerald-950/80 border border-emerald-500/40 backdrop-blur-md px-3 py-1.5 rounded-full text-xs font-mono text-emerald-300 flex items-center gap-1.5 shadow-lg">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Cleaned (Watermark & Metadata Stripped)</span>
          </div>
        </div>

        {/* Original Image (Clipped Overlay - Left Side) */}
        <div
          className="absolute inset-0 h-full overflow-hidden flex items-center justify-center bg-black/40 border-r-2 border-purple-400"
          style={{ width: `${sliderPosition}%` }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={originalUrl}
            alt="Original watermarked"
            className="absolute inset-0 w-full h-full object-contain max-w-none"
            style={{ width: containerRef.current?.clientWidth || '100%' }}
          />
          <div className="absolute top-4 left-4 bg-purple-950/80 border border-purple-500/40 backdrop-blur-md px-3 py-1.5 rounded-full text-xs font-mono text-purple-300 flex items-center gap-1.5 shadow-lg">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span>Original AI Watermarked</span>
          </div>
        </div>

        {/* Divider Handle Bar */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-gradient-to-b from-purple-400 via-indigo-400 to-emerald-400 cursor-ew-resize z-20 shadow-2xl"
          style={{ left: `${sliderPosition}%` }}
        >
          <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-9 h-9 rounded-full bg-cyber-dark border-2 border-purple-400 flex items-center justify-center text-purple-300 shadow-xl">
            <Eye className="w-4 h-4" />
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-gray-400 font-mono">
        <span>◀ Drag handle to inspect before & after</span>
        <span className="text-emerald-400 flex items-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5" /> Evasion Verification: 100% Disrupted
        </span>
      </div>
    </div>
  );
}
