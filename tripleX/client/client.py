#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from communication import mysocket
from graphic import UserInterface
import threading
from myThreading import MyThread #重写的线程类
import time
from queue import Queue
import pyperclip

server_add = ('152.136.147.50', 10086)

class Client:
    def __init__(self, server_add):
        self.socket = mysocket(server_add)
        # 将按键的动作回调传入ui类，当点击按键时调用带动作参数的回调函数（创建新线程运行）
        self.window = UserInterface(lambda cmd:MyThread(self.actions, cmd) )
        
        # 线程锁 进程信号（True:线程正常执行中，False:请求当前线程结束）
        self.lock = threading.Lock()
        self.rx_queue = Queue() #进程间通信

        # 执行动作的子线程，需要在类内登记。
        self.sub_threads = []

        MyThread(self.main)

    def _stop_sub_threads(self):
        # 给正在运行的线程发送停止通知
        for t in self.sub_threads:
            t.stop()
        while self.sub_threads:
            self.sub_threads.pop().join()

    def _await_any_sub_threads_terminated(self):
        # 等待任何一个子线程自己退出，当没有任何子线程时直接跳过
        while self.sub_threads:
            flag = True
            for t in self.sub_threads:
                flag = flag and t.is_alive()
            if not flag:
                break
            time.sleep(0.5)

    def actions(self, cmd):  
        '''
        被ui按键事件回调，回调时候带有参数cmd
        每次执行的action是一个新的线程，在执行具体业务功能之前先将通知已经在进行的线程退出
        '''
        self._stop_sub_threads()

        if cmd in ('COPY', 'PASTE'):
            # 控制显示
            self.window.action_btn_switch(False)
            state = '发送中..' if (cmd == 'COPY') else '接收中..'
            self.window.set_bottom_state(state)
            self.sub_threads.append( MyThread(self.progress_bar, 4) ) 
            
            # # 接收将要发送的信息
            tx_str = pyperclip.paste()
            self.sub_threads.append( MyThread( self.socket.report, 
                             cmd, self.rx_queue, tx_str) )
        
        elif cmd == 'CANCLE':
            self.socket.set_status('cancled')

        # 等待操作执行完毕（任何一个任务）
        self._await_any_sub_threads_terminated()
        self._stop_sub_threads()

        try:
            cases = {
            'recive success': '接收成功!',
            'send success':'发送成功!',
            'timeout':'超时!',
            'cancled':'已取消',
            }
            state = cases[self.socket.get_status()]
        except: # todo: 字典取值错误处理
            state = self.socket.get_status()
        finally: 
            # 改变底部状态
            self.window.progress_bar_visuality(False)
            self.window.set_bottom_state(state)  

        self.window.action_btn_switch(True)


    def progress_bar(self, t):
        '''
        设置进度条倒计时指定时间(s)
        '''
        this_thread = MyThread.current_thread()
        self.window.progress_bar_visuality(True)
        for x in range(t*10,-1,-1):
            self.window.set_progress_bar((x*100.0)/(t*10.0))
            # 如果监测结束线程通知，本线程则退出
            if this_thread.stopped():
                return
            time.sleep(0.1)
        self.socket.set_status('timeout')

    def main(self):
        print('client started..')
        self.window.msgbox_insert('Welcome, {}'.format(
                                self.socket.get_local_name()))

        while True:
            if not self.rx_queue.empty():
                data = self.rx_queue.get()
                pyperclip.copy(data)
                t = time.strftime('%H:%M:%S: ',time.localtime(time.time()))
                self.window.msgbox_insert('\n{}'.format(t) )
                self.window.msgbox_insert( '{}'.format(self.socket.get_status()) )

            time.sleep(0.5)

client = Client(server_add)

client.window.start_mainloop()
