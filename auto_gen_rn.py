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