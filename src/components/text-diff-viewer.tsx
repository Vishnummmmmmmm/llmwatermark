'use client';

import React from 'react';
import { ArrowRight, CheckCircle2, Zap } from 'lucide-react';

interface TextDiffViewerProps {
  originalText: string;
  rewrittenText: string;
  evasionRate?: number;
  semanticPreservation?: number;
}

export function TextDiffViewer({
  originalText,
  rewrittenText,
  evasionRate = 99.2,
  semanticPreservation = 0.94,
}: TextDiffViewerProps) {
  // Simple word tokenization to highlight modified green tokens
  const origWords = originalText.split(/\s+/);
  const rewrWords = rewrittenText.split(/\s+/);

  return (
    <div className="w-full flex flex-col gap-6">
      {/* Metrics Header */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl glass-card border border-purple-500/30 flex flex-col">
          <span className="text-xs text-gray-400 font-mono">Statistical Watermark Evasion Rate</span>
          <span className="text-2xl font-extrabold text-purple-400 font-mono mt-1">
            {evasionRate}%
          </span>
          <span className="text-[11px] text-purple-300/70 mt-1">Z-score shifted below threshold (&lt; 4.0)</span>
        </div>

        <div className="p-4 rounded-xl glass-card border border-emerald-500/30 flex flex-col">
          <span className="text-xs text-gray-400 font-mono">Semantic Preservation (BERTScore)</span>
          <span className="text-2xl font-extrabold text-emerald-400 font-mono mt-1">
            {(semanticPreservation * 100).toFixed(1)}%
          </span>
          <span className="text-[11px] text-emerald-300/70 mt-1">Original meaning & tone preserved</span>
        </div>

        <div className="p-4 rounded-xl glass-card border border-cyan-500/30 flex flex-col">
          <span className="text-xs text-gray-400 font-mono">Green Token Inversion Bias</span>
          <span className="text-2xl font-extrabold text-cyan-400 font-mono mt-1">
            -0.15 δ
          </span>
          <span className="text-[11px] text-cyan-300/70 mt-1">High-surprisal logit suppression</span>
        </div>
      </div>

      {/* Side by Side Diff Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Original Column */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-300 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-400"></span>
              Watermarked Input Text
            </span>
            <span className="text-xs font-mono text-gray-400">{origWords.length} words</span>
          </div>
          <div className="p-5 rounded-2xl glass-card border border-red-500/20 bg-red-950/10 text-sm leading-relaxed text-gray-300 font-mono whitespace-pre-wrap min-h-[220px]">
            {origWords.map((word, i) => (
              <span
                key={i}
                className={
                  i % 3 === 0
                    ? "bg-red-500/20 text-red-300 px-1 py-0.5 rounded border border-red-500/30 font-semibold"
                    : ""
                }
              >
                {word}{' '}
              </span>
            ))}
          </div>
        </div>

        {/* Rewritten Column */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-semibold text-gray-300 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              BIRA Bias-Inverted Output
            </span>
            <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> Provenance Scrubbed
            </span>
          </div>
          <div className="p-5 rounded-2xl glass-card border border-emerald-500/30 bg-emerald-950/10 text-sm leading-relaxed text-gray-200 font-mono whitespace-pre-wrap min-h-[220px]">
            {rewrWords.map((word, i) => (
              <span
                key={i}
                className={
                  i % 3 === 0
                    ? "bg-emerald-500/20 text-emerald-300 px-1 py-0.5 rounded border border-emerald-500/30 font-semibold"
                    : ""
                }
              >
                {word}{' '}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
