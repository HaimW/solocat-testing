@echo off
REM Audio Processing System - Windows Test Runner
setlocal enabledelayedexpansion

set "command=%~1"
set "options=%~2 %~3 %~4"

if "%command%"=="" set "command=help"

goto :%command% 2>nul || goto :unknown_command

:demo
    echo [INFO] Running demo tests...
    call :check_venv
    python pytest\demo_test.py
    goto :end

:unit
    echo [INFO] Running unit tests...
    call :check_venv
    python -m pytest pytest\unit_tests\ %options% --tb=short -p no:postgresql -p no:kubernetes
    goto :end

:functional
    echo [INFO] Running functional tests...
    call :check_venv
    python -m pytest pytest\functional_tests\ %options% --tb=short -p no:postgresql -p no:kubernetes
    goto :end

:performance
    echo [INFO] Running performance tests...
    call :check_venv
    python -m pytest pytest\performance_tests\ %options% --tb=short -p no:postgresql -p no:kubernetes -m "not slow"
    goto :end

:security
    echo [INFO] Running security tests...
    call :check_venv
    python -m pytest pytest\security_tests\ %options% --tb=short -p no:postgresql -p no:kubernetes
    goto :end

:all
    echo [INFO] Running all tests...
    call :check_venv
    python -m pytest pytest\ %options% --tb=short -p no:postgresql -p no:kubernetes --ignore=pytest\demo_test.py
    goto :end

:coverage
    echo [INFO] Running tests with coverage...
    call :check_venv
    python -m pytest pytest\ %options% --tb=short -p no:postgresql -p no:kubernetes --ignore=pytest\demo_test.py --cov=pytest --cov-report=html:coverage_html --cov-report=term-missing
    echo [INFO] Coverage report generated in coverage_html\
    goto :end

:help
    echo Audio Processing System Test Runner (Windows)
    echo Usage: %~nx0 [COMMAND] [OPTIONS]
    echo.
    echo Commands:
    echo   demo        Run demo tests (no dependencies)
    echo   unit        Run unit tests
    echo   functional  Run functional tests
    echo   performance Run performance tests
    echo   security    Run security tests
    echo   all         Run all tests
    echo   coverage    Run tests with coverage report
    echo   help        Show this help
    echo.
    echo Options:
    echo   -v          Verbose output
    echo   -q          Quiet output
    echo   -n auto     Run tests in parallel
    echo.
    echo Examples:
    echo   %~nx0 demo
    echo   %~nx0 unit -v
    echo   %~nx0 coverage -n auto
    goto :end

:check_venv
    if "%VIRTUAL_ENV%"=="" (
        echo [WARN] Virtual environment not activated
        echo [INFO] Activating virtual environment...
        call .venv\Scripts\activate.bat
    )
    exit /b

:unknown_command
    echo [ERROR] Unknown command: %command%
    echo.
    goto :help

:end
    if not "%command%"=="help" pause 