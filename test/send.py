# coding: utf-8 -*- coding: UTF-8 -*-

import requests
import json

HOST = 'http://192.168.56.105:8069'
SERVER = 'TT'

URI_LOGIN = HOST + '/json/user/login'
URI_REGISTER = HOST + '/json/user/register'
URI_RESET_PASSWORD = HOST + '/json/user/reset/password'

URI_API       = HOST + '/json/api'


def ret(r):
    print 'status_code:', r.status_code
    print 'raw:', r.raw.read()
    print 'content:', r.content
    #print 'text:', r.text
    print 'headers:', r.headers

def t1(host=HOST):
    headers = {"content-type": "application/json" ,"credentials": "include"  }
    uri = host + '/json/test1'
    params = {}
    data = {}
    rspd = requests.post(uri,params=params,
                      data=json.dumps(data),
                      headers=headers)
                      
    ret(rspd)

print('t1')
#t1()

def jsonrpc(uri, data=None, params=None, sid=None, client=None):
        headers = {"content-type": "application/json"  }
        data1 = {"jsonrpc":"2.0",
                "method":"call",
                "id":123,
                "params":data and data or {}
                }
        
        params1 = params and params.copy() or {}
        if sid:                      
            params1.update( {'session_id':usid} )

        
        if not client:
            client=requests
        
        rspd = client.post(uri,params=params1,
                          data=json.dumps(data1),
                          headers=headers)
        #ret(rspd)
        return json.loads(rspd.content).get('result',{})

def execute(sid, model, method, *args, **kwargs ):
    return jsonrpc(URI_API,{'model':model, 'method': method, 'args': args, 'kwargs': kwargs},sid=sid )

api = execute
        
class UserSudo(object):
    def login(self,user,psw,db=SERVER):
        """  check ok uid
        """
        result = jsonrpc(URI_LOGIN, {'db': db,'login':user, 'password':psw, 'type':'account'} )
        return result.get('sid',None)

    def register(self,user,psw, db=SERVER):
        """  sudo(), create(), uid
        """
        return jsonrpc(URI_REGISTER, {'db': db,'login':user, 'password':psw} )

    def reset_password(self, user,newpsw, db=SERVER):
        """  sudo(), write(), uid
        """
        return jsonrpc(URI_RESET_PASSWORD, {'db': db,'login':user, 'password':newpsw} )
    
print('usid')
#usid = UserSudo().login('u1','123')
usid = UserSudo().login('admin','123')
print(usid)


print( 't3 msg post' )

def t3(host=HOST):
    headers = {"content-type": "application/json"  }
    
    uri = host + '/web/dataset/call_kw/mail.channel/message_post'
    uri = host + '/web/dataset/call_kw'
    uri = host + '/json/api'
    
    
    msg_bid = {
        'uid':1,
        'board_id': 2,
        'table_id': 1,
        'state': 'bidding',
        'bidder': 'E',
        'call_ids':[1,2,3,4],
    }
    
    msg_play = {
        'uid':1,
        'board_id': 2,
        'table_id': 1,
        'state': 'playing',
        'call_ids':[1,2,3,4],
        'declarer': 'E',
        'contract': '2NTxx',
        'player': 'E',
        'last_trick':[1,2,3],
        'current_trick':[1,2,3],
        'win': 2,
        'opp_win': 2
        
    }
    
    
    data ={
                        #"model":"mail.channel",
                        "model":"og.channel",
                        "method":"message_post",
                        "args":[10],
                        "kwargs":{
                                  #"message_type":"comment",
                                  #"subtype":"mail.mt_comment",
                                  "subject":"game",
                                  "body":json.dumps( msg_bid ),
                                  }
                      }
    

    return jsonrpc(uri,data=data,sid=usid )

#print  t3()

print( 't4 bid then msg post' )

def bid(args,host=HOST):
    headers = {"content-type": "application/json"  }
    uri = host + '/json/api'
    
    data ={ "model":"og.board",
            "method":"bid",
            "args": args,
            "kwargs":{}
          }
    

    return jsonrpc(uri,data=data,sid=usid )

bid([2,'E','Pass'])
bid([2,'S','Pass'])
bid([2,'W','3S'])
bid([2,'N','Pass'])
bid([2,'E','Pass'])
bid([2,'S','Pass'])

