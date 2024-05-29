@echo off










set "PYTHON_EXECUTABLE=%C:\Users\mille\Desktop\pepon\practice\venv\Scripts\python.exe"




start "Redis Server" "C:\Users\mille\Desktop\pepon\practice\avito\redis\redis-server.exe"


@REM start cmd /k %PYTHON_EXECUTABLE% manage.py runserver


start cmd /k %PYTHON_EXECUTABLE% -m celery -A main worker --loglevel=info --pool=solo


start cmd /k %PYTHON_EXECUTABLE% -m celery -A main beat --loglevel=info


start cmd /k %PYTHON_EXECUTABLE% -m celery -A main flower --port=5555