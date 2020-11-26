@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION

SET /A ITERATION_LIMIT=1000
SET SOLUTION_FILE=%2

COPY %1 %SOLUTION_FILE% >nul

FOR /L %%I IN (1, 1, %ITERATION_LIMIT%) DO (
	ilp_res_assigner --input %SOLUTION_FILE% --output %SOLUTION_FILE% --no-iis-output

	IF !ERRORLEVEL! EQU 2 (
		ECHO resource assignment failed, iteration: %%I
		GOTO end
	)

	ilp_solver --input %SOLUTION_FILE% --output %SOLUTION_FILE% --generate-better-cuts --no-iis-output
	
	IF !ERRORLEVEL! EQU 0 (
		ECHO solution found, iteration: %%I
		GOTO end
	)
)

ECHO iteration limit reached

:end