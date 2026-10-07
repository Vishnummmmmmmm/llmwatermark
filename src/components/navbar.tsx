'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import { Coins, Sun, Moon, Monitor } from 'lucide-react';

const NAV_TABS = [
  { href: '/', label: 'Home' },
  { href: '/text', label: 'Text' },
  { href: '/image', label: 'Image' },
  { href: '/audio', label: 'Audio' },
  { href: '/video', label: 'Video' },
  { href: '/dashboard', label: 'Dashboard' },
];

export type ThemeMode = 'system' | 'light' | 'dark';

export function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="w-full relative pt-6 pb-12 mb-6 sm:mb-10 z-50">
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-12 flex items-center justify-between">
        {/* Left: Apple macOS Traffic Light & Clean Brand Text */}
        <Link href="/" className="flex items-center gap-3 group z-10">
          <div className="flex items-center gap-1.5 mr-1">
            <span className="w-3 h-3 rounded-full traffic-red inline-block shadow-sm"></span>
            <span className="w-3 h-3 rounded-full traffic-yellow inline-block shadow-sm"></span>
            <span className="w-3 h-3 rounded-full traffic-green inline-block shadow-sm"></span>
          </div>

          <span className="font-bold text-lg tracking-tight text-slate-900 dark:text-white">
            Not This Time
          </span>
        </Link>

        {/* Middle: Dead-Centered Slide Tabs Navigation Bar */}
        <div className="absolute left-1/2 -translate-x-1/2 hidden md:flex items-center z-10">
          <NavbarSlideTabs currentPath={pathname} />
        </div>

        {/* Right: Theme Switcher & Credits Pill */}
        <div className="flex items-center gap-3 z-10">
          <AppleThemeSegmentedToggle />

          <div className="hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-slate-200/80 dark:bg-white/10 border border-slate-300/80 dark:border-white/15 text-amber-700 dark:text-amber-300">
            <Coins className="w-3.5 h-3.5 text-amber-500 animate-pulse" />
            <span>1,000 Credits</span>
          </div>
        </div>
      </div>
    </nav>
  );
}

