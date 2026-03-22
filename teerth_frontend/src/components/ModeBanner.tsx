import React from 'react';

type ModeBannerProps = {
  mode: 'admin' | 'guest';
};

export default function ModeBanner({ mode }: ModeBannerProps) {
  if (mode === 'admin') {
    return (
      <div className="w-full bg-amber-700/95 text-amber-50 px-4 py-2.5 text-center text-sm font-semibold border-b border-amber-800 backdrop-blur-sm sticky top-0 z-50 shadow-md">
        Admin Mode On
      </div>
    );
  }
  
  if (mode === 'guest') {
    return (
      <div className="w-full bg-slate-800/95 text-slate-50 px-4 py-2.5 text-center text-sm border-b border-slate-900 backdrop-blur-sm sticky top-0 z-50 shadow-md">
        <span className="font-semibold text-slate-200 mr-1">Spectator Mode:</span> 
        <span className="text-slate-300">You are currently viewing a read-only spectator experience.</span>
      </div>
    );
  }
  
  return null;
}
