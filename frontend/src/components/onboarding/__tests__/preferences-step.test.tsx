/**
 * Tests for PreferencesStep component.
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { PreferencesStep } from '../preferences-step';

describe('PreferencesStep', () => {
  it('renders heading and preference controls', () => {
    render(<PreferencesStep />);

    expect(screen.getByRole('heading', { name: /preferences/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/theme/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/notification/i)).toBeInTheDocument();
  });

  it('toggles theme between light and dark', () => {
    render(<PreferencesStep />);

    const themeSelect = screen.getByLabelText(/theme/i);
    fireEvent.change(themeSelect, { target: { value: 'dark' } });
    expect(themeSelect).toHaveValue('dark');
  });

  it('toggles notification opt-in checkbox', () => {
    render(<PreferencesStep />);

    const checkbox = screen.getByLabelText(/notification/i);
    expect(checkbox).not.toBeChecked();

    fireEvent.click(checkbox);
    expect(checkbox).toBeChecked();
  });
});
