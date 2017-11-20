#coding=utf-8
import requests
import sys
import re
import json
import MySQLdb

headers = {'content-type':'application/json'}

def yunwei13():
    '''运维修改管理员接口，默认使用机器3005，管理员为601，亲友602'''
    url='http://58.60.230.238:11109/manager/permission?'
    params={"uid":"3005","robot":"aaaabbbbccccddddaaaabbbbcc102005",\
     "old_mgr":"qhtest601","new_mgr":"qhtest602","dsc":"modifymanager","opr_user":"ericyong"}
    response = requests.get(url, params=params, headers=headers)
    params['old_mgr']='qhtest602'
    params['new_mgr']='qhtest601'
    #再次运行接口将管理员改回qhtest601 
    response = requests.get(url, params=params, headers=headers)
    return response


def mps_get_token():
    token='get token empty'
    url='http://58.60.230.238:29285/api/v1/qlink/admin/authorize/token'
    params={"grant_type":"authorization_code","user_name":"qhtest1","password":"25d55ad283aa400af464c76d713c07ad"}
    token_response = requests.post(url, data=json.dumps(params), headers=headers)
    token_list= re.findall(r'"access_token":"(.+?)"',token_response.text,re.S)
    if token_list:
        token=token_list[0]
    else:
        token=' '
    return token
    
def mps4():
    '''手机端获取机器人分组数据'''
    #获取当前用户token
    token=mps_get_token()
    url='http://58.60.230.238:29285/api/v1/qlink/robot/group'
    params={ "access_token":token,"qlink_id":1}
    response = requests.post(url, data=json.dumps(params), headers=headers)
    return response

def mps5():
    '''手机端获取机器人数据'''
    #获取当前用户token
    token=mps_get_token()
    url='http://58.60.230.238:29285/api/v1/qlink/robot/page'
    params={"access_token":token,"qlink_id":1, "gid":0,"page_size":10,"page_index":1 }
    response = requests.post(url, data=json.dumps(params), headers=headers)
    return response
 
def mps6():
    '''手机端获取MPS业务类型'''
    #获取当前用户token
    token=mps_get_token()
    url='http://58.60.230.238:29285/api/v1/qlink/feature/type'
    params={"access_token":token,"qlink_id":1,"lang":"zh"}
    response = requests.post(url, data=json.dumps(params), headers=headers)
    return response

def mps7():
    '''手机端获取MPS具体类型业务数据'''
    #获取当前用户token
    token=mps_get_token()
    url='http://58.60.230.238:29285/api/v1/qlink/feature/type/page'
    params={"access_token":token,"qlink_id":1,"type":1,"page_size": 20,"page_index": 1}
    response = requests.post(url, data=json.dumps(params), headers=headers)
    return response

def mps8():
    '''手机端MPS业务推送'''
    #查询用户名下机器人
    conn = MySQLdb.connect(host='58.60.230.238',user='root',passwd='qhkj_mysql_987',port=3207)
    cur = conn.cursor()
    conn.select_db('qhmpms')
    cur.execute('select * from mpms_qlink_dev_id where qlinkId=1 limit 1')
    result=cur.fetchone()
    if result:
        did=result[3]
    #获取当前用户token
    token=mps_get_token()
    url='http://58.60.230.238:29285/api/v1/qlink/feature/push'
    params={"access_token":token,"qlink_id":1,"id":1,"type": 1,"dids":[did]}
    response = requests.post(url, data=json.dumps(params), headers=headers)
    return response


def mps9():
    '''手机端MPS业务推送记录查看'''
    #获取当前用户token
    token=mps_get_token()
    url='http://58.60.230.238:29285/api/v1/qlink/feature/push/log/page'
    params={"access_token":token,"qlink_id":1, "type":1,"page_size":20,"page_index":1}
    response = requests.post(url, data=json.dumps(params), headers=headers)
    return response


def mps10():
    '''手机端MPS业务推送详情查看'''
    #查询用户已推送任务id
    task_id='get task_id empty'
    conn = MySQLdb.connect(host='58.60.230.238',user='root',passwd='qhkj_mysql_987',port=3207)
    cur = conn.cursor()
    conn.select_db('qhmpms')
    cur.execute('select * from mpms_trumpet_push_history where qlinkId=1 limit 1')
    result=cur.fetchone()
    if result:
        task_id=result[-1]
    #获取当前用户token
    token=mps_get_token()
    url='http://58.60.230.238:29285/api/v1/qlink/feature/push/log/detail'
    params={"access_token":token,"qlink_id":1,"task_id":task_id}
    response = requests.post(url, data=json.dumps(params), headers=headers)
    return response




if __name__=='__main__':
   
    
    res=eval(sys.argv[1]+'()')
    print res.status_code
    print res.url
    print res.text
 
    
    
