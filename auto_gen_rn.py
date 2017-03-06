#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,re,sys

'自动生成RN工程并自动导入设定的库'

# 修改index.android.js和index.ios.js文件
def modifyRootIndex(projectPath,projectName):
	# 读取模板文件
	with open(os.path.join(projectPath,'templet','root_index_tmp.js'),'r') as tempIndexFile:

		# 获取匹配对象
		re_pro = re.compile(r'projectName')
		temp = tempIndexFile.read()
		result,number = re_pro.subn(projectName,temp)

		# 打开index.android.js以及index.ios.js文件
		with open(os.path.join(projectPath,projectName,'index.android.js'),'w') as indexAndroidFile:
			# 通过正则表达式匹配里面需要替换的工程名称projectName并进行替换
			# 将result写入Android文件
			indexAndroidFile.write(result)

		with open(os.path.join(projectPath,projectName,'index.ios.js'),'w') as indexIOSFile:
			indexIOSFile.write(result)

# 创建App index.js文件
def createAppIndex(projectPath,appPath,componentModule):
	# 读取模板文件
	with open(os.path.join(projectPath,'templet','app_index_tmp.js'),'r') as tempAppFile:
		
		module_replace_str = ''
		component_replace_str = ''

		# 需要import的modules
		for k,values in componentModule.items():
			components = ''
			for v in values:
				components += v + ','
				component_replace_str += '<' + v + '/>\n'

			# 移除最后的一个','
			components = components[:-1]

			temp_str = 'import {%s} from \'%s\'\n' % (components,k)
			module_replace_str += temp_str

		# 获取匹配对象，包括两个，一个是需要导入的模块名，还有一个是模块下面需要导入的Component名
		re_module = re.compile(r'importModules')
		re_component = re.compile(r'importComponents')
		temp = tempAppFile.read()
		result_module,num_module = re_module.subn(module_replace_str,temp)
		result,number = re_component.subn(component_replace_str,result_module)

		# 创建app/index.js文件，并把result的内容存入
		with open(os.path.join(appPath,'index.js'),'w') as indexFile:
			indexFile.write(result)


if __name__ == '__main__':

	# 需要创建的RN工程名
	projectName = 'AutoGenRNDemo'

	# 工程创建的位置，我们就在当前脚本目录下创建RN工程
	projectPath = os.path.split(os.path.realpath(__file__))[0]

	# print projectPath

	# 需要导入的与UI组件相关的模块名及需要的组件名
	componentModule = {'tfn_rn':['MyText','MyButton']}

	# 需要导入的非UI模块名
	dependencyModule = ['fbemitter']

	# 初始化RN工程
	os.system('cd %s && react-native init %s' % (projectPath,projectName))

	rootPath = os.path.join(projectPath,projectName)

	appPath = os.path.join(rootPath,'app')

	# 在工程根目录下创建app文件夹
	os.system('mkdir -p %s' % appPath)

	# npm install，将需要的模块依次安装
	map(lambda x:os.system('cd %s && npm install --save %s' % (rootPath,x)),componentModule.keys())
	map(lambda x:os.system('cd %s && npm install --save %s' % (rootPath,x)),dependencyModule)

	# 修改index.android.js和index.ios.js文件
	modifyRootIndex(projectPath,projectName)

	# 在	app文件夹下创建index.js文件
	createAppIndex(projectPath,appPath,componentModule)
