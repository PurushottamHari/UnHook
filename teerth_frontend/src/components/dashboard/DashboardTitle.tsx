'use client';

interface DashboardTitleProps {
  title?: string;
}

export default function DashboardTitle({ title = "Puru's Digest" }: DashboardTitleProps) {
  return (
    <h1 className='text-4xl md:text-5xl lg:text-6xl font-light text-amber-900 dark:text-amber-900 mb-8 leading-tight tracking-tight'>
      {title}
    </h1>
  );
}

