### ***2017-03-17 更新***

***Python脚本文件从2.x更新到3.x***

### ***2017-03-30 更新***

***增加NavBar背景颜色可配置***

# 可配置Python脚本自动生成多页面RN工程并初始化



本文主要简单介绍如何利用配置文件和模板文件，使用python通过正则匹配来实现自动生成多个页面的RN工程并初始化。



我们的目标是通过执行python脚本来自动生成RN工程，并能够按照我们在配置文件中定义的内容来初始化。



以两个页面为例，每个页面中有若干个各自独立的component，每个component均有发送消息和接收消息的功能，通过RxJS来实现，可以在不同界面间传递数据。目前这几个测试component被封装在[tfn_rn](https://www.npmjs.com/package/tfn_rn)插件里，关于这个测试插件的实现，可以参看我的这篇文章《通过RxJS实现RN自定义组件间消息传递》。



同时，不同的页面间的跳转通过React-Router与Navigator来实现，将原先传递component转变为传字符串路径，方便管理。



整个模板的总结构如下图所示：



![总结构](http://ok0hyxdgr.bkt.clouddn.com/17-3-30/4504617-file_1490849680632_14cdd.png)



可以看出总共分为三部分：配置文件：config.tfn，模板文件：templet文件夹，脚本文件：auto_gen_rn.py。



接下来一部分一部分的介绍下。



## 一、配置文件



如上所说，配置文件就是config.tfn，这个文件名或者后缀叫什么都无所谓，随便，反正都可以在脚本文件中改。配置文件内容如下：



```js

[base]

RNProjName=AAAutoGenRNDemo

RNProjPath=

dependencyModule=tfn_rn

navBarBackgroundColor=


[page]

page1=home{tfn_rn:MyText,MyButton}

page2=result{tfn_rn:MyText}



[default]

default=home

```



一个section用一个中括号表示，总共分为三块：



1. base：该section主要定义基本的属性，包括需要创建的RN工程的名称RNProjName（如果不填，默认AutoGenRNDemo），RN工程的创建路径（如果不填，默认是Python脚本所在路径）、RN工程的依赖库dependencyModule（脚本里默认会安装react-router和bebel插件来支持decorator特性）和页面导航标题栏NavBar的背景颜色值navBarBackgroundColor（，设置的颜色值使用#xxxxxx的格式表示，默认颜色值为#db2f37）；



2. page：该section用来定义到底需要多少个页面，每个页面的名称、所需要引入的component名称以及所在的依赖库名称：



    * 大括号之前是页面的名称；

    

    * 大括号内是该页面需要引入的component名称集合以及他们所在的依赖库。不同的依赖库通过“|”来分割，“:”之前是依赖库的名称，“:”之后直到“|”是该依赖库中需要引入的component名称，多个component之间用“,”来区分。



3. default：default属性主要用来定义默认的路由路径，表示初始页面，可以看出这个default的值就是上面page中的某个page的值。



当然如果有其他的需求，完全可以增删改这个配置文件，结合修改脚本来实现其他的功能。



## 二、模板文件



模板文件都在templet文件夹中，这里面分成了两部分：



* 一部分是app文件夹，这个文件夹里的模板文件包括文件夹，都是固定不变的，里面主要是一些与React-Router有关的工具类；



* 另一部分是6个js文件，这六个js文件是真正的模板文件，其中有些内容是在生成具体文件时替换的：



    * **root_index_tmp.js**：这个模板文件是用来替换程序入口文件index.android.js和index.ios.js的。

        

        ```js

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

        ```

        

        其中xProjectName用配置文件中的projectName替换。

        

    * **app_tmp.js**：这个模板文件用于在工程的app文件夹下生成App.js文件，它会起到一个总路由分发的作用。

        

        ```js

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

        ```

        

        该模板文件中需要替换的是初始路由**xHomePath**，这个值直接从配置文件中的default这个section中读取。

    * **nav_bar_tmp.js**：该模板文件最终会在工程app/pages文件夹下生成NavBar.js文件，它的作用是用来规范应用的导航栏标题信息。



        ```js
        import React, {Component, PropTypes} from 'react';

        import {
            View,
            Image,
            TouchableOpacity,
            Text,
            StyleSheet,
        } from 'react-native';
        import backImage from './assets/back.png';

        const styles = StyleSheet.create({
            container: {
                flex: 1,
            },
            navBar: {
                height: 44,
                paddingTop: 0,
                backgroundColor: 'xNavBarBGColor',
                justifyContent: 'center',
                alignItems: 'center',
                paddingHorizontal: 70,
            },
            title: {
                color: 'white',
                fontSize: 20,
            },
            left: {
                position: 'absolute',
                top: 0,
                left: 0,
                bottom: 0,
                justifyContent: 'center',
                paddingHorizontal: 15,
            },
            right: {
                position: 'absolute',
                top: 0,
                right: 0,
                bottom: 0,
                justifyContent: 'center',
                paddingHorizontal: 15,
            },
            button: {
                color: 'white',
                fontSize: 15,
            },
        });

        export default class NavBar extends Component {
            static contextTypes = {
                navigator: PropTypes.object,
                currentRoute: PropTypes.object,
            };
            static propTypes = {
                children: PropTypes.element,
                routes: PropTypes.arrayOf(PropTypes.object),
            };
            onLeftPressed = () => {
                if (this.childrenRef && this.childrenRef.onLeftPressed) {
                    this.childrenRef.onLeftPressed();
                } else {
                    this.context.navigator.pop();
                }
            };
            onRightPressed = () => {
                if (this.childrenRef && this.childrenRef.onRightPressed) {
                    this.childrenRef.onRightPressed();
                }
            };
            getRef = (ref) => {
                this.childrenRef = ref;
            };

            renderBack() {
                return (
                    <TouchableOpacity style={styles.left} onPress={this.onLeftPressed}>
                        <Image source={backImage}/>
                    </TouchableOpacity>
                );
            }

            render() {
                const {children, routes} = this.props;
                const routeConfig = routes[routes.length - 1] || {};
                if (children === null) {
                    console.error('childrendfdffdf');
                }
                const {navigator, currentRoute} = this.context;
                const currentIndex = navigator.getCurrentRoutes().indexOf(currentRoute);
                console.log('current route index:' + currentIndex);
                const {leftNavTitle: left, rightNavTitle: right} = routeConfig;

                return (
                    <View style={styles.container}>
                        {
                            !routeConfig.hideNavBar &&
                            <View style={styles.navBar}>
                                <Text style={styles.title} numberOfLines={1}>{routeConfig.title}</Text>
                                { currentIndex > 0 && !left && this.renderBack() }
                                {
                                    left && <TouchableOpacity style={styles.left} onPress={this.onLeftPressed}>
                                        <Text style={styles.button}>{left}</Text>
                                    </TouchableOpacity>
                                }
                                {
                                    right && <TouchableOpacity style={styles.right} onPress={this.onRightPressed}>
                                        <Text style={styles.button}>{right}</Text>
                                    </TouchableOpacity>
                                }
                            </View>
                        }
                        {/*加入children是否为null判断*/}
                        {children && React.cloneElement(children, {ref: this.getRef})}
                    </View>
                );
            }
        }

        ```


        其中xNavBarBGColor是需要替换的内容，它表示导航栏的背景颜色。

    * **pages_index_tmp.js**：该模板文件最终会在工程app/pages文件夹下生成index.js文件，它的作用是用来定义根路由以及它的子路由等信息。

        

        ```js

        import NavBar from './NavBar';

        

        xImportRootChildRoutes

        

        export default {

            path: '/',

            component: NavBar,

            childRoutes: [

        xRootChildRoutes

            ].map(v => v.routeConfig || v),

        };

        ```

        

        其中需要替换的是xImportRootChildRoutes和xRootChildRoutes。前者是import语句，用于导入根路由的子路由信息；后者是导入的具体子路由对象。

        

    * **page_index_tmp.js**：该模板文件最终会在工程app/pages/页面name文件夹下生成index.js文件，用来指定该页面的路由路径以及它的子路由信息。

        

        ```js

        xImportPageRoute

        

        export default {

            path: 'xChildParth',

            childRoutes: [

                xPageRoute,

            ].map(v => v.routeConfig || v),

        };

        ```

        

        其中需要替换的是xImportPageRoute、xPageRoute和xChildParth。xImportPageRoute和xPageRoute与跟路由下的作用类似；xChildParth是该页面的路由路径。

        

    * **page_tmp.js**：该模板文件最终会在工程app/pages/页面name文件夹下生成*页面name.js*文件，里面的具体的页面显示信息。

        

        ```js

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

        ```

        

        其中需要替换的内容有四个：xImportModules、xImportComponents、xPagePath和xPageName。xImportModules是import语句，用于导入该页面所需要的component信息；xImportComponents用于在render中渲染所需要的component；xPagePath是该页面的路由信息；xPageName是页面的名称。



## 三、脚本文件



脚本文件就是一个python文件：



```python

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'自动生成RN工程并自动导入设定的库'

__author__ = 'TFN'

import os,re,sys

import configparser 

# 安装babel插件，用于支持@（decorator）特性：
def installBabel(RNRootPath):
    os.system('cd %s && npm i babel-plugin-transform-decorators-legacy babel-preset-react-native-stage-0 --save-dev' % RNRootPath)

    content = '{\n"presets": ["react-native"],\n"plugins": ["transform-decorators-legacy"]\n}'

    # 修改.babelrc文件
    with open(os.path.join(RNRootPath,'.babelrc'),'w') as babelFile:
        babelFile.write(content)

# 修改index.android.js和index.ios.js文件
def modifyRootIndex(pythonPath,RNRootPath,RNProjectName):
    # 读取模板文件
    with open(os.path.join(pythonPath,'templet','root_index_tmp.js'),'r') as tempIndexFile:

        # 获取匹配对象
        re_pro = re.compile(r'xProjectName')
        temp = tempIndexFile.read()
        result,number = re_pro.subn(RNProjectName,temp)

        # 打开index.android.js以及index.ios.js文件
        with open(os.path.join(RNRootPath,'index.android.js'),'w') as indexAndroidFile:
            # 通过正则表达式匹配里面需要替换的工程名称projectName并进行替换
            # 将result写入Android文件
            indexAndroidFile.write(result)

        with open(os.path.join(RNRootPath,'index.ios.js'),'w') as indexIOSFile:
            indexIOSFile.write(result)

# 创建app/App.js文件
def createApp(pythonPath,RNRootPath,defaultRoute):
    # 读取模板文件
    with open(os.path.join(pythonPath,'templet','app_tmp.js'),'r') as tempAppFile:
        re_default = re.compile(r'xHomePath')
        temp = tempAppFile.read()
        result,number = re_default.subn(defaultRoute,temp)

        # 创建app/App.js文件，并把result的内容存入
        with open(os.path.join(RNRootPath,'app','App.js'),'w') as appFile:
            appFile.write(result)

# 创建导航栏NvaBar.js文件
def createNavBar(pythonPath,RNRootPath,navBarBackgroundColor):
    # 读取模板文件
    with open(os.path.join(pythonPath,'templet','nav_bar_tmp.js'),'r') as tempNavBarFile:
        re_bg = re.compile(r'xNavBarBGColor')

        temp = tempNavBarFile.read()
        result,number = re_bg.subn(navBarBackgroundColor,temp)

        # 创建app/pages/NavBar.js文件，并把result的内容存入
        with open(os.path.join(RNRootPath,'app','pages','NavBar.js'),'w') as navBarFile:
            navBarFile.write(result)

# 创建总路由index.js
def createRouteIndex(pythonPath,RNRootPath,pageNames):
    with open(os.path.join(pythonPath,'templet','pages_index_tmp.js'),'r') as tempIndexFile:
        import_replace_str = ''
        route_replace_str = ''

        re_import = re.compile(r'xImportRootChildRoutes')
        re_route = re.compile(r'xRootChildRoutes')

        for name in pageNames:
            import_replace_str += 'import %s from \'./%s\';\n' % (name,name)            
            route_replace_str += '\t\t' + name + ',\n'

        temp = tempIndexFile.read()
        result_import,num_import = re_import.subn(import_replace_str,temp)
        result_route,num_reoute = re_route.subn(route_replace_str,result_import)

        with open(os.path.join(RNRootPath,'app','pages','index.js'),'w') as indexFile:
            indexFile.write(result_route)

# 创建相应页面的路由index.js
def createPageIndex(pythonPath,RNRootPath,pageName):
    pagePath = os.path.join(RNRootPath,'app','pages',pageName)
    os.system('mkdir -p %s' % pagePath)
    with open(os.path.join(pythonPath,'templet','page_index_tmp.js'),'r') as tempIndexFile:
        
        import_replace_str = 'import %s from \'./%s\';\n' % (pageName[:1].upper() + pageName[1:],pageName[:1].upper() + pageName[1:])
        path_replace_str = pageName
        route_replace_str = pageName[:1].upper() + pageName[1:]

        re_import = re.compile(r'xImportPageRoute')
        re_path = re.compile(r'xChildParth')
        re_route = re.compile(r'xPageRoute')
        temp = tempIndexFile.read()
        result_import,num_import = re_import.subn(import_replace_str,temp)
        result_path,num_path = re_path.subn(path_replace_str,result_import)
        result_route,num_reoute = re_route.subn(route_replace_str,result_path)

        with open(os.path.join(pagePath,'index.js'),'w') as indexFile:
            indexFile.write(result_route)

# 创建相应页面的js
def createPage(pythonPath,RNRootPath,pageName,pageComp):
    pagePath = os.path.join(RNRootPath,'app','pages',pageName)
    with open(os.path.join(pythonPath,'templet','page_tmp.js'),'r') as tempNameFile:
        import_replace_str = ''
        component_replace_str = ''
        path_replace_str = pageName
        name_replace_str = pageName[:1].upper() + pageName[1:]

        for eachComp in pageComp.split('|'):
            comps = eachComp.split(':')
            importModule = comps[0]
            importComps = comps[1].split(',')

            temp_str = 'import {%s} from \'%s\';\n' % (comps[1],importModule)
            import_replace_str += temp_str

            for v in importComps:
                component_replace_str += '\t\t\t\t' + '<' + v + '/>\n'

        re_import = re.compile(r'xImportModules')
        re_comp = re.compile(r'xImportComponents')
        re_path = re.compile(r'xPagePath')
        re_name = re.compile(r'xPageName')
        temp = tempNameFile.read()
        result_import,num_import = re_import.subn(import_replace_str,temp)
        result_comp,num_comp = re_comp.subn(component_replace_str,result_import)
        result_path,num_path = re_path.subn(path_replace_str,result_comp)
        result_name,num_name = re_name.subn(name_replace_str,result_path)

        name = pageName[:1].upper() + pageName[1:]

        with open(os.path.join(pagePath,'%s.js' % name),'w') as nameFile:
            nameFile.write(result_name) 

# 读取配置文件，获取需要的插件信息，然后初始化
def init(pythonPath):

    config=configparser.ConfigParser() 

    # 读取配置文件
    with open(os.path.join(pythonPath,'config.tfn'),'r') as configFile:
        
        config.readfp(configFile)

        # 需要创建的RN工程名，默认AutoGenRNDemo
        RNProjName = config.get('base','RNProjName') or 'AutoGenRNDemo'

        # 工程创建的位置，默认在当前脚本目录下创建RN工程
        RNProjPath = config.get('base','RNProjPath') or os.path.split(os.path.realpath(__file__))[0]

        # 初始化RN工程
        os.system('cd %s && react-native init %s' % (RNProjPath,RNProjName))

        # 工程根目录
        RNRootPath = os.path.join(RNProjPath,RNProjName)

        # 将templet文件夹下的app文件夹及其子文件复制到在工程根目录下
        os.system('cp -r %s %s' % (os.path.join(pythonPath,'templet','app'),RNRootPath))

        # 修改index.android.js和index.ios.js文件
        modifyRootIndex(pythonPath,RNRootPath,RNProjName)

        # 获取默认路由
        defaultRoute = config.get('default','default')

        # 创建app/App.js文件
        createApp(pythonPath,RNRootPath,defaultRoute)

        # 需要导入的模块名
        dependencyModule = config.get('base','dependencyModule').split(',')

        # npm install，将需要的模块依次安装
        list(map(lambda x:os.system('cd %s && npm install --save %s ' % (RNRootPath,x)),dependencyModule))

        os.system('cd %s && npm install --save react-router@3.0.2' % RNRootPath)

        installBabel(RNRootPath)

        # 读取导航栏的背景颜色，默认颜色#db2f37
        navBarBackgroundColor = config.get('base','navBarBackgroundColor') or '#db2f37'
        # 创建导航栏NvaBar.js文件
        createNavBar(pythonPath,RNRootPath,navBarBackgroundColor)

        # 读取配置文件的page这个section，获取需要生成的页面数以及每个页面需要导入的Component
        pageNum = len(config.options('page'))

        pageNames = []

        for index in range(1,pageNum+1):
            eachPage = config.get('page','page%d' % index)
            # 分割，得到页面的名称
            pageName = eachPage[:eachPage.index('{')]

            # 创建相应页面的路由index.js
            createPageIndex(pythonPath,RNRootPath,pageName)

            pageNames.append(pageName)

            pageComp = eachPage[eachPage.index('{') + 1:len(eachPage) - 1]

            createPage(pythonPath,RNRootPath,pageName,pageComp)

        createRouteIndex(pythonPath,RNRootPath,pageNames)

if __name__ == '__main__':

    # 当前python文件的路径
    pythonPath = os.path.split(os.path.realpath(__file__))[0]

    init(pythonPath)

```



上面的代码注释已经够多啦，这里就直接说下主要的几个步骤吧：



1. 读取配置文件，得到包括工程名、工程路径、依赖库以及需要创建的页面等信息；



2. 通过react-native init 命令来创建RN工程；



3. 将templet文件夹下的app文件夹及其子文件复制到在工程根目录下；



4. 修改index.android.js和index.ios.js文件；



5. 创建app/App.js文件；



6. npm install需要的依赖（**包括React-Router，由于最新的4.x版本的React-Router与3.x版本的变化过大，因此这里直接写死安装3.0.2版本**）；



7. 安装babel插件以支持Decorator特性（同时需要修改工程.babelrc文件）；



8. 创建总的导航栏NavBar.js文件；



9. 创建相应页面文件夹以及该页面的路由index.js文件；



10. 创建相应页面文件；



11. 创建总路由index.js文件。



## 四、总结



经过上面的步骤，就可以直接通过命令行：



```shell

python3 xx/xx/AutoGenRNProj/auto_gen_rn.py

```



来生成所需要的RN工程了。



***当然了，这里有一个需要特别注意的***：**这里虽然自动生成了两个页面，但是并没有页面跳转的代码，这些代码需要手动写，因为每个页面的情况是不清楚的**。



我这里贴一个示例：在第一个页面中加了一个按钮：



```js

/**

 * Created by tfn on 17-3-8.

 */

import React, {Component, PropTypes,} from 'react';

import {

    StyleSheet,

    View,

    TouchableOpacity,

    Text,

} from 'react-native';

import router from '../../utils/routerDecorator';

import {MyText, MyButton} from 'tfn_rn'



@router('home')

export default class Home extends Component {

    static hideNavBar = false;

    static title = 'Home';

    static contextTypes = {

        navigator: PropTypes.object,

    };

    click = () => {

        this.context.navigator.push({

            location: '/result/result',

        });

    };



    render() {

        return (

            <View>

                <MyText/>

                <MyButton/>



                <TouchableOpacity style={styles.button} onPress={this.click}>

                    <Text style={styles.buttonText}>

                        点击跳转到第二页并携带总价

                    </Text>

                </TouchableOpacity>



            </View>

        );

    }

}



const styles = StyleSheet.create({

    button: {

        marginTop: 20,

        marginHorizontal: 20,

        backgroundColor: '#1e90ff',

        height: 40,

        borderRadius: 5,

        alignItems: 'center',

        justifyContent: 'center',

    },

    buttonText: {

        color: '#696969',

        textAlign: 'center',

        fontSize: 20,

    },

});

```



最后，各位如果有不清楚的，可以去这里clone下来自己运行看看：[https://github.com/speaklesstfn/AutoGenRNProj](https://github.com/speaklesstfn/AutoGenRNProj)。



**特别注意：要运行该python脚本，需要先安装python，我使用的是python3.5的语法写的，如果使用python2.x的环境可能会有运行错误，因为两个版本不兼容，但是大部分内容是一样的，各位可以自行按照对应语法修改下，不麻烦的。**