'use client';

import React, { useState, useRef } from 'react';
import { UploadCloud, File, AlertCircle, CheckCircle2, X } from 'lucide-react';

interface FileUploaderProps {
  accept: string;
  maxSizeMB?: number;
  onFileSelected: (file: File) => void;
  label?: string;
  description?: string;
}

export function FileUploader({
  accept,
  maxSizeMB = 50,
  onFileSelected,
  label = "Upload media file",
  description = "Drag & drop your file here or click to browse"
}: FileUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateAndPass = (file: File) => {
    setError(null);
    if (file.size > maxSizeMB * 1024 * 1024) {
      setError(`File size exceeds limit of ${maxSizeMB}MB`);
      return;
    }
    setSelectedFile(file);
    onFileSelected(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndPass(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndPass(e.target.files[0]);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer ${
            dragActive
              ? "border-purple-500 bg-purple-500/10 scale-[0.99]"
              : "border-white/15 bg-white/5 hover:border-purple-500/50 hover:bg-white/[0.07]"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept={accept}
            onChange={handleChange}
            className="hidden"
          />

          <div className="flex flex-col items-center gap-3">
            <div className="w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <UploadCloud className="w-7 h-7 animate-bounce" />
            </div>
            <div>
              <p className="text-base font-semibold text-gray-200">{label}</p>
              <p className="text-xs text-gray-400 mt-1">{description}</p>
            </div>
            <span className="text-[11px] font-mono text-purple-300/70 bg-purple-950/40 px-3 py-1 rounded-full border border-purple-500/20">
              Max file size: {maxSizeMB}MB
            </span>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between p-4 rounded-xl glass-card border border-purple-500/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-200 max-w-[240px] sm:max-w-md truncate">
                {selectedFile.name}
              </p>
              <p className="text-xs text-gray-400 font-mono">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
          </div>

          <button
            onClick={clearFile}
            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}

      {error && (
        <div className="mt-3 flex items-center gap-2 text-xs text-red-400 bg-red-950/30 border border-red-500/30 p-2.5 rounded-lg">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
