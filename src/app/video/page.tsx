'use client';

import React, { useState } from 'react';
import { Navbar } from '@/components/navbar';
import { CheckCircle2, Zap } from 'lucide-react';

export default function VideoModulePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleProcess = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch('/api/process/auto', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setResult(data.result);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-black text-gray-100 selection:bg-blue-500 selection:text-white">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full flex flex-col items-center text-center">
        {/* Header */}
        <div className="flex flex-col items-center gap-2 mb-8">
          <h1 className="text-3xl sm:text-5xl font-extrabold text-white">Clean AI Video</h1>
          <p className="text-sm text-gray-400 font-medium max-w-xl">
            Filter video frame latents, container metadata tags, and audio track signatures.
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
                macOS Video Inspector &amp; Stripper
              </span>
            </div>
            <span className="text-[11px] font-semibold text-cyan-400 apple-pill px-3 py-1">
              Zero AI Model Latency
            </span>
          </div>

          {/* File Upload Selector & Drag Box */}
          <div className="p-8 rounded-2xl apple-glass border-2 border-dashed border-white/15 flex flex-col items-center justify-center gap-3 text-center">
            <div className="w-12 h-12 rounded-2xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-2xl shadow-lg">
              🎬
            </div>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) setSelectedFile(e.target.files[0]);
              }}
              className="text-xs text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-bold file:bg-cyan-600 file:text-white hover:file:bg-cyan-500 cursor-pointer"
            />
            {selectedFile && (
              <span className="text-xs text-cyan-400 font-semibold mt-2">
                Attached: {selectedFile.name} ({(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)
              </span>
            )}
          </div>

          {/* Execute 1-Click Action Button */}
          <button
            onClick={handleProcess}
            disabled={loading || !selectedFile}
            className="w-full py-3.5 rounded-2xl apple-button-primary font-bold text-sm text-white flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span>Scrubbing Video Metadata...</span>
            ) : (
              <>
                <Zap className="w-4 h-4 text-white" />
                <span>Execute 1-Click Watermark Removal</span>
              </>
            )}
          </button>

          {/* Results Display Area (Directly Inside Container Box Below Button) */}
          {result && (
            <div className="p-5 rounded-2xl apple-glass border border-cyan-500/30 flex flex-col gap-4 text-xs animate-in fade-in duration-300">
              <div className="flex items-center justify-between pb-2 border-b border-white/10">
                <span className="text-xs font-bold text-cyan-400 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                  Cleaned Video Result
                </span>
                <span className="text-[11px] font-semibold text-cyan-300 apple-pill px-3 py-1">
                  {result.removal_summary || 'Video Metadata Scrubbed'}
                </span>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
