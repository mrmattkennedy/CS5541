import math
from LinkedList import LinkedList, Node

class ExplicitFreeList:
    def __init__(self):
        self.bytes_per_word = 4
        self.payload_string = '11111111111111111111111111111111'
        self.heap_size = 1000
            
        self.headers = LinkedList()
        self.footers = LinkedList()
        


    def first_fit(self, size, ptr):
        payload_words = int(size / self.bytes_per_word) 
        if math.ceil(size % self.bytes_per_word) != 0:
            payload_words += 1

        heap_expandable = True
        while heap_expandable: 
            header_node = self.headers.first_node
            while header_node:

                #If the node is free, and the size of the block is >= the size requested by user + 2 words for header/footer blocks
                if header_node.a == 1 and header_node.size >= payload_words:
                    #Check each available word in block for first aligned word to start
                    for word in range(header_node.addr, header_node.addr+header_node.size-payload_words+1, 1):
                        if ((word+1)*self.bytes_per_word) % 8 == 0:

                            #Create data to store in header footer - first 31 bits are size, LSB is to indicate free or not
                            new_header = self.headers.add_node(size=payload_words, a=0, addr=word, ptr=ptr)
                            new_footer = self.footers.add_node(size=payload_words, a=0, addr=word+payload_words+1, ptr=ptr)

                            #Coalesce and return node addr
                            self.coalesce()
                            return ptr

                header_node = header_node.next_node
            
            #Get last header in list
            last_header = self.headers.first_node
            while last_header.next_node:
                last_header = last_header.next_node

            #If last header is free space, add only necessary amount with current header size
            if last_header.a == 1:
                heap_expandable = self.mysbrk(payload_words - last_header.size + 3)
            #If not free space, add whatever is needed
            else:
                heap_expandable = self.mysbrk(payload_words + 3)

            if heap_expandable:
                new_addr = last_header.addr + last_header.size + 2
                new_size = self.heap_size - new_addr - 2 #-2 for header/footer space
                self.headers.add_node(size=new_size, a=1, addr=new_addr)

            #Coalesce
            #self.coalesce()

        return -1


    def best_fit(self, size, ptr):
        payload_words = int(size / self.bytes_per_word) 
        if math.ceil(size % self.bytes_per_word) != 0:
            payload_words += 1

        heap_expandable = True
        
        while heap_expandable: 
            best_fit_addr = {}
            header_node = self.headers.first_node
            while header_node:

                #If the node is free, and the size of the block is >= the size requested by user + 2 words for header/footer blocks
                if header_node.a == 1 and header_node.size >= payload_words:
                    #Check each available word in block for first aligned word to start
                    for word in range(header_node.addr, header_node.addr+header_node.size-payload_words+1, 1):
                        if ((word+1)*self.bytes_per_word) % 8 == 0:
                            best_fit_addr[word] = (header_node.size) - (payload_words)
                            break
                            

                header_node = header_node.next_node
            
            if len(best_fit_addr.keys()) > 0:
                best_fit_word = min(best_fit_addr, key=best_fit_addr.get)

                #Create data to store in header footer - first 31 bits are size, LSB is to indicate free or not
                new_header = self.headers.add_node(size=payload_words, a=0, addr=best_fit_word, ptr=ptr)
                new_footer = self.footers.add_node(size=payload_words, a=0, addr=best_fit_word+payload_words+1, ptr=ptr)

                #Coalesce and return node addr
                self.coalesce()
                return ptr


            #Get last header in list
            last_header = self.headers.first_node
            while last_header.next_node:
                last_header = last_header.next_node

            #If last header is free space, add only necessary amount with current header size
            if last_header.a == 1:
                heap_expandable = self.mysbrk(payload_words - last_header.size + 3)
                if heap_expandable:
                    last_header.size = self.heap_size - (last_header.addr + 2)
            #If not free space, add whatever is needed
            else:
                heap_expandable = self.mysbrk(payload_words + 3)
                if heap_expandable:
                    new_addr = last_header.addr + last_header.size + 2
                    new_size = self.heap_size - new_addr - 2 #-2 for header/footer space
                    self.headers.add_node(size=new_size, a=1, addr=new_addr)
            

            #Coalesce
            #self.coalesce()

        return -1



    def myfree(self, ptr):
        node = self.headers.first_node
        if node.ptr != ptr:
            while node.next_node and node.next_node.ptr != ptr:
                node = node.next_node
            
            if node.next_node:
                node.next_node = node.next_node.next_node
            else:
                node = None
        else:
            self.headers.first_node = self.headers.first_node.next_node
        
        self.coalesce()
        return 1


    def mysbrk(self, size):
        if self.heap_size + size <= 100000:
            self.heap_size += size
            return True
        return False



    def coalesce(self):
        if not self.headers.first_node:
            self.headers.add_node(addr=0, a=1, size=self.heap_size-2)
            return 

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

        #Step 3 - organize linked list by address. Using a list to cheat for this singly linked list sort
        nodes = []
        node = self.headers.first_node
        while node:
            nodes.append(node)
            node = node.next_node
        
        #Sort, then add back in
        sorted_nodes = sorted(nodes, key=lambda x: x.addr, reverse=False)
        self.headers.first_node = sorted_nodes[0]
        current_node = self.headers.first_node
        for node in sorted_nodes[1:]:
            current_node.next_node = node
            current_node = node
        
        current_node.next_node = None

        #Step 4 - fill in empty space before start if possible
        if self.headers.first_node.addr >= 3:
            old_head = self.headers.first_node
            new_size = old_head.addr - 2
            self.headers.add_node(size=new_size, a=1, addr=0, force_start=True)
            self.headers.first_node.next_node = old_head


        #Step 5 - fill in space between all nodes after first and before last
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

        '''
        #Step 6 - fill in space after last node
        last_header = self.headers.first_node
        while last_header.next_node:
            last_header = last_header.next_node
        
        #Get remaining space
        heap_max_addr = self.heap_size - 1
        if heap_max_addr - (last_header.addr + last_header.size + 1) >=3:
            new_addr = last_header.addr + last_header.size + 2 #New header addr is last header address + size + 2 (footer + 1 past footer)
            new_size = heap_max_addr - new_addr - 1 #Want to go until 998 for payload, so size is max heap address - new header address - 1 for footer
            self.headers.add_node(size=new_size, a=1, addr=new_addr)
        '''

        #Step 6 - sbrk down space after last node
        last_header = self.headers.first_node
        while last_header.next_node:
            last_header = last_header.next_node
        
        #If max addr doesn't == addr of last (or first) footer, sbrk down
        heap_max_addr = self.heap_size - 1
        if heap_max_addr > (last_header.addr + last_header.size + 1):
            self.mysbrk(-(heap_max_addr - (last_header.addr + last_header.size + 1)))

        #Step 7 - add footer nodes in afterwords
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

        print("Heap size: {}".format(self.heap_size))
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
        print('\n')
        


if __name__ == '__main__':
    pass