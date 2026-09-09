import React, { useEffect, useState } from 'react';
import { Zap } from 'lucide-react';
import { checkHealth } from '@/lib/api';

const Header: React.FC = () => {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth().then(setHealthy);
    const interval = setInterval(() => checkHealth().then(setHealthy), 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-white/8 bg-[#0A0A0F]/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-base gradient-text">BizzoraAI</span>
          <span className="hidden sm:block text-xs text-gray-500 border-l border-white/10 pl-2.5 ml-0.5">
            Content Engine
          </span>
        </div>

        {/* Nav */}
        <nav className="hidden md:flex items-center gap-6">
          <span className="text-sm text-violet-300 font-medium">Dashboard</span>
          <span className="text-sm text-gray-600 cursor-not-allowed">History</span>
          <span className="text-sm text-gray-600 cursor-not-allowed">Settings</span>
        </nav>

        {/* Status indicator */}
        <div className="flex items-center gap-2">
          <div className={`status-dot ${healthy === false ? 'bg-red-400' : ''}`} />
          <span className="text-xs text-gray-500 hidden sm:block">
            {healthy === null ? 'Connecting…' : healthy ? 'All Systems Operational' : 'API Offline'}
          </span>
        </div>
      </div>
    </header>
  );
};

export { Header };
