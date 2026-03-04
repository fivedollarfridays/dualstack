'use client';

import { useAuth } from '@clerk/nextjs';
import { PlanCard } from '@/components/billing/plan-card';
import { createCheckout, openPortal } from '@/lib/api/billing';

const FREE_FEATURES = ['1 project', 'Basic support', 'Community access'];
const PRO_FEATURES = [
  'Unlimited projects',
  'Priority support',
  'API access',
  'Advanced analytics',
];

export default function BillingPage() {
  const { getToken } = useAuth();

  async function handleSubscribe() {
    const token = await getToken();
    if (!token) return;
    const url = await createCheckout(token, 'price_pro_monthly');
    window.location.href = url;
  }

  async function handleManageSubscription() {
    const token = await getToken();
    if (!token) return;
    const url = await openPortal(token);
    window.location.href = url;
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
          onSubscribe={() => {}}
        />
        <PlanCard
          name="Pro"
          price="$10/mo"
          features={PRO_FEATURES}
          isCurrent={false}
          onSubscribe={handleSubscribe}
        />
      </div>
      <div className="mt-6">
        <button
          className="rounded-lg border border-gray-600 px-4 py-2 text-sm text-gray-300 hover:bg-gray-800"
          onClick={handleManageSubscription}
        >
          Manage Subscription
        </button>
      </div>
    </div>
  );
}
