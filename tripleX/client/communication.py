#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import time
import json
from queue import Queue
from myThreading import MyThread #重写的线程类

class mysocket:
    def __init__(self, add ):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.port = 10000
        while True:
            try:
                self.s.bind( ('', self.port) )
                break
            except:
                print('Port:', self.port, 'unavailable!')
                self.port +=1
                continue
        self.server_addr = add
        self.status = 'ready'
        self.info = self._get_local_info()
        print(self.info)

    def _get_local_info(self):
        import uuid
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
        mymac = ":".join([mac[e:e+2] for e in range(0,11,2)])     
        myname = socket.gethostname()
        myaddr = socket.gethostbyname(myname)

        info = {
            'mac':mymac,
            'name':myname,
            'addr':(myaddr, self.port),
        }
        return info

    def get_local_name(self):
        return self.info['name']

    def report(self, action, rx_queue, tx_str):
        this_thread = MyThread.current_thread()

        # 向服务器发送请求
        self.info['action'] = action
        self.info['time'] = time.time()
        request_cmd = bytes(json.dumps(self.info), encoding='utf-8' )

        self.s.sendto(request_cmd, self.server_addr)

        self.s.settimeout(0)
        self.s.setblocking(False)
        for t in range(30): # 通信阻塞接收时间最高是15秒(30*0.5)
            if this_thread.stopped():
                return
            try:
                msg, addr = self.s.recvfrom(1024) #阻塞直到接收数据
            except socket.error as e: # todo: 其他错误处理
                time.sleep(0.5)
                continue

            if addr:
                print('msg recived: ', msg)
                break
        else: # 超时 退出线程
            self.set_status('timeout')
            return

        if this_thread.stopped():
            return

        if(addr == self.server_addr):# 从服务器发来的接收者ip列表
            try:
                target_list = json.loads(msg.decode("utf-8"))
                
            except ValueError as e:
                self.set_status('send faild: json parse error')
                print(e)
                return
            # 向各个接收端发送数据
            for target in target_list:
                print('msg sent:', tuple(target))
                self.s.sendto(bytes(tx_str, encoding='utf-8'), tuple(target))
            self.set_status('send success')
        else: # 发送端的数据
            data = bytes.decode(msg,encoding='utf-8')
            rx_queue.put(data)  # 将数据放入队列
            self.set_status('recive success')
        
    def set_status(self, status):
        self.status = status

    def get_status(self):
        return self.status


if __name__ == '__main__':    
    import threading

    socketQueue = Queue(maxsize=1000)
    c = mysocket()
    while True:
        cmd, *data = input('give a command[cmd,msg]:').split(',')
        if(cmd == 'C'):
            threading.Thread(target=c.send_to_others, args=(data[0],)).start()
        elif(cmd == 'V'):
            threading.Thread( target=c.recive_from_others, args=(socketQueue,) ).start()
