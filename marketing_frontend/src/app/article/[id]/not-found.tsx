import TeerthLogo from '@/components/TeerthLogo';

export default function NotFound() {
  return (
    <div className='min-h-screen bg-yellow-50 dark:bg-amber-50 flex items-center justify-center'>
      <div className='text-center'>
        <div className='flex justify-center mb-8'>
          <TeerthLogo alt='Teerth Logo' size={200} />
        </div>
        <h1 className='text-4xl font-light text-amber-900 dark:text-amber-900 mb-4'>
          Article Not Found
        </h1>
      </div>
    </div>
  );
}
