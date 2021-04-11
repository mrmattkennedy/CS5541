#!/usr/bin/env python3

import os
import sys
from ImplicitFreeList import ImplicitFreeList
from ExplicitFreeList import ExplicitFreeList

class MemAllocSim:
    def __init__(self, args):
        self.check_args(args)
        self.create_list()
        self.current_pointers = []
        self.read_file()
        self.wordList.output()
     


    def myalloc(self, size, ptr):
        if not (ptr >= 0 and ptr <= 999):
            print("Reference address provided in last argument must be between 0 and 999")
            return

        if ptr in self.current_pointers:
            print("Pointer requested must not already exist")
            return

        if self.fit_type == 'F':
            result = self.wordList.first_fit(size, ptr)
        elif self.fit_type == 'B':
            result = self.wordList.best_fit(size, ptr)

        if result == -1:
            print("Heap space in excess of 100,000 words with this call, stopping simulator")
            sys.exit()
        else:
            self.current_pointers.append(result)
            return result



    def myfree(self, ptr):
        result = self.wordList.myfree(ptr)
        if result == 1:
            self.current_pointers.remove(ptr)



    def myrealloc(self, size, old_ptr, new_ptr):
        if old_ptr not in self.current_pointers:
            print("Pointer requested for resize must already exist")
            return

        self.myfree(old_ptr)

        if not (new_ptr >= 0 and new_ptr <= 999):
            print("Reference address provided in last argument must be between 0 and 999")
            return

        if new_ptr in self.current_pointers:
            print("Pointer requested must not already exist")
            return

        if self.fit_type == 'F':
            result = self.wordList.first_fit(size, new_ptr)
        elif self.fit_type == 'B':
            result = self.wordList.best_fit(size, new_ptr)

        if result == -1:
            print("Heap space in excess of 100,000 words with this call, stopping simulator")
            sys.exit()
        else:
            self.current_pointers.append(result)
            return result


    def read_file(self):
        with open(self.file_path, 'r') as f:
            for line in f:
                line = line.replace('\n', '').replace(' ', '')
                line_args = line.split(',')
                
                #print(line)
                if line_args[0] == 'a':
                    assert len(line_args) == 3, "alloc requests must have 3 parts: a, size, requested_pointer"
                    self.myalloc(int(line_args[1]), int(line_args[2]))
                elif line_args[0] == 'f':
                    assert len(line_args) == 2, "free requests must have 2 parts: f, pointer_to_free"
                    self.myfree(int(line_args[1]))
                elif line_args[0] == 'r':
                    assert len(line_args) == 4, "realloc requests must have 4 parts: r, new_size, old_ptr, new_ptr"
                    self.myrealloc(int(line_args[1]), int(line_args[2]), int(line_args[3]))

    
    def create_list(self):
        if self.list_type == 'I':
            self.wordList = ImplicitFreeList()
            self.wordList.headers.add_node(size=998, a=1, addr=0)
            self.wordList.footers.add_node(size=998, a=1, addr=999)

        elif self.list_type == 'E':
            self.wordList = ExplicitFreeList()
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