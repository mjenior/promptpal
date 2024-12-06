import re
import os
import requests

from openai import OpenAI

from src.lib import extDict


class OpenAIInterface:
    """
    Handles OpenAI API interactions including assembling, submitting, and processing queries.
    """

    def __init__(self, manager):
        """
        Initializes the query handler with the provided variables.
        """
        self.client = OpenAI()
        self.query = self._assemble_query(manager)
        
    def _assemble_query(self, manager):
        """
        Assembles the query dictionary for the API request.
        """
        query = [
            {"role": "user", "content": manager.prompt},
            {"role": "system", "content": manager.role}
        ]
        if manager.reflection:
            query.append({"role": "assistant", "content": manager.reflection})
        
        return query

    def submit_query(self, manager):
        """
        Submits the query to OpenAI's API and processes the response.
        """
        if not manager.silent:
            print("\nThinking...\n")
        if manager.label not in ["artist", "photo"]:
            return self._process_text_response(manager)
        return self._process_image_response(manager)

    def _process_text_response(self, manager):
        """
        Processes text-based responses from OpenAI's chat models.
        """
        self.reponse_type = "reponse"
        response = self.client.chat.completions.create(
            model=manager.model, messages=self.query
        )
        message = response.choices[0].message.content
        if manager.verbose:
            print(f"Response:\n{message}")

        if manager.code:
            os.makedirs('code', exist_ok=True)
            scripts = self._separate_code(message)
            if scripts and not manager.silent:
                print("\nCode identified and saved separately:")
                for script in scripts:
                    print(f"\t{script}")

        if manager.log:
            self._save_response_text(message, manager)

    def _process_image_response(self, manager):
        """
        Processes image generation requests using OpenAI's image models.
        """
        self.reponse_type = "revised_prompt"
        os.makedirs('images', exist_ok=True)
        response = self.client.images.generate(
            model=manager.model,
            prompt=manager.prompt,
            n=1,
            size=manager.size,
            quality=manager.quality
        )
        revised_prompt = response.data[0].revised_prompt
        if manager.verbose:
            print(f"Revised prompt:\n{revised_prompt}")

        image_data = requests.get(response.data[0].url).content
        image_file = f"images/{manager.model.replace('-', '')}.{manager.timestamp}.image.png"
        with open(image_file, 'wb') as outFile:
            outFile.write(image_data)
        if not manager.silent:
            print("\nGenerated image saved to:", image_file)

        if manager.log:
            self._save_response_text(revised_prompt, manager)

    def _save_response_text(self, message, manager):
        """
        Saves the current response text to a file if specified.
        """
        outFile = f"responses/{manager.label}.{manager.model.replace('-', '')}.{manager.timestamp}.{self.reponse_type}.txt"
        os.makedirs('responses', exist_ok=True)
        with open(outFile, "w", encoding="utf-8") as file:
            file.write(message)

        if not manager.silent:
            print(f"Response text saved to:\n\t{outFile}\n")

    def _separate_code(self, response):
        """
        Extracts and saves code snippets from the response into separate files.
        """
        code_found = False
        code = ''
        count = 0
        outFiles = []
        func_names = []

        lines = response.split('\n')
        for line in lines:
            if line.startswith('```') and not code_found:
                code_found = True
                count += 1
                code = ''
                lang = line.replace('```', '').lower().strip()
                ext = extDict.get(lang, lang)

            elif line.startswith('```') and code_found:
                name = max(func_names, key=len, default="code")
                code_file = f"code/{name}.{count}{ext}"
                code_file = code_file.lstrip('_')
                if len(code.splitlines()) > 2:
                    os.makedirs('code', exist_ok=True)
                    with open(code_file, "w", encoding="utf-8") as file:
                        file.write(code)
                    outFiles.append(code_file)
                code_found = False

            elif code_found:
                code += f"{line}\n"
                if "def " in line or "class " in line:
                    func_names.append(self._find_script_name(line))

        # Lint python code
        self._format_python_scripts(outFiles)

        return outFiles

    @staticmethod
    def _find_script_name(line):
        """
        Extracts a meaningful name for a script or class from the provided line of text.
        """
        name = line.split()[1].split('(')[0].lower()
        return re.sub(r'[^0-9a-zA-Z]+', '_', name) or 'script'

    @staticmethod
    def _format_python_scripts(scripts):
        """
        Formats Python scripts using `black`.
        """
        for script in scripts:
            if script.endswith('.py'):
                os.system(f'black {script} -q')
