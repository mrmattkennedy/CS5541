#!/usr/bin/env python3

import sys
import os

class CacheSim:
    """Class to simulate a cache with specified sets/associativity/block size

    Attributes:
        self.verbose (bool): Whether or not to print each line of a trace file
        self.set_bit_size (int): # of bits required to determine set
        self.num_lines (int): # of lines per set, this is also called associativity
        self.offset_bit_size (int): # of bits required to determine block offset
        self.trace_path (str): Path to the trace file to read from
        self.max_addr_size (int): Max # of bits of all addresses from trace file
        self.cache (dict): Cache representation, holds cache data
        self.tag_bit_size: # of bits in each tag
        self.stats (dict): Keeps track of # of hits/misses/evictions

    """

    def __init__(self, args):
        self.check_args(args)
        self.get_max_addr_size()
        self.create_cache()
        self.read_trace_file()


    def read_trace_file(self):
        """Reads the trace file specified after the -t flag
        Goes line-by-line, gets the bits for tag, set, and block offset
        Passes these to check_cache method, records hits/misses/evictions

        Args:
            None
        Returns:
            None
        """
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}

        with open(self.trace_path, 'r') as f:
            for trace in f:
                trace = trace.rstrip('\n').strip()

                #If the line is not an empty string, process it
                if trace:
                    #Get (op)eration, (addr)ess, and size from each line
                    op = trace[0]

                    if op in ['L', 'S', 'M']:
                        trace_split = trace[2:].split(',')
                        addr = int(trace_split[0].replace(' ', ''), base=16)
                        addr = bin(addr)[2:].zfill(self.max_addr_size)

                        #Get tag/set/offset bits
                        set_bit_start = -self.offset_bit_size - self.set_bit_size
                        set_bit_end = -self.offset_bit_size
                        set_bits = addr[set_bit_start:set_bit_end]
                        tag_bits = addr[:self.tag_bit_size]

                        if op == 'M':
                            result1 = self.check_cache(tag_bits, set_bits)
                            result2 = self.check_cache(tag_bits, set_bits)
                        else:
                            result1 = self.check_cache(tag_bits, set_bits)
                            result2 = ""

                        if self.verbose:
                            print("{} {} {}".format(trace, result1, result2))

        print(self.stats)



    def check_cache(self, tag_bits, set_bits):
        """Checks the cache for a hit/miss/eviction based on params passed in

        Args:
            tag_bits (str): The bits that make up the tag
            set_bits (str): the bits that makes up the set

        Returns:
            'hit' if hit found
            'miss' if miss with available empty spot, no eviction required
            'eviction' if miss and eviction required
        """

        #Perform cache operation(s)
        set_base_10 = int(set_bits, base=2)

        #Check if tag exists - look for hit
        for line in self.cache[set_base_10]:
            if line['tag'] == tag_bits and line['v'] == 1:
                self.stats['hits'] += 1
                return 'hit'

        #See if any invalid bits, take those
        self.stats['misses'] += 1
        for line in self.cache[set_base_10]:
            if line['v'] == 0:
                line['tag'] = tag_bits
                line['v'] = 1
                line['order'] = 0
                return 'miss'

        #Only case left - there are no empty spots, must evict something
        self.stats['evictions'] += 1
        orders = [i['order'] for i in self.cache[set_base_10]]
        max_orders_idx = orders.index(max(orders))
        self.cache[set_base_10][max_orders_idx]['tag'] = tag_bits
        self.cache[set_base_10][max_orders_idx]['order'] = -1

        for line in self.cache[set_base_10]:
            line['order'] += 1

        return 'miss eviction'



    def create_cache(self):
        """Creates the cache using a dictionary containing a list of dictionaries
        Highest level dictionary is the sets, the list in each set contains the levels
        Each level in the list contains a valid flag, a tag, and the order placed in for LIFO

        Args:
            None
        Returns:
            None
        """

        self.cache = {}
        num_sets = 2**self.set_bit_size
        for cache_set in range(num_sets):
            self.cache[cache_set] = []

            for _ in range(self.num_lines):
                self.cache[cache_set].append({'tag': None, 'v': 0, 'order': -1})

        #Also need to define sizes for tag/set/offset bits
        self.tag_bit_size = self.max_addr_size - self.set_bit_size - self.offset_bit_size



    def get_max_addr_size(self):
        """Gets the max number of bits from all addresses provided.
        Used to pad shorter addresses later if necessary.

        Args:
            None
        Returns:
            None
        """

        addresses = []
        with open(self.trace_path, 'r') as f:
            #Loop through each line (trace) in the file
            for trace in f:
                trace = trace.rstrip('\n').strip()

                #If the line is not an empty string, process it
                if trace:
                    #Get address, convert to binary, append the length to the addresses list
                    trace_split = trace[2:].split(',')
                    addr = int(trace_split[0].replace(' ', ''), base=16)
                    addr = bin(addr)[2:]
                    addresses.append(len(str(addr)))

        self.max_addr_size = max(addresses)
        assert self.max_addr_size - self.set_bit_size - self.offset_bit_size > 0, "Number of set bits + number of offset bits needs to be less than {}, which is the number of bits in each address provided in this trace)".format(self.max_addr_size)
        print(self.max_addr_size, self.set_bit_size, self.offset_bit_size)



    def check_args(self, args):
        """Parses command line arguments.
        Starts by checking for help flag. If present, print and exit.
        Next, checks for verbose flag, sets verbose mode
        Next, verifies -s, -E, and -b flags are present, and the arg following each flag is an int
        Last, verifies the -t flag is present, and the arg after it is a valid file path

        Args:
            args (list): Command line arguments passed in

        Returns:
            None

        """

        #If h flag, don't care about anything else, just print help
        if "-hv" in args or "-h" in args or "-vh" in args:
            self.print_help_exit(exit_flag=True)

        self.verbose = False
        if "-hv" in args or "-v" in args or "-vh" in args:
            self.verbose = True

        #Need to have -s, -E, and -b flags
        assert "-s" in args, self.print_help_exit(exit_flag=True)
        assert "-E" in args, self.print_help_exit(exit_flag=True)
        assert "-b" in args, self.print_help_exit(exit_flag=True)

        #Find the number of each flag
        num_set_bits = args[args.index("-s")+1]
        num_lines = args[args.index("-E")+1]
        num_block_bits = args[args.index("-b")+1]

        #Verify each flag is an int
        try:
            self.set_bit_size = int(num_set_bits)
            self.num_lines = int(num_lines)
            self.offset_bit_size = int(num_block_bits)
        except ValueError:
            print('Number of set bits, lines, block offfset bits must be integers')
            self.print_help_exit(exit_flag=True)


        #Read trace file
        assert "-t" in args, self.print_help_exit(exit_flag=True)
        self.trace_path = args[args.index("-t")+1]
        assert os.path.exists(self.trace_path), self.print_help_exit(exit_flag=True)



    def print_help_exit(self, exit_flag):
        """Prints help string, exits if specified

        Args:
            exit_flag: Specifies if program should exit after printing help message

        Returns:
            None

        """

        print("""
Usage: ./cache.py [-hv] -s <s> -E <E> -b <b> -t <tracefile>
-h: Optional help flag that prints usage info
-v: Optional verbose flag that displays trace info
-s <s>: Number of set index bits (S = 2 s is the number of sets)
-E <E>: Associativity (number of lines per set)
-b <b>: Number of block bits (B = 2 b is the block size)
-t <tracefile>: Name of the valgrind trace to replay""")

        if exit_flag:
            sys.exit()



if __name__ == '__main__':
    CS = CacheSim(sys.argv)
