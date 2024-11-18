#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf-8

from PySide6.QtCore import *
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6 import *
from PySide6.QtGui import *

import serial.tools.list_ports

# 1:FTHGAIL5A
# 2:A90DAHU5A
# 3:A9GB069DA
# 4:FTHG96PPA
# 5:FTHG80GEA
# 6:FTHG80GEA





import screeninfo
def get_desktop():
	minx =  1000000
	miny =  1000000
	maxx = -1000000
	maxy = -1000000
	a = screeninfo.get_monitors()
	for it in a:
		minx = min(minx, it.x)
		maxx = max(maxx, it.x+it.width)
		miny = min(miny, it.y)
		maxy = max(maxy, it.y + it.height)
	return minx, maxx, miny, maxy

def trim_position(x:int, y:int):
	x1, x2, y1, y2 = get_desktop()
	x = max(x1, x)
	x = min(x2, x)
	y = max(y1, y)
	y = min(y2, y)
	return x, y

def Qtrim_position(qp:QPoint) -> QPoint:
	x = int(qp.x())
	y = int(qp.y())
	x, y = trim_position(x,y)
	ans = QPoint(x, y)
	return ans


def debug_msg(p):
	print('----------------------------------------------------------')
	print('device       :{}'.format(p.device))
	print('name         :{}'.format(p.name))
	print('description  :{}'.format(p.description))
	print('hwid         :{}'.format(p.hwid))
	print('serial_number:{}'.format(p.serial_number))
	print('location     :{}'.format(p.location))
	print('manufacturer :{}'.format(p.manufacturer))
	print('product      :{}'.format(p.product))
	print('interface    :{}'.format(p.interface))
	print('vid          :{}'.format(p.vid))
	print('pid          :{}'.format(p.pid))


sn_list = {
	'DC008U81A':' 黄色いタカチケース ',
	'010D4CE2':' --- 半二重485ドングル',
	'FTHGAIL5A':' --- 秋月の黒/グレイのやつ #1/6',
	'A90DAHU5A':' --- 秋月の黒/グレイのやつ #2/6',
	'A9GB069DA':' --- 秋月の黒/グレイのやつ #3/6',
	'FTHG96PPA':' --- 秋月の黒/グレイのやつ #4/6',
	'FTHG7WCXA':' --- 秋月の黒/グレイのやつ #5/6',
	'FTHG80GEA':' --- 秋月の黒/グレイのやつ #6/6',
	'A10LU6Z5A':' --- RS485 絶縁型',
	'AQ00JKREA':' RS485 DSD TECH SH-U11 ',
	'FTBTXRP1A':' RS485 EasySync ',
	'DM001YKOA':' Red Pitaya UART ',
}

vid_list = {
	0x303A1001: 'LOLIN_C3_MINI',
	0x28330051: 'Oculus Rift-S' ,
	0x04036015: 'FT-230X',
	0x04036001: 'FT-230系',
	0x303A1001: 'LOLIN_C3_MINI',
}



def extractSerial(p):	# 固有のシリアルナンバー抽出
	ans = ''
	print('extractSerial:',p.serial_number)
	try:
		k = sn_list[p.serial_number]
		ans = ' S/N:[{}] {}'.format(p.serial_number, k)
	except KeyError:
		pass
	return ans


def getusbname(p):
	print('DEBUG ---', type(p))
	vid = p.vid
	pid = p.pid
	vpid = (vid <<16) + pid
	sn = p.serial_number
	ans = extractSerial(p)
	if 1<len(ans):
		return ans
	try:
		k = vid_list[vpid]+' '
	except KeyError:
		print('err:{:08X}'.format(vpid))
		k = None
	if None != k:
		ans += ' '+k

	if 1 <len(sn):
		ans += ' S/N:[{}]'.format(sn)
	if 0x0483 == vid:  # ST-MICRO
		if 0x3752 == pid:
			ans = ' ST-LINK FRISK {}'.format(sn)
		elif 0x374b == pid:
			ans = ' ST-LINK V2 {}'.format(sn)
	elif 0x067b == vid and 0x2303 == pid:
		ans = ' PL2303 S/N:[{}]'.format(sn)
	elif 0x10c4 == vid and 0xea60 == pid: # CP210X ESP32等
		if p.serial_number == '0216123D':
			ans = ' M5Stack Fire '+' S/N:{}'.format(p.serial_number)
		elif p.serial_number == '023592EE':
			ans = ' M5Stack Core2 ' + ' S/N:{}'.format(p.serial_number)
		else:
			ans = 'CP210X S/N:{}'.format(p.serial_number)
	if ans == '':
		ans = ' ----VID:{:04X} PID:{:04X} '.format(vid, pid)
	return ans


