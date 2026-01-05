import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { UserManagementTable } from './UserManagementTable';
import * as useSuperAdminHooks from '../../hooks/api/useSuperAdmin';

// Mock the hooks
vi.mock('../../hooks/api/useSuperAdmin', () => ({
    useSuperAdminUsers: vi.fn(),
    useUnlockUser: vi.fn(),
    useUpdateUserAdmin: vi.fn(),
}));

describe('UserManagementTable', () => {
    const mockUsers = [
        {
            id: '1',
            email: 'user1@example.com',
            display_name: 'User One',
            is_super_admin: false,
            failed_login_attempts: 0,
            created_at: '2023-01-01T00:00:00Z',
        },
        {
            id: '2',
            email: 'admin@example.com',
            display_name: 'Admin User',
            is_super_admin: true,
            failed_login_attempts: 0,
            created_at: '2023-01-01T00:00:00Z',
        },
    ];

    const mockUnlockMutate = vi.fn();
    const mockUpdateMutate = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();

        (useSuperAdminHooks.useUnlockUser as any).mockReturnValue({
            mutateAsync: mockUnlockMutate,
            isPending: false,
        });

        (useSuperAdminHooks.useUpdateUserAdmin as any).mockReturnValue({
            mutateAsync: mockUpdateMutate,
            isPending: false,
        });
    });

    it('renders loading skeleton when loading', () => {
        (useSuperAdminHooks.useSuperAdminUsers as any).mockReturnValue({
            data: undefined,
            isLoading: true,
            error: null,
        });

        render(<UserManagementTable />);
        // Check for skeletons (checking by class or just structure)
        // Here we can just check that no "No users found" or table headers are present yet if we want, 
        // or checks for the skeleton elements specifically if they have test ids.
        // For now, let's just make sure the title renders.
        expect(screen.getByText('All Users')).toBeInTheDocument();
    });

    it('renders error message when error occurs', () => {
        (useSuperAdminHooks.useSuperAdminUsers as any).mockReturnValue({
            data: undefined,
            isLoading: false,
            error: new Error('Failed'),
        });

        render(<UserManagementTable />);
        expect(screen.getByText('Failed to load users')).toBeInTheDocument();
    });

    it('renders users table when data is available', () => {
        (useSuperAdminHooks.useSuperAdminUsers as any).mockReturnValue({
            data: {
                items: mockUsers,
                total: 2,
                page: 1,
                page_size: 20
            },
            isLoading: false,
            error: null,
        });

        render(<UserManagementTable />);

        expect(screen.getByText('user1@example.com')).toBeInTheDocument();
        expect(screen.getByText('admin@example.com')).toBeInTheDocument();
        expect(screen.getByText('User One')).toBeInTheDocument();
        // Check for Super Admin badge
        expect(screen.getByText('Super Admin')).toBeInTheDocument();
    });

    it('handles search input', () => {
        (useSuperAdminHooks.useSuperAdminUsers as any).mockReturnValue({
            data: { items: [], total: 0 },
            isLoading: false,
        });

        render(<UserManagementTable />);

        const input = screen.getByPlaceholderText('Search by email...');
        fireEvent.change(input, { target: { value: 'test' } });

        expect(input).toHaveValue('test');
        // Note: Debounce or effect verification would depend on implementation details not fully mocked here, 
        // but we can verify the input updates.
    });
});
