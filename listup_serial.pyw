#! /usr/bin/python3
# -*- coding: utf-8 -*-
# coding: utf-8

from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit
import serial.tools.list_ports

# 1:FTHGAIL5A
# 2:A90DAHU5A
# 3:A9GB069DA
# 4:FTHG96PPA
# 5:FTHG80GEA
# 6:FTHG80GEA

def sjis2utf8( sjis ):
	# b = sjis.encode('cp932')
	# u = b.decode('utf8')
	return sjis


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

def extractSerial(p):	# 固有のシリアルナンバー抽出
	ans = ''
	sn = p.serial_number
	if 'DC008U81A' == sn:
		return sn+' 黄色いタカチケース '
	if '010D4CE2' == sn:
		ans = ' S/N:{} {}'.format(sn, p.manufacturer)
		ans += ' --- 半二重485ドングル'
	if 'FTHGAIL5A' == sn:
		ans = ' S/N:{} {}'.format(sn, p.manufacturer)
		ans += ' --- 秋月の黒/グレイのやつ #{}/{}'.format(1, 6)
	elif 'A90DAHU5A' == sn:
		ans = ' S/N:{} {}'.format(sn, p.manufacturer)
		ans += ' --- 秋月の黒/グレイのやつ #{}/{}'.format(2, 6)
	elif 'A9GB069DA' == sn:
		ans = ' S/N:{} {}'.format(sn, p.manufacturer)
		ans += ' --- 秋月の黒/グレイのやつ #{}/{}'.format(3, 6)
	elif 'FTHG96PPA' == sn:
		ans = ' S/N:{} {}'.format(sn, p.manufacturer)
		ans += ' --- 秋月の黒/グレイのやつ #{}/{}'.format(4, 6)
	elif 'FTHG7WCXA' == sn:
		ans = ' S/N:{} {}'.format(sn, p.manufacturer)
		ans += ' --- 秋月の黒/グレイのやつ #{}/{}'.format(5, 6)
	elif 'FTHG80GEA' == sn:
		ans = ' S/N:{} {}'.format(sn, p.manufacturer)
		ans += ' --- 秋月の黒/グレイのやつ #{}/{}'.format(6, 6)
	elif 'A10LU6Z5A' == sn:
		ans += ' S/N:{} --- RS485 絶縁型'.format(sn)
	elif 'AQ00JKREA' == sn:
		ans += ' RS485 DSD TECH SH-U11 S/N:{}'.format(sn)
	elif 'FTBTXRP1A' == sn:
		ans += ' RS485 EasySync S/N:{}'.format(sn)
	return ans

def getusbname(p):
	vid = p.vid
	pid = p.pid
	sn = p.serial_number
	ans = extractSerial(p)
	if 1<len(ans):
		return ans
	if 0x2833 == vid:  # FTDI
		if pid == 0x0051:
			ans += ' Oculus Rift-S '
	if 0x0403 == vid:  # FTDI
		if pid == 0x6015:
			if 'DN64A4H7A' == p.serial_number:
				ans += ' S/N:{} --- NHK切り替え器 IF317 '.format(sn, p.manufacturer)
			else:
				ans += ' FT230X S/N:{}'.format(p.serial_number)
		elif 0x6001 == pid:
			ans += ' FT232系 S/N:{} {} '.format(sn, p.manufacturer)
	elif 0x0483 == vid:  # ST-MICRO
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
			ans = ' S/N:{}'.format(p.serial_number)
	if ans == '':
		ans = ' ----VID:{:04X} PID:{:04X} '.format(vid, pid)
	return ans


class ListupSerialWindow(QtWidgets.QMainWindow):
	ports = []

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
		btn1.clicked.connect(QCoreApplication.instance().quit)
		v2.addWidget(btn1)
		btn1 = QPushButton('REFRESH')
		btn1.clicked.connect(self.setSize)
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
			#			print('-------------cn:{}'.format(cn))
			# debug_msg(p)
			if p.vid:
				#				print('vid          :{:04X}'.format(p.vid           ))
				#				print('pid          :{:04X}'.format(p.pid           ))
				p.description += getusbname(p)
			com_1.append(p)  # ポート１個分のデータ		[1]
			com_list.append(com_1)

		for p in sorted(com_list):  # COM番号でソートする
			self.add_one_line(v1, p[1])  # ,p[2].description, p[2].hwid )
		#		print(sorted(com_list))
		v1.addStretch()

		h1.addLayout(v1)
		h1.addLayout(v2)
		return h1

	#		self.setLayout(h1)
	#		self.setWindowTitle('LISTUP SERIAL PORTS')

	def __init__(self, parent=None):
		super(ListupSerialWindow, self).__init__(parent)
		levels = [
			(4, 4, "M refresh"),
		]
		menu = self.menuBar().addMenu("&Menu")
		for r, c, name in levels:
			action = menu.addAction(name)
			action.setData((r, c))
			action.triggered.connect(self.on_triggered)
		r, c, _ = levels[0]
		self.setSize()

	@QtCore.pyqtSlot()
	def on_triggered(self):
		# action = self.sender()
		# r, c = action.data()
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
		self.setWindowTitle('LISTUP SERIAL PORTS 2022-12-19')
		self.setGeometry(300, 50, 800, 80)

def main():
	import sys
	app = QtWidgets.QApplication(sys.argv)
	w = ListupSerialWindow()
	w.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()

### EOF ###
