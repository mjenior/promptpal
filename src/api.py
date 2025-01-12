import re
import os
import requests
from copy import copy
from collections import defaultdict

from openai import OpenAI

from src.lib import extDict, rewrite_options, refine_message

class OpenAIInterface():
    """
    Handles OpenAI API interactions including assembling, submitting, and processing queries.
    """

    def __init__(self, manager):
        """
        Initializes the query handler with the provided variables.
        """
        # Inherit core properties
        attributes = ["prompt", "role", "label", "verbose", 
            "timestamp", "model", "code", "logging", "log_text", 
            "size", "quality", "iterations", "prefix", "seed",
            "base_url", "api_key", "refine", "added_query"]
        for attr in attributes:
            setattr(self, attr, getattr(manager, attr))
        if self.logging == True:
            setattr(self, "log_file", getattr(manager, "log_file"))
        self.tokens = {'prompt':0, 'completion':0}

        # Initialize client
        if self.model == 'deepseek-chat':
            self.client = OpenAI(api_key=self.api_key, 
                base_url="https://api.deepseek.com")
        else:
            self.client = OpenAI(api_key=self.api_key)

        # Finalize query            
        self.query = self._assemble_query()
        
    def _assemble_query(self):
        """
        Assembles the query dictionary for the API request.
        """
        if self.refine == True:
            self.prompt = self._refine_prompt()
            if 'refactor' in self.prompt.lower() or 'rewrite' in self.prompt.lower():
                if len(self.added_query.strip()) > 0:
                    self.prompt += "\n\nImprove the following:\n"
                    self.prompt += self.added_query

            reportStr = "\n\nRefined query prompt:\n" + self.prompt
            if self.verbose == True:
                print(reportStr)
            if self.logging == True:
                self.log_text.append(reportStr)

        query = [{"role": "user", "content": self.prompt},
                 {"role": "system", "content": self.role}]

        return query

    def submit_query(self):
        """
        Submits the query to OpenAI's API and processes the response.
        """
        reportStr = "\n\nProcessing finalized "
        if self.label not in ["artist", "photo"]:
            reportStr += "completion query...\n"
            if self.verbose == True: print(reportStr)
            self._process_text_response()
        else:
            reportStr += "image request...\n"
            if self.verbose == True: print(reportStr)
            self._process_image_response()
            
        # Add to log file
        if self.logging == True:
            self.log_text.append(reportStr)

        # Find cost of the run
        token_report = self.gen_token_report()
        self.log_text.append(token_report)
        if self.verbose == True:
            print(token_report)

        # Save reporting transcript to txt file
        if self.logging == True:
            self.save_chat_transcript()

        # Complete run
        if self.verbose == True:
            print("\n\nFinished.\n\n")

    def _process_text_response(self):
        """
        Processes text-based responses from OpenAI's chat models.
        """
        self.reponse_type = "reponse"
        response = self.client.chat.completions.create(
            model=self.model, 
            messages=self.query, 
            n=self.iterations,
            seed=self.seed
        )
        message = self.condense_iterations(response)
        self.tokens['prompt'] += response.usage.prompt_tokens
        self.tokens['completion'] += response.usage.completion_tokens

        reportStr = "\nSystem response to query:\n" + message
        if self.verbose == True:
            print(reportStr)
        else:
            print(message)
        if self.logging == True:
            self.log_text.append(reportStr)

        if self.code:
            scripts = self._extract_code_from_reponse(message, self.timestamp)
            if scripts:
                os.makedirs('code', exist_ok=True)
                reportStr = "\nCode extracted from reponse text and saved to:\n\t" + '\n\t'.join(scripts) + "\n"
                if self.verbose == True:
                    print(reportStr)
                if self.logging == True:
                    self.log_text.append(reportStr)

    def _process_image_response(self):
        """
        Processes image generation requests using OpenAI's image models.
        """
        self.reponse_type = "revised_prompt"
        os.makedirs('images', exist_ok=True)
        response = self.client.images.generate(
            model=self.model, prompt=self.prompt,
            n=1, size=self.size, quality=self.quality)
        revised_prompt = response.data[0].revised_prompt
        self.tokens['prompt'] += response.usage.prompt_tokens
        self.tokens['completion'] += response.usage.completion_tokens
        
        reportStr = "\nRevised initial initial prompt:\n" + revised_prompt
        if self.verbose == True:
            print(reportStr)
        if self.logging == True:
            self.log_text.append(reportStr)

        image_data = requests.get(response.data[0].url).content
        image_file = f"images/{self.prefix}.image.png"
        with open(image_file, 'wb') as outFile:
            outFile.write(image_data)
        
        reportStr = "\nGenerated image saved to: " + image_file + "\n"
        print(reportStr)
        if self.logging == True:
            self.log_text.append(reportStr)

    def gen_token_report(self):
        """
        Calculates and generates report str for overall cost of the current query
        """
        prompt_cost = completion_cost = total_cost = 'Unknown model rate'
        total_tokens = self.tokens['prompt'] + self.tokens['completion']
        rates = {'gpt-4o': (2.5, 10), 'gpt-4o-mini': (0.150, 0.600), 'o1-mini': (3, 12), 'o1-preview': (15, 60)}
        if self.model.lower() in rates:
            prompt_rate, completion_rate = rates[self.model.lower()]
            prompt_cost = calculate_cost(self.tokens['prompt'], prompt_rate)
            completion_cost = calculate_cost(self.tokens['completion'], completion_rate)
        elif 'dall-e' in self.model.lower():
            prompt_cost = calculate_cost(self.tokens['prompt'], prompt_rate)
            completion_cost = 0.040

        total_cost = round(prompt_cost + completion_cost, 5)
        if total_cost < 0.01:
            total_cost = "<< $ 0.01"
        else:
            total_cost = f"$ {total_cost}"
        prompt_cost, completion_cost = f"$ {prompt_cost}", f"$ {completion_cost}"

        reportStr = f"""
Total tokens generated: {self.tokens['prompt'] + self.tokens['completion']}  ({total_cost})
    Prompt (i.e. input): {self.tokens['prompt']}  ({prompt_cost})
    Completion (i.e. output): {self.tokens['completion']}  ({completion_cost})
        """

        return reportStr

    def save_chat_transcript(self):
        """
        Saves the current response text to a file if specified.
        """
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write("\n".join(self.log_text))

        if self.verbose == True:
            print("\nSaving conversation transcript text to:", self.log_file)

    def _extract_code_from_reponse(self, response, timestamp):
        """
        Extracts and saves code snippets from the response into separate files.
        """
        # Initialize variables
        pyObjects = defaultdict(list)
        pyObjects["current_code"] = ["# Code generated by ChatGPT\n"]

        # Split response into lines and process
        for line in response.splitlines():

            # Start or end of a code block
            counter = 0
            if line.startswith("```"):
                if len(pyObjects["current_code"]) > 2:  # End of a code block
                    pyObjects["code"] = "\n".join(pyObjects["current_code"]) + "\n"

                    # Determine output filename
                    counter += 1
                    name = self._select_outfile_ext(pyObjects['classes'], pyObjects['functions'], lang)
                    file_name = f"code/{name}.{timestamp}.{counter}{extDict.get(lang, f".{lang}")}".lstrip('_')
                    pyObjects['files'].append(file_name)

                    # Save code snippet to file
                    os.makedirs("code", exist_ok=True)
                    with open(file_name, "w", encoding="utf-8") as file:
                        file.write(pyObjects["code"])

                    # Reset code accumulator
                    pyObjects["current_code"] = ["# Code generated by ChatGPT\n"]

                else:  # Start of a new code block
                    lang = line.replace("```", "").lower()
                    pyObjects["current_code"].append(f"# {lang}\n")

            # Process lines within a code block
            elif len(pyObjects["current_code"]) > 1:
                pyObjects["current_code"].append(line)
                if len(line.strip()) > 0 and line.split()[0] in ['def', 'class']:
                    f, c = self._scrape_object_name(line)
                    pyObjects['functions'].append(f)
                    pyObjects['classes'].append(c)

        return pyObjects["files"]

    @staticmethod
    def _select_outfile_ext(classes, funcs, lng):
        """
        Select name for code files based on generated functions and classes
        """
        classes = [x for x in classes if len(x.strip()) >= 1]
        funcs = [x for x in funcs if len(x.strip()) >= 1]
        if len(classes) != 0:
            name = max(classes, key=len, default=lng)
        else:
            name = max(funcs, key=len, default=lng)

        return max([name, 'code'], key=len)

    @staticmethod
    def _scrape_object_name(line):
        """
        Extracts a meaningful name for a script or class from the provided line of text.
        """
        name = line.split()[1].split('(')[0].lower()
        name = re.sub(r'[^0-9a-zA-Z]+', '_', name)
    
        func, clss = '', ''
        if line.startswith("def ") and " main(" not in line:
            func = name
        elif line.startswith("class "):
            clss = name

        return func, clss

    def condense_iterations(self, api_response, sys_text=refine_message):
    
        api_responses = [r.message.content.strip() for r in api_response.choices]
        if len(api_responses) > 1:
            condensed = self.client.chat.completions.create(
                model=self.model,
                seed=self.seed,
                messages = [
                    {"role": "system", "content": sys_text},
                    {"role": "user", "content": "\n\n".join(api_responses)}])
            self.tokens['prompt'] += condensed.usage.prompt_tokens
            self.tokens['completion'] += condensed.usage.completion_tokens
            
            return condensed.choices[0].message.content.strip()
        else:
            return api_responses[0]

    def _refine_prompt(self, actions=['expand','amplify'], temp=0.7):
        """
        Refines an LLM prompt using specified rewrite actions.
        
        Parameters:
            prompt (str): The original prompt to be refined.
            actions (list of str): A list of rewrite actions (keys from the rewrite_options dictionary).
            temp (float): Tempature to set model to.
        
        Returns:
            A string containing the refined prompt
        """
        reportStr = "\nRefining initial prompt..."
        if self.verbose == True:
            print(reportStr)
        if self.logging == True:
            self.log_text.append(reportStr)
        
        # Check prompt for additional action keywords
        actions = set(actions)
        words = set([re.sub(r'[^\w\s]','', word).lower() for word in self.prompt.split() if len(word) >= 1])
        actions |= set(rewrite_options.keys()).intersection(words)
        action_str = ""
        for a in actions:
            action_str += f"{a}; {rewrite_options[a]}" + "\n"

        # Generate the system message for the action
        updated_role = self.role + "Your primary task is to refine or improve the user prompt, do not respond directly to the provided request."
        updated_message = refine_message + action_str
        if self.role: # Add specific expertise if provided
            updated_prompt = self.prompt + updated_message
        
        # Make an API call to refine the prompt over X iterations:
        refined = self.client.chat.completions.create(
            model=self.model, 
            temperature=temp, 
            n=self.iterations,
            seed=self.seed,
            messages=[
                {"role": "system", "content": updated_role},
                {"role": "user", "content": updated_prompt}])
        self.tokens['prompt'] += refined.usage.prompt_tokens
        self.tokens['completion'] += refined.usage.completion_tokens

        # Parse iterations and synthesize for more optimal response
        return self.condense_iterations(refined)


def calculate_cost(tokens, perM, dec=5):
    """Calculates approximate cost (USD) of LLM tokens generated to a given decimal place"""
    return round((tokens * perM) / 1e6, dec)
