'use client';

import DatePicker from '@/components/DatePicker';

interface DashboardDatePickerProps {
  selectedDate: string;
  onDateChange: (date: string) => void;
  variant: 'mobile' | 'desktop';
}

export default function DashboardDatePicker({
  selectedDate,
  onDateChange,
  variant,
}: DashboardDatePickerProps) {
  if (variant === 'desktop') {
    return (
      <div className='hidden md:block absolute top-0 right-0 z-50'>
        <DatePicker selectedDate={selectedDate} onDateChange={onDateChange} />
      </div>
    );
  }

  return (
    <div className='md:hidden flex justify-center'>
      <DatePicker selectedDate={selectedDate} onDateChange={onDateChange} />
    </div>
  );
}

