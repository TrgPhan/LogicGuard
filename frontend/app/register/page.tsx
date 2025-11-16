"use client";

import { Suspense } from "react";
import { AuthForm } from "@/components/auth-form";
import Link from "next/link";

function RegisterPageContent() {
  return (
    <div className="min-h-screen bg-[#F7F5F3] flex flex-col">
      {/* Header */}
      <header className="w-full border-b border-[rgba(55,50,47,0.12)] bg-[#F7F5F3]">
        <div className="max-w-[1060px] mx-auto px-4 py-4">
          <Link
            href="/"
            className="text-[#37322F] font-semibold text-lg hover:opacity-80"
          >
            LogicGuard
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <AuthForm mode="register" />
      </main>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={null}>
      <RegisterPageContent />
    </Suspense>
  );
}
