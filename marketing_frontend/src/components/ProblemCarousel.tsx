'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ProblemCard {
  front: string;
  back: string;
  icon: string;
}

interface ProblemCarouselProps {
  cards: ProblemCard[];
}

export default function ProblemCarousel({ cards }: ProblemCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isRevealed, setIsRevealed] = useState(false);

  const nextCard = useCallback(() => {
    setCurrentIndex(prev => (prev + 1) % cards.length);
    setIsRevealed(false); // Reset reveal state when changing cards
  }, [cards.length]);

  const prevCard = () => {
    setCurrentIndex(prev => (prev - 1 + cards.length) % cards.length);
    setIsRevealed(false); // Reset reveal state when changing cards
  };

  const goToCard = (index: number) => {
    setCurrentIndex(index);
    setIsRevealed(false); // Reset reveal state when changing cards
  };

  const handleToggle = () => {
    setIsRevealed(!isRevealed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleToggle();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prevCard();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      nextCard();
    }
  };

  // Auto-advance carousel every 8 seconds (optional)
  useEffect(() => {
    const interval = setInterval(() => {
      nextCard();
    }, 8000);

    return () => clearInterval(interval);
  }, [currentIndex, nextCard]);

  const currentCard = cards[currentIndex];

  return (
    <div className='w-full max-w-4xl mx-auto'>
      {/* Main Carousel Container */}
      <div className='relative mb-8'>
        {/* Navigation Arrows */}
        <button
          onClick={prevCard}
          className='absolute left-4 top-1/2 -translate-y-1/2 z-10 bg-white/80 hover:bg-white text-amber-600 hover:text-amber-700 rounded-full p-3 shadow-lg transition-all duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-amber-500/50'
          aria-label='Previous card'
        >
          <svg
            className='w-6 h-6'
            fill='none'
            stroke='currentColor'
            viewBox='0 0 24 24'
          >
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              strokeWidth={2}
              d='M15 19l-7-7 7-7'
            />
          </svg>
        </button>

        <button
          onClick={nextCard}
          className='absolute right-4 top-1/2 -translate-y-1/2 z-10 bg-white/80 hover:bg-white text-amber-600 hover:text-amber-700 rounded-full p-3 shadow-lg transition-all duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-amber-500/50'
          aria-label='Next card'
        >
          <svg
            className='w-6 h-6'
            fill='none'
            stroke='currentColor'
            viewBox='0 0 24 24'
          >
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              strokeWidth={2}
              d='M9 5l7 7-7 7'
            />
          </svg>
        </button>

        {/* Card Container */}
        <div className='relative h-[300px] overflow-hidden rounded-2xl'>
          <div className='flex items-center justify-center h-full'>
            <div className='w-[55%] h-[300px] relative'>
              <AnimatePresence mode='wait'>
                <motion.div
                  key={currentIndex}
                  initial={{ opacity: 0, x: 300 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -300 }}
                  transition={{ duration: 0.5, ease: 'easeInOut' }}
                  className='w-full h-full'
                >
                  <motion.button
                    role='button'
                    tabIndex={0}
                    aria-expanded={isRevealed}
                    aria-label={`${currentCard.front}. Click to reveal more details.`}
                    onClick={handleToggle}
                    onKeyDown={handleKeyDown}
                    className='w-full h-full p-8 rounded-2xl cursor-pointer text-left focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:ring-offset-2 relative group'
                    whileHover={{ y: -2, scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    transition={{ duration: 0.2, ease: 'easeOut' }}
                  >
                    {/* Subtle tap indicator */}
                    <div className='absolute top-4 right-4 text-amber-400/40 group-hover:text-amber-400/60 transition-all duration-300'>
                      <div className='w-2 h-2 rounded-full bg-current opacity-60 group-hover:opacity-80 transition-opacity duration-300'></div>
                    </div>

                    {/* Front Side - Illusion */}
                    <motion.div
                      className='w-full h-full flex flex-col items-center justify-center text-center'
                      style={{
                        background:
                          'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(254,243,199,0.7) 100%)',
                        border: '1px solid rgba(251,191,36,0.3)',
                        boxShadow: '0 4px 20px rgba(251,191,36,0.1)',
                      }}
                      animate={{
                        opacity: isRevealed ? 0 : 1,
                        y: isRevealed ? -10 : 0,
                      }}
                      transition={{ duration: 0.4, ease: 'easeOut' }}
                    >
                      <div className='text-4xl mb-4'>🌀</div>
                      <div className='text-sm text-amber-600/70 font-medium mb-3 tracking-wide'>
                        Feels like...
                      </div>
                      <p className='text-lg text-amber-800 font-light leading-relaxed px-4 mb-4 max-w-2xl'>
                        {currentCard.front}
                      </p>
                      <div className='text-2xl opacity-60'>
                        {currentCard.icon}
                      </div>
                    </motion.div>

                    {/* Back Side - Reality */}
                    <motion.div
                      className='absolute inset-0 w-full h-full flex flex-col items-center justify-center text-center p-8 rounded-2xl'
                      style={{
                        background:
                          'linear-gradient(135deg, rgba(248,250,252,0.95) 0%, rgba(241,245,249,0.9) 100%)',
                        border: '1px solid rgba(148,163,184,0.3)',
                        boxShadow:
                          '0 6px 24px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.5)',
                      }}
                      animate={{
                        opacity: isRevealed ? 1 : 0,
                        y: isRevealed ? 0 : 10,
                      }}
                      transition={{ duration: 0.4, ease: 'easeOut' }}
                    >
                      <div className='text-4xl mb-4'>🔍</div>
                      <div className='text-sm text-slate-600/70 font-medium mb-3 tracking-wide'>
                        In reality...
                      </div>
                      <motion.p
                        className='text-base text-slate-700 font-medium leading-relaxed px-4 max-w-2xl'
                        initial={{ opacity: 0, y: 5 }}
                        animate={{
                          opacity: isRevealed ? 1 : 0,
                          y: isRevealed ? 0 : 5,
                        }}
                        transition={{
                          duration: 0.5,
                          delay: isRevealed ? 0.2 : 0,
                          ease: 'easeOut',
                        }}
                      >
                        {currentCard.back}
                      </motion.p>
                    </motion.div>
                  </motion.button>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>

      {/* Carousel Indicators */}
      <div className='flex justify-center items-center space-x-3 mb-4'>
        {cards.map((_, index) => (
          <button
            key={index}
            onClick={() => goToCard(index)}
            className={`w-3 h-3 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-amber-500/50 ${
              index === currentIndex
                ? 'bg-amber-600 scale-125'
                : 'bg-amber-300 hover:bg-amber-400'
            }`}
            aria-label={`Go to card ${index + 1}`}
          />
        ))}
      </div>

      {/* Card Counter */}
      <div className='text-center'>
        <p className='text-sm text-amber-600/70 font-medium'>
          {currentIndex + 1} of {cards.length}
        </p>
      </div>

      {/* Instructions */}
      <div className='text-center mt-4'>
        <p className='text-sm text-amber-600/70 font-light'>
          Click on cards to flip
        </p>
      </div>
    </div>
  );
}
