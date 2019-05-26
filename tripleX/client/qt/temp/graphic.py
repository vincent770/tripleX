from tkinter import *    #注意模块导入方式，否则代码会有差别
from tkinter import ttk
from tkinter.ttk import Progressbar
from myThreading import MyThread #重写的线程类
import time

class UserInterface:
    def __init__(self,cbs):
        # self.cbs ={'btn_send':cb_send,'btn_recv':cb_recv}
        self.btn_list = []

        self.master = Tk()
        self.master.title("TripleX - Version:1.0.0")
        self.master.geometry('350x210')

        frm_btn = Frame(self.master,bg='#141414')	# 操作按钮
        frm_msg = Frame(self.master) # 信息展示
        frm_btn_bar = Frame(self.master) # 进度信息条

        frm_btn.pack(expand=True)
        frm_msg.pack(expand=True, fill = X)
        frm_btn_bar.pack(expand=True, fill = X)

        self.btn_send = Button(frm_btn,
                                command=lambda: cbs('COPY'), 
                                text='发送')
        self.btn_send.pack(side=LEFT)  

        self.btn_recv = Button(frm_btn,
                                command=lambda: cbs('PASTE'), 
                                text='接收')
        self.btn_recv.pack(side=RIGHT)  

        self.btn_cancle = Button(frm_btn,
                                command=lambda: cbs('CANCLE'), 
                                text='取消操作')

        self.msgbox = Text(frm_msg, bg='#FAFAFA', height=10)
        self.msgbox.pack()
        self.msgbox.config(state=DISABLED)

        self.lable_text = StringVar()
        self.lable_text.set('状态 ')
        self.btn_lable = Label(frm_btn_bar, textvariable=self.lable_text)
        self.btn_lable.pack(side=LEFT)

        self.pro_bar = Progressbar(frm_btn_bar)
        
    def action_btn_switch(self, condition = True):
        if condition:
            self.btn_send.pack(side=LEFT)  
            self.btn_recv.pack(side=RIGHT)
            self.btn_cancle.forget()
        else:
            self.btn_send.forget()
            self.btn_recv.forget()
            self.btn_cancle.pack(side=LEFT)
             
    def set_bottom_state(self, str):
        if str:
            self.lable_text.set(str)

    def progress_bar_visuality(self, condition):
        '''
        设置底部进度条的可视性
        参数：
        True: 显示
        False: 隐藏
        '''
        if condition:
            self.pro_bar.pack(side=LEFT, fill = X, expand =True)
        else:
            self.pro_bar.forget()

    def set_progress_bar(self, value):
        self.pro_bar["value"]= value
        return value

    def start_mainloop(self):
        self.master.mainloop()

    def msgbox_insert(self, str):
        self.msgbox.config(state=NORMAL)
        self.msgbox.insert(INSERT, str)
        self.msgbox.config(state=DISABLED)

if __name__ == '__main__':   
    
    def on_btn_r():
        print('recieve button clicked..')
        xUI.action_btn_switch(False)

    def on_btn_s():
        print('send button clicked..')
        xUI.action_btn_switch(False)

    def on_cancle():
        xUI.action_btn_switch(True)

    xUI = UI(on_btn_r, on_btn_s, on_cancle)
    xUI.start_mainloop()


