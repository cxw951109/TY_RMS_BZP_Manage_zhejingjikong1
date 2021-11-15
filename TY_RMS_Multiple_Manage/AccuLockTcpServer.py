import socket
import re
import time
import threading
import binascii
from Business.BllMedicament import *


class AccuLockTcpServer:
    """
    Acculock锁监听控制服务
    """

    def __init__(self):
        super().__init__()

    BUFSIZ = 2048
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('192.168.1.100', 1234))
    server.listen(9)
    acceptClientFlag = False
    monitorLockFlag = True
    lig_list = {str(i) : [] for i in range(1,10)}
    Data = {"terminal": "", "mes": ""}
    deviceSetList = {
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
                terminal = cls.deviceSetList[addr[0]]
                threading.Thread(target=cls.monitorLockFun, args=(sock, terminal,)).start()
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
    def get_data(cls, termianl, data, clientId, clientSock):
        """
        接收数据入库
        """
        print(termianl,clientId)
        data_list2 = []
        for i in data:
            barcode = str(i["rfid"])
            index = i["index"] + 1
            try:
                if barcode == '0000000000000000':
                    print(clientId)
                    medicament_obj = BllMedicament().findEntity(
                        and_(EntityMedicament.ClientId == clientId, EntityMedicament.Place == index))
                    print("0000000000000",medicament_obj)
                    if medicament_obj:
                        medicament_obj.Place = ''
                        medicament_obj.Status = DrugStatus.Out
                        BllMedicament().update(medicament_obj)
                        data_list2.append(str(index))
                        print('取出', index)
                else:
                    medicament_obj = BllMedicament().findEntity(
                        and_(EntityMedicament.ClientId == clientId, EntityMedicament.BarCode == barcode))
                    print("11111111111111",medicament_obj)
                    if medicament_obj:
                        print(clientId)
                        medicament_obj.Place = index
                        medicament_obj.Status = DrugStatus.Normal
                        BllMedicament().update(medicament_obj)
                        data_list2.append(str(index))
                        print('放入', index)
                cls.lig_list[termianl].remove(str(index))
            except Exception as e:
                print(e)

        if data_list2:
            if cls.lig_list[termianl]:   
                ClientUseCode =BllMedicament().get_usecode(clientId)
                re_list = BllMedicament().get_lig(cls.lig_list[termianl],ClientUseCode)
                Msg = 'lig~' + "~".join(cls.lig_list[termianl]) + '~'+'~'.join(re_list)+'~'
            else:
                Msg = 'lig'
            print(Msg)
            time.sleep(0.01)
            clientSock.send(Msg.encode())
            clientSock.recv(1024)
            print(termianl + '灭灯：' + "~".join(data_list2))

    @classmethod
    def monitorLockFun(cls, clientSock, terminal):
        """
        监听用户
        """
        print(terminal, clientSock)
        clientSock.send('lig'.encode())
        last_result = []
        startFlag = True
        warming =0
        door_num =0
        while cls.monitorLockFlag and startFlag:
            try:
                time.sleep(0.01)
                if cls.Data["terminal"] == terminal:
                    print("**************************************",cls.Data)
                    clientSock.send(cls.Data["mes"].encode())
                    try:
                        x = clientSock.recv(cls.BUFSIZ)
                    except:
                        pass
                    if cls.Data["mes"] == 'gio1on':
                        print(terminal + "开锁")
                        client_obj = BllClient().findEntity(EntityClient.ClientCode == terminal)
                        client_obj.IsEnabled = 1
                        BllClient().update(client_obj)
                        time.sleep(0.1)
                        clientSock.send('gio2on'.encode())
                        x = clientSock.recv(cls.BUFSIZ)

                    if cls.Data["mes"] == 'gio1off':
                        print(terminal + "关锁")
                        client_obj = BllClient().findEntity(EntityClient.ClientCode == terminal)
                        client_obj.IsEnabled = 0
                        BllClient().update(client_obj)
                    print(cls.Data["terminal"] + "发送信号:" + cls.Data["mes"])
                    print('接收返回值', x)
                    cls.Data = {"terminal": "", "mes": ""}

                time.sleep(0.01)
                clientSock.send('getb'.encode())
                door_status = clientSock.recv(cls.BUFSIZ)  # 获取门状态1开门0关门
                if door_status == b'\x01\x00':
                    door_num =1
                    time.sleep(0.01)
                    clientSock.send('geta'.encode())
                    result_data = clientSock.recv(cls.BUFSIZ)
                    warming =0
                    result_data = binascii.b2a_hex(result_data).decode()
                    t = 0
                    while len(result_data) != 2880:
                        t += 1
                        result_data += binascii.b2a_hex(clientSock.recv(cls.BUFSIZ)).decode()
                        if len(result_data) == 2880:
                            break
                        else:
                            if t == 2:
                                break
                    if len(result_data) == 2880:
                        result_data1 = re.findall('.{16}', result_data)
                        # list=[item for item in result_data1 if item!='0000000000000000']
                        # print(len(list))
                        # print(result_data1)
                        if last_result != []:
                            diff = [{"index": i, "rfid": result_data1[i]} for i in range(len(result_data1)) if
                                    result_data1[i] != last_result[i]]
                        else:
                            diff = [{"index": i, "rfid": result_data1[i]} for i in range(len(result_data1))]
                        if len(diff) < 10 and diff:
                            # lightcmd = 'lig~' +str(int(diff[0]['index'])+1)+ '~'
                            # print(lightcmd)
                            # time.sleep(0.01)
                            # clientSock.send(lightcmd.encode())
                            # print('return1:',binascii.b2a_hex(clientSock.recv(cls.BUFSIZ)).decode())
                            # time.sleep(1)
                            # lightcmd = 'lig'
                            # clientSock.send(lightcmd.encode())
                            # print('return2:',binascii.b2a_hex(clientSock.recv(cls.BUFSIZ)).decode())
                            print(terminal + 'diff=', diff)
                            print("亮灯列表", cls.lig_list)
                            client_obj = BllClient().findEntity(EntityClient.ClientCode == terminal)
                            cls.get_data(terminal, diff, client_obj.ClientId, clientSock)
                            # 与上次结果对比,RMS_Medicament入库位置
                            last_result = result_data1
                        if len(diff) == 180:
                            # print("启动校准",result_data1)
                            # 启动校准
                            last_result = result_data1
                else:
                    if door_num == 1:
                        door_num =0
                        try:
                            time.sleep(0.01)
                            clientSock.send('lig'.encode())
                            x = clientSock.recv(cls.BUFSIZ)
                            time.sleep(0.01)
                            clientSock.send('gio2off'.encode())
                            x = clientSock.recv(cls.BUFSIZ)
                        except Exception as e:
                                print(e)    

                            #灭所有灯    ，doornum状态改为0   
            except Exception as e:
                warming +=1
                print('连续warming次数',warming)
                if warming > 10 and str(e)== 'timed out':
                    clientSock.send('reset'.encode())
                    print('重置')
                    x = clientSock.recv(cls.BUFSIZ)
                    startFlag = False
                print('监听' + terminal + '错误:', str(e))
                if e.errno == 10053 or e.errno == 10038:
                    break
                if e.errno == 10054:
                    print('...', clientSock)
                    print('....', threading.enumerate())
                    startFlag = False


AccuLockTcpServer().startAcceptClient()
