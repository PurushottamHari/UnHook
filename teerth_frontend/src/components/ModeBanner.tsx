import React from 'react';

type ModeBannerProps = {
  mode: 'admin' | 'guest';
};

export default function ModeBanner({ mode }: ModeBannerProps) {
  if (mode === 'admin') {
    return (
      <div className="w-full bg-amber-700/95 text-amber-50 px-4 py-2.5 text-center text-sm font-semibold border-b border-amber-800 backdrop-blur-sm sticky top-0 z-50 shadow-md">
        Admin
      </div>
    );
  }
  
  if (mode === 'guest') {
    return (
      <div className="w-full bg-slate-800/95 text-slate-50 px-4 py-2.5 text-center text-sm font-semibold border-b border-slate-900 backdrop-blur-sm sticky top-0 z-50 shadow-md">
        Guest View
      </div>
    );
  }
  
  return null;
}
