
import os
import pickle
from datetime import datetime


def gen_timestamp():
    timestamp = str(datetime.now()).replace('-','.').replace(':','.').split()
    timestamp[1] = '.'.join(timestamp[1].split('.')[0:-1])
    return '_'.join(timestamp)


path = os.path.dirname(os.path.realpath(__file__))
with open(f"{path}/lib/extDict.pkl", "rb") as inFile:
    ExtDict = pickle.load(inFile)


def pull_code(response, curr_time):
    code_found = False; code = ''; func = ''; outFiles = []
    lines = response.split('\n')
    for line in lines:
        if len(line.strip()) == 0:
            continue

        elif line.startswith('```') and code_found == False:
            code_found = True
            ext = line.replace('```','').lower().split()[0]
            codeFile = f"{curr_time}.{ext}"
            continue

        elif line.startswith('```') and code_found == True:
            code_found = False
            codeFile = '_'.join([func, codeFile])
            outFiles.append(codeFile)
            if codeFile.startswith('_'): codeFile = codeFile.lstrip('_')
            if len(code.split('\n')) > 2:
                with open(codeFile, "w") as outFile:
                    outFile.write(code)
            code = ''; func = ''
            continue
        
        elif code_found == True:
            code += f"{line}\n"
            if "def " in line:
                func = line.split()[1].split("(")[0].split("_")
                for i, s in enumerate(func):
                    if i >= 1:
                        func[i] = s.capitalize()
                func = "".join(func)
            elif "<- function(" in line:
                func = line.split()[0].split("_")
                for i, s in enumerate(func):
                    if i >= 1:
                        func[i] = s.capitalize()
                func = "".join(func)
        continue

    return outFiles