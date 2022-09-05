cd /d %~dp0
call usepy3
pyinstaller listup_serial.pyw --onefile --clean --noconsole
