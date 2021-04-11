import math
from LinkedList import LinkedList, Node

class ImplicitFreeList:
    """Class to use Implicit Free List for memory allocation simulator

    Attributes:
        self.headers (LinkedList): LinkedList of header nodes
        self.footers (LinkedList): LinkedList of footer nodes
        self.heap_size (int): Keeps track of heap size
        self.bytes_per_word (int): Used for double world alignment and calculating payload size

    """

    def __init__(self):
        """Performs setup for Implicit Free List
        Sets bytes per word and initial heap size, as well as headers and footers list

        Args:
            None

        Returns:
            None
        """

        self.bytes_per_word = 4
        self.heap_size = 1000
            
        self.headers = LinkedList()
        self.footers = LinkedList()
        


    def first_fit(self, size, ptr):
        """First fit for implicit list
        Starts by getting payload size from number of bytes (size)
        Next, while the heap is expandable, goes through each block until one is found that can be allocated
        Creates new header/footer, coalesce.

        If no block found, sbrk and redo

        Args:
            size (int): Size in bytes of block to create
            ptr (int): ptr to new block
            
        Returns:
            ptr if successfully allocated
            -1 if not successfull (heap is too full)
        """

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

            #If last header is free space, add only necessary amount with current header size, plus 1 extra for potential double word alignment
            if last_header.a == 1:
                heap_expandable = self.mysbrk(payload_words - last_header.size + 4)
            #If not free space, add whatever is needed
            else:
                heap_expandable = self.mysbrk(payload_words + 3)

            if heap_expandable:
                new_addr = last_header.addr + last_header.size + 2
                new_size = self.heap_size - new_addr - 2 #-2 for header/footer space
                self.headers.add_node(size=new_size, a=1, addr=new_addr)

        return -1



    def best_fit(self, size, ptr):
        """Best fit for implicit list
        Starts by getting payload size from number of bytes (size)
        Next, while the heap is expandable, goes through each available free block. 
        Stores each free block into a dict, then after, sorts these based on which one has the least space leftover after fill.
        Creates new header/footer, coalesce.

        If no block found, sbrk and redo

        Args:
            size (int): Size in bytes of block to create
            ptr (int): ptr to new block
            
        Returns:
            ptr if successfully allocated
            -1 if not successfull (heap is too full)
        """

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

        return -1



    def myfree(self, ptr):
        """Frees a pointer
        If the pointer is not the first node, then find it as the next node, then remove it from the list.
        If very first node, just set the first node as the next node after first node

        Args:
            ptr (int): Block to free
            
        Returns:
            1 if successfully free'd
        """

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
        """Changes size of heap

        Args:
            size (int): How much to change heap by (can be negative or positive)
            
        Returns:
            True if successfully changed heap size, false if not.
        """

        if self.heap_size + size <= 100000:
            self.heap_size += size
            return True
        return False



    def coalesce(self):
        """Coalesces implicit list. Definitely not optimized, but it works as intended.
        Step 1, find the first used block, remove all free blocks prior so we can just make 1 free block before this used block
        Step 2, delete all other free blocks
        Step 3, organize linked list of used blocks
        Step 4, fill in empty space at beginning of heap if possible with a free block
        Step 5, fill in empty space between each used node with a free block
        Step 6, sbrk down empty space after last used node
        Step 7, add footers in to correspond

        Args:
            None
            
        Returns:
            None
        """

        if not self.headers.first_node:
            self.headers.add_node(addr=0, a=1, size=self.heap_size-2)
            return 

        #Step 1 - remove all first blocks in header until first block is full block
        while self.headers.first_node and self.headers.first_node.a == 1:
            self.headers.first_node = self.headers.first_node.next_node

        #Step 2 - go through each header, delete all free blocks
        node = self.headers.first_node
        if not node:
            self.headers.add_node(addr=0, a=1, size=self.heap_size-2)
        else:
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
            if self.headers.first_node.addr >= 2:
                old_head = self.headers.first_node
                new_size = old_head.addr - 2
                self.headers.add_node(size=new_size, a=1, addr=0, force_start=True)
                self.headers.first_node.next_node = old_head


            #Step 5 - fill in space between all nodes after first and before last
            node = self.headers.first_node
            while node.next_node:
                #Get difference between 2 headers. If there is a space greater than 3, add new block between
                header_diff = node.next_node.addr - (node.addr + node.size + 1)
                if header_diff >= 3:
                    new_addr = node.addr + node.size + 2 #New header addr is previous start (addr) + size + 2, 1 for footer, 1 more for next block after footer
                    new_size = node.next_node.addr - new_addr - 2 #Difference between following node start, new start, and 2 more for header/footer
                    new_node = Node(size=new_size, a=1, addr=new_addr)
                    new_node.next_node = node.next_node
                    node.next_node = new_node
                node = node.next_node

            #Step 6 - sbrk down space after last node
            last_header = self.headers.first_node
            while last_header.next_node:
                last_header = last_header.next_node
            
            #If max addr doesn't == addr of last (or first) footer, sbrk down
            heap_max_addr = self.heap_size - 1
            if heap_max_addr > (last_header.addr + last_header.size + 1):
                self.mysbrk(-(heap_max_addr - (last_header.addr + last_header.size + 1)))

        #Step 7 - add footer nodes in afterwords
        last_header = self.headers.first_node
        while last_header.next_node:
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



    def output(self):
        """Outputs heap to output.txt file

        Args:
            None
            
        Returns:
            None
        """

        with open("output.txt", "w") as f:
            for i in range(self.heap_size):
                line = '{}, '.format(i)
                node = self.headers.first_node
                while node:
                    if node.addr == i:
                        line += "0x{}{}".format(format(node.size,"07x"), node.a)
                        break
                    node = node.next_node
                
                node = self.footers.first_node
                while node:
                    if node.addr == i:
                        line += "0x{}{}".format(format(node.size,"07x"), node.a)
                        break
                    node = node.next_node
                
                f.write(line)
                f.write('\n')


#if trying to run as standalone, just pass
if __name__ == '__main__':
    pass