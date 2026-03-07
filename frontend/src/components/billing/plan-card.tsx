import { Card } from '@/components/ui/card';

interface PlanCardProps {
  name: string;
  price: string;
  features: string[];
  isCurrent: boolean;
  onSubscribe: () => void;
}

export function PlanCard({
  name,
  price,
  features,
  isCurrent,
  onSubscribe,
}: PlanCardProps) {
  return (
    <Card>
      <h3 className="text-xl font-bold text-white">{name}</h3>
      <p className="mt-2 text-3xl font-bold text-white">{price}</p>
      <ul className="mt-4 space-y-2">
        {features.map((feature) => (
          <li key={feature} className="text-sm text-gray-300">
            {feature}
          </li>
        ))}
      </ul>
      <button
        className={`mt-6 w-full rounded-lg px-4 py-2 text-sm font-medium ${
          isCurrent
            ? 'cursor-not-allowed bg-gray-600 text-gray-400'
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
        disabled={isCurrent}
        onClick={onSubscribe}
      >
        {isCurrent ? 'Current Plan' : 'Subscribe'}
      </button>
    </Card>
  );
}
