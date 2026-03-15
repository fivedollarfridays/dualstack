/**
 * Tests for OnboardingLayout component.
 */
import { render, screen } from '@testing-library/react';
import OnboardingLayout from '../layout';

describe('OnboardingLayout', () => {
  it('renders children inside a centered container', () => {
    render(
      <OnboardingLayout>
        <p>Test child</p>
      </OnboardingLayout>
    );

    expect(screen.getByText('Test child')).toBeInTheDocument();
  });

  it('applies centering classes to wrapper div', () => {
    const { container } = render(
      <OnboardingLayout>
        <span>Content</span>
      </OnboardingLayout>
    );

    const wrapper = container.firstElementChild as HTMLElement;
    expect(wrapper.className).toContain('flex');
    expect(wrapper.className).toContain('min-h-screen');
    expect(wrapper.className).toContain('items-center');
    expect(wrapper.className).toContain('justify-center');
  });
});
