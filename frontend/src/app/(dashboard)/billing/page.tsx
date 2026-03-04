'use client';

import { useState } from 'react';
import { useAuth } from '@clerk/nextjs';
import { PlanCard } from '@/components/billing/plan-card';
import { createCheckout } from '@/lib/api/billing';

const STRIPE_PRO_PRICE_ID = process.env.NEXT_PUBLIC_STRIPE_PRO_PRICE_ID || 'price_pro_monthly';

const FREE_FEATURES = ['1 project', 'Basic support', 'Community access'];
const PRO_FEATURES = [
  'Unlimited projects',
  'Priority support',
  'API access',
  'Advanced analytics',
];

export default function BillingPage() {
  const { getToken } = useAuth();
  const [error, setError] = useState<string | null>(null);

  async function handleSubscribe() {
    try {
      setError(null);
      const token = await getToken();
      if (!token) return;
      const url = await createCheckout(token, STRIPE_PRO_PRICE_ID);
      window.location.href = url;
    } catch {
      setError('Failed to start checkout. Please try again.');
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-white">Billing</h1>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <PlanCard
          name="Free"
          price="$0/mo"
          features={FREE_FEATURES}
          isCurrent={true}
          onSubscribe={handleSubscribe}
        />
        <PlanCard
          name="Pro"
          price="$10/mo"
          features={PRO_FEATURES}
          isCurrent={false}
          onSubscribe={handleSubscribe}
        />
      </div>

      {error && (
        <div className="mt-4 rounded-lg border border-red-500/50 bg-red-900/20 p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {/* TODO: Add "Manage Subscription" button once you have a user->customer mapping.
          See backend/app/billing/service.py for the portal endpoint. */}
    </div>
  );
}