class ListupSerialWindow(QtWidgets.QMainWindow):
	ports = []
	def __init__(self, parent=None):
		super(ListupSerialWindow, self).__init__(parent)
		self.setFont(QFont('ＭＳ ゴシック'))

		self.settings = QSettings('listup_serial.txt',QSettings.IniFormat)
		levels = [
			(4, 4, "M refresh"),
		]
		menu = self.menuBar().addMenu("&Menu")
		for r, c, name in levels:
			action = menu.addAction(name)
			action.setData((r, c))
			action.triggered.connect(self.refresh)
		r, c, _ = levels[0]
		self.setSize()

	def savepos(self):
		# ------------------------------------------------------------ window位置の保存
		self.settings.beginGroup('window')
		self.settings.setValue("size", self.size())
		self.settings.setValue("pos", self.pos())
		self.settings.endGroup()
		self.settings.sync()
		# ------------------------------------------------------------ window位置の保存

	def closeEvent(self, e):
		self.savepos()

	@staticmethod
	def add_one_line(layout, p):
		ah = QHBoxLayout()
		b1 = QLabel(p.device)
		b1.setFixedWidth(50)  # ラベルサイズの固定
		b2 = QLineEdit(p.description)
		b2.setToolTip(p.hwid)
		ah.addWidget(b1)
		ah.addWidget(b2)
		layout.addLayout(ah)
		return

	def makeLayout(self):
		h1 = QHBoxLayout()
		v1 = QVBoxLayout()
		v2 = QVBoxLayout()

		btn1 = QPushButton('QUIT')
		btn1.clicked.connect(self.close)
		v2.addWidget(btn1)
		btn1 = QPushButton('REFRESH')
		btn1.clicked.connect(self.refresh)
		v2.addWidget(btn1)
		v2.addStretch()
		com_list = []
		for p in self.ports:
			com_1 = []
			cn = p.device
			if 0 == cn.find('COM'):  # ソートキーの抽出
				cn1 = int(cn[3:])   # 'COM1'  'COM255'
				#				print('{}->{}'.format(cn,cn1))
				com_1.append(cn1)  # ソートキー
			else:
				com_1.append(cn)  # ソートキー
			# print('-------------cn:{}'.format(cn))
			# debug_msg(p)
			if p.vid:
				# print('vid          :{:04X}'.format(p.vid           ))
				# print('pid          :{:04X}'.format(p.pid           ))
				p.description += getusbname(p)
			com_1.append(p)  # ポート１個分のデータ		[1]
			com_list.append(com_1)

		for p in sorted(com_list):  # COM番号でソートする
			self.add_one_line(v1, p[1])  # ,p[2].description, p[2].hwid )
			# print(sorted(com_list))
		v1.addStretch()

		h1.addLayout(v1)
		h1.addLayout(v2)
		return h1


	@QtCore.Slot()
	def refresh(self):
		self.savepos()
		self.setSize()

	def setSize(self):
		# delete the old container
		widget = self.centralWidget()
		if widget is not None:
			widget.deleteLater()
		self.ports = list(serial.tools.list_ports.comports())
		# create new container
		widget = QtWidgets.QWidget()
		self.setCentralWidget(widget)
		h = self.makeLayout()
		widget.setLayout(h)
		# ------------------------------------------------------------ window位置の再生
		self.settings.beginGroup('window')
		# 初回起動のサイズの指定とか、復元とか
		self.resize(self.settings.value("size", QSize(900, 180)))
		self.move(Qtrim_position(self.settings.value("pos", QPoint(0, 0))))
		self.settings.endGroup()
		# ------------------------------------------------------------ window位置の再生
		self.setWindowTitle('LISTUP SERIAL PORTS 2024.11.19')
		# self.setGeometry(300, 50, 800, 80)


def main():
	import sys
	app = QtWidgets.QApplication(sys.argv)
	w = ListupSerialWindow()
	w.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()

### EOF ###
