import math
from LinkedList import LinkedList, Node

class ExplicitFreeList:
    """Class to use Explicit Free List for memory allocation simulator

    Attributes:
        self.headers (LinkedList): LinkedList of header nodes
        self.footers (LinkedList): LinkedList of footer nodes
        self.heap_size (int): Keeps track of heap size
        self.bytes_per_word (int): Used for double world alignment and calculating payload size
        self.used_blocks (dict): Used for free method

    """

    def __init__(self):
        """Performs setup for Explicit Free List
        Sets bytes per word and initial heap size, as well as headers and footers list

        Args:
            None

        Returns:
            None
        """

        self.bytes_per_word = 4
        self.heap_size = 1000
        #This feels like cheating, but I think it is necessary. In an explicit list, only free blocks are tracked. 
        #So when a user passes in some arbitrary pointer to free a block, how do we know anything about the block, since we only track free blocks?
        self.used_blocks = {}
            
        self.headers = LinkedList()
        self.footers = LinkedList()
        


    def first_fit(self, size, ptr):
        """First fit for explicit list
        Starts by getting payload size from number of bytes (size)
        Next, while the heap is expandable, goes through each block until one is found that can be allocated
        Coalesce

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
                            
                            self.used_blocks[ptr] = [word, payload_words]

                            #Coalesce and return node addr
                            self.coalesce(word, payload_words, header_node)
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
                self.headers.add_node(size=new_size, a=1, addr=new_addr, prev=True)

            #Coalesce
            #self.coalesce()

        return -1


    def best_fit(self, size, ptr):
        """Best fit for explicit list
        Starts by getting payload size from number of bytes (size)
        Next, while the heap is expandable, goes through each available free block. 
        Stores each free block into a dict with the related node, then after, sorts these based on which one has the least space leftover after fill.
        Coalesce

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
                            best_fit_addr[word] = [(header_node.size) - (payload_words), header_node]
                            break
                            

                header_node = header_node.next_node
            
            if len(best_fit_addr.keys()) > 0:
                sorted_fits = sorted(best_fit_addr.items(), key=lambda e: e[1][0])

                best_fit_word = sorted_fits[0][0]
                #Create data to store in header footer - first 31 bits are size, LSB is to indicate free or not
                self.used_blocks[ptr] = [best_fit_word, payload_words]

                #Coalesce and return node addr
                self.coalesce(best_fit_word, payload_words, sorted_fits[0][1][1])
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
                    self.headers.add_node(size=new_size, a=1, addr=new_addr, prev=True)

        return -1



    def myfree(self, ptr):
        """Frees a pointer from list of used blocks

        Args:
            ptr (int): Block to free
            
        Returns:
            1 if successfully free'd
        """

        assert ptr in self.used_blocks
        self.headers.add_node(size=self.used_blocks[ptr][1], a=1, addr=self.used_blocks[ptr][0], prev=True)
            
        #Create new free block here, then coalesce
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



    def coalesce(self, new_block_start=None, new_block_size=None, header_to_resize=None):
        """Coalesces implicit list. Definitely not optimized, but it works as intended.
        Step 1: Replace free block that was allocated in
        Step 2: Combine adjacted free blocks
        Step 3, sbrk down empty space after last used node
        Step 4, add footers in to correspond

        Args:
            new_block_start (int): Start of used block that was just allocated, not required
            new_block_size (int): Size of used block that was just allocated, not required
            header_to_resize (Node): Free block that was allocated in, not required
            
        Returns:
            None
        """

        if not self.headers.first_node:
            self.headers.add_node(addr=0, a=1, size=self.heap_size-2)
            return 

        #Step 1: Replace free block that was taken
        if new_block_size and new_block_start and header_to_resize:
            new_header_start = new_block_start + new_block_size + 2
            remaining_header_space = (header_to_resize.addr + header_to_resize.size + 1) - new_header_start - 1
            if remaining_header_space >= 2:
                header_to_resize.addr = new_header_start
                header_to_resize.size = remaining_header_space

        #Step 2: Check if any free blocks directly adjacent, combine into one block
        nodes_to_change = True
        nodes = []
        node = self.headers.first_node
        while node:
            nodes.append(node)
            node = node.next_node

        while nodes_to_change:
            #Create list of current nodes
            nodes_to_change = False
            

            if len(nodes) == 1: break
            for x, node1 in enumerate(nodes[:-1]):
                for node2 in nodes[x+1:]:
                    #Combine
                    if (node1.addr + node1.size + 2 == node2.addr):
                        start_address = node1.addr
                        size = node1.size + node2.size + 2
                        node2.addr = start_address
                        node2.size = size
                        node2.prev_node = node1.prev_node
                        nodes.remove(node1)
                        nodes_to_change = True

                    elif (node2.addr + node2.size + 2 == node1.addr):
                        start_address = node2.addr
                        size = node1.size + node2.size + 2
                        node1.addr = start_address
                        node1.size = size
                        node1.prev_node = node2.prev_node
                        nodes.remove(node2)
                        nodes_to_change = True

        self.headers.first_node = None
        self.headers.first_node = nodes[0]
        self.headers.first_node.next_node = None
        self.headers.first_node.prev_node = None
        for node in nodes[1:]:
            self.headers.add_node(addr=node.addr, a=1, size=node.size, prev=True)
                

        #Step 3 - sbrk down space after last node
        last_header = self.headers.first_node
        while last_header.next_node:
            last_header = last_header.next_node
        
        #If max addr doesn't == addr of last (or first) footer, sbrk down
        heap_max_addr = self.heap_size - 1
        if heap_max_addr > (last_header.addr + last_header.size + 1):
            self.mysbrk(-(heap_max_addr - (last_header.addr + last_header.size + 1)))

        #Step 4 - add footer nodes in afterwords
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
        


if __name__ == '__main__':
    pass