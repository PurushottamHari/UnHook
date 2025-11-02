'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import TeerthLogoIcon from '@/components/TeerthLogoIcon';
import WaitlistForm from '@/components/WaitlistForm';

interface WaitlistSectionProps {
  variant?: 'detailed' | 'concise';
  title?: string;
  subtitle?: string;
  features?: Array<{
    icon: string;
    text: string;
  }>;
  showFeatures?: boolean;
  showLearnMoreButton?: boolean;
  learnMoreHref?: string;
  className?: string;
}

const defaultFeatures = [
  {
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    text: 'No clickbait, no noise',
  },
  {
    icon: 'M13 10V3L4 14h7v7l9-11h-7z',
    text: 'Focused, meaningful articles',
  },
  {
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
    text: 'Hyper personalized',
  },
  {
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    text: 'Enhance your time and attention',
  },
];

const fadeInUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: 'easeOut' },
};

export default function WaitlistSection({
  variant = 'detailed',
  title,
  features = defaultFeatures,
  showFeatures = true,
  showLearnMoreButton = false,
  learnMoreHref = '/about',
  className = '',
}: WaitlistSectionProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case 'concise':
        return {
          container:
            'bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-amber-200/50 dark:border-amber-300/50 p-8 md:p-12',
          layout: 'max-w-2xl mx-auto',
          title:
            'text-2xl md:text-3xl font-light text-amber-900 dark:text-amber-900 mb-4 leading-tight',
          formVariant: 'concise' as const,
        };
      default: // detailed (used for both dashboard and article)
        return {
          container:
            'mt-16 bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-amber-200/50 dark:border-amber-300/50 p-8 md:p-12',
          layout: 'flex flex-col lg:flex-row gap-8 lg:gap-16',
          title:
            'text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-6 leading-tight',
          formVariant: 'detailed' as const,
        };
    }
  };

  const styles = getVariantStyles();
  const defaultTitle =
    variant === 'concise'
      ? 'Join us, help us shape Teerth'
      : 'Want Full Access?';

  const isConciseVariant = variant === 'concise';

  return (
    <motion.div
      className={`${styles.container} ${className}`}
      initial='initial'
      whileInView='animate'
      viewport={{ once: true }}
      variants={fadeInUp}
    >
      <div className={styles.layout}>
        {isConciseVariant ? (
          // Concise variant - centered layout
          <>
            <div className='text-center mb-8'>
              <div className='flex justify-center mb-6'>
                <TeerthLogoIcon alt='Teerth Logo Icon' size={150} />
              </div>
              <h3 className={styles.title}>{title || defaultTitle}</h3>
            </div>

            <WaitlistForm
              variant={styles.formVariant}
              showLearnMoreButton={showLearnMoreButton}
              learnMoreHref={learnMoreHref}
              source={`waitlist-section-${variant}`}
            />
          </>
        ) : (
          // Detailed variant - side by side layout
          <>
            {/* Left side - Text content */}
            <div className='w-full lg:w-[35%]'>
              {/* Teerth Logo Icon at the top */}
              <div className='flex justify-center mb-6'>
                <TeerthLogoIcon alt='Teerth Logo Icon' size={150} />
              </div>
              
              <h3 className={styles.title}>{title || defaultTitle}</h3>

              {showFeatures && (
                <ul className='space-y-3'>
                  {features.map((feature, index) => (
                    <li key={index} className='flex items-start gap-3'>
                      <div className='flex-shrink-0 w-6 h-6 mt-0.5'>
                        <svg
                          className='w-6 h-6 text-amber-600'
                          fill='none'
                          stroke='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path
                            strokeLinecap='round'
                            strokeLinejoin='round'
                            strokeWidth={2}
                            d={feature.icon}
                          />
                        </svg>
                      </div>
                      <span className='text-amber-800 dark:text-amber-900'>
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>
              )}

               {/* Learn More Button */}
               <div className='mt-6'>
                 <Link
                   href={learnMoreHref}
                   className='inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105'
                 >
                   <span>Learn More</span>
                   <svg
                     className='w-4 h-4'
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
                 </Link>
               </div>

            </div>

            {/* Divider */}
            <div className='hidden lg:block w-px bg-amber-300 dark:bg-amber-400'></div>

            {/* Right side - Form */}
            <div className='w-full lg:w-[60%]'>
              <WaitlistForm
                variant={styles.formVariant}
                showLearnMoreButton={showLearnMoreButton}
                learnMoreHref={learnMoreHref}
                source={`waitlist-section-${variant}`}
              />
            </div>
          </>
        )}
      </div>
    </motion.div>
  );
}
