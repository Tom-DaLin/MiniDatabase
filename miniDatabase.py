
"""
Created on Sat Oct 24 09:02:18 2020

@author: Team317
"""
from tkinter import Tk
from tkinter import Toplevel
from tkinter.scrolledtext import ScrolledText
from tkinter import Text
from tkinter import Button
from tkinter import END
from tkinter import UNITS
from time import localtime, strftime, time
from pmydb.core.field import Field
from pmydb.core.temp import Engine
import prettytable
import sys
import threading


class GUI(Tk):  # @1
    
    def __init__(self, title):
        super(GUI, self).__init__()
        
        # 销毁窗口信号
        self.flag = True
        
        # 设置窗口的大小
        self.geometry('%dx%d' % (790, 505))
        
        # 设置窗口不可修改
        self.resizable(True, True)
        
        # 添加组件
        self.add_weight()
        
        # 设置标题
        self.set_title(title)
        
        # 数据库
        self.e = Engine()
        
        # 点击事件
        self.on_send_button_click(lambda: self.append_message("result", self.get_inputs()))
        
        
        
    def add_weight(self):
        """添加组件的方法"""
        
        ## 采用grid布局
        
        # 交互区
        chat_input_area = Text(self, name='chat_input_area')        
        chat_input_area['width'] = 100
        chat_input_area['height'] = 7
        chat_input_area.grid(row=0, column=0,pady=10)
        
        # run按钮
        send_button = Button(self, name='send_button')
        send_button['text'] = 'Run'
        send_button['width'] = 5
        send_button['height'] = 2
        send_button.grid(row=0, column=1)
        
        
        # 响应区
        chat_text_area = ScrolledText(self)
        chat_text_area['width'] = 110
        chat_text_area['height'] = 30
        chat_text_area.grid(row=1, column=0, columnspan =2)

        chat_text_area.tag_config('green', foreground='#008B00')
        chat_text_area.tag_config('system', foreground='red')
        
        self.children['chat_text_area'] = chat_text_area 
        
        
    def set_title(self, title):
        """设置标题"""
        self.title(title)

        
    def on_send_button_click(self, command):
        """注册事件， 当run按钮被点击时执行command方法"""
        self.children['send_button']['command'] = command
        
    def get_inputs(self):
        """获取输入框内容"""
        return self.children['chat_input_area'].get(0.0, END)        
        
    def clear_inputs(self):
        """清空输入框"""
        self.children['chat_input_area'].delete(0.0, END)
     
    def append_message(self, sender, message):
        
        try:
            print(message)
            message = self.e.handle(message)
            
        except Exception as exc:
                print('\033[00;31m' + str(exc))
                
        print("打印得到的信息：", message)
        if message[0] in ['insert', 'update', 'delete', 'create', 'drop', 'use']:
            print("返回成功执行")
            result = message[1]
            
        if message[0] in ['select','show']:
            data = message[1]
            print("data : ", data)
            pt = prettytable.PrettyTable(data[0].keys())
            pt.align = 'l'
            for line in data:
                pt.align = 'r'
                pt.add_row(line.values())
            print("返回表格内容")
            result = pt.get_string()
        
        if message == 'exit':
            print("goodby!")
            result = 'goodby'
            self.on_window_closed()
        
        """添加一条消息到聊天区"""
        print('result: ', result)
        send_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
        send_info = "%s: %s \n" % (sender, send_time)
        self.children['chat_text_area'].insert(END, send_info, 'green')
        self.children['chat_text_area'].insert(END, result + '\n')
         
        # 向下滚动屏幕
        self.children['chat_text_area'].yview_scroll(3, UNITS)
     
    def on_window_closed(self):
        """注册关闭窗口时执行的指令"""
        self.flag = False
        sys.exit
       

if __name__ == '__main__':
    window = GUI('miniDatabase')
    window.mainloop()
    
    def destory():
        if window.flag == False:
            print("destory-- 该退出了")
            window.destroy()
    t1 = threading.Thread(target=destory)
    t1.start()     
    
    # while True:
        
    #     if(window.flag == False):
    #         print("即将销毁窗口")
    #         window.destroy()
    #         print("窗口被销毁")
    #         break
        