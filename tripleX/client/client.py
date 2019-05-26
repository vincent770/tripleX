#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from communication import mysocket
import threading
from myThreading import MyThread #重写的线程类
import time
from queue import Queue
import pyperclip

from qttray import Window_tray
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

server_add = ('106.12.205.8', 49322)

import sys
import os
app = QApplication(sys.argv)
clipboard = QApplication.clipboard()

class Client:
    def __init__(self, server_add):
        self.socket = mysocket(server_add)
        
        # 将按键的动作回调传入ui类，当点击按键时调用带动作参数的回调函数（创建新线程运行）
        self.window = Window_tray( lambda cmd:self.actions(cmd), 
                str(self.socket._get_local_info()['addr']))
    
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
            # check if data is local file paths.
            data  = clipboard.mimeData()
            self.recent_msg = data
            self.window.set_menu_visibility(cmd)
            action_thread = MyThread( self.socket.report, 
                                    cmd, self.rx_queue, data)
            self.sub_threads.append(action_thread)
        elif cmd == 'CANCEL':
            self.window.set_menu_visibility('INIT')
            self.socket.set_status('cancel')
        elif cmd == 'SHOW':
            self.window.show()
            self.window.write_to_textEdit(self.history)

    def socket_status_handling(self):
        if self.socket.get_status() == 'files to be sent':
            send_thread = MyThread(self.socket.send_files)
            if not send_thread.is_alive():
                self.socket.set_status('files sent') 

            self.socket.set_status('file sending') 
        if self.socket.get_status() != 'ready':
            try:
                cases = {
                'recive success': '接收成功!',
                'send success':'发送成功!',
                'timeout':'超时!',
                'cancel':'已取消!',
                'file sending':'发送文件..',
                'receiving files':'接收文件..',
                'file received': '文件接收成功',
                'files sent':'文件发送成功'
                }
                state = cases[self.socket.get_status()]
            except: # todo: 字典取值错误处理
                state = self.socket.get_status()
            finally:     
                self.socket.set_status('ready')
                self.window.set_menu_visibility('INIT')
                self.window.tray_notify(title='tripleX', message=state )


    def save_files_to_clipboard(self):
        while True:
            local_paths = self.socket.save_files()
            
            self.socket.set_status('file received')
            
            print('put path into clipboard:',local_paths)
            data = QtCore.QMimeData()
            url = [QtCore.QUrl.fromLocalFile(path) for path in local_paths]
            data.setUrls(url)
            clipboard.setMimeData(data)


    def main(self):
        print('client started..')
        
        MyThread(self.save_files_to_clipboard)

        while True:
            if not self.rx_queue.empty():
                data = self.rx_queue.get()
                # pyperclip.copy(data)
                clipboard.setText(data)
                t = time.strftime('%H:%M:%S   ',time.localtime(time.time()))
                self.history += t + '\r\nrecived:' + data+'\r\n'

            self.socket_status_handling()
            time.sleep(1)

client = Client(server_add)
sys.exit(app.exec())