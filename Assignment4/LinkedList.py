class LinkedList:
    def __init__(self):
        self.first_node = None

    def add_node(self, size, a, addr, ptr=None, force_start=False, prev=False):
        new_node = Node(size, a, addr, ptr)

        if force_start:
            self.first_node = new_node
            return new_node
        else:
            try:
                last_node = self.first_node
                while last_node.next_node:
                    last_node = last_node.next_node
                last_node.next_node = new_node
                if prev:
                    new_node.prev_node = last_node
            except AttributeError:
                self.first_node = new_node

            return new_node

    def get_node(self, word):
        current_word_count = 0
        node = self.first_node
        while node:
            node_block_size = node.size
            if word <= current_word_count + node_block_size:
                return node

            current_word_count += node_block_size
            node = node.next_node


class Node:
    def __init__(self, size, a, addr, ptr=None):
        self.size = size
        self.a = a
        self.next_node = None
        self.prev_node = None
        self.addr = addr
        self.ptr = ptr

if __name__ == '__main__':
    pass