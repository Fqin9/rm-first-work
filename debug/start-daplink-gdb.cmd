@echo off
setlocal
for %%I in (openocd.exe) do set "OPENOCD_EXE=%%~$PATH:I"
if not defined OPENOCD_EXE (
    echo OpenOCD was not found in PATH.
    pause
    exit /b 1
)
for %%I in ("%OPENOCD_EXE%") do set "OPENOCD_SCRIPTS=%%~dpI..\share\openocd\scripts"
"%OPENOCD_EXE%" -s "%OPENOCD_SCRIPTS%" -f interface/cmsis-dap.cfg -c "transport select swd" -f target/stm32f1x.cfg -c "adapter speed 1000"
pause
