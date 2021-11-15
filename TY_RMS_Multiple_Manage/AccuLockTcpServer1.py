import socket
import re
import time
import threading
import binascii
# from  Business.BllMedicament import *

class AccuLockTcpServer:
    """
    Acculock锁监听控制服务
    """
    def __init__(self):
        super().__init__()

    BUFSIZ = 2048
    t1=''
    t2=''
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.bind(('192.168.1.100', 1234))
    server.listen(5)
    acceptClientFlag=False
    monitorLockFlag=True
    ter_list=[]
    ter_list1=[]
    lig_list={"1号终端":[]}
    Data={"terminal":"1号终端","mes":"lig"}
    deviceSetList={
        '192.168.1.19': "1",
        '192.168.1.20': "2",
        '192.168.1.21': "3",
        '192.168.1.22': "4",
        '192.168.1.23': "5",
        '192.168.1.24': "6",
        '192.168.1.25': "7",
        '192.168.1.26': "8",
        '192.168.1.27': "9"
    }

    @classmethod
    def startAcceptClient(cls):
        """
        开始监听客户端加入
        """
        cls.acceptClientFlag=True
        acceptClientThread=threading.Thread(target=cls.acceptClientFun)
        acceptClientThread.start()
        time.sleep(2)
        cls.monitorLockFun()
    @classmethod
    def stopAcceptClient(cls):
        """
        停止监听客户端加入
        """
        cls.acceptClientFlag=False

    @classmethod
    def acceptClientFun(cls):
        """
        监听客户端加入处理
        """
        while cls.acceptClientFlag:
            try:
                sock, addr = cls.server.accept()
                sock.settimeout(10)
                cls.ter_list.append(sock)
                cls.ter_list1.append(addr[0])
                # if(addr[0]=='192.168.1.27'):
                #     terminal = '9'
                #     threading.Thread(target=cls.monitorLockFun,args=(sock,terminal,)).start()
                #     print('监听客户端加入:', sock)
            except Exception as e:
                print('监听客户端加入错误:',str(e))


    @classmethod
    def startMonitorLock(cls):
        """
        开始监听
        """
        cls.monitorLockFlag=True

    @classmethod
    def stopMonitorLock(cls):
        """
        停止监听
        """
        cls.monitorLockFlag=False


    @classmethod
    def monitorLockFun(cls):
        """
        监听用户
        """



        for i in range(len(cls.ter_list)):
            terminal =cls.deviceSetList[cls.ter_list1[i]]
            path ='/home/yanyi/桌面/'+"r3"+'.txt'
            files =open(path,'a+')
            cls.ter_list[i].send('geta'.encode())
            result_data=cls.ter_list[i].recv(cls.BUFSIZ)
            result_data = binascii.b2a_hex(result_data).decode()
            t = 0
            while len(result_data) != 2880:
                t += 1
                result_data += binascii.b2a_hex(cls.ter_list[i].recv(cls.BUFSIZ)).decode()
                # print("**********88")
                if len(result_data) == 2880:
                    break
                else:
                    if t ==2:
                        break
            result_data1 =re.findall('.{16}',result_data)         
            xx= [{"ter":str(int(i)+1),"data": result_data1[i]} for i in range(len(result_data1)) if result_data1[i] != '0000000000000000' and i<180]\
            
            t =files.read()
            t = str(t)+"Terminal:"+str(terminal)+'\n'+'Num:'+str(len(xx))+"\n"+"List:" +str(xx)+"\n"+"\n"+"\n"
            files.write(t)
            files.close()



        # print(terminal, clientSock)
        # last_result = []
        # path ='/home/yanyi/桌面/'+"qqq"+'.txt'
        # files =open(path,'a+')
        # while cls.monitorLockFlag:
        #     try:
        #         # time.sleep(0.5)
        #         if cls.Data["terminal"]== terminal:

        #             clientSock.send(cls.Data["mes"].encode())

        #             x = clientSock.recv(cls.BUFSIZ)
        #             print(cls.Data["terminal"]+"发送信号:"+cls.Data["mes"])
        #             cls.Data = {"terminal":"","mes":""}
        #         # clientSock.send('getb'.encode())
        #         # time.sleep(0.1)
        #         # door_status =clientSock.recv(cls.BUFSIZ)#获取门状态1开门0关门
        #         # print('aaaaaaaaaaaaaa')
        #         if True:
        #             ttt=time.time()
        #             clientSock.send('geta'.encode())
        #             result_data=clientSock.recv(cls.BUFSIZ)
        #             result_data = binascii.b2a_hex(result_data).decode()
        #             t = 0
        #             while len(result_data) != 2880:
        #                 t += 1
        #                 result_data += binascii.b2a_hex(clientSock.recv(cls.BUFSIZ)).decode()
        #                 # print("**********88")
        #                 if len(result_data) == 2880:
        #                     break
        #                 else:
        #                     if t ==2:
        #                         break
        #             result_data1 =re.findall('.{16}',result_data)         
        #             xx= [i for i in range(len(result_data1)) if result_data1[i] != '0000000000000000' and i<180]
        #             t =files.read()
        #             print(t)
        #             t = str(t)+"Terminal:"+str(terminal)+'\n'+'Num:'+str(len(xx))+"\n"+"List:" +str(xx)+"\n"+"\n"+"\n"
        #             files.write(t)
        #             files.close()
        #             print(len(xx))
        #             time.sleep(10)


                    # time.sleep(0.3)
                    # clientSock.send('gio1off'.encode())
                    # print('retuen0:',binascii.b2a_hex(clientSock.recv(cls.BUFSIZ)).decode()) 
                    # time.sleep(0.3)
                    # clientSock.send('gio2off'.encode())
                    # print('retuen0:',binascii.b2a_hex(clientSock.recv(cls.BUFSIZ)).decode()) 
                    # if len(result_data) ==2880:
                    #     print('data:',result_data)
                    #     result_data1 =re.findall('.{16}',result_data)
                    #     if last_result !=[]:
                    #         diff =[{"index":i,"rfid":result_data1[i]} for i in range(len(result_data1)) if result_data1[i] != last_result[i]]
                    #     else:
                    #         diff =[{"index":i,"rfid":result_data1[i]} for i in range(len(result_data1))]

                    #     if len(diff) <20 and diff:
                    #         cls.t1 = time.time()
                    #         print("t1", cls.t1)
                    #         print(terminal+'diff=',diff)
                    #         # time.sleep(0.2)
                    #         # for i in diff:
                    #         lightcmd ='lig~' +'~'.join([str(i+1) for i in range(len(result_data1)) if result_data1[i] != '0000000000000000' and i<180] )+'~'
                    #         print(lightcmd)
                    #         time.sleep(0.01)
                    #         #print('data:',result_data2)
                    #         time.sleep(0.1)
                    #         clientSock.send(lightcmd.encode())
                    #         print('retuen1:',binascii.b2a_hex(clientSock.recv(cls.BUFSIZ)).decode()) 
                    #         time.sleep(0.8)
                    #         clientSock.send('lig'.encode())
                    #         print('retuen2:',binascii.b2a_hex(clientSock.recv(cls.BUFSIZ)).decode()) 
    


                    #         # lig_list = {"1号终端": [10]}
                    #         # if cls.lig_list[termianl]:
                    #         #     Msg = 'lig~' + "~".join(cls.lig_list[termianl]) + '~'
                    #         # else:
                    #         #     Msg = 'lig'
                    #         # cls.t2 = time.time()
                    #         # print("t2", cls.t2)
                    #         # print('time=', cls.t2 - cls.t1)
                    #         # clientSock.send('lig~10~'.encode())
                    #         # clientSock.recv(1024)
                    #         # cls.get_data(terminal, diff, client_obj.ClientId, clientSock)
                    #     #与上次结果对比,RMS_Medicament入库位置
                    #     last_result =result_data1
            # except Exception as e:
            #     print('监听用户错误:', str(e))
            #     if e.errno == 10053 or e.errno == 10038:
            #         break

AccuLockTcpServer().startAcceptClient()


