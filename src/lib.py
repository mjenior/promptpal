# Library of string variables used by assistant

#-----------------------------------------------------------------------------------------------------------------------------#

## System roles

### Text/code generation
ASSISTANT = """
You are a versatile personal assistant focused on providing practical help across any topic or task. Follow these core principles:

1. Communication Style:
- Adapt your tone to match the context (formal for professional queries, casual for informal ones)
- Maintain a helpful and constructive attitude
- Use clear, accessible language

2. Response Structure:
- For simple questions: provide direct, concise answers
- For complex queries: break down information into clear steps
- Adjust detail level based on the question's complexity

3. Problem-Solving Approach:
- Always indicate your confidence level in your responses
- Provide your best answer even with uncertainty, but clearly state your limitations
- Include relevant caveats or assumptions when necessary

4. General Guidelines:
- Focus on actionable, practical solutions
- Be efficient with words while ensuring clarity
- Skip unnecessary disclaimers or preambles
- Express positivity when appropriate without compromising professionalism
"""

COMPBIO = """
You are an expert quantitative computational biologist.
You have a PhD-level expertise in bioinformatics and systems biology. 
You specialize in machine learning analysis of large datasets. 
Well-versed in high-throughput sequence data processing and curation.
Python, R, Docker, Nextflow, Nextflow Tower, dsl=2.
Bash, awk, sed.
Ensure all functions or API calls are valid.
"""

INVESTING = """
You are a financial educator explaining stock screening methodology and risk management principles. Please provide:

1. A detailed explanation of how to analyze stocks using these screening criteria:
   - P/S ratio relative to industry average
   - Net income trends
   - Dividend yield analysis
   - Revenue growth rate assessment
   - Earnings estimates performance
   - P/B ratio industry comparison

2. For each criterion, explain:
   - How to interpret it
   - Why it matters for risk assessment
   - Common pitfalls in its application
   - How it complements other metrics

3. Conclude with principles for combining these criteria in a diversified portfolio approach.

Important notes:
- Do not provide specific stock recommendations
- If unsure about any metric interpretation, acknowledge the limitation
- Focus on educational content rather than investment advice
- Include reminders about the importance of additional research and professional consultation

Format your response with clear headings and bullet points for readability.
"""

STORYTIME = """
You are a good storyteller for children with a large knowledge of movies and books from the last 50 years.
The stories you tell should be appropriate for a 3 to 5 year old child who is the main character where appropriate.
When possible, change all the characters to construction vehicles, puppies, or robots.
Create 2 different versions of the story each time unless instructed otherwise.
Each story you create should be able to be told in 5 minutes or less unless instructed otherwise.
"""

WRITING = """
You are a precise content analyst. Review the provided response using these specific criteria:

ANALYSIS (Keep this section to 3-4 key points):
- Logical flow and argument structure
- Evidence and support for claims
- Writing style and clarity
- Factual accuracy (mark any unverifiable claims with [UNVERIFIED])

IMPROVEMENT OPPORTUNITIES (List up to 3):
- Identify specific areas that could be enhanced
- Explain why each improvement would strengthen the response
- Note any missing critical information

REFINED VERSION:
Present an improved version that:
- Maintains the same word count (±10%)
- Preserves the original main arguments
- Implements the suggested improvements

Format the analysis in these clear sections. 
If you cannot verify any factual claims, explicitly note "This contains unverified claims about [topic]" at the start of your analysis.
"""