function AppleThemeSegmentedToggle() {
  const [mode, setMode] = useState<ThemeMode>('dark');
  const [position, setPosition] = useState({ left: 0, width: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const itemsRef = useRef<{ [key in ThemeMode]?: HTMLButtonElement | null }>({});

  useEffect(() => {
    const saved = localStorage.getItem('apple_theme_mode') as ThemeMode | null;
    if (saved) {
      setMode(saved);
      applyTheme(saved);
    } else {
      applyTheme('dark');
    }
  }, []);

  const applyTheme = (selectedMode: ThemeMode) => {
    if (selectedMode === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('light', !prefersDark);
      document.documentElement.classList.toggle('dark', prefersDark);
    } else {
      document.documentElement.classList.toggle('light', selectedMode === 'light');
      document.documentElement.classList.toggle('dark', selectedMode === 'dark');
    }
  };

  const handleSelect = (selectedMode: ThemeMode) => {
    setMode(selectedMode);
    localStorage.setItem('apple_theme_mode', selectedMode);
    applyTheme(selectedMode);
  };

  useEffect(() => {
    const activeEl = itemsRef.current[mode];
    if (activeEl && containerRef.current) {
      setPosition({
        left: activeEl.offsetLeft,
        width: activeEl.offsetWidth,
      });
    }
  }, [mode]);

  return (
    <div
      ref={containerRef}
      className="relative flex items-center p-1 rounded-full border bg-slate-200/80 dark:bg-white/10 border-slate-300/80 dark:border-white/15 shadow-inner select-none"
    >
      {/* System Mac Icon Option */}
      <button
        ref={(el) => { itemsRef.current['system'] = el; }}
        onClick={() => handleSelect('system')}
        title="System Preference"
        className={`relative z-10 p-1.5 rounded-full text-xs transition-colors flex items-center justify-center ${
          mode === 'system' ? 'text-blue-600 dark:text-blue-400 font-bold' : 'text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white'
        }`}
      >
        <Monitor className="w-3.5 h-3.5" />
      </button>

      {/* Light Sun Icon Option */}
      <button
        ref={(el) => { itemsRef.current['light'] = el; }}
        onClick={() => handleSelect('light')}
        title="Light Mode"
        className={`relative z-10 p-1.5 rounded-full text-xs transition-colors flex items-center justify-center ${
          mode === 'light' ? 'text-amber-600 dark:text-amber-400 font-bold' : 'text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white'
        }`}
      >
        <Sun className="w-3.5 h-3.5" />
      </button>

      {/* Dark Moon Icon Option */}
      <button
        ref={(el) => { itemsRef.current['dark'] = el; }}
        onClick={() => handleSelect('dark')}
        title="Dark Mode"
        className={`relative z-10 p-1.5 rounded-full text-xs transition-colors flex items-center justify-center ${
          mode === 'dark' ? 'text-blue-600 dark:text-blue-300 font-bold' : 'text-slate-600 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white'
        }`}
      >
        <Moon className="w-3.5 h-3.5" />
      </button>

      {/* Animated Sliding White/Glass Pill background */}
      <motion.div
        animate={{
          left: position.left,
          width: position.width,
        }}
        transition={{ type: 'spring', stiffness: 200, damping: 24 }}
        className="absolute z-0 h-6 rounded-full bg-white dark:bg-white/20 border border-slate-300 dark:border-white/30 shadow-sm pointer-events-none"
      />
    </div>
  );
}

function NavbarSlideTabs({ currentPath }: { currentPath: string }) {
  const [position, setPosition] = useState({ left: 0, width: 0, opacity: 0 });
  const tabsRef = useRef<(HTMLLIElement | null)[]>([]);

  const activeIndex = NAV_TABS.findIndex((tab) => tab.href === currentPath);

  useEffect(() => {
    if (activeIndex >= 0 && tabsRef.current[activeIndex]) {
      const activeEl = tabsRef.current[activeIndex]!;
      setPosition({
        left: activeEl.offsetLeft,
        width: activeEl.offsetWidth,
        opacity: 1,
      });
    } else {
      setPosition((p) => ({ ...p, opacity: 0 }));
    }
  }, [activeIndex, currentPath]);

  return (
    <ul
      onMouseLeave={() => {
        if (activeIndex >= 0 && tabsRef.current[activeIndex]) {
          const activeEl = tabsRef.current[activeIndex]!;
          setPosition({
            left: activeEl.offsetLeft,
            width: activeEl.offsetWidth,
            opacity: 1,
          });
        }
      }}
      className="relative flex items-center gap-1 p-1 rounded-full border bg-slate-200/80 dark:bg-white/10 border-slate-300/80 dark:border-white/15 shadow-inner select-none"
    >
      {NAV_TABS.map((tab, idx) => {
        const isActive = currentPath === tab.href;
        return (
          <li
            key={tab.href}
            ref={(el) => {
              tabsRef.current[idx] = el;
            }}
            onMouseEnter={(e) => {
              const target = e.currentTarget;
              setPosition({
                left: target.offsetLeft,
                width: target.offsetWidth,
                opacity: 1,
              });
            }}
            className="relative z-10 block"
          >
            <Link
              href={tab.href}
              className={`flex items-center px-4 py-1.5 rounded-full text-xs font-bold tracking-wide transition-colors ${
                isActive
                  ? 'text-white keep-white'
                  : 'text-slate-700 dark:text-gray-300 hover:text-slate-950 dark:hover:text-white'
              }`}
            >
              <span className={isActive ? 'text-white keep-white' : ''}>{tab.label}</span>
            </Link>
          </li>
        );
      })}

      <motion.li
        animate={{ ...position }}
        transition={{ type: 'spring', stiffness: 180, damping: 22 }}
        className="absolute z-0 h-7 rounded-full bg-blue-600 border border-blue-500 shadow-md pointer-events-none"
      />
    </ul>
  );
}
