import { createRoute } from '@tanstack/react-router';
import { Route as authenticatedRoute } from '../_authenticated';
import { DashboardPage } from '../../components/pages/dashboard/DashboardPage';

export const Route = createRoute({
  getParentRoute: () => authenticatedRoute,
  path: '/dashboard',
  component: DashboardPage,
});
