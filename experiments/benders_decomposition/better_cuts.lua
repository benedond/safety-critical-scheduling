inputFile = arg[1]
outputFile = arg[2]
iterationLimit = 1000
enablePrintProgress = true
infeasiblScheduleFile = "infeasible_schedule.ilp"
ilpResAssigner = "ilp_res_assigner.exe"
ilpSolver = "ilp_solver.exe"


json = require("json")

function readFile(file)
	local f = assert(io.open(file))
	local content = f:read("*all")
	f:close()
	return content
end

function writeFile(file, content)
	f = assert(io.open(file, "w"))
	f:write(content)
	f:close()
end

function copyFile(fileIn, fileOut)
	writeFile(fileOut, readFile(fileIn))
end	

function printProgress(message)
	if not enablePrintProgress then return end
	print(message)
end

function findUnschedulableTasks(scheduleData)
	tasks = {}
	
	lines = scheduleData:gmatch("[^\r\n]+")
	for line in lines do
		task = line:match("(.*)_scheduled")
		if task ~= nil then
			task = task:gsub("^%s*(.-)%s*$", "%1")
			tasks[task] = task
		end
	end

	return tasks
end

copyFile(inputFile, outputFile)

iteration = 1
while iteration <= iterationLimit do
	printProgress("iteration " .. iteration)

	ar, _, assignResult = os.execute(ilpResAssigner .. " --input " .. outputFile .. " --output " .. outputFile)
	if assignResult == nil then assignResult = ar end

	if assignResult == 2 then
		print("assign failed (iteration " .. iteration .. ")")
		break
	end

	os.remove(infeasiblScheduleFile)
	sr, _, solveResult = os.execute(ilpSolver .. " --input " .. outputFile .. " --output " .. outputFile)
	if solveResult == nil then solveResult = sr end

	if solveResult == 0 then
		print("solve succeeded (iteration " .. iteration .. ")")
		break
	end

	printProgress("adding cut:")

	instance = json.decode(readFile(outputFile))
	tasks = findUnschedulableTasks(readFile(infeasiblScheduleFile))

	assignmentCut = {}
	for i, task in pairs(instance["tasks"]) do
		if tasks[task["name"]] ~= nil then
			printProgress(task["name"] .. " -!-> " .. task["assignmentIndex"])
			assignmentCut[#assignmentCut+1] = { task = task["name"], assignmentIndex = task["assignmentIndex"] }
		end
	end

	if instance["assignmentCuts"] == nil then instance["assignmentCuts"] = {} end
	instance["assignmentCuts"][#instance["assignmentCuts"]+1] = assignmentCut

	writeFile(outputFile, json.encode(instance))
	
	printProgress("")
	iteration = iteration + 1
end	

if iteration > iterationLimit then print("iteration limit reached") end
