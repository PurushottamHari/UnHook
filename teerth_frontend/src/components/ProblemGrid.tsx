'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

interface ProblemCardData {
  front: string;
  back: string;
  icon: string;
}

interface ProblemGridProps {
  cards: ProblemCardData[];
}

function ProblemCard({ card }: { card: ProblemCardData }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className='relative h-64 w-full cursor-pointer group overflow-hidden rounded-2xl'
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => setIsHovered(!isHovered)}
    >
      {/* Reality Base (Always Underneath) */}
      <div 
        className='absolute inset-0 w-full h-full bg-white dark:bg-amber-50 rounded-2xl p-6 flex flex-col items-center justify-center text-center border border-slate-200 dark:border-amber-200/50 shadow-sm'
        style={{
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)',
        }}
      >
        <div className='text-3xl mb-4'>🔍</div>
        <div className='text-[10px] text-slate-500 dark:text-amber-700 font-bold mb-2 tracking-[0.2em] uppercase'>The Reality</div>
        <p className='text-slate-800 dark:text-amber-900 font-medium leading-relaxed text-sm'>{card.back}</p>
        <div className='mt-4'>
           <span className='text-[10px] text-slate-400 font-medium tracking-widest uppercase'>Click to cover</span>
        </div>
      </div>

      {/* Illusion Overlay (Curtains) */}
      <div className='absolute inset-0 w-full h-full flex overflow-hidden pointer-events-none'>
        {/* Left Curtain */}
        <motion.div
          className='w-1/2 h-full bg-gradient-to-br from-amber-100 to-amber-200 border-r border-amber-300/30 shadow-[inset_-2px_0_10px_rgba(251,191,36,0.1)]'
          animate={{ x: isHovered ? '-100%' : '0%' }}
          transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        />
        {/* Right Curtain */}
        <motion.div
          className='w-1/2 h-full bg-gradient-to-bl from-amber-100 to-amber-200 border-l border-amber-300/30 shadow-[inset_2px_0_10px_rgba(251,191,36,0.1)]'
          animate={{ x: isHovered ? '100%' : '0%' }}
          transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        />
      </div>

      {/* Illusion Content (Fades out) */}
      <motion.div
        className='absolute inset-0 w-full h-full flex flex-col items-center justify-center text-center p-6 pointer-events-none z-10'
        animate={{ 
          opacity: isHovered ? 0 : 1,
          scale: isHovered ? 1.1 : 1,
          filter: isHovered ? 'blur(10px)' : 'blur(0px)'
        }}
        transition={{ duration: 0.4 }}
      >
        {/* Decorative elements for the "Illusion" side */}
        <div className='absolute -top-10 -right-10 w-32 h-32 bg-amber-200/20 blur-3xl rounded-full'></div>
        <div className='absolute -bottom-10 -left-10 w-32 h-32 bg-amber-100/30 blur-3xl rounded-full'></div>
        
        <div className='text-3xl mb-4 group-hover:scale-110 transition-transform duration-300'>{card.icon}</div>
        <div className='text-[10px] text-amber-600 font-bold mb-2 tracking-[0.2em] uppercase'>The Illusion</div>
        <p className='text-amber-900 font-light leading-relaxed'>{card.front}</p>
        
        <div className='mt-5'>
           <div className='flex items-center space-x-2 text-amber-700 font-bold'>
             <span className='text-[10px] tracking-widest uppercase'>Reveal truth</span>
             <svg className='w-3.5 h-3.5 animate-pulse' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
               <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M14 5l7 7m0 0l-7 7m7-7H3' />
             </svg>
           </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function ProblemGrid({ cards }: ProblemGridProps) {
  return (
    <div className='w-full'>
      <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6'>
        {cards.map((card, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <ProblemCard card={card} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}
