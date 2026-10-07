'use client';

import React, { useState } from 'react';
import { Navbar } from '@/components/navbar';
import { LayoutDashboard, Coins, History, ShieldCheck, CheckCircle2, Clock, Zap, ArrowUpRight } from 'lucide-react';

const MOCK_JOBS: any[] = [];

const PRICING_PACKS = [
  { name: 'Basic', price: '$5', credits: '1,000', costPerCredit: '$0.005', popular: false },
  { name: 'Standard', price: '$10', credits: '2,000', costPerCredit: '$0.005', popular: true },
  { name: 'Professional', price: '$20', credits: '4,000', costPerCredit: '$0.005', popular: false },
  { name: 'Business', price: '$50', credits: '10,000', costPerCredit: '$0.005', popular: false },
];

export default function DashboardPage() {
  const [credits, setCredits] = useState(1000);

  return (
    <div className="min-h-screen flex flex-col bg-black text-gray-100 selection:bg-blue-500 selection:text-white">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full flex flex-col gap-10">
        {/* User Balance macOS Header Card */}
        <div className="p-8 mac-window flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-xl shadow-blue-500/20">
              <Coins className="w-8 h-8 text-amber-300" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-blue-400 font-semibold uppercase tracking-wider">Available Credit Balance</span>
              <span className="text-3xl font-extrabold text-white font-mono mt-0.5">
                {credits.toLocaleString()} Credits
              </span>
              <span className="text-xs text-gray-400 mt-1">18 credits / image • Variable per text length</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setCredits(c => c + 1000)}
              className="apple-button-primary px-6 py-3 font-bold text-xs text-white flex items-center gap-2 shadow-lg"
            >
              <Zap className="w-4 h-4 text-amber-300" />
              <span>Add Mock Credits (+1,000)</span>
            </button>
          </div>
        </div>

        {/* Top-up Packs Grid */}
        <div className="flex flex-col gap-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-blue-400" />
            Credit Refill Packs
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {PRICING_PACKS.map((pack, index) => (
              <div
                key={index}
                className={`p-6 rounded-2xl apple-card border flex flex-col justify-between relative transition-all ${
                  pack.popular
                    ? 'border-blue-500/60 shadow-xl shadow-blue-500/10 scale-[1.02]'
                    : 'border-white/10'
                }`}
              >
                {pack.popular && (
                  <span className="absolute top-3 right-3 bg-blue-600 text-white text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full apple-pill">
                    Most Popular
                  </span>
                )}
                <div>
                  <span className="text-xs text-gray-400 font-medium">{pack.name} Pack</span>
                  <div className="text-3xl font-extrabold text-white mt-1">{pack.price}</div>
                  <div className="text-sm font-semibold text-blue-400 mt-2">
                    {pack.credits} Credits
                  </div>
                  <span className="text-[11px] text-gray-400">{pack.costPerCredit} per credit</span>
                </div>

                <button
                  onClick={() => setCredits(c => c + parseInt(pack.credits.replace(',', '')))}
                  className="mt-6 w-full py-2.5 rounded-full apple-pill hover:bg-blue-600 text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5"
                >
                  <span>Purchase Credits</span>
                  <ArrowUpRight className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Jobs History macOS Window Table */}
        <div className="flex flex-col gap-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-emerald-400" />
            Recent Provenance Removal Jobs
          </h2>

          <div className="mac-window overflow-hidden">
            <div className="flex items-center gap-2 p-4 border-b border-white/10">
              <span className="w-3 h-3 rounded-full traffic-red inline-block"></span>
              <span className="w-3 h-3 rounded-full traffic-yellow inline-block"></span>
              <span className="w-3 h-3 rounded-full traffic-green inline-block"></span>
              <span className="ml-2 text-xs font-medium text-gray-400">Job Activity Console</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-white/5 border-b border-white/10 text-gray-400 uppercase text-[10px] tracking-wider">
                  <tr>
                    <th className="p-4">Job ID</th>
                    <th className="p-4">Module Type</th>
                    <th className="p-4">Input Asset</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Credits</th>
                    <th className="p-4">Metadata</th>
                    <th className="p-4">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-gray-300">
                  {MOCK_JOBS.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="p-8 text-center text-gray-400 font-medium">
                        No activity recorded yet. Process text, image, audio, or video files to view job logs.
                      </td>
                    </tr>
                  ) : (
                    MOCK_JOBS.map((job) => (
                      <tr key={job.id} className="hover:bg-white/5 transition-colors">
                        <td className="p-4 text-blue-400 font-semibold">{job.id}</td>
                        <td className="p-4">{job.type}</td>
                        <td className="p-4 max-w-[200px] truncate">{job.input}</td>
                        <td className="p-4">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full apple-pill text-emerald-300 text-[10px] font-semibold">
                            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                            Completed
                          </span>
                        </td>
                        <td className="p-4 text-amber-400 font-semibold">{job.creditsUsed}</td>
                        <td className="p-4 text-emerald-400 font-semibold">Stripped</td>
                        <td className="p-4 text-gray-400">{job.createdAt}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
