import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Hero Section */}
      <div className="flex flex-col items-center justify-center px-4 py-24 text-center">
        <h1 className="text-5xl font-bold tracking-tight text-white sm:text-6xl">
          DualStack
        </h1>
        <p className="mt-4 text-xl text-gray-300">
          FastAPI + Next.js SaaS Starter Kit
        </p>
        <p className="mt-2 max-w-2xl text-gray-400">
          Production-ready full-stack template with authentication, database,
          billing, and dashboard — so you can focus on building your product.
        </p>

        <div className="mt-10 flex gap-4">
          <Link
            href="/sign-up"
            className="rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white hover:bg-blue-500 transition-colors"
          >
            Get Started
          </Link>
          <Link
            href="/sign-in"
            className="rounded-lg border border-gray-600 bg-transparent px-6 py-3 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
          >
            Sign In
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="mx-auto max-w-5xl px-4 py-16">
        <h2 className="text-center text-3xl font-bold text-white">
          What&apos;s Included
        </h2>
        <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-lg border border-gray-700 bg-gray-800/50 p-6"
            >
              <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
              <p className="mt-2 text-sm text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

const features = [
  {
    title: 'Authentication',
    description: 'Clerk-powered auth with sign-in, sign-up, and protected routes out of the box.',
  },
  {
    title: 'Database',
    description: 'Turso (LibSQL) with Drizzle ORM — migrations, schema, and type-safe queries.',
  },
  {
    title: 'Billing',
    description: 'Stripe integration for subscriptions and one-time payments.',
  },
  {
    title: 'FastAPI Backend',
    description: 'Python backend with auto-generated OpenAPI docs and async support.',
  },
  {
    title: 'Dashboard',
    description: 'Pre-built dashboard layout with navigation, settings, and overview pages.',
  },
  {
    title: 'UI Components',
    description: 'shadcn/ui primitives with dark mode, Tailwind CSS, and Geist fonts.',
  },
];
