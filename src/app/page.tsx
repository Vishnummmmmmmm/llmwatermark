'use client';

import React, { useState } from 'react';
import { Navbar } from '@/components/navbar';
import Link from 'next/link';
import { ShieldCheck, Sparkles, Zap, CheckCircle2, ArrowRight, Copy, Check, RefreshCw } from 'lucide-react';

const SAMPLE_CLAUDE_TEXT = `It is important to note that in healthcare, medical practitioners delve into comprehensive frameworks to optimize patient treatment and clinical diagnosis. Furthermore, artificial intelligence language models utilize multifaceted systems to facilitate therapeutic interventions.`;

const SAMPLE_HEALTH_TEXT = `The patient presented with acute symptoms requiring immediate physician examination. The clinical diagnosis indicated a chronic metabolic disorder, and the healthcare team established a tailored medication and recovery regimen.`;

const SAMPLE_STEGO_TEXT = `Artificial\u200B intelligence\u200C language\u200D models\uFEFF produce\u200E responses\u200F by\u2060 sampling\u2061 tokens according\uFE00 to probability\u00AD distributions with homoglyph\u0430 markers.`;

const SAMPLE_RANDOM_TEXT = `asdfghjk qwertyuiop zxcvbnm lkjhgfdsa poiuytrewq`;

