'use client';

import { motion } from 'framer-motion';
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
  const [isFlipped, setIsFlipped] = useState(false);

  return (
    <div
      className='relative h-64 w-full perspective-1000 cursor-pointer group'
      onMouseEnter={() => setIsFlipped(true)}
      onMouseLeave={() => setIsFlipped(false)}
      onClick={() => setIsFlipped(!isFlipped)}
    >
      <motion.div
        className='relative w-full h-full preserve-3d'
        animate={{ rotateY: isFlipped ? 180 : 0 }}
        transition={{ duration: 0.6, type: 'spring', stiffness: 260, damping: 20 }}
      >
        {/* Front Side - Illusion */}
        <div 
          className='absolute inset-0 w-full h-full backface-hidden rounded-2xl p-6 flex flex-col items-center justify-center text-center shadow-md'
          style={{
            background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(254,243,199,0.7) 100%)',
            border: '1px solid rgba(251,191,36,0.2)',
          }}
        >
          <div className='text-3xl mb-4 group-hover:scale-110 transition-transform duration-300'>{card.icon}</div>
          <div className='text-xs text-amber-600/70 font-medium mb-2 tracking-wide uppercase'>The Illusion</div>
          <p className='text-amber-900 font-light leading-relaxed'>{card.front}</p>
          <div className='mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300'>
             <span className='text-[10px] text-amber-500 font-medium tracking-widest uppercase'>Reveal reality →</span>
          </div>
        </div>

        {/* Back Side - Reality */}
        <div 
          className='absolute inset-0 w-full h-full backface-hidden rounded-2xl p-6 flex flex-col items-center justify-center text-center shadow-lg'
          style={{
            background: 'linear-gradient(135deg, rgba(248,250,252,0.95) 0%, rgba(241,245,249,0.9) 100%)',
            border: '1px solid rgba(148,163,184,0.3)',
            transform: 'rotateY(180deg)',
          }}
        >
          <div className='text-3xl mb-4'>🔍</div>
          <div className='text-xs text-slate-600/70 font-medium mb-2 tracking-wide uppercase'>The Reality</div>
          <p className='text-slate-800 font-medium leading-relaxed text-sm'>{card.back}</p>
          <div className='mt-4'>
             <span className='text-[10px] text-slate-400 font-medium tracking-widest uppercase'>← Flip back</span>
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
      <div className='text-center mt-12'>
        <p className='text-sm text-amber-600/60 font-light italic'>
          Hover or tap on the cards to see the hidden cost of traditional feeds.
        </p>
      </div>
    </div>
  );
}
