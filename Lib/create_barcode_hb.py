"""
此文件是用来生成Code128条形码 并实现打印功能
"""
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtPrintSupport import QPrinter
from pystrich.code128 import Code128Encoder
import uuid


class CreateBarcodeHB:

    """
            Code128Encoder(options={}) options参数
        * ttf_font：用于呈现标签的truetype字体文件的绝对路径
        * ttf_fontsize：绘制标签的字体大小
        * label_border：条形码和标签之间的像素空间数
        * bottom_border：标签和底部边框之间的像素空间数
        * height：图像的高度（以像素为单位）
        * show_label：是否在条形码下面显示标签（默认为True）“”
    """
    def __init__(self):
        pass

    def create_Code128_img(self, drugObj):
        a = Code128Encoder(drugObj.get('BarCode'), options={
            'ttf_font': r'static/fonts/arial.ttf',
             'height': 10,  'bottom_border': 0,'show_label':False
        })
        # bar_width 条码宽度尺寸
        file_name = str(uuid.uuid4()) + '.png'
        a.save(file_name, bar_width=1)
        self.printer_code(file_name,drugObj)

    def printer_code(self, file_name,drugObj):
        a = QApplication([])
        document = QTextDocument()
        document.setDocumentMargin(0)
        font = document.defaultFont()
        fontId = QFontDatabase.addApplicationFont(r"static/fonts/simsun.ttc")
        fontName = QFontDatabase.applicationFontFamilies(fontId)[0]
        font.setFamily("新宋体")
        # font.setBold(True)
        # font.setPixelSize(12)
        # font.setPointSize(20)
        document.setDefaultFont(font)
        # 设置全局生效的默认样式
        document.setDefaultStyleSheet('''
        * {padding:0;margin: 0;letter-spacing:10px;}

        .box{width: 50px;}
        .header{font-size: 10px;text-indent: 28px;}
        .content{font-size: 8px;height: 20px; list-style: none;}
        ''')
        html = """
        
        <head>
        <title>Report</title>
        <style>
        </style>
        </head>
        <body >
        <div class="box">
        <div class="header">标准物质</div>
        <div class="content">
            <div><label>唯一性标识：</label>{0}</div>
            <div><label>标准物质：</label>{1}</div>
            <div><label>样品浓度：</label>{2}</div>
            <div><label>有效日期：</label>{3}</div>
        </div>
        <div><img src="{4}"></div>
        </div>
        </body>
        """.format(drugObj.get("ID"),drugObj.get("Name"),drugObj.get("Purity"),drugObj.get("DrugYXQ"),file_name)

        document.setHtml(html)
        printer = QPrinter()
        printer.setPageSize(QPagedPaintDevice.Custom)
        printer.setPaperSize(QSizeF(20.0,50.0),QPrinter.Millimeter)
        # 设置纸张到条码的边距  左上下右
        printer.setPageMargins(3, 0, 0, 0, QPrinter.Millimeter)

        document.setPageSize(QSizeF(printer.pageRect().size()))
        # document.setPageSize(QSizeF(160.0,50.0))
        
        print(document.pageSize(), printer.resolution(), printer.pageRect())
        print('正在打印中。。。。')
        document.print_(printer)
        print('打印完成。。')
        # os.remove(file_name)


if __name__ == '__main__':
    CreateBarcode().create_Code128_img('100080')
