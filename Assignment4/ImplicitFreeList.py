import math
from LinkedList import LinkedList, Node

class ImplicitFreeList:
    def __init__(self):
        self.bytes_per_word = 4
        self.payload_string = '11111111111111111111111111111111'
        self.heap = {}
        for i in range(1000):
            self.heap[i] = '{:032b}'.format(0)
            
        self.headers = LinkedList()
        self.footers = LinkedList()
        


    def myalloc(self, size):
        payload_words = int(size / self.bytes_per_word) + math.ceil(size % self.bytes_per_word)
        header_node = self.headers.first_node
        while header_node:

            #If the node is free, and the size of the block is >= the size requested by user + 2 words for header/footer blocks
            if header_node.a == 1 and header_node.size >= payload_words:
                #Check each available word in block for first aligned word to start
                for word in range(header_node.addr, header_node.addr+header_node.size-(payload_words+2), 1):
                    if ((word+1)*self.bytes_per_word) % 8 == 0:

                        #Create data to store in header footer - first 31 bits are size, LSB is to indicate free or not
                        new_header = self.headers.add_node(size=payload_words, a=0, addr=word)
                        new_footer = self.footers.add_node(size=payload_words, a=0, addr=word+payload_words+1)

                        #Coalesce and return node addr
                        self.coalesce()
                        return word

            header_node = header_node.next_node



    def myfree(self, addr):
        node = self.headers.first_node
        if node.addr != addr:
            while node.next_node and node.next_node.addr != addr:
                node = node.next_node
            
            node.next_node = node.next_node.next_node
        else:
            self.headers.first_node = self.headers.first_node.next_node
        
        self.coalesce()
        


    def first_fit(self, size):
        pass



    def coalesce(self):
        #Step 1 - remove all first blocks in header until first block is full
        while self.headers.first_node.a == 1:
            self.headers.first_node = self.headers.first_node.next_node

        #Step 2 - go through each header, delete all free blocks
        node = self.headers.first_node
        while node and node.next_node:
            if node.next_node.a == 1:
                next_full_block = node.next_node
                while next_full_block and next_full_block.a == 1:
                    next_full_block = next_full_block.next_node
                node.next_node = next_full_block
            node = node.next_node

        #Step 3 - fill in empty space before start if possible
        if self.headers.first_node.addr >= 3:
            old_head = self.headers.first_node
            new_size = old_head.addr - 2
            self.headers.add_node(size=new_size, a=1, addr=0, force_start=True)
            self.headers.first_node.next_node = old_head

        #Step 4 - fill in space between all nodes after first and before last
        node = self.headers.first_node
        while node.next_node:
            #Get difference between 2 headers. If there is a space greater than 3, add new block between
            header_diff = node.next_node.addr - (node.addr + node.size + 1)
            if header_diff > 3:
                new_addr = node.addr + node.size + 2 #New header addr is previous start (addr) + size + 2, 1 for footer, 1 more for next block after footer
                new_size = node.next_node.addr - new_addr - 2 #Difference between following node start, new start, and 2 more for header/footer
                new_node = Node(size=new_size, a=1, addr=new_addr)
                new_node.next_node = node.next_node
                node.next_node = new_node
            node = node.next_node

        #Step 5 - fill in space after last node
        last_header = self.headers.first_node
        while last_header.next_node:
            last_header = last_header.next_node
        
        #Get remaining space
        heap_max_addr = list(self.heap.keys())[-1]
        if heap_max_addr - last_header.addr + last_header.size + 1 >=3:
            new_addr = last_header.addr + last_header.size + 2 #New header addr is last header address + size + 2 (footer + 1 past footer)
            new_size = heap_max_addr - new_addr - 1 #Want to go until 998 for payload, so size is max heap address - new header address - 1 for footer
            self.headers.add_node(size=new_size, a=1, addr=new_addr)

        #Step 6 - add footer nodes in afterwords
        last_header = last_header.next_node
        matching_footer_addr = last_header.addr + last_header.size + 1
        matching_footer_size = last_header.size
        self.footers.add_node(size=matching_footer_size, a=last_header.a, addr=matching_footer_addr, force_start=True)
        previous_header_checked = last_header

        #Continue adding footers in reverse order of header list until done with starting header node
        while previous_header_checked != self.headers.first_node:
            last_header = self.headers.first_node
            while last_header.next_node != previous_header_checked:
                last_header = last_header.next_node

            #Add in footer
            matching_footer_addr = last_header.addr + last_header.size + 1
            matching_footer_size = last_header.size
            self.footers.add_node(size=matching_footer_size, a=last_header.a, addr=matching_footer_addr)

            #Increment previous_header_checked down an element in the single linked list
            previous_header_checked = last_header

        print('Headers:')
        node = self.headers.first_node
        while node:
            print(node.addr, node.size, node.a)
            node = node.next_node

        print('\nFooters:')
        node = self.footers.first_node
        while node:
            print(node.addr, node.size, node.a)
            node = node.next_node


if __name__ == '__main__':
    pass