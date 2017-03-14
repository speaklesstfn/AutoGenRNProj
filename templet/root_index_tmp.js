import React, { Component } from 'react';
import {
  AppRegistry,
} from 'react-native';

import App from './app/App';

export default class xProjectName extends Component {
  render() {
    return (
        <App />
    );
  }
}

AppRegistry.registerComponent('xProjectName', () => xProjectName);
