'use client';

import { useState } from 'react';
import CTAButton from '@/components/CTAButton';
import { submitToWaitlist, WaitlistFormData } from '@/lib/waitlist';

interface WaitlistFormProps {
  variant?: 'detailed' | 'concise';
  showLearnMoreButton?: boolean;
  learnMoreHref?: string;
  className?: string;
  source?: string; // Track where the form was submitted from
}

export default function WaitlistForm({
  variant = 'detailed',
  showLearnMoreButton = true,
  learnMoreHref = '/about',
  className = '',
  source = 'waitlist-form',
}: WaitlistFormProps) {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submitMessage, setSubmitMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) return;

    setIsLoading(true);
    setSubmitMessage('');

    try {
      const formData: WaitlistFormData = {
        email: email.trim(),
        message: message.trim(),
        source: source,
      };

      const result = await submitToWaitlist(formData);

      setSubmitMessage(result.message);

      if (result.success) {
        setIsSubmitted(true);
        setEmail('');
        setMessage('');
      }
    } catch (error) {
      setSubmitMessage(
        'There was an error submitting your information. Please try again.'
      );
      console.error('Form submission error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'concise':
        return {
          container: 'space-y-6',
          input:
            'w-full px-4 py-3 rounded-xl border border-amber-200/50 dark:border-amber-300/50 bg-white/80 dark:bg-amber-100/80 text-amber-800 dark:text-amber-900 placeholder-amber-600/70 dark:placeholder-amber-700/70 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-transparent transition-all duration-300',
          textarea:
            'w-full px-4 py-3 rounded-xl border border-amber-200/50 dark:border-amber-300/50 bg-white/80 dark:bg-amber-100/80 text-amber-800 dark:text-amber-900 placeholder-amber-600/70 dark:placeholder-amber-700/70 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-transparent transition-all duration-300 resize-none',
          button:
            'bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white font-medium py-3 px-8 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-amber-500/50',
          buttonContainer: 'text-center',
          showIcon: true,
        };
      default: // detailed (used for both dashboard and article)
        return {
          container: 'max-w-md mx-auto lg:mx-0',
          input:
            'w-full px-4 py-3 rounded-xl border border-amber-200/50 dark:border-amber-300/50 bg-white/80 dark:bg-amber-100/80 text-amber-800 dark:text-amber-900 placeholder-amber-600/70 dark:placeholder-amber-700/70 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-transparent transition-all duration-300',
          textarea:
            'w-full px-4 py-3 rounded-xl border border-amber-200/50 dark:border-amber-300/50 bg-white/80 dark:bg-amber-100/80 text-amber-800 dark:text-amber-900 placeholder-amber-600/70 dark:placeholder-amber-700/70 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-transparent transition-all duration-300 resize-none',
          button:
            'w-full bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white font-light py-4 px-8 rounded-2xl transition-all duration-300 text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] mb-4',
          buttonContainer: '',
          showIcon: false,
        };
    }
  };

  const styles = getVariantStyles();
  const isConciseVariant = variant === 'concise';

  // Show success message if submitted
  if (isSubmitted) {
    return (
      <div className={`${styles.container} ${className}`}>
        <div className='text-center'>
          <div className='w-16 h-16 bg-amber-100 dark:bg-amber-200 rounded-full flex items-center justify-center mx-auto mb-4'>
            <svg
              className='w-8 h-8 text-amber-600 dark:text-amber-700'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M5 13l4 4L19 7'
              />
            </svg>
          </div>
          <h3 className='text-lg font-light text-amber-900 dark:text-amber-900 mb-2'>
            You&apos;re on the list!
          </h3>
          <p className='text-amber-800 dark:text-amber-800 text-sm font-light'>
            {submitMessage}
          </p>
        </div>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`${styles.container} ${className}`}
    >
      {/* Email Input */}
      <div className={`${isConciseVariant ? 'relative' : 'mb-6'}`}>
        <input
          type='email'
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder='Enter your email address'
          className={styles.input}
          required
          disabled={isLoading}
        />
        {styles.showIcon && (
          <div className='absolute right-3 top-1/2 -translate-y-1/2'>
            <div className='w-6 h-6 bg-purple-500 rounded-md flex items-center justify-center'>
              <span className='text-white text-xs'>❄</span>
            </div>
          </div>
        )}
      </div>

      {/* Message Input */}
      <div className={isConciseVariant ? '' : 'mb-6'}>
        <textarea
          value={message}
          onChange={e => setMessage(e.target.value)}
          placeholder='We would love to hear your thoughts, feedback, or questions…'
          rows={4}
          className={styles.textarea}
          disabled={isLoading}
        />
      </div>

      {/* Submit Message */}
      {submitMessage && (
        <div
          className={`mb-4 p-3 rounded-lg text-sm font-light ${
            submitMessage.includes('Thank you') ||
            submitMessage.includes('already')
              ? 'bg-amber-50 dark:bg-amber-100/50 text-amber-800 dark:text-amber-900 border border-amber-200 dark:border-amber-300'
              : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
          }`}
        >
          {submitMessage}
        </div>
      )}

      {/* Submit Button */}
      <div className={styles.buttonContainer}>
        <button
          type='submit'
          className={styles.button}
          disabled={isLoading || !email.trim()}
        >
          {isLoading ? 'Joining...' : 'Join Waitlist'}
        </button>

        {showLearnMoreButton && (
          <CTAButton
            href={learnMoreHref}
            variant='secondary'
            size='lg'
            className='w-full bg-amber-100 hover:bg-amber-200 text-amber-800 hover:text-amber-900 border border-amber-300 hover:border-amber-400'
          >
            Learn More
          </CTAButton>
        )}
      </div>
    </form>
  );
}
