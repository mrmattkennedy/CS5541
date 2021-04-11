class LinkedList:
    """LinkedList class, used for headers and footers in free lists.

    Attributes:
        self.first_node (Node): Start is None, reference to start of linked list.

    """

    def __init__(self):
        """Creates new LinkedList, with nothing as the first item.

        Args:
            None

        Returns:
            None
        """

        self.first_node = None

    def add_node(self, size, a, addr, ptr=None, force_start=False, prev=False):
        """Adds a node to the LinkedList, using size, a (free or not), and addr to keep track of double word alignment
        User can force node to be inserted at start of list.
        If not, new node is inserted at end of list. If prev is specified, link to prev node is added as well

        Args:
            size (int): Size of node
            a (int): 0 for not free, 1 for free
            addr (int): Address of node
            ptr (int): Pointer associated with node, can be None
            force_start (boolean): Inserted as first node in list, thus deleting list. Default is False
            prev (boolean): Whether a link to prior node should be added as well (for Explicit list). Default is False
            
        Returns:
            The new node
        """

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



class Node:
    """Node class, used for LinkedList.

    Attributes:
        self.size (int): Size of Node
        self.a (int): 0 for used, 1 for free
        self.next_node (Node): Reference to next Node in LinkedList. Default is None.
        self.prev_node (Node): Reference to previous Node in LinkedList. Default is None, only used by explicit lists.
        self.addr (int): Address of Node
        self.ptr (int): Pointer associated with Node, default is None.

    """

    def __init__(self, size, a, addr, ptr=None):
        """Creates new Node to be used in LinkedList.

        Args:
            size (int): Size of Node
            a (int): 0 for used, 1 for free
            addr (int): Address of Node
            ptr (int): Pointer associated with Node, default is None.

        Returns:
            None
        """

        self.size = size
        self.a = a
        self.next_node = None
        self.prev_node = None
        self.addr = addr
        self.ptr = ptr



if __name__ == '__main__':
    pass