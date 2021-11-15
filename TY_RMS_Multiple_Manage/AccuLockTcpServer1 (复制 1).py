import socket
import re
import time
import threading
import pymysql
import binascii
from Business.Repository import *
from Business.BllMedicament import *


# from  Business.BllMedicament import *

class AccuLockTcpServer():
    """
    Acculock锁监听控制服务
    """

    def __init__(self):
        super().__init__()

    BUFSIZ = 2048
    t1 = ''
    t2 = ''
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 1234))
    server.listen(5)
    acceptClientFlag = False
    monitorLockFlag = True
    ter_list = []
    ter_list1 = []
    lig_list = {"1号终端": []}
    Data = {"terminal": "1号终端", "mes": "lig"}
    deviceSetList = {
        '127.0.0.1': "1",
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
        cls.acceptClientFlag = True
        acceptClientThread = threading.Thread(target=cls.acceptClientFun)
        acceptClientThread.start()



    @classmethod
    def stopAcceptClient(cls):
        """
        停止监听客户端加入
        """
        cls.acceptClientFlag = False

    @classmethod
    def acceptClientFun(cls):
        """
        监听客户端加入处理
        """
        while cls.acceptClientFlag:
            try:
                sock, addr = cls.server.accept()
                sock.settimeout(10)
                if addr[0] =="192.168.1.20":
	            cls.ter_list.append(sock)
	            cls.ter_list1.append(addr[0])
	            cls.monitorLockFun(addr)
            except Exception as e:
                print('监听客户端加入错误:', str(e))

    @classmethod
    def startMonitorLock(cls):
        """
        开始监听
        """
        cls.monitorLockFlag = True

    @classmethod
    def stopMonitorLock(cls):
        """
        停止监听
        """
        cls.monitorLockFlag = False

    @classmethod
    def monitorLockFun(cls,addr):
        """
        监听用户
        """
        print(addr)
        cls.ter_list =['1']
        for i in range(len(cls.ter_list)):
            terminal = cls.deviceSetList[cls.ter_list1[i]]
            client_obj = BllClient().findEntity(EntityClient.ClientCode == terminal)
            List = BllMedicament().findList(and_(EntityMedicament.FlowNo ==4, EntityMedicament.Status == '1',EntityMedicament.FlowPositionCode=='A1B1')).order_by(asc(EntityMedicament.PutInDate)).all()
            cls.ter_list[i].send('geta'.encode())
            result_data = cls.ter_list[i].recv(cls.BUFSIZ)
            result_data = binascii.b2a_hex(result_data).decode()
            t = 0
            while len(result_data) != 2880:
                t += 1
                result_data += binascii.b2a_hex(cls.ter_list[i].recv(cls.BUFSIZ)).decode()
                # print("**********88")
                if len(result_data) == 2880:
                    break
                else:
                    if t == 2:
                        break
            result_data1 = re.findall('.{16}', result_data)
            xx = [result_data1[i] for i in range(len(result_data1))]
            print(len(xx))
            if len(xx) == 180:
                xx =xx[0:121]
                for i in range(len(xx)):
                    if xx[i] != '0000000000000000':
                        print(i,xx[i],terminal,client_obj.ClientId,i+1)# 对应序号，barcode，终端code，clientID，Place
                        List[i].BarCode =xx[i]
                        List[i].ClientId = client_obj.ClientId
                        List[i].ClientCode =terminal
                        List[i].Place =str(i+1)
                	BllMedicament().update(List)

AccuLockTcpServer().startAcceptClient()


