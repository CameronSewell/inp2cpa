# inp2cpa
File conversion tool to extract relevant data from inp files and use it to create cpa files to help automate cyber-physical testing

## Windows Standard Install 
 * Create a virtual environment for inp2cpa using Python 3.6.4 as target interpreter. This can be done by manually installing Python 3.6.4 from https://www.python.org/downloads/release/python-364/ and running ```python -m virtualenv env python=<path_to_python364>``` with the appropriate path if you are doing manual path and version management, or if you are using Anaconda this can be done by running ``` conda create -n py364 python=3.6.4 anaconda ``` and ensuring you run the install and program from the correct environment
 * From within this virtual environment execute: ``` pip install fbs PyQt5==5.15.2 wntr ```
 * Clone the repository: git clone https://github.com/CameronSewell/inp2cpa. This can be done with any built-in CLI git package, or with the official git GUI. In Windows you can download and use a bash emulator such as Git for Windows (https://gitforwindows.org/)
 * Change to the root directory (inp2cpa), where the 'src' folder should be visible, and execute: ``` fbs run ```
 * If having issues installing packages in the target language you can use a later verison like python 3.8 to install fbs, PyQt5, and wntr. But be sure to change your target language back to 3.6 before attempting to execute '```fbs run```

## Mac Stardard Install
* Create a virtual environment for inp2cpa using Python 3.6.13 as target interpreter. This an be done using a package manager such as Anaconda. Anaconda can be installed from https://docs.anaconda.com/anaconda/install/. If using Anaconda, run ``` conda create -n dev python=3.6.13 anaconda``` to create a new virtual environment. 
* From within this virtual environment execute: ``` pip install fbs PyQt5==5.15.2 wntr ```
* Clone the repository: git clone https://github.com/CameronSewell/inp2cpa. This can be done with any built-in CLI git package, or with the official git GUI. 
* Change to the root directory (inp2cpa), where the 'scr' folder should be visable, and execute: ``` fbs run ```
* If running the program in a source-code editor such as Visual Studio Code, the target interpreter may have to be selected again. To do so, open the command palette (⇧⌘P), and type and select "Python: Select Interpreter". From the drop-down menu, select the 'dev' virtual environment, which should be python version 3.6.13. 
