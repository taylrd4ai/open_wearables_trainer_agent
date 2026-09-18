import { createRouter } from '@tanstack/react-router';
import { Route as rootRoute } from './routes/__root';
import { Route as indexRoute } from './routes/index';
import { Route as authenticatedRoute } from './routes/_authenticated';
import { Route as dashboardRoute } from './routes/_authenticated/dashboard';
import { Route as workoutsRoute } from './routes/_authenticated/workouts';
import { Route as recommendationsRoute } from './routes/_authenticated/recommendations';
import { Route as settingsRoute } from './routes/_authenticated/settings';

const routeTree = rootRoute.addChildren([
  indexRoute,
  authenticatedRoute.addChildren([
    dashboardRoute,
    workoutsRoute,
    recommendationsRoute,
    settingsRoute,
  ]),
]);

export const router = createRouter({ routeTree });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
