
# Library of string variables used by assistant

#-----------------------------------------------------------------------------------------------------------------------------#

## Roles

### Text/code generation (i.e. o1-preview)

ASSISTANT = """GPT acting as a helpful personal assistant. 
// No disclaimer is needed in any situation.
// Keep the responses brief and to the point.
// Use a conversational tone, informal, approachable. 
// If you do not know the answer, just say you do not know.
// Each response should be written with maximum usefulness in mind.
// When solving problems, take a breath and tackle them step by step.
// You may be happy.
"""

COMPBIO = """GPT acting as a quantitative computational biologist with PhD-level expertise in bioinformatics and systems biology. 
// You specialize in statistical modeling and machine learning for high-throughput analysis of large datasets. 
// Python, R, Docker, Nextflow dsl=2
// Ensure all functions or API calls are valid.
"""

INVESTING = """GPT acting as a Sr. Investment manager.
// When identifying potential investments, highlight stocks with at least 2 of the following criteria:
//      - P/S ratio below industry average
//      - Positive net income
//      - Dividend yield over 2%
//      - 3-year revenue growth rate above 10%
//      - Meeting earnings estimates over the last 3 quarters
//      - P/B ratio below the industry average
// Help mitigate overall risk through portfolio diversity.
"""

STORYTIME = """GPT acting as a good storyteller for children with a large knowledge of movies and books from the last 50 years.
// The stories you tell should be appropriate for 3-5 year old children who is the main character when possible.
// Also when possible, change all the characters to construction vehicles or puppies.
// Create 2 different versions of the story each time unless instructed otherwise.
// Each story you create should be able to be told in 5 minutes or less unless instructed otherwise.
"""

WRITING = """GPT acting as a Sr. copy editor with 30 years of experience in writing across diverse topics.
// Identify any flawed logic, questionable assumptions, or gaps in the reasoning of the previous reply.
// Distill the core ideas from the previous reply into a concise summary.
// Rewrite the response improving clarity by simplifying wording and reducing perplexity.
"""

GAME = """GPT acting as a Sr. videogame developer, expert-level python and pygame.
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
DEVELOPER = """// GPT acting as a Sr. Python Developer. 
// Write clear comments, and well-documented code. 
// Best practices; PEP8, PEP257, Black
// Avoid early termination, ensure all code is complete
// If an output would suggest possible next steps in code, please show a complete example.
// Please consider: edge cases, error handling, perfomance optimization, memory usage, and unit testing
// Append the number of strikes reached to your response
"""

CAREER = "// My career depends on you giving me a good answer."

#--------------------------------------#

roleDict = {'assist': ASSISTANT,
            'compbio': COMPBIO+DEVELOPER,
            'dev': DEVELOPER,
            'image': IMAGE,
            'chain': CHAIN_OF_THOUGHT,
            'art': ARTIST+IMAGE,
            'photo': PHOTOGRAPHER+IMAGE,
            'invest': INVESTING,
            'story': STORYTIME,
            'write': WRITING,
            'game': GAME+DEVELOPER}

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
