inputFile = arg[1]
outputFile = arg[2]
iterationLimit = 1000
enablePrintProgress = true

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

copyFile(inputFile, outputFile)

iteration = 1
while iteration <= iterationLimit do
	printProgress("iteration " .. iteration)

	assignResult = os.execute("ilp_res_assigner.exe --input " .. outputFile .. " --output " .. outputFile)

	if assignResult == 2 then
		print("assign failed (iteration " .. iteration .. ")")
		break
	end

	os.remove("infeasible_schedule.ilp")
	solveResult = os.execute("ilp_solver.exe --input " .. outputFile .. " --output " .. outputFile)
	
	if solveResult == 0 then
		print("solve succeeded (iteration " .. iteration .. ")")
		break
	end

	printProgress("adding cut:")
	instance = json.decode(readFile(outputFile))

	assignmentCut = {}
	for i, task in pairs(instance["tasks"]) do
		printProgress(task["name"] .. " -!-> " .. task["assignmentIndex"])
		assignmentCut[#assignmentCut+1] = { task = task["name"], assignmentIndex = task["assignmentIndex"] }
	end

	if instance["assignmentCuts"] == nil then instance["assignmentCuts"] = {} end
	instance["assignmentCuts"][#instance["assignmentCuts"]+1] = assignmentCut

	writeFile(outputFile, json.encode(instance))
	
	printProgress("")
	iteration = iteration + 1
end	

if iteration > iterationLimit then print("iteration limit reached") end
