#coding=utf-8
import requests
import threading
import time
from Tkinter import END,NORMAL
import json
import xlsxwriter
import os
import logging,traceback
import sys 
reload(sys) 
sys.setdefaultencoding('utf-8')

path_list=os.path.abspath(sys.argv[0]).split('\\')
path_list.pop()
path='\\'.join(path_list)+'\\'
path=unicode(path,"gb2312")  
result_path=path+'result\\'

if not os.path.exists(result_path):#目录不存在则创建
    os.makedirs(result_path)

def createlogger(name): 
    logger = logging.getLogger(name)
    logger.setLevel("DEBUG")
    fh = logging.FileHandler(result_path+"http_request.log")
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d: [%(levelname)s] [%(name)s] [%(funcName)s] %(message)s',
        '%y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def log_traceback(traceback):
    """print traceback information with the log style."""
    str_list = traceback.split("\n")
    for string in str_list:
        logger.warning(string)   
    
logger = createlogger("http_request")


class Request(threading.Thread):
    
    def __init__(self,test_list,data_list,excel_name,app):
        threading.Thread.__init__(self)
        self.test_list=test_list
        self.data_list=data_list
        self.test_num=len(test_list)
        self.excel_name=excel_name
        self.app=app
        self.result_list=[]
        self.response_list=[]
        
    def get_response(self):
        headers = {'content-type':'application/json'}
        for uid in self.test_list:
            name = self.data_list[0][uid]
            url=self.data_list[1][uid]
            req_path=self.data_list[2][uid]
            params=eval(self.data_list[3][uid])
            params_type=self.data_list[4][uid]
            req_type=self.data_list[5][uid]
            expect=self.data_list[6][uid]
            func=self.data_list[7][uid]
            
            if func == '' or func.isspace():
                if req_type == 'GET':
                    response = requests.get(url + req_path, params=params, headers=headers)
                elif req_type == 'POST':
                    if params_type=='dict':
                        response = requests.post(url + req_path, data=params, headers=headers)
                    elif params_type=='json':
                        response = requests.post(url + req_path, data=json.dumps(params), headers=headers)
                elif req_type == 'PUT':
                    response = requests.put(url + req_path, data=params, headers=headers)

                res_code=str(response.status_code)
                res_url=response.url
                res_text=response.text.encode('utf-8')
            else:
                if not os.path.exists(path+'function.py'):
                    self.app.text_msglist.insert(END,'文件丢失，请将function.py文件放到当前目录下\n','red')
                    logger.debug('文件丢失，请将function.py文件放到当前目录下')
                cmd='python '+path+'function.py '+func+' > '+result_path+'11.txt'
                logger.debug(cmd)
                os.popen(cmd)
                time.sleep(0.5)
                res=self.get_function()
                res_code=res[0]
                res_url=res[1]
                res_text=res[2].encode('utf-8')
                
            if expect in res_text:
                pf='Pass'
                bg='blue'
            else:
                pf='Fail'
                bg='red'
            self.result_list.append(pf)   
            self.response_list.append([res_code,res_url,res_text])
            self.app.text_msglist.insert(END,name+':'+res_code+'\n','blue')
            self.app.text_msglist.insert(END,pf+'\n\n',bg)
            self.app.text_msglist.see(END)
            logger.debug(name+':'+res_code)
            logger.debug('---------------------request url:--------------------------')
            logger.debug(res_url+'\n')
            logger.debug('---------------------response text:-----------------------')
            logger.debug(res_text+'\n\n')
            time.sleep(0.1)

    def get_function(self):
        f=open(result_path+'11.txt','rb')
        res_code=f.readline()
        res_url=f.readline()
        res_url=res_url.rstrip('\n')# 移除行尾换行符
        res_url=res_url.rstrip('\r')#防止excel打开报错‘发现不可读取内容’
        res_text=f.readline()
        f.close()
        return(res_code,res_url,res_text)
        
    

    def write_xlsx(self):
        w=xlsxwriter.Workbook(result_path+'result_'+self.excel_name)
        ws1=w.add_worksheet('result')
        ws2=w.add_worksheet('test_url')
        format_dict={'align':'vcenter','font_name':'Microsoft yahei','font_size':'10','text_wrap':'true'}
        rowformat=w.add_format(format_dict)
        bg_format1=w.add_format(format_dict)
        bg_format1.set_fg_color('#008B00')
        bg_format2=w.add_format(format_dict)
        bg_format2.set_fg_color('#FF4500')
        ws1.set_column('A:A',20)
        ws1.set_column('B:B',15)
        ws1.set_column('C:C',110)
        ws1.set_column('D:D',15)
        ws2.set_column('A:A',20)
        ws2.set_column('B:B',200)
        title1=['interface_name','response code','response text','expect match','result']
        title2=['interface_name','url']
        ws1.write_row('A1',title1,rowformat)
        ws2.write_row('A1',title2,rowformat)
        
        for i in range(self.test_num):
            ws1.set_row(i+1,30,rowformat)
            ws1.write(i+1,0,self.data_list[0][self.test_list[i]])
            ws2.write(i+1,0,self.data_list[0][self.test_list[i]])
            ws2.write(i+1,1,self.response_list[i][1])
            ws1.write(i+1,1,self.response_list[i][0])
            ws1.write(i+1,2,self.response_list[i][2])
            ws1.write(i+1,3,self.data_list[6][self.test_list[i]])
            if self.result_list[i]=='Pass':
                ws1.write(i+1,4,self.result_list[i],bg_format1)
            else:
                ws1.write(i+1,4,self.result_list[i],bg_format2)
        w.close()
    
    def run(self):
        try:
            self.get_response()
            self.write_xlsx()
            self.app.text_msglist.insert(END,'测试完成，结果请查看当前目录下excel文件\n','blue')
            self.app.b1.config(state=NORMAL)
        except Exception,e:
            print e
            log_traceback(traceback.format_exc())
            self.app.text_msglist.insert(END, traceback.format_exc(),'red')
            self.app.b1.config(state=NORMAL)
