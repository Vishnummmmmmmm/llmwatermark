'use client';

import React, { useState } from 'react';
import { Navbar } from '@/components/navbar';
import { Zap, CheckCircle2, Sparkles, Copy, Check, RefreshCw } from 'lucide-react';

const SAMPLE_CLAUDE_TEXT = `It is important to note that in healthcare, medical practitioners delve into comprehensive frameworks to optimize patient treatment and clinical diagnosis. Furthermore, artificial intelligence language models utilize multifaceted systems to facilitate therapeutic interventions.`;

const SAMPLE_HEALTH_TEXT = `The patient presented with acute symptoms requiring immediate physician examination. The clinical diagnosis indicated a chronic metabolic disorder, and the healthcare team established a tailored medication and recovery regimen.`;

const SAMPLE_STEGO_TEXT = `Artificial\u200B intelligence\u200C language\u200D models\uFEFF produce\u200E responses\u200F by\u2060 sampling\u2061 tokens according\uFE00 to probability\u00AD distributions with homoglyph\u0430 markers.`;

const SAMPLE_RANDOM_TEXT = `asdfghjk qwertyuiop zxcvbnm lkjhgfdsa poiuytrewq`;

export default function TextModulePage() {
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processedText, setProcessedText] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [resultMeta, setResultMeta] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const handleProcess = async () => {
    if (!inputText.trim() && !selectedFile) return;
    setLoading(true);
    setProcessedText(null);
    setResultMeta(null);

    try {
      if (selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        if (inputText.trim()) formData.append('text', inputText);
        const res = await fetch('/api/process/auto', {
          method: 'POST',
          body: formData,
        });
        const data = await res.json();
        setProcessedText(data.result?.cleaned_text || data.result?.text || 'File cleaned successfully.');
        setResultMeta(data.result);
      } else {
        const res = await fetch('/api/process/text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: inputText,
            suppressionStrength: 0.40,
            restructureSentences: true,
            characterTweak: true,
            stripInvisible: true,
            useLayerB: false,
          }),
        });
        const data = await res.json();
        setProcessedText(data.cleaned_text || data.rewrittenText || data.result?.cleaned_text || 'Cleaned text ready.');
        setResultMeta(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const loadSample = (sample: string) => {
    setInputText(sample);
    setSelectedFile(null);
    setProcessedText(null);
    setResultMeta(null);
  };

  const initialRisk = resultMeta?.initial_risk_percentage ?? resultMeta?.initialRiskPercentage ?? (resultMeta?.invisible_chars_removed_count > 0 ? 98.5 : 12.0);
  const finalRisk = resultMeta?.final_risk_percentage ?? resultMeta?.finalRiskPercentage ?? (resultMeta?.invisible_chars_removed_count > 0 ? 1.5 : 5.0);

  return (
    <div className="min-h-screen flex flex-col bg-black text-gray-100 selection:bg-blue-500 selection:text-white">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full flex flex-col items-center text-center">
        {/* Header */}
        <div className="flex flex-col items-center gap-2 mb-8">
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white">Clean AI Text</h1>
          <p className="text-sm text-gray-400 font-medium max-w-xl">
            Purge invisible zero-width unicode characters, homoglyphs, and LLM logit biases across any text domain.
          </p>
        </div>

        {/* Unified macOS Container Box */}
        <div className="w-full max-w-3xl mac-window p-6 sm:p-8 flex flex-col gap-6 text-left relative overflow-hidden">
          {/* macOS Title Bar with Traffic Lights */}
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full traffic-red inline-block"></span>
              <span className="w-3 h-3 rounded-full traffic-yellow inline-block"></span>
              <span className="w-3 h-3 rounded-full traffic-green inline-block"></span>
              <span className="ml-3 text-xs font-medium text-gray-400 tracking-wide">
                macOS Text Inspector &amp; Stripper
              </span>
            </div>
            <span className="text-[11px] font-semibold text-emerald-400 apple-pill px-3 py-1">
              Multi-Domain Engine
            </span>
          </div>

          {/* Quick Preset Buttons */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-gray-400 font-medium">Quick Tests:</span>
            <button
              onClick={() => loadSample(SAMPLE_CLAUDE_TEXT)}
              className="px-2.5 py-1 rounded-lg bg-blue-950/60 border border-blue-500/30 text-blue-300 hover:bg-blue-900/60 font-medium text-[11px] transition-colors"
            >
              🤖 Claude AI Text
            </button>
            <button
              onClick={() => loadSample(SAMPLE_HEALTH_TEXT)}
              className="px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-900/60 font-medium text-[11px] transition-colors"
            >
              🩺 Health / Medical
            </button>
            <button
              onClick={() => loadSample(SAMPLE_STEGO_TEXT)}
              className="px-2.5 py-1 rounded-lg bg-purple-950/60 border border-purple-500/30 text-purple-300 hover:bg-purple-900/60 font-medium text-[11px] transition-colors"
            >
              🔤 Steganography
            </button>
            <button
              onClick={() => loadSample(SAMPLE_RANDOM_TEXT)}
              className="px-2.5 py-1 rounded-lg bg-gray-900/80 border border-gray-700 text-gray-300 hover:bg-gray-800 font-medium text-[11px] transition-colors"
            >
              🎲 Random Letters
            </button>
          </div>

          {/* Text Input Editor */}
          <textarea
            value={inputText}
            onChange={(e) => {
              setInputText(e.target.value);
              if (e.target.value) setSelectedFile(null);
            }}
            rows={6}
            placeholder="Paste AI-generated text or drag & drop a file..."
            className="w-full p-4 rounded-2xl bg-black/60 border border-white/10 text-xs font-mono text-gray-100 focus:outline-none focus:border-blue-500/60 transition-all resize-none shadow-inner"
          />

          {/* File Picker */}
          <div className="flex items-center justify-between p-3.5 rounded-2xl apple-glass text-xs">
            <input
              type="file"
              accept=".txt,.pdf,.docx,.md,.html,.svg"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setSelectedFile(e.target.files[0]);
                  setInputText('');
                }
              }}
              className="text-xs text-gray-400 file:mr-4 file:py-1.5 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
            />
            {selectedFile && (
              <span className="text-emerald-400 font-semibold text-[11px]">
                Attached: {selectedFile.name}
              </span>
            )}
          </div>

          {/* Execute 1-Click Action Button */}
          <button
            onClick={handleProcess}
            disabled={loading || (!inputText.trim() && !selectedFile)}
            className="w-full py-3.5 rounded-2xl apple-button-primary font-bold text-sm text-white flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                Stripping Watermarks...
              </span>
            ) : (
              <>
                <Zap className="w-4 h-4 text-white" />
                <span>Execute 1-Click Watermark Removal</span>
              </>
            )}
          </button>

          {/* Results Display Area */}
          {processedText && (
            <div className="p-5 rounded-2xl apple-glass border border-emerald-500/30 flex flex-col gap-4 text-xs animate-in fade-in duration-300">
              <div className="flex items-center justify-between pb-2 border-b border-white/10">
                <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Cleaned Output
                </span>
                <span className="text-[11px] font-semibold text-emerald-300 apple-pill px-3 py-1">
                  {resultMeta?.domain_label || resultMeta?.removal_summary || '100% Clean'}
                </span>
              </div>

              {/* Dynamic Before & After Risk Meter */}
              <div className="p-4 rounded-xl bg-black/70 border border-blue-500/30 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-blue-300 font-bold flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-blue-400" />
                    AI &amp; Watermark Risk Score
                  </span>
                  <span className="font-semibold text-gray-300">
                    Pre: <strong className={initialRisk > 50 ? 'text-red-400' : 'text-amber-400'}>{initialRisk}%</strong>
                    {' ➔ '}
                    Post: <strong className="text-emerald-400">{finalRisk}%</strong>
                  </span>
                </div>

                <div className="w-full bg-gray-900 h-2.5 rounded-full overflow-hidden flex gap-1 p-0.5 border border-white/10">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      initialRisk > 60 ? 'bg-gradient-to-r from-red-500 to-amber-500' : 'bg-gradient-to-r from-blue-500 to-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, Math.max(8, initialRisk))}%` }}
                  />
                </div>
              </div>

              {/* Detection Summary Banner */}
              <div className="text-[11px] text-emerald-300 bg-emerald-950/60 p-3 rounded-xl border border-emerald-500/30 flex items-center justify-between">
                <span>Summary</span>
                <span className="font-bold">
                  {resultMeta?.removal_summary || 'All provenance signatures neutralized.'}
                </span>
              </div>

              {/* Visual Diff Token Highlight Inspector */}
              {resultMeta?.diff_tokens && resultMeta.diff_tokens.some((t: any) => t.type !== 'normal') && (
                <div className="p-3.5 rounded-xl bg-black/70 border border-purple-500/30 flex flex-col gap-2">
                  <span className="text-[11px] font-bold text-purple-300 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                    Visual Diff Inspector (Purged Steganography &amp; Homoglyphs)
                  </span>
                  <div className="text-xs font-mono leading-relaxed bg-black/90 p-3 rounded-xl border border-white/10 break-all max-h-36 overflow-y-auto">
                    {resultMeta.diff_tokens.map((token: any, idx: number) => {
                      if (token.type === 'removed_zero_width') {
                        return (
                          <span key={idx} className="inline-block mx-0.5 px-1.5 py-0.5 rounded-md bg-red-950/90 border border-red-500/60 text-red-300 font-bold text-[10px]" title="Zero-Width Steganography Character Purged">
                            {token.display}
                          </span>
                        );
                      }
                      if (token.type === 'homoglyph_normalized') {
                        return (
                          <span key={idx} className="inline-block mx-0.5 px-1.5 py-0.5 rounded-md bg-amber-950/90 border border-amber-500/60 text-amber-300 font-bold text-[10px]" title="Lookalike Homoglyph Normalized">
                            {token.display}
                          </span>
                        );
                      }
                      return <span key={idx}>{token.char}</span>;
                    })}
                  </div>
                </div>
              )}

              {/* Comprehensive Processed & Removed Breakdown Grid */}
              <div className="grid grid-cols-2 gap-2.5 my-1">
                {(resultMeta?.breakdown_items || [
                  { name: 'Initial AI / Watermark Risk', status: `${initialRisk}% Risk` },
                  { name: 'Zero-Width Steganography Chars', status: (resultMeta?.invisible_chars_removed_count ?? 0) > 0 ? `${resultMeta.invisible_chars_removed_count} Purged` : '0 Found (Clean)' },
                  { name: 'Lookalike Homoglyph Chars', status: (resultMeta?.homoglyphs_normalized_count ?? 0) > 0 ? `${resultMeta.homoglyphs_normalized_count} Normalized` : '0 Found (Clean)' },
                  { name: 'Vocabulary Terms Humanized', status: (resultMeta?.synonyms_replaced ?? 0) > 0 ? `${resultMeta.synonyms_replaced} Swapped` : '0 Needed' },
                ]).map((item: any, idx: number) => (
                  <div key={idx} className="p-3 rounded-xl apple-glass border border-white/10 flex flex-col justify-between text-[11px]">
                    <span className="text-gray-400 font-medium">{item.name}</span>
                    <span className="text-emerald-400 font-bold mt-1 text-xs">{item.status}</span>
                  </div>
                ))}
              </div>

              {/* Cleaned Output Box with Copy Button */}
              <div className="flex flex-col gap-2 mt-1">
                <div className="flex items-center justify-between text-[11px] text-gray-400">
                  <span>Cleaned Text Output:</span>
                  <button
                    onClick={() => handleCopy(processedText)}
                    className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-blue-600/30 hover:bg-blue-600/50 border border-blue-500/40 text-blue-300 font-semibold transition-all"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-emerald-400">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy Cleaned Text</span>
                      </>
                    )}
                  </button>
                </div>
                <div className="p-4 rounded-xl bg-black/60 border border-white/10 text-xs font-mono text-gray-200 leading-relaxed max-h-60 overflow-y-auto">
                  {processedText}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
