 [ ABOUT ]
 
   hcsbuilder is a utility that compiles HSB files 
   (base HTML pages with YAML data and template insertion points) into 
   standard HTML.

 [ SYNOPSIS ]

   hcsbuilder.py [-h] [--version] [-v] [--template-dir PATH]
                 [--output-dir PATH] input_file


 [ ARGUMENTS ]

   input_file
       Path to the file or directory to process.
       - If a compilation FILE is specified, that single file is built.
       - If a DIRECTORY is specified, the utility enters batch mode,
         recursively finding and building all .hsb files within.

   -h, --help
       Show the help message and exit.

   --version
       Show the program's version number and exit.

   -v, --verbose
       Enable verbose output. Useful for debugging manifest parsing
       or seeing detailed processing steps.
       * NOTE: If 'rich' library is installed, manifest data is
         pretty-printed in color.

   --template-dir PATH
       Override the default template directory (./templates).
       Use this if your HTML templates are stored elsewhere.

   --output-dir PATH
       Specify where generated HTML files should be placed.
       Default is './output'.


 [ BATCH PROCESSING MODE ]

   When a DIRECTORY is passed as the input_file:
   
   1. The utility recursively scans for supported files (.hsb, .txt, etc).
   2. It preserves the directory structure in the output folder.
      (e.g., ./pages/blog/post.hsb -> ./output/pages/blog/post.html)
   3. It continues execution even if individual files fail.
   4. A SUMMARY REPORT is generated at the end, listing:
      - Total files processed
      - Success count
      - Failure count
      - List of any failed files


 [ EXIT CODES ]

   0 : Success (all files processed correctly)
   1 : Error (generic error, or failures occurred during batch processing)


 [ EXAMPLES ]

   1. Build a single page:
      $ ./hcsbuilder.sh index.hsb

   2. Build an entire site from the current directory:
      $ ./hcsbuilder.sh ./

   3. Build with custom output folder and verbose logging:
      $ ./hcsbuilder.sh ./content --output-dir ./dist -v