import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Settings } from './settings';

// Mock dependencies
vi.mock('@/hooks/useAuth', () => ({
    useAuth: () => ({
        user: { email: 'test@example.com' },
        signOut: vi.fn(),
    }),
}));

vi.mock('@/components/settings', () => ({
    ProfileForm: () => <div data-testid="profile-form">Profile Form</div>,
    SessionList: () => <div data-testid="session-list">Session List</div>,
    MFASetup: () => <div data-testid="mfa-setup">MFA Setup</div>,
    PreferencesForm: () => <div data-testid="preferences-form">Preferences Form</div>,
}));

vi.mock('@tanstack/react-router', () => ({
    createFileRoute: () => () => ({}),
    Link: ({ children }: { children: React.ReactNode }) => <a>{children}</a>,
}));

describe('Settings Page', () => {
    it('renders correctly with default profile tab', () => {
        render(<Settings />);

        expect(screen.getByText('Settings')).toBeInTheDocument();
        expect(screen.getByText('test@example.com')).toBeInTheDocument();
        expect(screen.getByTestId('profile-form')).toBeInTheDocument();
    });

    it('switches tabs correctly', () => {
        render(<Settings />);

        // Check initial state
        expect(screen.getByTestId('profile-form')).toBeInTheDocument();

        // Switch to Security
        fireEvent.click(screen.getByText('Security'));
        expect(screen.getByTestId('session-list')).toBeInTheDocument();
        expect(screen.getByTestId('mfa-setup')).toBeInTheDocument();
        expect(screen.queryByTestId('profile-form')).not.toBeInTheDocument();

        // Switch to Privacy
        fireEvent.click(screen.getByText('Privacy'));
        expect(screen.getByTestId('preferences-form')).toBeInTheDocument();
    });
});
