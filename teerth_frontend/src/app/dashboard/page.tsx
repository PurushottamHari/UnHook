"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";

export default function DashboardRedirect() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated && user?.id && user.role !== "guest") {
      router.replace(`/dashboard/${user.id}`);
    } else {
      router.replace("/dashboard/607d95f0-47ef-444c-89d2-d05f257d1265");
    }
  }, [isAuthenticated, user, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-yellow-50 dark:bg-amber-50">
      <div className="w-8 h-8 rounded-full border-4 border-amber-600 border-t-transparent animate-spin"></div>
    </div>
  );
}
