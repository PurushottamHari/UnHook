'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import TeerthLogo from '@/components/TeerthLogo';
import ProblemCarousel from '@/components/ProblemCarousel';
import WaitlistSection from '@/components/WaitlistSection';
import Breadcrumb from '@/components/navigation/Breadcrumb';

export default function About() {
  const [showAfter, setShowAfter] = useState(false);

  const fadeInUp = {
    initial: { opacity: 0, y: 60 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6, ease: 'easeOut' },
  };

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return (
    <div className='min-h-screen bg-yellow-50 dark:bg-amber-50'>
      <div className='w-full px-4 sm:px-6 lg:px-8 py-8'>
        <div className='max-w-6xl mx-auto'>
          {/* Breadcrumb */}
          <Breadcrumb href="/dashboard" label="Puru's Digest" />
          
          {/* Hero Section */}
          <motion.div
            className='text-center mb-16'
            initial='initial'
            animate='animate'
            variants={fadeInUp}
          >
            <div className='flex justify-center mb-8'>
              <TeerthLogo alt='Teerth Logo' size={200} />
            </div>

            <h1 className='text-4xl md:text-5xl lg:text-6xl font-light text-amber-900 dark:text-amber-900 mb-8 leading-tight tracking-tight'>
              🌱 Reclaim your attention.
            </h1>
            <p className='text-xl md:text-2xl text-amber-700 dark:text-amber-800 font-light leading-relaxed max-w-4xl mx-auto mb-8'>
              Daily reads that sharpen focus instead of scatter it.
            </p>
          </motion.div>

          {/* The Problem Section */}
          <motion.section
            id='problem'
            className='mb-16'
            initial='initial'
            whileInView='animate'
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            <div className='relative bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-amber-200/50 dark:border-amber-300/50 shadow-lg overflow-hidden'>
              <h2 className='text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-4 text-center'>
                The Problem With Feeds
              </h2>

              <p className='text-lg text-amber-700 dark:text-amber-800 font-light text-center mb-8'>
                Social, video, and news feeds — endless streams designed to grab
                your attention.
              </p>

              <motion.div
                className='flex flex-col items-center mb-6 relative z-10'
                variants={fadeInUp}
              >
                <ProblemCarousel
                  cards={[
                    {
                      front: "I'm always learning something new.",
                      back: 'But how much of this sticks? Am I truly reflecting — or just skimming, collecting fleeting knowledge?',
                      icon: '🧠',
                    },
                    {
                      front: 'Endless scroll gives me choice.',
                      back: 'It sparks craving and leaves me empty. The more I scroll, the less satisfied I feel.',
                      icon: '🔄',
                    },
                    {
                      front: 'I feel happy and relaxed while scrolling.',
                      back: "But am I running from my real emotions — numbing what needs attention? Who's quietly keeping me hooked to this fleeting relief?",
                      icon: '🌿',
                    },
                    {
                      front: 'Feeds surprise me with exciting, edgy content.',
                      back: 'But much of it is engineered provocation — sexual, shocking, or agitating — designed to hijack emotion, not nurture focus or clarity.',
                      icon: '🎭',
                    },
                    {
                      front: 'It helps me stay informed.',
                      back: 'But is it neutral facts, or am I being provoked constantly to react?',
                      icon: '📰',
                    },
                    {
                      front: 'Feeds keep me connected.',
                      back: 'Yet in real life, I feel lonelier, more divided, subtly provoked — connection feels shallow.',
                      icon: '🤝',
                    },
                  ]}
                />
              </motion.div>

              <motion.div
                className='mt-12 mb-4'
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
              >
                <motion.p
                  className='text-xl md:text-2xl lg:text-3xl text-amber-900 dark:text-amber-900 font-light leading-relaxed text-center italic max-w-4xl mx-auto'
                  initial={{ opacity: 0 }}
                  whileInView={{ opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 1.2, delay: 0.3, ease: 'easeOut' }}
                >
                  &ldquo;Feeds feel like they serve us — but on retrospection,
                  they quietly shape habits we didn&apos;t choose.&rdquo;
                </motion.p>
              </motion.div>
            </div>
          </motion.section>

          {/* Divider */}
          <div className='flex justify-center mb-16'>
            <div className='w-24 h-px bg-amber-300 dark:bg-amber-400'></div>
          </div>

          {/* We Need Something Section */}
          <motion.div
            className='mb-16'
            initial='initial'
            whileInView='animate'
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            <div className='bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-amber-200/50 dark:border-amber-300/50 shadow-lg'>
              <h2 className='text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-6 text-center'>
                We need something that respects our attention.
              </h2>

              <div className='text-center mb-12'>
                <p className='text-lg text-amber-800 dark:text-amber-900 font-light leading-relaxed italic'>
                  The first step to habits that serve you, not control you.
                </p>
              </div>

              {/* Progress Steps with Connector Line */}
              <motion.div className='relative mb-12' variants={staggerChildren}>
                {/* Vertical Progress Line */}
                <div className='absolute left-8 md:left-1/2 md:transform md:-translate-x-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-amber-300 via-amber-400 to-amber-500 dark:from-amber-400 dark:via-amber-500 dark:to-amber-600'></div>

                {/* Steps */}
                <div className='space-y-12'>
                  {[
                    {
                      step: 1,
                      title: 'Define what matters',
                      text: 'Set themes that align with your goals.',
                      icon: '🎯',
                      bgClass:
                        'bg-gradient-to-br from-amber-50/80 to-amber-100/80 dark:from-amber-100/80 dark:to-amber-200/80',
                    },
                    {
                      step: 2,
                      title: 'Clarity, not noise',
                      text: 'We give you exactly that — no clickbait, no tricks.',
                      icon: '📜',
                      bgClass:
                        'bg-gradient-to-br from-amber-100/80 to-amber-150/80 dark:from-amber-150/80 dark:to-amber-200/80',
                    },
                    {
                      step: 3,
                      title: 'Grow with reflection',
                      text: 'Your digest adapts to make you sharper, not distracted.',
                      icon: '🌱',
                      bgClass:
                        'bg-gradient-to-br from-amber-150/80 to-amber-200/80 dark:from-amber-200/80 dark:to-amber-250/80',
                    },
                  ].map((item, index) => (
                    <motion.div
                      key={index}
                      className='relative flex items-center'
                      variants={fadeInUp}
                    >
                      {/* Step Circle with Icon */}
                      <div className='absolute left-0 md:left-1/2 md:transform md:-translate-x-1/2 w-16 h-16 bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-full border-4 border-amber-300/50 dark:border-amber-400/50 shadow-lg flex items-center justify-center z-10'>
                        <span className='text-2xl'>{item.icon}</span>
                      </div>

                      {/* Step Number Circle */}
                      <div className='absolute left-0 md:left-1/2 md:transform md:-translate-x-1/2 -bottom-2 w-8 h-8 bg-amber-600 dark:bg-amber-700 rounded-full flex items-center justify-center shadow-md z-20'>
                        <span className='text-white font-bold text-sm'>
                          {item.step}
                        </span>
                      </div>

                      {/* Content Card */}
                      <div
                        className={`ml-20 md:ml-0 md:w-1/2 ${index % 2 === 0 ? 'md:mr-auto md:pr-8' : 'md:ml-auto md:pl-8'}`}
                      >
                        <motion.div
                          className='p-6 rounded-2xl border border-amber-200/50 dark:border-amber-300/50 hover:shadow-lg hover:scale-[1.02] transition-all duration-300 bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm'
                          whileHover={{ y: -2 }}
                        >
                          <div className='text-xl font-bold text-amber-800 dark:text-amber-900 mb-3'>
                            Step {item.step} – {item.title}
                          </div>
                          <p className='text-base text-amber-700 dark:text-amber-800 font-light leading-relaxed'>
                            {item.text}
                          </p>
                        </motion.div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* Divider line */}
              <div className='flex justify-center mb-8'>
                <div className='w-32 h-px bg-amber-300 dark:bg-amber-400'></div>
              </div>
            </div>
          </motion.div>

          {/* Divider */}
          <div className='flex justify-center mb-16'>
            <div className='w-24 h-px bg-amber-300 dark:bg-amber-400'></div>
          </div>

          {/* The Transformation Section */}
          <motion.div
            className='mb-16'
            initial='initial'
            whileInView='animate'
            viewport={{ once: true }}
            variants={fadeInUp}
          >
            <div
              className={`rounded-3xl p-8 md:p-12 border backdrop-blur-sm shadow-lg transition-all duration-700 ${
                showAfter
                  ? 'bg-white/80 dark:bg-amber-100/80 border-amber-200/50 dark:border-amber-300/50'
                  : 'bg-white/80 dark:bg-red-100/80 border-red-200/50 dark:border-orange-300/50'
              }`}
            >
              <h2 className='text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-8 text-center'>
                The Transformation
              </h2>

              {/* Toggle */}
              <div className='flex justify-center mb-8'>
                <div className='bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-full p-1 border border-amber-200/50 dark:border-amber-300/50'>
                  <button
                    onClick={() => setShowAfter(false)}
                    className={`px-6 py-2 rounded-full transition-all duration-300 ${
                      !showAfter
                        ? 'bg-red-500 text-white shadow-lg'
                        : 'text-amber-800 dark:text-amber-900 hover:bg-amber-100/50'
                    }`}
                  >
                    Before
                  </button>
                  <button
                    onClick={() => setShowAfter(true)}
                    className={`px-6 py-2 rounded-full transition-all duration-300 ${
                      showAfter
                        ? 'bg-amber-600 text-white shadow-lg'
                        : 'text-amber-800 dark:text-amber-900 hover:bg-amber-100/50'
                    }`}
                  >
                    After
                  </button>
                </div>
              </div>

              <motion.div
                className='text-center'
                key={showAfter ? 'after' : 'before'}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <div
                  className={`p-8 rounded-2xl border mb-6 transition-all duration-700 ${
                    showAfter
                      ? 'bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm border-amber-200/50 dark:border-amber-300/50'
                      : 'bg-white/80 dark:bg-red-100/80 backdrop-blur-sm border-red-200/50 dark:border-orange-300/50'
                  }`}
                >
                  <div
                    className={`transition-colors duration-700 ${
                      showAfter
                        ? 'text-amber-800 dark:text-amber-900'
                        : 'text-red-800 dark:text-red-900'
                    }`}
                  >
                    {showAfter ? (
                      <div className='space-y-8'>
                        <div className='text-center'>
                          <h3 className='text-2xl md:text-3xl font-medium leading-tight mb-2'>
                            This Space Empowers You
                          </h3>
                          <p className='text-lg font-light text-amber-600 dark:text-amber-700 mb-8 sm:mb-6'>
                            You end up feeling…
                          </p>
                        </div>
                        
                        <div className='grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto'>
                          <div className='flex items-center space-x-3 p-4 rounded-2xl bg-amber-50/30 dark:bg-amber-100/20 shadow-sm hover:shadow-md transition-all duration-300'>
                            <div className='flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 dark:from-amber-200 dark:to-amber-300 flex items-center justify-center shadow-sm'>
                              <span className='text-amber-600 dark:text-amber-700 text-sm font-medium'>✓</span>
                            </div>
                            <span className='text-lg font-medium text-amber-800 dark:text-amber-900'>In control</span>
                          </div>
                          
                          <div className='flex items-center space-x-3 p-4 rounded-2xl bg-amber-50/30 dark:bg-amber-100/20 shadow-sm hover:shadow-md transition-all duration-300'>
                            <div className='flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 dark:from-amber-200 dark:to-amber-300 flex items-center justify-center shadow-sm'>
                              <span className='text-amber-600 dark:text-amber-700 text-sm font-medium'>✓</span>
                            </div>
                            <span className='text-lg font-medium text-amber-800 dark:text-amber-900'>Grounded</span>
                          </div>
                          
                          <div className='flex items-center space-x-3 p-4 rounded-2xl bg-amber-50/30 dark:bg-amber-100/20 shadow-sm hover:shadow-md transition-all duration-300'>
                            <div className='flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 dark:from-amber-200 dark:to-amber-300 flex items-center justify-center shadow-sm'>
                              <span className='text-amber-600 dark:text-amber-700 text-sm font-medium'>✓</span>
                            </div>
                            <span className='text-lg font-medium text-amber-800 dark:text-amber-900'>Time preserved</span>
                          </div>
                          
                          <div className='flex items-center space-x-3 p-4 rounded-2xl bg-amber-50/30 dark:bg-amber-100/20 shadow-sm hover:shadow-md transition-all duration-300'>
                            <div className='flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-amber-100 to-amber-200 dark:from-amber-200 dark:to-amber-300 flex items-center justify-center shadow-sm'>
                              <span className='text-amber-600 dark:text-amber-700 text-sm font-medium'>✓</span>
                            </div>
                            <span className='text-lg font-medium text-amber-800 dark:text-amber-900'>Focused</span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className='space-y-8'>
                        <div className='text-center'>
                          <h3 className='text-2xl md:text-3xl font-medium leading-tight mb-2'>
                            Social Feeds Exploit You
                          </h3>
                          <p className='text-lg font-light text-red-600 dark:text-red-700 mb-8 sm:mb-6'>
                            You end up feeling…
                          </p>
                        </div>
                        
                        <div className='grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto'>
                          <div className='flex items-center space-x-3 p-4 rounded-2xl bg-red-50/30 dark:bg-red-100/20 shadow-sm hover:shadow-md transition-all duration-300'>
                            <div className='flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-red-100 to-red-200 dark:from-red-200 dark:to-red-300 flex items-center justify-center shadow-sm'>
                              <span className='text-red-600 dark:text-red-700 text-sm font-medium'>✗</span>
                            </div>
                            <span className='text-lg font-medium text-red-800 dark:text-red-900'>Addicted</span>
                          </div>
                          
                          <div className='flex items-center space-x-3 p-4 rounded-2xl bg-red-50/30 dark:bg-red-100/20 shadow-sm hover:shadow-md transition-all duration-300'>
                            <div className='flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-red-100 to-red-200 dark:from-red-200 dark:to-red-300 flex items-center justify-center shadow-sm'>
                              <span className='text-red-600 dark:text-red-700 text-sm font-medium'>✗</span>
                            </div>
                            <span className='text-lg font-medium text-red-800 dark:text-red-900'>Provoked</span>
                          </div>
                          
                          <div className='flex items-center space-x-3 p-4 rounded-2xl bg-red-50/30 dark:bg-red-100/20 shadow-sm hover:shadow-md transition-all duration-300'>
                            <div className='flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-red-100 to-red-200 dark:from-red-200 dark:to-red-300 flex items-center justify-center shadow-sm'>
                              <span className='text-red-600 dark:text-red-700 text-sm font-medium'>✗</span>
                            </div>
                            <span className='text-lg font-medium text-red-800 dark:text-red-900'>Time drained</span>
                          </div>
                          
                          <div className='flex items-center space-x-3 p-4 rounded-2xl bg-red-50/30 dark:bg-red-100/20 shadow-sm hover:shadow-md transition-all duration-300'>
                            <div className='flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-red-100 to-red-200 dark:from-red-200 dark:to-red-300 flex items-center justify-center shadow-sm'>
                              <span className='text-red-600 dark:text-red-700 text-sm font-medium'>✗</span>
                            </div>
                            <span className='text-lg font-medium text-red-800 dark:text-red-900'>Distracted</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            </div>
          </motion.div>

          {/* Divider */}
          <div className='flex justify-center mb-16'>
            <div className='w-24 h-px bg-amber-300 dark:bg-amber-400'></div>
          </div>

          {/* Final CTA Section */}
          <WaitlistSection variant='concise' />
        </div>
      </div>
    </div>
  );
}

