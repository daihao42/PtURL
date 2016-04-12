#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'dai'

"""
	开多线程并发，每条线程利用urllib打开页面，
	测试网站在高并发下redis的统计功能是否loss
	"""
import urllib.error , urllib.request
import threading
import time
import configparser
#for fix the error 'unknown encoding:idna' in py2exe
import encodings.idna


"""
	config
	"""
config = configparser.ConfigParser()
config.read("conf.ini")

#测试网址
TEST_URL = config.get('option','TEST_URL')
#线程数
THREAD_NUM = config.getint('option','THREAD_NUM')
#每个线程循环次数
A_THREAD_LOOP = config.getint('option','A_THREAD_LOOP')
#每次请求间隔时间
LOOP_SLEEP = config.getfloat('option','LOOP_SLEEP')
#每次请求的timeout(超时)时间
TIMEOUT = config.getfloat('option','TIMEOUT')
#输出到文件
OUTPUT_FILE = config.get('option','OUTPUT_FILE')
#读取失败的结果
CHECK_REP = config.get('option','CHECK_REP')

#出错数
ERROR_NUM = 0

#获取到的数目
GET_TAR = 0

class TEST:

	def __init__(self):
		if OUTPUT_FILE != '0':
		#打开输出文件
			try:
				self.f = open(OUTPUT_FILE, 'w+')
				print('输出到',OUTPUT_FILE)
				self.is_open = 1
			except Exception:
				print('打开文件失败！直接打印结果如下：')
				self.is_open = 0
		else:
			self.is_open = 0


	def __del__(self):
		if self.is_open:
			self.f.close()

	#打印输出值
	def i_print(self,str):
		if self.is_open :
			print(str,file=self.f)
		else:
			print(str)

	#用request获取网页
	def getHtml(self,index):
	#当前线程名字，用于打印出错信息
		t = threading.currentThread()
		req = urllib.request.Request(TEST_URL, headers = {'Connection': 'Keep-Alive',
				'Accept': 'text/html, application/xhtml+xml, */*',
				'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
				})
		try:
			oper = urllib.request.urlopen(req,timeout=TIMEOUT)
			rep = oper.read().decode()
			if rep != CHECK_REP:
                                self.i_print("["+t.name+" "+str(index)+"] Get "+rep)
                                global GET_TAR
                                GET_TAR += 1
		except Exception as e:
			self.i_print("["+t.name+" "+str(index)+"]")
			self.i_print(e)
			global ERROR_NUM
			ERROR_NUM += 1

	#每条线程循环进行测试
	def thread_loop(self):
		t = threading.currentThread()
		self.i_print("["+t.name+"] Sub Thread Begin")

		i = 0
		while i < A_THREAD_LOOP:
			i += 1
			self.getHtml(i)
			#循环间隔
			time.sleep(LOOP_SLEEP)

		self.i_print("["+t.name+"] Sub Thread End")

	def test(self):
		#线程列表
		Threads = []

		#创建线程
		for i in range(THREAD_NUM):
			t = threading.Thread(target=self.thread_loop, name="T"+str(i))
			t.setDaemon(True)
			Threads.append(t)  

		#记录测试开始时间
		t1 = time.time()

		#打开线程
		for t in Threads:
			t.start()
		for t in Threads:
			t.join()

			
		self.i_print("main thread end")

		#记录结束时间
		t2 = time.time()
		self.i_print("=====================================")
		self.i_print("URL:"+TEST_URL)
		self.i_print("任务数量:"+str(THREAD_NUM)+"*"+str(A_THREAD_LOOP)+ "="+str(THREAD_NUM*A_THREAD_LOOP))
		self.i_print("总耗时(秒):"+ str(t2-t1))
		self.i_print("每次请求耗时(秒):"+ str((t2-t1) / (THREAD_NUM*A_THREAD_LOOP)))
		self.i_print("每秒承载请求数:"+ str(1 / ((t2-t1) / (THREAD_NUM*A_THREAD_LOOP))))
		self.i_print("错误数量:"+ str(ERROR_NUM))
		self.i_print("获取数目:"+ str(GET_TAR))
		print('Press Any Key To Exit!')


if __name__ == '__main__':
	t = TEST()
	t.test()
	input()
	#getHtml(1)
	#print(TEST_URL)
