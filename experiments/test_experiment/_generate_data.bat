@echo off

FOR /L %%i IN (1,1,15) DO (
	..\..\tools\bin\generator.exe --environment ../../data/test_environment.json >instance_%%i.json
)	
