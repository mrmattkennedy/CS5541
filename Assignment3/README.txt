Date: 03/08/2021

Class: CS5541

Assignment: Cache Simulator

Author: Matt Kennedy

Email: mfj0222@wmich.edu


General info:
For this program, I decided to use Python. My version is 3.8.2, but this should work for most versions of Python 3.
I used the Google Style Python Docstrings, found here: https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
All algorithms/code are mine, except for filling leading zeros for addresses that were shorter than others, which I found here https://stackoverflow.com/questions/1395356/how-can-i-make-bin30-return-00011110-instead-of-0b11110
I used both vim on ubuntu 20.04 LTS, as well as visual studio code on Windows 10 to run this. It ran fine on both.
If the help flag is specified, then the code will exit after printing help. This is done because the example cache simulator provided does the same thing.

Running:
There are 2 different ways this can be run, both of which vary depending on the python command you use on your system. 

The first is just like a compiled executable, with the following format:
./cache.py [-hv] -s <s> -E <E> -b <b> -t <path_to_trace>
If this method provides an error, this will be due to the shebang, which is the first line of code. The shebang points to your system's python 3 location.
On your system, you may need to remove the very last character and change it to just "python" instead of "python3". Or use the second method of execution.

The other way to run this is using the python command. For example, on my system, it is:
python3 cache.py [-hv] -s <s> -E <E> -b <b> -t <path_to_trace>
If you have the python3 command on your system, you shouldn't have issues. If you instead just use python, use that instead.
