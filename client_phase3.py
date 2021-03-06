# -*- coding: utf-8 -*-
"""Client_phase3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Tl4CoolacPkHraFrByN4G0rQBd6R-QIR
"""

!pip install ecpy

#!pip install ecpy
#!pip install pycryptodome

import math
import timeit
import random
import sympy
import warnings
from random import randint, seed
import sys
from ecpy.curves import Curve,Point
from Crypto.Hash import SHA3_256, SHA256, HMAC
import requests
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import random
import hashlib, hmac, binascii
import json
API_URL = 'http://cryptlygos.pythonanywhere.com'

stuID =  25359 
stuID_B = 18007
max_ephemeral_keys = 10

#create a long term key

curve = Curve.get_curve('secp256k1')
q = curve.order
p = curve.field
P = curve.generator

sL = 7607314394506061677990466796842274315842801300199560769842840753281729479854
QCli_long = Point(0x8642a0854b673af6989e0d4e109228543dabb4bf989beb4ff7d9324947405d9e , 0x17508f7382c066dc1e92f58a1a6268aa8f1a2a6ab88fd1ff151ccf30ba307824, curve)

def SignSL(message):
  k = Random.new().read(int(math.log(q-2,2)))
  k = int.from_bytes(k, byteorder='big')%q
  R = k*P
  r = R.x % q
  mr = bytes(message, 'utf-8')+ r.to_bytes((r.bit_length()+7)//8, byteorder = 'big')
  hashVal = SHA3_256.new(mr)
  h = int.from_bytes(hashVal.digest(), 'big') % q
  s = (sL*h + k)%q 
  return s,h

def Encryption(k_enc, k_mac, plaintext):
  cipher = AES.new(k_enc, AES.MODE_CTR)
  message_without_nonce = cipher.encrypt(plaintext)
  HMAC_val = HMAC.new(k_mac, message_without_nonce, digestmod=SHA256)
  hmac = HMAC_val.digest()
  ctext = cipher.nonce + message_without_nonce + hmac
  ctext = int.from_bytes(ctext, byteorder='big')
  return ctext

def Decryption(ctext,key,nonce_len):
  ctext = ctext.to_bytes((ctext.bit_length()+7)//8, byteorder = 'big')
  cipher = AES.new(key, AES.MODE_CTR, nonce=ctext[0:nonce_len])
  dtext = cipher.decrypt(ctext[nonce_len:])
  decrypt_text = dtext.decode('utf-8')
  return decrypt_text
  
def SessionKeyGen(i, QBj_x, QBj_y, Dict):
  QBj = Point(QBj_x, QBj_y, curve)

  sA = Dict[i]
  T = sA * QBj
  message_for_U = "NoNeedToRunAndHide"
  U = str(T.x) + str(T.y) + message_for_U

  hashVal= SHA3_256.new(bytes(U, 'utf-8'))
  k_enc = hashVal.digest()

  hashVal_ = SHA3_256.new(k_enc)
  k_mac = hashVal_.digest()

  return k_enc, k_mac

####Register Long Term Key
"""
s, h = SignSL(str(stuID))

mes = {'ID':stuID, 'H': h, 'S': s, 'LKEY.X': QCli_long.x, 'LKEY.Y': QCli_long.y}
response = requests.put('{}/{}'.format(API_URL, "RegLongRqst"), json = mes)
print(response.json())

code = int(input())

mes = {'ID':stuID, 'CODE': code}
response = requests.put('{}/{}'.format(API_URL, "RegLong"), json = mes)
print(response.json())
"""

s, h = SignSL(str(stuID))

#Check Status
mes = {'ID_A':stuID, 'H': h, 'S': s}
response = requests.get('{}/{}'.format(API_URL, "Status"), json = mes)
print("Status ", response.json())

response_str = response.json()
need_to_send = response_str[response_str.find("send") + 5:response_str.rfind("keys")-1]
need_int = int(need_to_send)
unread_message = response_str[response_str.rfind("have") + 5:response_str.rfind("unread")-1]
unread_int = int(unread_message)

#dictionary of the ephemeral key id and the corresponding private ephemeral key
Dict = {0: 89141965786423435840797420380355836096653042808803414164320931726939256741322, 1: 85408997245305018879852243595351434377720192169459515924324448333805843918456, 2: 113617829862859405107291964305177104153633259512561595875812429279647352021841, 3: 37365355089091788013052515307653562633405795792457031849104271052775593476173, 4: 109410299895252056375904917530051072098320550311933644088618698239394623415507, 5: 65743277605672016057851904455441138272960721675717082611824807663375113668590, 6: 110098272627378131850980929802686541345473009573441524198227284335377648218565, 7: 5644944751569955177812028886484266990094401800979020264125728454352387840921, 8: 22866335666007822239051249791273123267744058624360877050799760549019807203078, 9: 104262428460334175471047514657572538321235157425025725190855548064497752271803}
print("Dictionary that keeps the ephemeral private keys with the ID =", Dict)


### Get key of the Student B
s, h = SignSL(str(stuID_B))
mes = {'ID_A': stuID, 'ID_B':stuID_B, 'S': s, 'H': h}
response = requests.get('{}/{}'.format(API_URL, "ReqKey"), json = mes)
res = response.json()
print(res)

if res!= str(stuID_B)+" has no ephemeral key":

  i = int(res.get('i')) 
  j = int(res.get('j'))

  QBj_x = res.get('QBJ.x')
  QBj_y = res.get('QBJ.y')

  k_enc, k_mac = SessionKeyGen(i, QBj_x, QBj_y, Dict)
  myMessage = "Lutfen olsun :("
  myMessage_bytes = bytes(myMessage, 'utf-8')

  msg = Encryption(k_enc, k_mac, myMessage_bytes)

  ### Send message to student B
  mes = {'ID_A': stuID, 'ID_B':stuID_B, 'I': i, 'J':j, 'MSG': msg}
  response = requests.put('{}/{}'.format(API_URL, "SendMsg"), json = mes)
  print(response.json())


## Get your message
for k in range(unread_int):
  s, h = SignSL(str(stuID))
  mes = {'ID_A': stuID, 'S': s, 'H': h}
  response = requests.get('{}/{}'.format(API_URL, "ReqMsg_PH3"), json = mes)
  print(response.json())
  if(response.ok): ## Decrypt message
    res= response.json()

    if res == "You dont have any new messages":
      break

    keyID = int(res.get('KEYID'))
    message = res.get('MSG')
    #ephemeral public key of the pseudo-client
    QBj_x = res.get('QBJ.X')
    QBj_y = res.get('QBJ.Y')
    QBj = Point(QBj_x, QBj_y, curve)

    sA = Dict[keyID]
    T = sA * QBj
    message_for_U = "NoNeedToRunAndHide"
    U = str(T.x) + str(T.y) + message_for_U

    hashVal= SHA3_256.new(bytes(U, 'utf-8'))
    k_enc = hashVal.digest()

    hashVal_ = SHA3_256.new(k_enc)
    k_mac = hashVal_.digest()

    #Whole message with nonce-message itself-hmac is converted into byte array
    msg_bytes = message.to_bytes((message.bit_length() + 7)//8, byteorder= 'big')
    #Last 32 bytes is the hmac
    HMAC_extracted = msg_bytes[len(msg_bytes)-32:]
    #First portion is the nonce and the message itself
    message_withnonce = msg_bytes[:len(msg_bytes)-32]
    #message without nonce to get the MAC of the message
    message_without_nonce = msg_bytes[8:len(msg_bytes)-32]
    #message in int format to decrypt it
    message_int = int.from_bytes(message_withnonce, 'big')

    #get the HMAC-SHA256 of the message with k_mac
    HMAC_val = HMAC.new(k_mac, message_without_nonce, digestmod=SHA256)
    hmac = HMAC_val.digest()

    #if the mac computed and mac extracted from the message are the same then the message is authenticated
    if hmac == HMAC_extracted:
      print("The MAC of the message is verified, it is authentic!")
    else:
      print("The message is not authentic!")

    decrypted_text = Decryption(message_int, k_enc, 8)
    print("The decrypted message is:", decrypted_text)


#The following part handles the key exhange. If 2 of the keys have been used by the other party of the communication, we directly compansate
#2 keys and add that to the dictionary. Therefore, no matter the runtime history of the receiver, it is always ready to receive 10 messages securely.
max_key = max(Dict) + 1

for i in range(need_int):
  sA = Random.new().read(int(math.log(q-1,2)))
  sA = int.from_bytes(sA, byteorder='big') % q

  Dict[max_key] = sA

  ekey = sA*P
  toMessage = str(ekey.x) + str(ekey.y)
  s, h = SignSL(toMessage)
  print()
  print("index is", max_key)
  #Send Ephemeral keys
  mes = {'ID': stuID, 'KEYID': max_key , 'QAI.X': ekey.x, 'QAI.Y': ekey.y, 'Si': s, 'Hi': h}
  response = requests.put('{}/{}'.format(API_URL, "SendKey"), json = mes)
  print(response.json())
  max_key+=1

print("The updated dictionary =", Dict)