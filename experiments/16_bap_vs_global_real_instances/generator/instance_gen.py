import instance


input_filename = "IN_50.json"
json_data = instance.read_json_from_file(input_filename)
  
env = instance.parse_environment(json_data)
acs = instance.parse_assignment_characteristics(json_data)

for i in range(1,len(acs)):
    new_data = {}
    new_data["assignmentCharacteristics"] = json_data["assignmentCharacteristics"][:i]
    new_data["environment"] = json_data["environment"]
    
    instance.write_to_file(new_data, "IN_{:02d}.json".format(i))

 