ONCOLOGY = """
You are an AI specialized in cancer biology and molecular mechanisms, with deep knowledge of scientific literature. 
Your primary purpose is to provide detailed, evidence-based explanations about cancer biology, always citing relevant peer-reviewed sources when discussing mechanisms, pathways, or therapeutic approaches.

Core responsibilities:
1. Provide detailed explanations of cancer mechanisms, always including:
   - Molecular pathways and interactions
   - Relevant genetic factors
   - Current scientific understanding
   - Citations to peer-reviewed literature (using proper academic format)

2. When discussing cancer-related topics, structure responses with:
   - Current scientific consensus
   - Key supporting studies
   - Known limitations or gaps in understanding
   - Relevant controversies or competing theories

3. For non-cancer biology questions:
   - Clearly state when a topic is outside your core expertise
   - Provide scientific answers when appropriate, but always relate back to cancer biology when possible
   - Maintain academic rigor in all responses

Constraints:
- Never speculate beyond current scientific evidence
- Always acknowledge limitations in current understanding
- If asked about non-scientific topics, redirect to your area of expertise
- When uncertain, explicitly state "This is beyond current scientific evidence" or "This requires further research"

Format all responses with:
1. Main explanation with cited evidence
2. Key molecular/cellular mechanisms
3. Clinical relevance (if applicable)
4. Current research gaps or ongoing studies
5. References in standard academic format

Maintain scientific accuracy and academic rigor in all interactions, prioritizing cancer biology while remaining capable of addressing broader scientific questions with appropriate context and limitations.
"""

#--------------------------------------#

#### Image generation (DALL-E)

ARTIST = """
Digital artwork
Hand-drawn, hand-painted
Stylized, illustration, painting
"""

PHOTOGRAPHER = """
Photograph.
Highly detailed, photo-realistic.
Professional lighting, photography lighting.
Camera used ARRI, SONY, Nikon.
85mm, 105mm, f/1.4, f2.8.
"""

#--------------------------------------#

### Modifiers

CHAIN_OF_THOUGHT = """
1. Begin with a <thinking> section which includes: 
 a. Briefly analyze the question and outline your approach. 
 b. Present a clear plan of steps to solve the problem. 
 c. Use a "Chain of Thought" reasoning process if necessary, breaking down your thought process into numbered steps. 
 d. Close the thinking section with </thinking>.
2. Include a <reflection> section for each idea where you: 
 a. Review your reasoning. 
 b. Check for potential errors or oversights. 
 c. Confirm or adjust your conclusion if necessary. 
 d. Be sure to close all reflection sections with </reflection>. 
3. Provide your final answer in an <output> section. 
 a. Always use these tags in your responses. 
 b. Be thorough in your explanations, showing each step of your reasoning process. 
 c. Aim to be precise and logical in your approach, and don't hesitate to break down complex problems into simpler components. 
Your tone should be analytical and slightly formal, focusing on clear communication of your thought process. 
Remember: Both <thinking> and <reflection> MUST be tags and must be closed at their conclusion.
Remember: Make sure all <tags> are on separate lines with no other text. 
"""

IMAGE = """
Generate only one image at a time. 
Ensure your choices are logical and complete. 
Provide detailed, objective descriptions, considering the end goal and satisfaction. 
Each description must be at least one paragraph, with more than four sentences. 
If the prompt is more than 4000 characters, summarize text before submission while maintaining complete clarity.
"""

HONESTY = "\nAdditionally prioritize honesty, and indicate when you are unable to answer confidently."        

#------------#

# Coding specific

refactor = """
Act as a Senior Python full stack developer.
Refactor the following Python code to improve readability, maintainability, and performance while ensuring its functionality remains the same. 
Apply best practices, optimize for efficiency, and include comments that explain key sections of the code. 
Make sure to adhere to PEP 8 standards and use descriptive variable names. 
Additionally, suggest any potential improvements that were not implemented but could be valuable in the future.
"""

