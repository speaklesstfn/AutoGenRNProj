import NavBar from './NavBar';

xImportRootChildRoutes

export default {
    path: '/',
    component: NavBar,
    childRoutes: [
xRootChildRoutes
    ].map(v => v.routeConfig || v),
};