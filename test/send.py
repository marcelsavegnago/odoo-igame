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

class Board( object ):
    
    def __init__(self,sid,bd_id):
        self.sid = usid
        self.id = bd_id
        self.model = "og.board"
        
        self.fields = ['number','vulnerable','dealer','hands',
            'auction',
            'declarer',
            'contract',
            'last_trick',
            'current_trick',
            'ns_win','ew_win','result','point','ns_point','ew_point',
            'player',
            'state',
            
            ]

    def read(self):
        rec = execute(self.sid,self.model,"read",self.id,self.fields)
        self.number = rec[0]['number']
        self.vulnerable = rec[0]['vulnerable']
        self.dealer = rec[0]['dealer']
        self.hands = rec[0]['hands']
        self.auction = rec[0]['auction']
        self.declarer = rec[0]['declarer']
        self.contract = rec[0]['contract']
        self.last_trick = rec[0]['last_trick']
        self.current_trick = rec[0]['current_trick']
        self.ns_win = rec[0]['ns_win']
        self.ew_win = rec[0]['ew_win']
        self.player = rec[0]['player']
        self.state = rec[0]['state']
        self.result = rec[0]['result']
        self.point = rec[0]['point']
        self.ns_point = rec[0]['ns_point']
        self.ew_point = rec[0]['ew_point']
        
        return rec
        


    def get_random_call(self):
        return execute(self.sid,self.model,'get_random_call',self.id)
    
    def get_random_play(self):
        return execute(self.sid,self.model,'get_random_play',self.id)
    
    def get_random_claim(self):
        return execute(self.sid,self.model,'get_random_claim',self.id)
    
    
    def bid(self,pos,call):
        return execute(self.sid,self.model,"bid",self.id,pos,call)

    def play(self,pos,card):
        return execute(self.sid,self.model,"play",self.id,pos,card)
        
    def claim(self,pos,num):
        return execute(self.sid,self.model,"claim",self.id,pos,num)
        
    def claim_ok(self,pos):
        return execute(self.sid,self.model,"claim_ok",self.id,pos)


board = Board(usid,6)
self = board

def bid():
    rec = board.read()
    print 'deal', self.number, self.vulnerable, self.dealer
    print 'hands',self.hands
    print 'state,player',self.state,self.player
    print 'auction',self.auction
    print 'contract',self.declarer, self.contract

    player = board.player
    call = board.get_random_call()
    #player = 'N'
    #call = '2D'
    print player, call
    print board.bid(player,call)
    self.read()
    print 'auction',self.auction
    print 'contract',self.declarer, self.contract
    print 'tricks', self.last_trick,self.current_trick
    print 'win',self.ns_win, self.ew_win

    print 'state,player',self.state,self.player

def play():
    self.read()
    player = self.player
    flag, pos, card = self.get_random_play()
    print flag, pos, card
    if flag:
        self.play(pos, card)
    else:
        self.claim(pos, card)

    self.read()
    print 'hands',self.hands
    print 'tricks', self.last_trick,self.current_trick
    print 'win',self.ns_win, self.ew_win
    print 'state,player',self.state,self.player
    print 'result', self.result, self.point, self.ns_point,self.ew_point

def read():
    self.read()
    print 'deal', self.number, self.vulnerable, self.dealer
    print 'hands',self.hands
    print 'auction',self.auction
    print 'contract',self.declarer, self.contract
    print 'win',self.ns_win, self.ew_win
    print 'tricks', self.last_trick,self.current_trick
    print 'result', self.result, self.point, self.ns_point,self.ew_point

def claim():
    self.read()
    pos, num = self.get_random_claim()
    pos = self.declarer
    print pos, num
    print self.claim(pos, num)
    self.read()
    print 'hands',self.hands
    print 'tricks', self.last_trick,self.current_trick
    print 'win',self.ns_win, self.ew_win
    print 'state,player',self.state,self.player
    print 'result', self.result, self.point, self.ns_point,self.ew_point
   
#claim()
def claim_ok_lho():
    self.read()
    pos = self.declarer
    print self.claim_ok('S')
    print 'state,player',self.state,self.player
    
def claim_ok_rho():
    self.read()
    pos = self.declarer
    print self.claim_ok('N')
    print 'state,player',self.state,self.player
    
claim_ok_lho() 
read()
#bid()

#play()