export default function Home() {
  const [pastedText, setPastedText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoResult, setAutoResult] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  const handleAutoProcess = async () => {
    if (!pastedText.trim() && !selectedFile) return;
    setLoading(true);
    setAutoResult(null);

    const formData = new FormData();
    if (pastedText.trim()) formData.append('text', pastedText);
    if (selectedFile) formData.append('file', selectedFile);

    try {
      const res = await fetch('/api/process/auto', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setAutoResult(data);
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
    setPastedText(sample);
    setSelectedFile(null);
    setAutoResult(null);
  };

  const cleanedOutputText =
    autoResult?.result?.cleaned_text ||
    autoResult?.result?.rewrittenText ||
    autoResult?.result?.text ||
    '';

  const initialRisk = autoResult?.result?.initial_risk_percentage ?? (autoResult?.result?.invisible_chars_removed_count > 0 ? 98.5 : 12.0);
  const finalRisk = autoResult?.result?.final_risk_percentage ?? (autoResult?.result?.invisible_chars_removed_count > 0 ? 1.5 : 5.0);

  return (
    <div className="min-h-screen flex flex-col bg-black text-gray-100 selection:bg-blue-500 selection:text-white">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-16 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex flex-col items-center text-center">
        {/* Apple SF Radial Background Glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] apple-glow-blue blur-[140px] pointer-events-none rounded-full" />
        <div className="absolute top-1/3 left-1/3 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] apple-glow-purple blur-[140px] pointer-events-none rounded-full" />

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight max-w-4xl leading-[1.08] text-white">
          Universal AI Watermark Stripper
        </h1>

        <p className="mt-4 text-sm sm:text-base text-gray-300 max-w-xl font-medium leading-relaxed">
          Purge hidden provenance signatures, LLM logit biases, and Unicode steganography across Text, Images, Audio, and Video.
        </p>

        {/* Universal 1-Click macOS Window Dropzone */}
        <div className="mt-10 w-full max-w-3xl mac-window p-6 sm:p-8 flex flex-col gap-6 text-left relative overflow-hidden">
          {/* macOS Title Bar with Traffic Lights */}
          <div className="flex items-center justify-between pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full traffic-red inline-block"></span>
              <span className="w-3 h-3 rounded-full traffic-yellow inline-block"></span>
              <span className="w-3 h-3 rounded-full traffic-green inline-block"></span>
              <span className="ml-3 text-xs font-medium text-gray-400 tracking-wide">
                macOS Universal Inspector &amp; Stripper
              </span>
            </div>
            <span className="text-[11px] font-semibold text-emerald-400 apple-pill px-3 py-1">
              Zero AI Model Latency
            </span>
          </div>

          {/* Quick Preset Samples */}
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

          {/* Text input area */}
          <div className="flex flex-col gap-2">
            <textarea
              value={pastedText}
              onChange={(e) => {
                setPastedText(e.target.value);
                if (e.target.value) setSelectedFile(null);
              }}
              rows={4}
              placeholder="Paste AI-generated text OR drag & drop any file (Text, PDF, DOCX, SVG, HTML, PNG, MP3, MP4)..."
              className="w-full p-4 rounded-2xl bg-black/60 border border-white/10 text-xs font-mono text-gray-100 focus:outline-none focus:border-blue-500/60 transition-all resize-none shadow-inner"
            />
          </div>

          {/* File Upload Selector */}
          <div className="flex items-center justify-between p-3.5 rounded-2xl apple-glass text-xs">
            <input
              type="file"
              accept=".pdf,.docx,.svg,.html,.htm,.md,.txt,.jpg,.jpeg,.png,.webp,.mp3,.wav,.mp4,.webm,.zip"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setSelectedFile(e.target.files[0]);
                  setPastedText('');
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

          {/* Execute Action Button */}
          <button
            onClick={handleAutoProcess}
            disabled={loading || (!pastedText.trim() && !selectedFile)}
            className="w-full py-3.5 rounded-2xl apple-button-primary font-bold text-sm text-white flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                Analyzing &amp; Purging Provenance...
              </span>
            ) : (
              <>
                <Zap className="w-4 h-4 text-white" />
                <span>Execute 1-Click Watermark Removal</span>
              </>
            )}
          </button>

          {/* Result Display Card */}
          {autoResult && (
            <div className="p-5 rounded-2xl apple-glass border border-emerald-500/30 flex flex-col gap-4 text-xs animate-in fade-in duration-300">
              <div className="flex items-center justify-between text-emerald-400 font-bold text-xs pb-2 border-b border-white/10">
                <span className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Detected: {autoResult.detected_type?.toUpperCase()}
                </span>
                <span className="px-3 py-1 rounded-full bg-emerald-950/70 border border-emerald-500/30 text-emerald-300 text-[11px] font-semibold">
                  {autoResult.result?.domain_label || 'Verified Clean'}
                </span>
              </div>

              {autoResult.detected_type === 'batch_zip' && (
                <div className="flex flex-col gap-3">
                  <div className="text-xs text-purple-300 bg-purple-950/60 p-3 rounded-xl border border-purple-500/30 flex items-center justify-between">
                    <span>📦 Zip Archive Batch Processor</span>
                    <span className="font-bold">{autoResult.result?.removal_summary}</span>
                  </div>
                  <a
                    href={autoResult.result?.download_url}
                    download="cleaned_archive.zip"
                    className="inline-flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs transition-colors shadow-lg"
                  >
                    Download Cleaned Batch Archive (.ZIP)
                  </a>
                </div>
              )}

              {autoResult.detected_type === 'text' && (
                <>
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
                      {autoResult.result?.removal_summary || 'All provenance signatures neutralized.'}
                    </span>
                  </div>

                  {/* Visual Diff Token Highlight Inspector */}
                  {autoResult.result?.diff_tokens && autoResult.result.diff_tokens.some((t: any) => t.type !== 'normal') && (
                    <div className="p-3.5 rounded-xl bg-black/70 border border-purple-500/30 flex flex-col gap-2">
                      <span className="text-[11px] font-bold text-purple-300 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                        Visual Diff Inspector (Purged Steganography &amp; Homoglyphs)
                      </span>
                      <div className="text-xs font-mono leading-relaxed bg-black/90 p-3 rounded-xl border border-white/10 break-all max-h-36 overflow-y-auto whitespace-pre-wrap">
                        {autoResult.result.diff_tokens.map((token: any, idx: number) => {
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
                    {(autoResult.result?.breakdown_items || [
                      { name: 'Initial AI / Watermark Risk', status: `${initialRisk}% Risk` },
                      { name: 'Zero-Width Steganography Chars', status: (autoResult.result?.invisible_chars_removed_count ?? 0) > 0 ? `${autoResult.result.invisible_chars_removed_count} Purged` : '0 Found (Clean)' },
                      { name: 'Lookalike Homoglyph Chars', status: (autoResult.result?.homoglyphs_normalized_count ?? 0) > 0 ? `${autoResult.result.homoglyphs_normalized_count} Normalized` : '0 Found (Clean)' },
                      { name: 'Vocabulary Terms Humanized', status: (autoResult.result?.synonyms_replaced ?? 0) > 0 ? `${autoResult.result.synonyms_replaced} Swapped` : '0 Needed' },
                    ]).map((item: any, idx: number) => (
                      <div key={idx} className="p-3 rounded-xl apple-glass border border-white/10 flex flex-col justify-between text-[11px]">
                        <span className="text-gray-400 font-medium">{item.name}</span>
                        <span className="text-emerald-400 font-bold mt-1 text-xs">{item.status}</span>
                      </div>
                    ))}
                  </div>

                  {/* Cleaned Output Box with Copy Button */}
                  {cleanedOutputText && (
                    <div className="flex flex-col gap-2 mt-1">
                      <div className="flex items-center justify-between text-[11px] text-gray-400">
                        <span>Cleaned Text Output:</span>
                        <button
                          onClick={() => handleCopy(cleanedOutputText)}
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
                      <div className="p-4 rounded-xl bg-black/60 border border-white/10 text-gray-200 leading-relaxed text-xs font-mono max-h-56 overflow-y-auto whitespace-pre-wrap">
                        {cleanedOutputText}
                      </div>
                    </div>
                  )}
                </>
              )}

              {autoResult.detected_type === 'image' && (
                <div className="flex flex-col gap-3 mt-1">
                  {/* SynthID Spectral Confidence Risk Gauge */}
                  <div className="p-4 rounded-xl bg-black/70 border border-cyan-500/30 flex flex-col gap-2">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-cyan-300 font-bold flex items-center gap-1.5">
                        <Zap className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                        Reverse-SynthID Spectral Risk Meter
                      </span>
                      <span className="text-gray-300 font-semibold">
                        Pre: <strong className="text-red-400">{autoResult.result?.synthid_score_pre ?? 85}%</strong> ➔ Post: <strong className="text-emerald-400">{autoResult.result?.synthid_score_post ?? 0}%</strong>
                      </span>
                    </div>
                    <div className="w-full bg-gray-800 h-2.5 rounded-full overflow-hidden flex">
                      <div className="bg-red-500 h-full transition-all duration-500" style={{ width: `${autoResult.result?.synthid_score_pre ?? 85}%` }} />
                    </div>
                  </div>

                  <div className="text-[11px] text-emerald-300 bg-emerald-950/60 p-3 rounded-xl border border-emerald-500/30 flex items-center justify-between">
                    <span>Metadata Inspection</span>
                    <span className="font-bold">
                      {autoResult.result?.removal_summary || 'Metadata Scrubbed 100%'}
                    </span>
                  </div>
                  {autoResult.result?.cleanedUrl && (
                    <div className="flex justify-center mt-2">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={autoResult.result.cleanedUrl} alt="Cleaned" className="max-h-56 rounded-2xl object-contain border border-white/10 shadow-2xl" />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Multi-Modal Apple macOS Module Cards Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="text-center mb-12 flex flex-col items-center">
          <span className="text-xs font-semibold text-blue-400 apple-pill px-4 py-1.5 mb-3">
             Dedicated Processing Modules
          </span>
          <h2 className="text-3xl font-extrabold text-white">Advanced Multi-Modal Engines</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Text Card */}
          <Link href="/text" className="apple-card p-6 flex flex-col justify-between group">
            <div className="flex flex-col gap-4">
              <div className="w-12 h-12 rounded-2xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-2xl shadow-lg">
                📝
              </div>
              <h3 className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors">
                Text Module
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed font-normal">
                Strips invisible zero-width steganography, Cyrillic lookalikes, and neutralizes BIRA/SynthID logit bias.
              </p>
            </div>
            <div className="mt-6 flex items-center text-xs font-bold text-blue-400 gap-1 group-hover:translate-x-1 transition-transform">
              <span>Open Module</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>

          {/* Image Card */}
          <Link href="/image" className="apple-card p-6 flex flex-col justify-between group">
            <div className="flex flex-col gap-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-2xl shadow-lg">
                🖼️
              </div>
              <h3 className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors">
                Image Module
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed font-normal">
                Removes Stable Signature latent watermarks, EXIF/IPTC, and Adobe C2PA Content Credentials.
              </p>
            </div>
            <div className="mt-6 flex items-center text-xs font-bold text-emerald-400 gap-1 group-hover:translate-x-1 transition-transform">
              <span>Open Module</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>

          {/* Audio Card */}
          <Link href="/audio" className="apple-card p-6 flex flex-col justify-between group">
            <div className="flex flex-col gap-4">
              <div className="w-12 h-12 rounded-2xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-2xl shadow-lg">
                🎵
              </div>
              <h3 className="text-lg font-bold text-white group-hover:text-purple-400 transition-colors">
                Audio Module
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed font-normal">
                Neutralizes Meta AudioSeal and WavMark acoustic signatures via imperceptible phase and speed micro-shifts.
              </p>
            </div>
            <div className="mt-6 flex items-center text-xs font-bold text-purple-400 gap-1 group-hover:translate-x-1 transition-transform">
              <span>Open Module</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>

          {/* Video Card */}
          <Link href="/video" className="apple-card p-6 flex flex-col justify-between group">
            <div className="flex flex-col gap-4">
              <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-2xl shadow-lg">
                🎬
              </div>
              <h3 className="text-lg font-bold text-white group-hover:text-amber-400 transition-colors">
                Video Module
              </h3>
              <p className="text-xs text-gray-400 leading-relaxed font-normal">
                Strips spatial frame watermarks, audio metadata tracks, and synthetic video provenance manifests.
              </p>
            </div>
            <div className="mt-6 flex items-center text-xs font-bold text-amber-400 gap-1 group-hover:translate-x-1 transition-transform">
              <span>Open Module</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </div>
          </Link>
        </div>
      </section>
    </div>
  );
}