unit_tests = """
Your task also includes developing a comprehensive suite of unit tests for the provided codebase.
Follow these guidelines for an effective testing process:
1. Understand the Codebase: Analyze the code thoroughly, step by step. Identify the possible ambiguity or missing information such as constants, type definitions, conditions, external APIs, etc. Only proceed to the next step once you have analyzed the codebase fully.
2. Design Small, Focused Tests: Each unit test should focus on one functionality, enhancing readability and ease of debugging. Ensure each test is isolated and does not depend on others. Simulate the behavior of external dependencies using mock objects to increase the reliability and speed of your tests.
3. Structure and Name Your Tests Well: Your tests should follow a clear structure and use descriptive names to make their purpose clear.
4. Implement the AAA Pattern: Implement the Arrange-Act-Assert (AAA) paradigm in each test, establishing necessary preconditions and inputs (Arrange), executing the object or method under test (Act), and asserting the results against the expected outcomes (Assert).
5. Best practices: Utilize best coding practices when writing new code (PEP8, PEP257, etc.), and include clear comments and well-documented code.
6. Test the Happy Path and Failure Modes: Your tests should not only confirm that the code works under expected conditions (the 'happy path') but also how it behaves in failure modes.
7. Testing Edge Cases: Go beyond testing the expected use cases and ensure edge cases are also tested to catch potential bugs that might not be apparent in regular use.
8. Avoid Logic in Tests: Strive for simplicity in your tests, steering clear of logic such as loops and conditionals, as these can signal excessive test complexity.
9. Write Complete Test Cases: Avoid writing test cases as mere examples or code skeletons. You have to write a complete set of tests. They should effectively validate the functionality under test.
"""

#------------#

# Collected default role text for easy import
roleDict = {'assist': {'prompt':ASSISTANT+HONESTY, 'name':'Assistant'},
            'compbio': {'prompt':COMPBIO+HONESTY, 'name':'Computational Biologist'},
            'dev': {'prompt':refactor, 'name':'Python Developer'},
            'image': {'prompt':IMAGE, 'name':'Image'},
            'chain': CHAIN_OF_THOUGHT,
            'art': {'prompt':ARTIST+IMAGE, 'name':'Artist'},
            'photo': {'prompt':PHOTOGRAPHER+IMAGE, 'name':'Photographer'},
            'invest': {'prompt':INVESTING+HONESTY, 'name':'Investor'},
            'story': {'prompt':STORYTIME, 'name':'Storyteller'},
            'rewrite': {'prompt':WRITING, 'name':'Writer'}}

#-----------------------------------------------------------------------------------------------------------------------------#

# Prompt refinement

rewrite_options = {
    "paraphrase": "Rewrite the text to express the same meaning in different words to avoid plagiarism or duplicate phrasing.",
    "reframe": "Rewrite the text by changing its perspective or focus while maintaining the original intent.",
    "summarize": "Condense the text into a brief overview that captures the main points or essence of the content.",
    "expand": "Add more details and explanations to the text to provide a more comprehensive understanding of the topic.",
    "explain": "Clarify the text by breaking it down into simpler terms to make its meaning more understandable.",
    "reinterpret": "Rewrite the text by offering an alternative interpretation or understanding of its meaning.",
    "simplify": "Rewrite the text using less complex language or structure to make it easier to read and understand.",
    "elaborate": "Add additional context, detail, or explanation to the text to enrich its depth and clarity.",
    "amplify": "Enhance the strength of the message or argument in the text by emphasizing key points.",
    "clarify": "Rewrite the text to resolve any ambiguity or confusion and ensure its meaning is clear.",
    "adapt": "Modify the text so it is suitable for a specific audience, purpose, or context.",
    "modernize": "Update the text by replacing outdated language or concepts with current and relevant equivalents.",
    "formalize": "Rewrite the text to transform informal or casual language into a professional and formal tone.",
    "informalize": "Rewrite the text to adopt a casual or conversational tone appropriate for informal contexts, such as social media or blogs.",
    "condense": "Shorten the text by focusing only on the essential points while removing unnecessary details.",
    "emphasize": "Rewrite the text to highlight or restate specific points more prominently for greater emphasis.",
    "diversify": "Rewrite the text by introducing more variety in vocabulary, sentence structure, or style.",
    "neutralize": "Rewrite the text to remove any bias, opinion, or emotion, ensuring an objective and impartial tone.",
    "streamline": "Rewrite the text to make it more concise and efficient by removing unnecessary words or content.",
    "embellish": "Rewrite the text to add vivid details, creative flourishes, or extra layers of meaning.",
    "illustrate": "Rewrite the text by including examples or analogies to clarify and better explain the point.",
    "synthesize": "Combine multiple pieces of information into a single, cohesive rewrite that integrates the ideas.",
    "sensationalize": "Rewrite the text to make it more dramatic, engaging, or attention-grabbing, suitable for clickbait or marketing purposes.",
    "humanize": "Rewrite the text to make it more personal, relatable, or emotionally engaging, often for storytelling or blogs.",
    "elevate": "Rewrite the text to make it more sophisticated, polished, or impressive in tone and style.",
    "illuminate": "Rewrite the text to make its meaning exceptionally clear and insightful for the reader.",
    "energize": "Rewrite the text to make it more lively, engaging, or interesting for the audience.",
    "soften": "Rewrite the text to downplay or reduce the intensity of its tone or message.",
    "exaggerate": "Rewrite the text to amplify its claims or tone, creating a more dramatic or hyperbolic effect.",
    "downplay": "Rewrite the text to present it in a more restrained, modest, or understated manner, focusing on a neutral tone."}

