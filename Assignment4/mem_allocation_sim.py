#!/usr/bin/env python3

import os
import sys
from ImplicitFreeList import ImplicitFreeList

class MemAllocSim:
    def __init__(self, args):
        self.check_args(args)
        self.create_list()
        first = self.myalloc(5)
        print(self.myalloc(5))
        third = self.myalloc(5)
        print(self.myalloc(24))
        self.myfree(first)
        self.myfree(third)
        self.myalloc(6)



    def myalloc(self, size):
        return self.wordList.myalloc(size)

    def myfree(self, addr):
        self.wordList.myfree(addr)
    
    def create_list(self):
        if self.list_type == 'I':
            self.wordList = ImplicitFreeList()
            self.wordList.headers.add_node(size=998, a=1, addr=0)
            self.wordList.footers.add_node(size=998, a=1, addr=999)



    def check_args(self, args):
        #If -h specified, print and exit
        if '-h' in args:
            self.print_help_then_quit()

        #Check for -f flag, then -l followed by I or E, then -a followed by F or B
        assert '-f' in args, self.print_help_then_quit("-f argument required in command line arguments")
        assert '-l' in args, self.print_help_then_quit("-l argument required in command line arguments")
        assert '-a' in args, self.print_help_then_quit("-a argument required in command line arguments")

        #Get item after each flag
        self.file_path = args[args.index('-f')+1]
        self.list_type = args[args.index('-l')+1]
        self.fit_type = args[args.index('-a')+1]

        #Verify file path exists
        assert os.path.exists(self.file_path), self.print_help_then_quit("File path must be valid")
        #Verify list_type is either I or E
        assert self.list_type == 'I' or self.list_type == 'E', self.print_help_then_quit("List type must be either I for Implicit, or E for Explicit")
        #Verify list_type is either I or E
        assert self.fit_type == 'F' or self.fit_type == 'B', self.print_help_then_quit("Fit type must be either F for First-fit, or B for Best-fit")



    def print_help_then_quit(self, error_msg=None):
        #If an additional error message, print it out
        if error_msg:
            print("\n\nERROR: " + error_msg)
        
        #Print help message
        print("""
Usage: ./mem_allocation_sim.py [-h] -f <filepath> -l <IE> -a <FB>
-h: Optional help flag that prints usage info then exits
-f <input text file>: Path to the input file to read from
-l <IE>: Free list type. Either I is specified, for Implicit, or E is specified, for Explicit
-a <FB>: Allocation type. Either F is specified, for First-fit, or B is specified, for Best-fit""")

        #Exit
        sys.exit()



if __name__ == '__main__':
    MAS = MemAllocSim(sys.argv)