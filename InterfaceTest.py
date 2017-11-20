from Tkinter import *
import tkFileDialog
import os
import xlrd
import http_request
import traceback


class InterfacePage (Frame):
    
    def __init__(self,master):
        Frame.__init__(self,master)
        self.root=master
        self.root.title('interface test')
        self.root.geometry('810x650')
        self.root.protocol("WM_DELETE_WINDOW",self.close)
        self.createPage()
        
    def get_data(self,file_name):
        wb = xlrd.open_workbook(file_name)
        table_data = wb.sheet_by_index(0) 
        name_list=table_data.col_values(1)[1:]
        url_list=table_data.col_values(2)[1:]
        path_list=table_data.col_values(3)[1:]
        params_list=table_data.col_values(4)[1:]
        params_type_list=table_data.col_values(5)[1:]
        type_list=table_data.col_values(6)[1:]
        expec_list=table_data.col_values(7)[1:]
        func_list=table_data.col_values(8)[1:]
        self.data_list=[name_list,url_list,path_list,params_list,params_type_list,type_list,expec_list,func_list]
        wb.release_resources()
        del wb

    def createPage(self):
        self.file_path=StringVar()
        frame_left_top = Frame(self.root, width=430, height=100, bg='#C1CDCD')
        frame_left_center = Frame(self.root, width=430, height=435, bg='#C1CDCD')
        frame_left_bottom = Frame(self.root, width=430, height=115, bg='#C1CDCD')
        frame_right = Frame(self.root, width=380, height=650, bg='#C1CDCD')
        frame_left_top.grid_propagate(0)
        frame_left_center.grid_propagate(0)
        frame_left_bottom.grid_propagate(0)
        frame_right.propagate(0)
        frame_right.grid_propagate(0)
        frame_left_top.grid(row=0,column=0)
        frame_left_center.grid(row=1,column=0)
        frame_left_bottom.grid(row=2,column=0)
        frame_right.grid(row=0,column=1,rowspan=3)
      
        Label(frame_left_top, text = u'请选择相应的接口配置文件',bg='#C1CDCD').grid(row=0,column=0,columnspan=2,padx=20, pady=8)
        Entry(frame_left_top, width=51,textvariable=self.file_path).grid(row=1, column=0, padx=2,stick=W,pady=8)  
        Button(frame_left_top, text = '选择文件',command=self.open_file,bg='#C1CDCD').grid(row=1, column=2,stick=W, pady=8)  
        #Scrollbar
        scrollbar = Scrollbar(frame_right,bg='#C1CDCD')
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_msglist = Text(frame_right, yscrollcommand=scrollbar.set,bg='#C1CDCD')
        self.text_msglist.pack(side=RIGHT, fill=BOTH)
        scrollbar['command'] = self.text_msglist.yview
        self.text_msglist.tag_config('blue', foreground='#0000FF')
        self.text_msglist.tag_config('red', foreground='#FF3030')

        # Add a canvas in center frame
        self.Can1 = Canvas(frame_left_center, bg='#C1CDCD',width=410,height=435)
        self.Can1.grid(row=0, column=0)
        vsbar = Scrollbar(frame_left_center, orient="vertical", command=self.Can1.yview)
        vsbar.grid(row=0, column=1, sticky='ns')
        self.Can1.configure(yscrollcommand=vsbar.set)
        
        Button(frame_left_bottom, text=u"全选",command=self.select, bg='#C1CDCD').grid(row=0,column=0,padx=86,pady=8,sticky=W)
        Button(frame_left_bottom, text=u"反选",command=self.deselect, bg='#C1CDCD').grid(row=0,column=1,padx=86,pady=8,sticky=W)
        self.b1=Button(frame_left_bottom, text=u"开始测试",command=self.start_test, bg='#C1CDCD')
        self.b1.grid(row=1,column=0,columnspan=2,padx=60,pady=10)


    def set_frame_buttons(self):
        self.Can1.delete("all")
        self.frame_buttons = Frame(self.Can1, bg='#C1CDCD', bd=1,relief=GROOVE)
        self.Can1.create_window((0,0), window=self.frame_buttons,anchor='nw')
        self.frame_buttons.bind("<Configure>", self.resize)
        
    def resize(self,event):
        self.Can1.configure(scrollregion=self.Can1.bbox("all"), width=410, height=435)
            
    def open_file(self):    
        file_name = tkFileDialog.askopenfilename()
        if file_name == '':
            return 0
        self.file_path.set(file_name)
        self.set_frame_buttons()
        self.initialize_page(file_name)

    def initialize_page(self,file_name):
        self.var={}
        self.ck={}
        self.get_data(file_name)
        self.num=len(self.data_list[0])
        self.excel_name=os.path.basename(file_name)
        self.root.title(self.excel_name)
        for i in range(self.num):
            self.var[i]=IntVar()
            text=self.data_list[0][i]
            name=self.get_name(text)
            self.ck[i]=Checkbutton(self.frame_buttons,variable = self.var[i],text=name,bg='#C1CDCD')
            self.ck[i].grid(row=i/2+1,column=i%2,padx=5,pady=6,sticky='w')
        flag=self.num%2
        if flag:
            Checkbutton(self.frame_buttons,text=' ',bg='#C1CDCD').grid(row=self.num/2+1,column=1,padx=6,pady=6,sticky='w')
        for j in range(22-self.num-flag):
            Checkbutton(self.frame_buttons,text=' ',bg='#C1CDCD').grid(row=self.num/2+j/2+1+flag,column=j%2,padx=6,pady=6,sticky='w')
        
        
    def get_name(self,text):
        '''固定名称长度大小'''
        text=text+' '*60
        textBytes = text.encode('utf-8')
        i=40
        while 1:
            try:
                name=textBytes[:i].decode('utf-8')
                break
            except UnicodeDecodeError ,e:
                i=i+1
        return name   
        
    def start_test(self):
        test_list=[]
        for i in range(self.num):    
            if self.var[i].get():
                test_list.append(i)
        self.b1.config(state=DISABLED)
        thread=http_request.Request(test_list,self.data_list,self.excel_name,self)
        thread.setDaemon(True)
        thread.start()
        
    def close(self):  
        self.root.quit()
        self.root.destroy()

    def select(self):
        for ck in self.ck:
            self.ck[ck].select()
    
    def deselect(self):
        for v in self.var:
            if self.var[v].get():
                self.ck[v].deselect()
            else:
                self.ck[v].select()

if __name__ == "__main__":
    #try:
        root = Tk()   
        InterfacePage(root)
        root.mainloop()
    #except Exception,e:
        #http_request.log_traceback(traceback.format_exc())
        