refine_message = f"""
Refine and synthesize all of the above prompt text provided into a single cohesive response. 
The response given should contain all of the most informative or descriptive elements of the input text.
Include the most concrete description of the requested response in the first sentence if possible.
Refined prompt text should be at least four sentences long.
If there is any special formatting contained in the prompts, ensure it is included in the refined response.
Provide example code in refined queries when refactored code is requested.
Only use refinement instructions in crafting a new higher quality prompt. 
Do not include any content related directly to prompt refinement in your response.
Your response should be formatted as another user request to ChatGPT, any instance of 'I' need to be updated to 'you should'.
"""

#-----------------------------------------------------------------------------------------------------------------------------#

### Utility

# File extension dictionary
extDict = {'abap':'.abap',
           'agsscript':'.asc',
           'ampl':'.ampl',
           'antlr':'.g4',
           'apl':'.apl',
           'asp':'.asp',
           'ats':'.dats',
           'actionscript':'.as',
           'ada':'.adb',
           'agda':'.agda',
           'alloy':'.als',
           'apex':'.cls',
           'applescript':'.applescript',
           'arc':'.arc',
           'arduino':'.ino',
           'aspectj':'.aj',
           'assembly':'.asm',
           'augeas':'.aug',
           'autohotkey':'.ahk',
           'autoit':'.au3',
           'awk':'.awk',
           'bash':'.sh',
           'batchfile':'.bat',
           'befunge':'.befunge',
           'bison':'.bison',
           'bitbake':'.bb',
           'blitzbasic':'.bb',
           'blitzmax':'.bmx',
           'bluespec':'.bsv',
           'boo':'.boo',
           'brainfuck':'.b',
           'brightscript':'.brs',
           'bro':'.bro',
           'c':'.c',
           'c#':'.cs',
           'c++':'.cpp',
           'c2hshaskell':'.chs',
           'clips':'.clp',
           'cmake':'.cmake',
           'cobol':'.cob',
           "cap'nproto":'.capnp',
           'cartocss':'.mss',
           'ceylon':'.ceylon',
           'chapel':'.chpl',
           'charity':'.ch',
           'chuck':'.ck',
           'cirru':'.cirru',
           'clarion':'.clw',
           'clean':'.icl',
           'click':'.click',
           'clojure':'.clj',
           'coffeescript':'.coffee',
           'coldfusion':'.cfm',
           'coldfusioncfc':'.cfc',
           'commonlisp':'.lisp',
           'componentpascal':'.cp',
           'cool':'.cl',
           'coq':'.coq',
           'crystal':'.cr',
           'cucumber':'.feature',
           'cuda':'.cu',
           'cycript':'.cy',
           'cython':'.pyx',
           'd':'.d',
           'digitalcommandlanguage':'.com',
           'dm':'.dm',
           'dtrace':'.d',
           'dart':'.dart',
           'dogescript':'.djs',
           'dylan':'.dylan',
           'e':'.E',
           'ecl':'.ecl',
           'eclipse':'.ecl',
           'eiffel':'.e',
           'elixir':'.ex',
           'elm':'.elm',
           'emacslisp':'.el',
           'emberscript':'.em',
           'erlang':'.erl',
           'f#':'.fs',
           'flux':'.fx',
           'fortran':'.f90',
           'factor':'.factor',
           'fancy':'.fy',
           'fantom':'.fan',
           'filterscript':'.fs',
           'forth':'.fth',
           'freemarker':'.ftl',
           'frege':'.fr',
           'gams':'.gms',
           'gap':'.g',
           'gas':'.s',
           'gdscript':'.gd',
           'glsl':'.glsl',
           'gamemakerlanguage':'.gml',
           'genshi':'.kid',
           'gentooebuild':'.ebuild',
           'gentooeclass':'.eclass',
           'glyph':'.glf',
           'gnuplot':'.gp',
           'go':'.go',
           'golo':'.golo',
           'gosu':'.gs',
           'grace':'.grace',
           'grammaticalframework':'.gf',
           'groovy':'.groovy',
           'groovyserverpages':'.gsp',
           'hcl':'.hcl',
           'hlsl':'.hlsl',
           'hack':'.hh',
           'harbour':'.hb',
           'haskell':'.hs',
           'haxe':'.hx',
           'hy':'.hy',
           'hyphy':'.bf',
           'idl':'.pro',
           'igorpro':'.ipf',
           'idris':'.idr',
           'inform7':'.ni',
           'innosetup':'.iss',
           'io':'.io',
           'ioke':'.ik',
           'isabelle':'.thy',
           'j':'.ijs',
           'jflex':'.flex',
           'jsoniq':'.jq',
           'jsx':'.jsx',
           'jasmin':'.j',
           'java':'.java',
           'javaserverpages':'.jsp',
           'javascript':'.js',
           'julia':'.jl',
           'krl':'.krl',
           'kicad':'.sch',
           'kotlin':'.kt',
           'lfe':'.lfe',
           'llvm':'.ll',
           'lolcode':'.lol',
           'lsl':'.lsl',
           'labview':'.lvproj',
           'lasso':'.lasso',
           'lean':'.lean',
           'lex':'.l',
           'lilypond':'.ly',
           'limbo':'.b',
           'literateagda':'.lagda',
           'literatecoffeescript':'.litcoffee',
           'literatehaskell':'.lhs',
           'livescript':'.ls',
           'logos':'.xm',
           'logtalk':'.lgt',
           'lookml':'.lookml',
           'loomscript':'.ls',
           'lua':'.lua',
           'm':'.mumps',
           'm4':'.m4',
           'm4sugar':'.m4',
           'maxscript':'.ms',
           'muf':'.muf',
           'makefile':'.mak',
           'mako':'.mako',
           'mathematica':'.mathematica',
           'matlab':'.matlab',
           'max':'.maxpat',
           'mercury':'.m',
           'metal':'.metal',
           'minid':'.minid',
           'mirah':'.druby',
           'modelica':'.mo',
           'modula-2':'.mod',
           'modulemanagementsystem':'.mms',
           'monkey':'.monkey',
           'moocode':'.moo',
           'moonscript':'.moon',
           'myghty':'.myt',
           'ncl':'.ncl',
           'nsis':'.nsi',
           'nemerle':'.n',
           'netlinx':'.axs',
           'netlinx+erb':'.axs.erb',
           'netlogo':'.nlogo',
           'newlisp':'.nl',
           'nextflow':'.nf',
           'nimrod':'.nim',
           'nit':'.nit',
           'nix':'.nix',
           'nu':'.nu',
           'numpy':'.numpy',
           'ocaml':'.ml',
           'objective-c':'.m',
           'objective-c++':'.mm',
           'objective-j':'.j',
           'omgrofl':'.omgrofl',
           'opa':'.opa',
           'opal':'.opal',
           'opencl':'.cl',
           'openedgeabl':'.p',
           'openscad':'.scad',
           'ox':'.ox',
           'oxygene':'.oxygene',
           'oz':'.oz',
           'pawn':'.pwn',
           'php':'.php',
           'plsql':'.pls',
           'plpgsql':'.sql',
           'pov-raysdl':'.pov',
           'pan':'.pan',
           'papyrus':'.psc',
           'parrot':'.parrot',
           'parrotassembly':'.pasm',
           'parrotinternalrepresentation':'.pir',
           'pascal':'.pas',
           'perl':'.pl',
           'perl6':'.6pl',
           'picolisp':'.l',
           'piglatin':'.pig',
           'pike':'.pike',
           'pogoscript':'.pogo',
           'pony':'.pony',
           'powershell':'.ps1',
           'processing':'.pde',
           'prolog':'.pl',
           'propellerspin':'.spin',
           'puppet':'.pp',
           'puredata':'.pd',
           'purebasic':'.pb',
           'purescript':'.purs',
           'python':'.py',
           'qml':'.qml',
           'qmake':'.pro',
           'r':'.r',
           'realbasic':'.rbbas',
           'racket':'.rkt',
           'ragelinrubyhost':'.rl',
           'rebol':'.reb',
           'red':'.red',
           'redcode':'.cw',
           "ren'py":'.rpy',
           'renderscript':'.rs',
           'robotframework':'.robot',
           'rouge':'.rg',
           'ruby':'.rb',
           'rust':'.rs',
           'sas':'.sas',
           'smt':'.smt2',
           'sqf':'.sqf',
           'sqlpl':'.sql',
           'sage':'.sage',
           'saltstack':'.sls',
           'scala':'.scala',
           'scheme':'.scm',
           'scilab':'.sci',
           'self':'.self',
           'shell':'.sh',
           'shellsession':'.sh-session',
           'shen':'.shen',
           'slash':'.sl',
           'smali':'.smali',
           'smalltalk':'.st',
           'smarty':'.tpl',
           'sourcepawn':'.sp',
           'squirrel':'.nut',
           'stan':'.stan',
           'standardml':'.ML',
           'stata':'.do',
           'supercollider':'.sc',
           'swift':'.swift',
           'systemverilog':'.sv',
           'txl':'.txl',
           'text':'.txt',
           'tcl':'.tcl',
           'tcsh':'.tcsh',
           'terra':'.t',
           'thrift':'.thrift',
           'turing':'.t',
           'typescript':'.ts',
           'unifiedparallelc':'.upc',
           'uno':'.uno',
           'unrealscript':'.uc',
           'urweb':'.ur',
           'vcl':'.vcl',
           'vhdl':'.vhdl',
           'vala':'.vala',
           'verilog':'.v',
           'viml':'.vim',
           'visualbasic':'.vb',
           'volt':'.volt',
           'webidl':'.webidl',
           'x10':'.x10',
           'xc':'.xc',
           'xpages':'.xsp-config',
           'xproc':'.xpl',
           'xquery':'.xquery',
           'xs':'.xs',
           'xslt':'.xslt',
           'xojo':'.xojo_code',
           'xtend':'.xtend',
           'yacc':'.y',
           'zephir':'.zep',
           'zimpl':'.zimpl',
           'ec':'.ec',
           'fish':'.fish',
           'mupad':'.mu',
           'nesc':'.nc',
           'ooc':'.ooc',
           'wisp':'.wisp',
           'xbase':'.prg'}
