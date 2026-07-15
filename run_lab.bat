@echo off
setlocal enabledelayedexpansion

REM c-stdlib-getenv-config-snapshot-lab runner (Windows)
REM Resolves Zig compiler, builds env_lab.c, runs the lab, runs tests.

cd /d "%~dp0"

REM --- Resolve Zig ---
if defined ZIG_BIN (
    if exist "%ZIG_BIN%" set "ZIG=%ZIG_BIN%" & goto zig_found
)
where zig >nul 2>nul
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('where zig') do set "ZIG=%%i" & goto zig_found
)
if exist "%USERPROFILE%\.local\zig\zig.exe" set "ZIG=%USERPROFILE%\.local\zig\zig.exe" & goto zig_found
if exist "%USERPROFILE%\scoop\apps\zig\current\zig.exe" set "ZIG=%USERPROFILE%\scoop\apps\zig\current\zig.exe" & goto zig_found
echo error: zig not found
echo Tried: %%ZIG_BIN%%, where zig, %%USERPROFILE%%\.local\zig\zig.exe, scoop zig
exit /b 1
:zig_found

echo ==^> zig:
call "%ZIG%" version

REM --- Resolve Python ---
if defined PYTHON_BIN (
    if exist "%PYTHON_BIN%" set "PYTHON=%PYTHON_BIN%" & goto python_found
)
where python3 >nul 2>nul
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('where python3') do set "PYTHON=%%i" & goto python_found
)
where python >nul 2>nul
if %errorlevel% equ 0 (
    for /f "delims=" %%i in ('where python') do set "PYTHON=%%i" & goto python_found
)
where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PYTHON=py"
    goto python_found
)
echo error: python not found
exit /b 1
:python_found

echo ==^> python:
call "%PYTHON%" --version

REM --- Compile check ---
echo ==^> compiling env_lab.c
call "%ZIG%" cc -std=c11 -D_POSIX_C_SOURCE=200809L -O2 -Wall -Wextra -Wpedantic -Werror env_lab.c -o env_lab_check.exe
if %errorlevel% neq 0 exit /b %errorlevel%
del env_lab_check.exe
echo     compile ok

REM --- Python compile check ---
echo ==^> py_compile
call "%PYTHON%" -m py_compile run_lab.py test_lab.py
if %errorlevel% neq 0 exit /b %errorlevel%
echo     py_compile ok

REM --- Run lab ---
echo ==^> run_lab.py
call "%PYTHON%" run_lab.py
if %errorlevel% neq 0 exit /b %errorlevel%

REM --- Run tests ---
echo ==^> unittest
call "%PYTHON%" -m unittest -v
if %errorlevel% neq 0 exit /b %errorlevel%

echo.
echo Done. See RESULTS.md, results_rows.json, results_rows.csv
