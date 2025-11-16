'use client';

interface CategoriesErrorProps {
  message?: string;
}

export default function CategoriesError({ 
  message = 'Unable to load categories' 
}: CategoriesErrorProps) {
  return (
    <div className='text-center text-amber-700 dark:text-amber-800 mb-8'>
      <p className='text-sm text-amber-600 dark:text-amber-700'>
        {message}
      </p>
    </div>
  );
}

