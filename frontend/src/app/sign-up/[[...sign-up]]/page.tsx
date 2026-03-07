'use client';

import { SignUp } from '@clerk/nextjs';
import { clerkAppearance } from '@/lib/clerk-config';
import { isClerkEnabled } from '@/lib/auth-config';
import { DevSignUp } from '@/components/auth/dev-sign-up';

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 to-gray-800">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">Get Started</h1>
          <p className="mt-2 text-gray-400">Create your account</p>
        </div>

        {isClerkEnabled() ? (
          <SignUp
            appearance={clerkAppearance}
            path="/sign-up"
            routing="path"
            signInUrl="/sign-in"
            forceRedirectUrl="/dashboard"
          />
        ) : (
          <DevSignUp />
        )}
      </div>
    </div>
  );
}
