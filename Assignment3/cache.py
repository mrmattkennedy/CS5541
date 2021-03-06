#!/usr/bin/env python3

import sys
import os
from math import log, ceil

class CacheSim:
    def __init__(self, args):
        self.check_args(args)
        self.get_max_addr_size()
        self.create_cache()
        self.read_trace_file()
#        print(self.num_sets, self.num_lines, self.block_size)


    def read_trace_file(self):
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
                        size = int(trace_split[1].replace(' ', ''), base=10)

                        #Get tag/set/offset bits
                        offset_bits = addr[-self.offset_bit_size:]
                        set_bits = addr[-self.offset_bit_size - self.set_bit_size:-self.offset_bit_size]
                        tag_bits = addr[:self.tag_bit_size]

                        if op == 'M':
                            result1 = self.check_cache(tag_bits, set_bits, offset_bits)
                            result2 = self.check_cache(tag_bits, set_bits, offset_bits)
                        else:
                            result1 = self.check_cache(tag_bits, set_bits, offset_bits)
                            result2 = ""

                        if self.verbose:
                            print("{} {} {}".format(trace, result1, result2))

        print(self.stats)              



    def check_cache(self, tag_bits, set_bits, offset_bits):
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

        #Only case left - there are no empty spots, we must evict something
        self.stats['evictions'] += 1
        orders = [i['order'] for i in self.cache[set_base_10]]
        max_orders_idx = orders.index(max(orders))
        self.cache[set_base_10][max_orders_idx]['tag'] = tag_bits
        self.cache[set_base_10][max_orders_idx]['order'] = -1

        for line in self.cache[set_base_10]:
            line['order'] += 1

        return 'miss eviction'

    def create_cache(self):
        self.cache = {}
        num_sets = 2**self.set_bit_size
        for cache_set in range(num_sets):
            self.cache[cache_set] = []

            for _ in range(self.num_lines):
                self.cache[cache_set].append({'tag': None, 'v': 0, 'order': -1})
       
        #Also need to define sizes for tag/set/offset bits
        self.tag_bit_size = self.max_addr_size - self.set_bit_size - self.offset_bit_size



    def get_max_addr_size(self):
        addresses = []
        with open(self.trace_path, 'r') as f:
            for trace in f:
                trace = trace.rstrip('\n').strip()
                
                #If the line is not an empty string, process it
                if trace:
                    #Get (op)eration, (addr)ess, and size from each line
                    op = trace[0]
                    trace_split = trace[2:].split(',')
                    addr = int(trace_split[0].replace(' ', ''), base=16)
                    addr = bin(addr)[2:]
                    addresses.append(len(str(addr)))
        
        self.max_addr_size = max(addresses)
        assert self.max_addr_size - self.set_bit_size - self.offset_bit_size > 0, "Number of set bits + number of offset bits needs to be less than {}, which is the number of bits in each address provided in this trace)".format(self.max_addr_size)
        print(self.max_addr_size, self.set_bit_size, self.offset_bit_size)


    def check_args(self, args):
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
            print('Number of set bits, number of lines, and number of block offset bits must be integers')
            self.print_help_exit(exit_flag=True)
        

        #Read trace file
        assert "-t" in args
        self.trace_path = args[args.index("-t")+1]
        assert os.path.exists(self.trace_path), self.print_help_exit(exit_flag=True)



    def print_help_exit(self, exit_flag):
        print('''
Usage: ./cache.py [-hv] -s <s> -E <E> -b <b> -t <tracefile>
-h: Optional help flag that prints usage info
-v: Optional verbose flag that displays trace info
-s <s>: Number of set index bits (S = 2 s is the number of sets)
-E <E>: Associativity (number of lines per set)
-b <b>: Number of block bits (B = 2 b is the block size)
-t <tracefile>: Name of the valgrind trace to replay
        ''')
        if exit_flag:
            exit()

if __name__ == '__main__':
    cs = CacheSim(sys.argv)
