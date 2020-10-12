@echo off

..\..\tools\bin\stat.exe --no-input --write-header >stats.csv

FOR /L %%i IN (1,1,15) DO (
	..\..\tools\bin\solver.exe --input instance_%%i.json --method 0 >solution_%%i_0.json
	..\..\tools\bin\solver.exe --input instance_%%i.json --method 1 >solution_%%i_1.json
	..\..\tools\bin\stat.exe --input solution_%%i_0.json >>stats.csv
	..\..\tools\bin\stat.exe --input solution_%%i_1.json >>stats.csv
)	
