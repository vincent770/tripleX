#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import time
import json
import logging

logging.basicConfig(level=logging.INFO,
                    filename='tripleX.log',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')
class Server:
    def __init__(self):
        # hostIP = socket.gethostbyname(socket.gethostname())
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.port = 10086
        while True:
            try:
                # 尝试绑定未被占用的端口，直到成功
                self.s.bind( ('', self.port) )
                break
            except:
                logging.warning('Port:{} is unavailable, change one another.'.format(self.port))
                self.port +=1
                continue

        self.info = self._get_local_info()
        self.info['port'] = self.port
        logging.info('server info:{}'.format(self.info) )
        logging.info('Triple X server is started on port:{}'.format(self.port) )

    def _get_local_info(self):
        import uuid
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
        mymac = ":".join([mac[e:e+2] for e in range(0,11,2)])     
        myname = socket.gethostname()
        myaddr = socket.gethostbyname(myname)

        info = {
            'mac':mymac,
            'name':myname,
            'addr':myaddr,
        }
        return info

    def wait_for_pairing(self, timeout=10):
        request_list = {}
        time_recv = 0
        while True:
            msg, addr = self.s.recvfrom(1024) #阻塞直到接收到数据
            request_info = json.loads(msg.decode("utf-8"))
            request_info['scoure address'] = addr
            logging.debug('recieved a request, info:{}'.format(request_info) )

            # 若离上一次接收到的数据间隔时间很长，则清空列表并将此用户设为第一个 
            if((time.time() - time_recv) > timeout):    
                request_list = {}

            # 同一用户只保留最新指令   
            request_list[str(addr)] = request_info

            logging.info('clients refresh:{}'.format(request_list))
            
            time_recv = time.time()
            # 监测是否同时存在发送者和接收者
            cmds = [info['action'] for info in request_list.values()]

            if('COPY' in cmds) and ('PASTE' in cmds):
                logging.debug('matched!')
                return request_list

    def server_mainloop(self):          
        while True:
            clients = self.wait_for_pairing()

            sender_request = [r for r in clients.values() if r['action']=='COPY']
            reciver_requests = [r for r in clients.values() if r['action']=='PASTE']

            if(len(sender_request) != 1):
                logging.error('number of sender(s) is not 1, abord.')
            else:
                reciver_addrs = [msg['addr'] for msg in reciver_requests]

                self.s.sendto( bytes( json.dumps(reciver_addrs), encoding='utf-8' ),
                                sender_request[0]['scoure address'])

                logging.info('requests handled.\r\nfrom:{}\r\nto:{} \r\nCommunication addr is:{}'.format(
                            sender_request[0]['addr'], # 局域网发送者地址
                            reciver_addrs,  # 局域网接收者地址
                            sender_request[0]['scoure address'] ) ) # 公网发送者地址


x_server =  Server()
x_server.server_mainloop()