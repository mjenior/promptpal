
import os
from datetime import datetime

from bin.lib import extDict

# Generate timestamp string
def gen_timestamp(time=True):
    date_time = str(datetime.now()).split()
    date = date_time[0].split('-'); time = date_time[1].split('.')[0]
    date = f"{int(date[1])}_{int(date[2])}_{int(date[0])}"; time = time.replace(':','')
    
    if time:
        return f"{date}.{time}"
    else:
        return date

# Find code snippets in responses and save to separate scripts with appropriate file extensions
def pull_code(response, name_ext='script', extensions=extDict):
    os.makedirs('code', exist_ok=True)

    code_found = False; code = ''; count = 0; outFiles = []
    lines = response.split('\n')
    for line in lines:
        if len(line.strip()) == 0:
            continue

        if line.startswith('```') and code_found == False:
            code_found = True; count += 1; code = ''
            lang = line.replace('```','').lower().split()[0]
            try:
                ext = extensions[lang]
            except KeyError:
                ext = lang
            codeFile = f"code/{name_ext}.{count}.{ext}"

        elif line.startswith('```') and code_found == True:
            code_found = False
            outFiles.append(codeFile)
            if codeFile.startswith('_'): codeFile = codeFile.lstrip('_')
            if len(code.split('\n')) > 2:
                with open(codeFile, "w") as outFile:
                    outFile.write(code)
        
        elif code_found == True:
            code += f"{line}\n"

    return outFiles


