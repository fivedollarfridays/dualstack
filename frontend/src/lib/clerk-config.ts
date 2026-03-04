/**
 * Shared Clerk appearance configuration for dark theme.
 * Used by ClerkProvider, SignIn, and SignUp components.
 */
export const clerkAppearance = {
  variables: {
    colorPrimary: '#2563eb',
    colorBackground: '#1f2937',
    colorText: '#ffffff',
    colorTextSecondary: '#9ca3af',
    colorInputBackground: '#374151',
    colorInputText: '#ffffff',
  },
  elements: {
    rootBox: 'mx-auto',
    card: 'bg-gray-800 border border-gray-700',
    headerTitle: 'text-white',
    headerSubtitle: 'text-gray-400',
    socialButtonsBlockButton: 'bg-gray-700 border-gray-600 text-white hover:bg-gray-600',
    formFieldLabel: 'text-gray-300',
    formFieldInput: 'bg-gray-700 border-gray-600 text-white',
    footerActionLink: 'text-blue-400 hover:text-blue-300',
    formButtonPrimary: 'bg-blue-600 hover:bg-blue-500',
  },
};
