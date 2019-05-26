#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import time
import json
from queue import Queue
from myThreading import MyThread #重写的线程类
import ifolder

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

        self.file_recv = ifolder.Receiver()

        self.server_addr = add
        self.status = 'ready'

        import tempfile
        self.tmp_folder = tempfile.mkdtemp(suffix='', prefix='tripleX', dir=None)
        print('temp_folder created: ', self.tmp_folder)

        self.info = self._get_local_info()
        print(self.info)


    def _get_local_ip(self):
        local_ip = ""
        try:
            socket_objs = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
            ip_from_ip_port = [(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in socket_objs][0][1]
            ip_from_host_name = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
            local_ip = [l for l in (ip_from_ip_port, ip_from_host_name) if l][0]
        except (Exception) as e:
            print("get_local_ip found exception : %s" % e)
        
        return local_ip if("" != local_ip and None != local_ip) else socket.gethostbyname(socket.gethostname())
        

    def _get_local_info(self):
        import uuid
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
        mymac = ":".join([mac[e:e+2] for e in range(0,11,2)])     
        myname = socket.gethostname()

        info = {
            'mac':mymac,
            'name':myname,
            'addr':(self._get_local_ip(), self.port),
            'file_recv_port':self.file_recv.get_IP(),
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
                recv_requests = json.loads(msg.decode("utf-8"))
                
            except ValueError as e:
                self.set_status('send faild: json parse error')
                print(e)
                return
            # 向各个接收端发送数据
            for recv_request in recv_requests:
                print('recv request:', recv_request)
                
                data = tx_str
                if data.hasFormat('text/uri-list'):
                    self.files_paths = [url.path() for url in data.urls()]       
                    # to do   弹窗提示是否要发送
                    self.files_ip = tuple(recv_request['file_recv_port'])
                    self.set_status('files to be sent')
                    
                    self.s.sendto(b'10086cd641232178899ffef'+bytes(data.text(), encoding='utf-8'), tuple(recv_request['addr']))
                    return # 监测到文件，需要返回主线程处理
                else:
                    self.s.sendto(bytes(data.text(), encoding='utf-8'), tuple(recv_request['addr']))
            
            self.set_status('send success')
        else: # 发送端的数据
            data = bytes.decode(msg,encoding='utf-8')
            if data.startswith('10086cd641232178899ffef'):
                self.set_status('receiving files')
            else:
                data = data[23:]  
                rx_queue.put(data)  # 将数据放入队列
                self.set_status('recive success')

    def save_files(self): 
        files_path = self.file_recv.save_files_to(self.tmp_folder)
        return files_path


    def send_files(self):
        ifolder.Sender(self.files_ip).send(self.files_paths)


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
