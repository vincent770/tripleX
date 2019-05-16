#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from communication import mysocket
import threading
from myThreading import MyThread #重写的线程类
import time
from queue import Queue
import pyperclip

from PyQt5.QtWidgets import QApplication
from qttray import Window_tray

server_add = ('152.136.147.50', 10086)

class Client:
    def __init__(self, server_add):
        self.socket = mysocket(server_add)
        
        # # 将按键的动作回调传入ui类，当点击按键时调用带动作参数的回调函数（创建新线程运行）
        self.window = Window_tray( lambda cmd:self.actions(cmd) )
    
        # 线程锁 进程信号（True:线程正常执行中，False:请求当前线程结束）
        self.lock = threading.Lock()
        self.rx_queue = Queue() #进程间通信
        # 执行动作的子线程，需要在类内登记。
        self.sub_threads = []

        self.history = ''
        self.recent_msg = ''
        MyThread(self.main)

    def _stop_sub_threads(self):
        # 给正在运行的线程发送停止通知
        for t in self.sub_threads:
            t.stop()
        while self.sub_threads:
            self.sub_threads.pop().join()

    def actions(self, cmd):  
        '''
        被ui按键事件回调，回调时候带有参数cmd
        每次执行的action是一个新的线程，在执行具体业务功能之前先将通知已经在进行的线程退出
        '''
        self._stop_sub_threads()
        if cmd in ('COPY', 'PASTE'):
            tx_str = pyperclip.paste()
            self.recent_msg = tx_str
            self.window.set_menu_visibility(cmd)
            action_thread = MyThread( self.socket.report, 
                                    cmd, self.rx_queue, tx_str)
            self.sub_threads.append(action_thread)
            # action_thread.join()

        elif cmd == 'CANCEL':
            self.window.set_menu_visibility('INIT')
            self.socket.set_status('cancel')
        elif cmd == 'SHOW':
            self.window.show()
            self.window.write_to_textEdit(self.history)

    def user_notifing(self):
        if self.socket.get_status() != 'ready':
            try:
                cases = {
                'recive success': '接收成功!',
                'send success':'发送成功!',
                'timeout':'超时!',
                'cancel':'已取消!',
                }
                state = cases[self.socket.get_status()]
            except: # todo: 字典取值错误处理
                state = self.socket.get_status()
            finally:     
                self.socket.set_status('ready')
                self.window.set_menu_visibility('INIT')
                self.window.tray_notify(title='tripleX', message=state )


    def main(self):
        print('client started..')
        while True:
            if not self.rx_queue.empty():
                data = self.rx_queue.get()
                pyperclip.copy(data)

                t = time.strftime('%H:%M:%S   ',time.localtime(time.time()))
                self.history += t + '\r\nrecived:' + data+'\r\n'

            self.user_notifing()
            time.sleep(0.5)
import sys
app = QApplication(sys.argv)

client = Client(server_add)
sys.exit(app.exec())
