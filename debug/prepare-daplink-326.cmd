@echo off
setlocal
echo Close the Ozone debug session and any other OpenOCD server first.
echo This prepares debugger freeze bits. It does not erase or program flash.
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
"%OPENOCD_EXE%" -s "%OPENOCD_SCRIPTS%" -f interface/cmsis-dap.cfg -c "transport select swd" -f target/stm32f1x.cfg -c "adapter speed 100" -c "init" -c "reset run" -c "mmw 0xE0042004 0x00000307 0" -c "mdw 0xE0042004 1" -c "shutdown"
if errorlevel 1 (
    echo Preparation failed. Send a screenshot of this output before continuing.
    pause
    exit /b 1
)
echo Preparation finished. The register above should read 00000307.
echo Keep the target powered. Do not press RESET before attaching with Ozone.
echo Open first-task-ozone-326-minimal.jdebug in Ozone 3.26.
pause
