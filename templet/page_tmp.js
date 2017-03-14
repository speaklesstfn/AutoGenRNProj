import React, {Component, PropTypes,} from 'react';
import {
    View,
} from 'react-native';
import router from '../../utils/routerDecorator';
xImportModules

@router('xPagePath')
export default class xPageName extends Component {
    static hideNavBar = false;
    static title = 'xPageName';
    static contextTypes = {
        navigator: PropTypes.object,
    };

    render() {
        return (
            <View>
xImportComponents
            </View>
        );
    }
}
