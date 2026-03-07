'use client';

import { SignIn } from '@clerk/nextjs';
import { clerkAppearance } from '@/lib/clerk-config';
import { isClerkEnabled } from '@/lib/auth-config';
import { DevSignIn } from '@/components/auth/dev-sign-in';

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 to-gray-800">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white">Welcome Back</h1>
          <p className="mt-2 text-gray-400">Sign in to continue</p>
        </div>

        {isClerkEnabled() ? (
          <SignIn
            appearance={clerkAppearance}
            path="/sign-in"
            routing="path"
            signUpUrl="/sign-up"
            forceRedirectUrl="/dashboard"
          />
        ) : (
          <DevSignIn />
        )}
      </div>
    </div>
  );
}
