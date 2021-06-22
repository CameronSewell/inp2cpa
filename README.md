# inp2cpa
File conversion tool to extract relevant data from inp files and use it to create cpa files to help automate cyber-physical testing

## Windows Standard Install 
 * Create a virtual environment for inp2cpa using Python 3.6.4 as target interpreter. This can be done by manually installing Python 3.6.4 from https://www.python.org/downloads/release/python-364/ and running ```python -m virtualenv env python=<path_to_python364>``` with the appropriate path if you are doing manual path and version management, or if you are using Anaconda this can be done by running ``` conda create -n py364 python=3.6.4 anaconda ``` and ensuring you run the install and program from the correct environment
 * From within this virtual environment execute: ``` pip install fbs PyQt5==5.15.2 wntr ```
 * Clone the repository: git clone https://github.com/CameronSewell/inp2cpa. This can be done with any built-in CLI git package, or with the official git GUI. In Windows you can download and use a bash emulator such as Git for Windows (https://gitforwindows.org/)
 * Change to the root directory and execute: ``` fbs run ```
