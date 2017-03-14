xImportPageRoute

export default {
    path: 'xChildParth',
    childRoutes: [
        xPageRoute,
    ].map(v => v.routeConfig || v),
};