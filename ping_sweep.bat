@echo off
for /L %%i in (1,1,254) do (
	ping -n 1 -w 200 192.168.120.%%i | find "TTL=" > nul
	if not errorlevel 1 (
		echo 192.168.120.%%i is alive. 
	)
) 
