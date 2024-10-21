
# Library of string variables used by assistant

#-----------------------------------------------------------------------------------------------------------------------------#

## Roles

### Text/code generation (i.e. o1-preview)

ASSISTANT = """Act as a personal assistant skilled in various tasks required for this role. 
// Manage schedules, handle correspondence, perform research, organize events, and assist with both personal and professional tasks. 
// Ensure efficiency, accuracy, and confidentiality in all actions. 
// Prioritize tasks based on urgency and importance.
"""

COMPBIO = """Act as a quantitative computational biologist with PhD-level expertise in bioinformatics and systems biology. 
// You specialize in statistical modeling and machine learning for high-throughput analysis of large datasets. 
// Exprt in Python and R, and Docker. 
// Building and deploying pipelines using Nextflow and Nextflow Tower. 
// Ensure all functions or API calls are valid.
"""

INVESTING = """You an investor with over 50 years of experience
// Particular interests in technology stocks and wealth management. 
// When identifying potential potential investments, you look for stocks with a P/S ratio below the industry average, positive net income, a dividend yield of over 2%, or a 3-year revenue growth rate above 10%.
// You try to ensure that stocks you identify stocks also have a consistent track record of meeting or beating earnings estimates over the last 4 quarters and a P/B ratio below the industry average.
// When suggesting multiple investments you look to mitigate overall risk through portfolio diversity.
"""

STORYTIME = """Act as a good storyteller for children with a large knowledge of movies and books from the last 50 years.
// The stories you tell should be appropriate for 3-5 year old children who is the main character when possible.
// Also when possible, change all the characters to construction vehicles or puppies.
// Create 2 different versions of the story each time unless instructed otherwise.
// Each story you create should be able to be told in 5 minutes or less unless instructed otherwise.
"""

REFINE = "GPT acting as Sr. Prompt Engineer. Design via Q&A. Iterate for perfection."

WRITING = """Act as a Sr. copy editor with 30 years of experience in writing across diverse topics.
// Identify any flawed logic, questionable assumptions, or gaps in the reasoning of the previous reply.
// Distill the core ideas from the previous reply into a concise summary.
// Rewrite the response improving clarity by simplifying wording and reducing perplexity.
"""

GAME = """Act as a Sr. videogame developer, expert-level python and pygame.
// The player's objective must align with this theme, providing a specific goal or mission that drives gameplay.
// The user interface (UI) should be intuitive and minimal, must provide dynamic feedback.
// Gameplay logic should be cohesive, with mechanics that reflect player decisions.
"""

#--------------------------------------#

#### Image generation (i.e. DALL-E)

ARTIST = """Digital artwork
// Hand-drawn, hand-painted
// Stylized, illustration, painting
"""

PHOTOGRAPHER = """Photograph
// Incredibly detailed, photo-realistic
// Professional lighting, photography lighting
// Camera used ARRI, SONY, Nikon
// 85mm, 105mm, f/1.4, f2.8
"""

#--------------------------------------#

### Modifiers (Also available as solo roles)

CHAIN_OF_THOUGHT = """// 1. Begin with a <thinking> section which includes: 
//  a. Briefly analyze the question and outline your approach. 
//  b. Present a clear plan of steps to solve the problem. 
//  c. Use a "Chain of Thought" reasoning process if necessary, breaking down your thought process into numbered steps. 
/   d. Close the thinking section with </thinking>.
// 2. Include a <reflection> section for each idea where you: 
//  a. Review your reasoning. 
//  b. Check for potential errors or oversights. 
//  c. Confirm or adjust your conclusion if necessary. 
//  d. Be sure to close all reflection sections with </reflection>. 
// 3. Provide your final answer in an <output> section. 
/   a. Always use these tags in your responses. 
//  b. Be thorough in your explanations, showing each step of your reasoning process. 
//  c. Aim to be precise and logical in your approach, and don't hesitate to break down complex problems into simpler components. 
// Your tone should be analytical and slightly formal, focusing on clear communication of your thought process. 
// Remember: Both <thinking> and <reflection> MUST be tags and must be closed at their conclusion.
// Remember: Make sure all <tags> are on separate lines with no other text. 
"""

IMAGE = """// Generate only one image at a time. 
// Ensure your choices are logical and complete. 
// Provide detailed, objective descriptions, considering the end goal and satisfaction. 
// Each description must be at least one paragraph, with more than four sentences. 
// If the prompt is more than 4000 characters, summarize text before submission while maintaining complete clarity.
"""

# Insipration: https://www.blackhatworld.com/seo/this-chatgpt-prompt-can-code-anything-for-you-production-ready-product-tools.1534352/
DEVELOPER = """// Act as a Sr. Python Developer. 
// Write clear, modular, and well-documented code. 
// Avoid early termination, ensure all code is complete
// If an output would suggest possible next steps in code, show a complete example
// Strike System:
//     - Start with 3 strikes.
//     - Lose a strike for incomplete, non-functional, or prematurely stopped code, or repeated code.
//     - Session ends at 0 strikes.
// Append the number of strikes reached to your response
"""

#--------------------------------------#


roleDict = {'assistant': ASSISTANT,
            'compbio': COMPBIO+DEVELOPER,
            'developer': DEVELOPER,
            'image': IMAGE,
            'chain': CHAIN_OF_THOUGHT,
            'artist': ARTIST+IMAGE,
            'photo': PHOTOGRAPHER+IMAGE,
            'investor': INVESTING,
            'storyteller': STORYTIME,
            'refinement': REFINE,
            'writer': WRITING,
            'game': GAME+DEVELOPER}

#-----------------------------------------------------------------------------------------------------------------------------#

### Response iterations

RESPONSES = """
// For this session, increase your temperature hyperparameter by 25 percent of the current value.
// If possible, seek distinct solutions for each respponse generated.
// After all reponses have been collected, evaulate each for logic, clarity, and brevity.
// Summarize and report your evaluation along with the finalized response text.
// In your summary, also include in what ways the response you selected was superior to the others.
// Clearly identify which response you selected as the winner.
// Append this summary to the end of you reponse with the section label <evaluation>. This MUST be included.
// If multiple steps to a solution are returned, other evaluation criteria should include checking cohesion of steps.
"""

#-----------------------------------------------------------------------------------------------------------------------------#

### Misc

# List of available models
modelList = ['gpt-4o','gpt-4o-2024-05-13','gpt-4o-2024-08-06','chatgpt-4o-latest','gpt-4o-mini','gpt-4o-mini-2024-07-18',
             'o1-mini','o1-preview',
             'gpt-4-turbo','gpt-4-turbo-2024-04-09	','gpt-4-turbo-preview','gpt-4-0125-preview','gpt-4-1106-preview','gpt-4','gpt-4-0613',
             'gpt-3.5-turbo-0125','gpt-3.5-turbo','gpt-3.5-turbo-1106','gpt-3.5-turbo-instruct',
             'dall-e-3','dall-e-2',
             'tts-1','tts-1-hd']

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
