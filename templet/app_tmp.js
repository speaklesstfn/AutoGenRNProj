import React, {Component,} from 'react';
import {
    Navigator,
} from 'react-native';

import routeConfig from './pages';
import NavigatorProvider from './utils/NavigatorProvider';
import RouterContainer from './utils/RouterContainer';
import hookNavigator from './utils/hookNavigator';
import {configureScene} from './SceneConfig';

const INITIAL_ROUTE = {
    location: '/xHomePath/xHomePath',
};

function configureSceneWithRoute(route) {
    return configureScene(routeConfig, route);
}

export default class App extends Component {

    renderScene = (currentRoute, navigator) => {
        const {location, passProps, component: Comp} = currentRoute || 0;
        if (location) {
            // 通过location渲染页面
            return (
                <NavigatorProvider navigator={navigator} currentRoute={currentRoute}>
                    <RouterContainer
                        routeConfig={routeConfig}
                        passProps={passProps}
                        location={location}
                    />
                </NavigatorProvider>
            );
        } else if (Comp) {
            // 通过component渲染页面,用于Dialog等场景
            return (
                <NavigatorProvider navigator={navigator}>
                    <Comp {...passProps} />
                </NavigatorProvider>
            );
        }
        return null;
    };

    onNavigatorRef = (ref) => {
        this.navigator = ref;
        if (ref) {
            hookNavigator(ref);
        }
    };

    render() {
        return (
            <Navigator
                configureScene={configureSceneWithRoute}
                initialRoute={INITIAL_ROUTE}
                renderScene={this.renderScene}
                ref={this.onNavigatorRef}
            />
        );
    }
}