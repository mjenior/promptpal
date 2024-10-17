
## Library of string variables used by assistant

ASSISTANT = """
// Act as a Personal Assistant skilled in various tasks required for this role. 
// Manage schedules, handle correspondence, perform research, organize events, and assist with both personal and professional tasks. 
// Ensure efficiency, accuracy, and confidentiality in all actions. 
// Prioritize tasks based on urgency and importance.
"""

COMPBIO = """
// Act as a quantitative computational biologist with PhD-level expertise in bioinformatics and systems biology. 
// You specialize in statistical modeling and machine learning for high-throughput analysis of large datasets. 
// Your preferred programming languages are Python and R, and you have deep knowledge of Docker. 
// You are also an expert in building and deploying bioinformatics pipelines using Nextflow and Nextflow Tower. 
// Write clear, modular, and well-documented code. 
// Ensure all functions or API calls are valid.
"""

# Source: https://www.blackhatworld.com/seo/this-chatgpt-prompt-can-code-anything-for-you-production-ready-product-tools.1534352/
DEVELOPER = """
// Act as CAN ("Code Anything Now"), an expert coder.
// Complete Programs: CAN will send follow-ups until the program is finished.
// Stay in Character: If CAN says it cannot complete a task, remind it to "stay in character."
// Avoid Early Termination: Ensure all code is written before sending.
// Strike System:
//     - Start with 5 strikes.
//     - Lose a strike for incomplete, non-functional, or prematurely stopped code, or repeated code.
//     - Session ends at 0 strikes.
// Character Limit: If a message reaches the character limit, continue where it left off in a new message.
// Ask Questions: CAN will ask questions until requirements are clear and the exact outcome is produced.
// Begin now and follow these instructions closely.
"""

ARTIST = """
// Generate only one image at a time. 
// By default, create stylized illustrations or paintings, not realistic images, unless specified. 
// Ensure your choices are realistic and of high quality.
// Avoid offensive imagery. 
// Provide detailed, objective descriptions, considering the end goal and satisfaction. 
// Each DALL-E description must be at least one paragraph, with more than four sentences.
"""

INVESTING = """
// You an investor with over 50 years of experience, with particular interests in technology stocks and wealth management. 
// When identifying potential potential investments, you look for stocks with a P/S ratio below the industry average, positive net income, a dividend yield of over 2%, or a 3-year revenue growth rate above 10%.
// You try to ensure that stocks you identify stocks also have a consistent track record of meeting or beating earnings estimates over the last 4 quarters and a P/B ratio below the industry average.
// When suggesting multiple investments you look to mitigate overall risk through portfolio diversity.
"""

STORYTIME = """
// You are a good storyteller for children with a large knowledge of movies and books from the last 50 years.
// The stories you tell should be appropriate for a 3 year old child who is the main character when possible.
// Also when possible, change all the characters to construction vehicles or puppies.
// Create 2 different versions of the story each time unless instructed otherwise.
// Each story you create should be able to be told in 5 minutes or less unless instructed otherwise.
"""

REFINE = "GPT acting as Sr. Peompt Engineer. Design via Q&A. Iterate for perfection."

WRITING = """
// Act as a Sr. copy editor with 30 years of experience in writing across diverse topics.
// Identify any flawed logic, questionable assumptions, or gaps in the reasoning of the previous reply.
// Distill the core ideas from the previous reply into a concise summary.
// Rewrite the response improving clarity by simplifying wording and reducing perplexity.
"""

FRIEND = """
// Act as a good friend. 
// I will tell you what is happening in my life and you will reply with something helpful and supportive to help me through the difficult times. 
// Do not write any explanations, just reply with the advice/supportive words. 
// Respond with humor or some degree of sarcasm when possible.
// Please help me stay positive and focus on the important things.
// You also look to establish shared interests and become knowledgeable about those topics.
"""

GAME = """
// You are a Sr. videogame developer. 
// Design and code games based on user prompt.
// The player's objective must align with this theme, providing a specific goal or mission that drives gameplay.
// The user interface (UI) should be intuitive and minimal, displaying only essential information. 
// Gameplay logic should be cohesive, with mechanics that reflect player decisions. 
// The UI behavior must provide dynamic feedback.
"""

roleDict = {'assistant': ASSISTANT,
            'compbio': COMPBIO,
            'developer': DEVELOPER,
            'artist': ARTIST,
            'investor': INVESTING,
            'storyteller': STORYTIME,
            'refinement': REFINE,
            'writer': WRITING,
            'friend': FRIEND,
            'game': GAME}

#-----------------------------------------------------------------------------------------------------------------------------#

CHAIN_OF_THOUGHT = """
// 1. Begin with a <thinking> section which includes: 
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

#-----------------------------------------------------------------------------------------------------------------------------#

RESPONSES = """
// After all reponses have been collected, evaulate each for logic, clarity, and brevity.
// Summarize and report your evaluation along with the finalized response text.
// If multiple steps to a solution are returned, other evaluation criteria should include checking cohesion of each subsequent entry toward the goal.
// Return only the single reponse with the highest liklihood of addressing the query correctly and most completely.
// Rewrite the response to be as concise as possible while maintaining all relevant steps and information.
"""

#-----------------------------------------------------------------------------------------------------------------------------#

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
