'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import TeerthLogo from '@/components/TeerthLogo';
import LoadingSpinner from '@/components/LoadingSpinner';
import CategoryTagsSkeleton from '@/components/CategoryTagsSkeleton';
import DashboardDatePicker from '@/components/dashboard/DashboardDatePicker';
import DashboardTitle from '@/components/dashboard/DashboardTitle';
import CategoriesError from '@/components/dashboard/CategoriesError';
import MobileMetadataDropdown from '@/components/MobileMetadataDropdown';
import CategoryTag from '@/components/CategoryTag';
import ModeBanner from '@/components/ModeBanner';
import ArticlesWidget from '@/components/dashboard/ArticlesWidget';
import WaitlistSection from '@/components/WaitlistSection';

async function fetchUserCategories(userId: string, date: string): Promise<string[]> {
  const response = await fetch(`/api/users/categories/today?userId=${userId}&date=${date}`);
  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch user categories');
  }

  return data.categories || [];
}

interface GuestViewProps {
  userId: string;
}

export default function GuestView({ userId }: GuestViewProps) {
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    return new Date().toISOString().split('T')[0];
  });

  const todayDate = new Date().toISOString().split('T')[0];
  const {
    data: userCategories,
    isLoading: isLoadingCategories,
    isFetching: isFetchingCategories,
    error: categoriesError,
  } = useQuery<string[]>({
    queryKey: ['userCategories', userId],
    queryFn: () => fetchUserCategories(userId, todayDate),
    enabled: !!userId,
    meta: {
      persist: true,
    },
    staleTime: 5 * 60 * 1000, 
  });

  return (
    <div className='min-h-screen bg-yellow-50 dark:bg-amber-50'>
      <ModeBanner mode="guest" />
      <div className='w-full px-4 sm:px-6 lg:px-8 py-8'>
        <div className='max-w-6xl mx-auto'>
          <div className='relative mb-12'>
            <DashboardDatePicker
              selectedDate={selectedDate}
              onDateChange={setSelectedDate}
              variant='desktop'
            />

            <div className='text-center'>
              <div className='flex justify-center mb-6'>
                <TeerthLogo alt='Teerth Logo' size={200} />
              </div>

              <DashboardTitle title="Puru's Space" />

              <DashboardDatePicker
                selectedDate={selectedDate}
                onDateChange={setSelectedDate}
                variant='mobile'
              />

              {isLoadingCategories && !userCategories ? (
                <CategoryTagsSkeleton />
              ) : categoriesError ? (
                <CategoriesError />
              ) : userCategories && userCategories.length > 0 ? (
                <div className='text-center text-amber-700 dark:text-amber-800 mb-8'>
                  {isFetchingCategories && userCategories && (
                    <div className='flex justify-center mb-2'>
                      <LoadingSpinner size='sm' />
                    </div>
                  )}

                  <MobileMetadataDropdown
                    label="In Focus Today:"
                    items={userCategories.map((category: string, index: number) => (
                      <CategoryTag key={index} category={category} variant="default" />
                    ))}
                  />

                  <div className="hidden md:flex flex-col items-center mb-3">
                    <p className="text-lg font-medium leading-relaxed mb-3">
                      In Focus Today:
                    </p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {userCategories.map((category: string, index: number) => (
                        <CategoryTag key={index} category={category} variant="default" />
                      ))}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
          
          <ArticlesWidget userId={userId} selectedDate={selectedDate} />
          
          <WaitlistSection variant='detailed' />
        </div>
      </div>
    </div>
  );
}
