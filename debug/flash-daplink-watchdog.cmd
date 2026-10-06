@echo off
setlocal
echo Close Ozone and other OpenOCD windows before programming.
echo Reconnect the DAPLink USB cable first. Keep the target board powered.
for %%I in (openocd.exe) do set "OPENOCD_EXE=%%~$PATH:I"
if not defined OPENOCD_EXE (
    set "OPENOCD_EXE=%USERPROFILE%\OpenOCD\OpenOCD-20260302-0.12.0\bin\openocd.exe"
)
if not exist "%OPENOCD_EXE%" (
    echo OpenOCD was not found.
    pause
    exit /b 1
)
for %%I in ("%OPENOCD_EXE%") do set "OPENOCD_SCRIPTS=%%~dpI..\share\openocd\scripts"
set "WATCHDOG_ELF=%~dp0..\build\first-task.elf"
if not exist "%WATCHDOG_ELF%" (
    echo Watchdog firmware was not found: %WATCHDOG_ELF%
    pause
    exit /b 1
)
set "WATCHDOG_ELF=%WATCHDOG_ELF:\=/%"
set "PROGRAM_LOG=%~dp0flash-daplink-watchdog.log"
echo Programming build/first-task.elf and verifying its contents...
"%OPENOCD_EXE%" -s "%OPENOCD_SCRIPTS%" -f interface/cmsis-dap.cfg -c "transport select swd" -f target/stm32f1x.cfg -c "adapter speed 1000" -c "tcl port disabled" -c "telnet port disabled" -c "gdb port disabled" -c "program {%WATCHDOG_ELF%} verify reset exit" > "%PROGRAM_LOG%" 2>&1
set "PROGRAM_RESULT=%ERRORLEVEL%"
type "%PROGRAM_LOG%"
echo.
echo Log saved to: %PROGRAM_LOG%
echo Programming exit code: %PROGRAM_RESULT%
if not "%PROGRAM_RESULT%"=="0" (
    echo Programming failed. Send this output before continuing.
) else (
    echo Check that the output above contains Verified OK.
    echo Close this window, reconnect DAPLink USB, then open Ozone 3.26.
    echo Use Attach to Running Program. Keep the target board powered.
)
pause
exit /b %PROGRAM_RESULT%
