from identifier import *

# from Integrator.SemanticModel import *


# step 1: get win-win inputs from file

# step 2: figure out file Noun Phrases

# step 3: figure out relationships

# step 4: generate json for UMLViewer


class Proccesser:
    def identify(self):
        input_path = os.getcwd() + "/input/"

        sentence_size = 0
        execption_size = 0

        file_list = glob.glob(input_path + "*.txt") #2014-USC-Project01.txt

        print "Total size: " + str(len(file_list))

        identifier = Identifier()

        
        for file in file_list:
            print "Proceessing " + file + "..."
            try:
                with open(file) as f:
                    sentences = f.read().splitlines()
                    for s in sentences:
                        result = identifier.identify(s)
                        if not result is None:
                            sentence_size += 1
                        else:
                            execption_size += 1

                    prefix, file_name = os.path.split(file)
                    with fileOps.safe_open_w(os.getcwd() + "/result/project/" + file_name) as o:
                        o.write(json.dumps(result, indent=4))
                        identifier.clear()
            except Exception as e:
                print "Error in " + file
                print exc_info()
                continue

        # identifier.display("Final Result", final_result)

        print "total combination: " + str(len(result))
        print "total sentence size: " + str(sentence_size)
        print "total exception size: " + str(execption_size)
    

if __name__ == "__main__":
    
    proccesser = Proccesser()
    proccesser.identify()