"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import TeerthLogo from "@/components/TeerthLogo";
import LoadingSpinner from "@/components/LoadingSpinner";
import CategoryTagsSkeleton from "@/components/CategoryTagsSkeleton";
import DashboardDatePicker from "@/components/dashboard/DashboardDatePicker";
import DashboardTitle from "@/components/dashboard/DashboardTitle";
import CategoriesError from "@/components/dashboard/CategoriesError";
import CategoryTag from "@/components/CategoryTag";
import ArticlesWidget from "@/components/dashboard/ArticlesWidget";

async function fetchUserCategories(
  userId: string,
  date: string,
): Promise<string[]> {
  const response = await fetch(
    `/api/users/categories/today?userId=${userId}&date=${date}`,
  );
  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || "Failed to fetch user categories");
  }

  return data.categories || [];
}

interface UserViewProps {
  userId: string;
}

export default function UserView({ userId }: UserViewProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const dateParam = searchParams.get("date");

  const [selectedDate, setSelectedDate] = useState<string>(() => {
    return dateParam || new Date().toISOString().split("T")[0];
  });

  const handleDateChange = (newDate: string) => {
    setSelectedDate(newDate);
    const params = new URLSearchParams(searchParams.toString());
    params.set("date", newDate);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  };

  useEffect(() => {
    if (dateParam && dateParam !== selectedDate) {
      setSelectedDate(dateParam);
    } else if (!dateParam) {
      const today = new Date().toISOString().split("T")[0];
      if (selectedDate !== today) {
        setSelectedDate(today);
      }
    }
  }, [dateParam, selectedDate]);

  const todayDate = new Date().toISOString().split("T")[0];
  const {
    data: userCategories,
    isLoading: isLoadingCategories,
    isFetching: isFetchingCategories,
    error: categoriesError,
  } = useQuery<string[]>({
    queryKey: ["userCategories", userId],
    queryFn: () => fetchUserCategories(userId, todayDate),
    enabled: !!userId,
    meta: {
      persist: true,
    },
    staleTime: 5 * 60 * 1000,
  });

  return (
    <div className="min-h-screen bg-yellow-50 dark:bg-amber-50 md:snap-none snap-container">
      <div className="w-full px-4 sm:px-6 lg:px-8 py-2 md:py-8">
        <div className="max-w-6xl mx-auto">
          <div className="relative mb-4 md:mb-12 snap-start">
            <DashboardDatePicker
              selectedDate={selectedDate}
              onDateChange={handleDateChange}
              variant="desktop"
            />

            <div className="text-center">
              <div className="flex items-center justify-center relative mb-6">
                <TeerthLogo
                  alt="Teerth Logo"
                  size={200}
                  useIconOnMobile={true}
                />
                <div className="absolute right-0 md:hidden">
                  <DashboardDatePicker
                    selectedDate={selectedDate}
                    onDateChange={handleDateChange}
                    variant="mobile"
                  />
                </div>
              </div>

              <DashboardTitle title="Welcome Puru" />

              {isLoadingCategories && !userCategories ? (
                <CategoryTagsSkeleton />
              ) : categoriesError ? (
                <CategoriesError />
              ) : userCategories && userCategories.length > 0 ? (
                <div className="hidden md:block text-center text-amber-700 dark:text-amber-800 mb-8">
                  {isFetchingCategories && userCategories && (
                    <div className="flex justify-center mb-2">
                      <LoadingSpinner size="sm" />
                    </div>
                  )}

                  <div className="hidden md:flex flex-col items-center mb-3">
                    <p className="text-lg font-medium leading-relaxed mb-3">
                      In Focus Today:
                    </p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {userCategories.map((category: string, index: number) => (
                        <CategoryTag
                          key={index}
                          category={category}
                          variant="default"
                        />
                      ))}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          </div>

          {/* No ModeBanner in UserView */}

          <ArticlesWidget userId={userId} selectedDate={selectedDate} />
        </div>
      </div>
    </div>
  );
}
