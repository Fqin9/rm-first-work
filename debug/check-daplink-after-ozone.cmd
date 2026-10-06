@echo off
setlocal
echo Close Ozone and other OpenOCD windows first. Keep the target powered.
echo Do not press RESET before this check. Reading target status takes a few seconds.
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
set "DIAG_LOG=%~dp0daplink-after-ozone.log"
rem Suppress the default examine-end register writes to observe the existing state.
rem No reset, halt, resume, flash, option-byte, or memory-write commands are issued.
"%OPENOCD_EXE%" -s "%OPENOCD_SCRIPTS%" -f interface/cmsis-dap.cfg -c "transport select swd" -f target/stm32f1x.cfg -c "adapter speed 100" -c "stm32f1x.cpu configure -event examine-end {}" -c "tcl port disabled" -c "telnet port disabled" -c "gdb port disabled" -c "init" -c "poll" -c "mdw 0x40021024 1" -c "mdw 0xE0042004 1" -c "mdw 0xE000EDF0 1" -c "mdw 0x20000080 1" -c "sleep 1200" -c "mdw 0x20000080 1" -c "sleep 1200" -c "mdw 0x20000080 1" -c "mdw 0x40021024 1" -c "poll" -c "shutdown" > "%DIAG_LOG%" 2>&1
set "DIAG_RESULT=%ERRORLEVEL%"
type "%DIAG_LOG%"
echo.
echo Log saved to: %DIAG_LOG%
echo Diagnostic exit code: %DIAG_RESULT%
echo Send a screenshot of this output. Do not rerun prepare-daplink-326.cmd yet.
pause
exit /b %DIAG_RESULT%
