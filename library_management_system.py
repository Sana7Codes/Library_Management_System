class WaitlistQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, user):
        self.queue.append(user)

    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def is_empty(self):
        return len(self.queue) == 0


class LinkedList:
    def __init__(self):
        self.head = None

    def add(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def remove(self):
        if self.head is None:
            return None
        removed_node = self.head
        self.head = self.head.next
        return removed_node.data

    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next


class UndoStack:
    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        if not self.stack:
            return None
        return self.stack.pop()


class TreeNode:
    def __init__(self, category):
        self.category = category
        self.children = {}

    def add_child(self, child_node):
        if child_node.category not in self.children:
            self.children[child_node.category] = child_node


class Graph:
    def __init__(self):
        self.graph = {}

    def add_edge(self, node1, node2):
        if node1 not in self.graph:
            self.graph[node1] = []
        if node2 not in self.graph:
             self.graph[node2] = []
        if node2 not in self.graph[node1]:
            self.graph[node1].append(node2)
        if node1 not in self.graph[node2]:
            self.graph[node2].append(node1)

class Book:
    def __init__(self, title, author, genre):
        self.title = title
        self.author = author
        self.genre = genre
        self.available = True
        self.waitlist = WaitlistQueue()


class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.borrowed_books = LinkedList()


class LibraryManager:
    def __init__(self):
        self.books = {}
        self.users = {}
        self.undo_stack = UndoStack()
        self.genre_tree = TreeNode("Books")
        self.author_graph = Graph()

    def add_book(self, title, author, genre):
        if title in self.books:
            print(f"Book '{title}' already exists.")
            return

        new_book = Book(title, author, genre)
        self.books[title] = new_book

        if genre not in self.genre_tree.children:
            self.genre_tree.add_child(TreeNode(genre))
        self.author_graph.add_edge(author, genre)

    def add_user(self, user_id, name):
        if user_id in self.users:
            print(f"User with ID '{user_id}' already exists.")
            return

        new_user = User(user_id, name)
        self.users[user_id] = new_user

    def borrow_book(self, user_id, title):
        book = self.books.get(title)
        user = self.users.get(user_id)

        if not book:
            print(f"Book '{title}' not found.")
            return
        if not user:
            print(f"User with ID '{user_id}' not found.")
            return

        if book.available:
            book.available = False
            user.borrowed_books.add(book)
            print(f"Book '{title}' borrowed by user '{user.name}'.")
        else:
            book.waitlist.enqueue(user)
            print(f"Book '{title}' is unavailable. User '{user.name}' added to waitlist.")

    def return_book(self, user_id, title):
        book = self.books.get(title)
        user = self.users.get(user_id)

        if not book or not user:
            print(f"Book '{title}' or user with ID '{user_id}' not found.")
            return

        removed_book = user.borrowed_books.remove()
        if removed_book:
            book.available = True
            self.undo_stack.push((user, book))
            print(f"Book '{title}' returned by user '{user.name}'.")

            if not book.waitlist.is_empty():
                next_user = book.waitlist.dequeue()
                if next_user and next_user.user_id in self.users:
                    self.borrow_book(next_user.user_id, title)
        else:
            print(f"User '{user.name}' has no borrowed books to return.")

    def undo_return(self):
        action = self.undo_stack.pop()
        if action:
            user, book = action
            if not book.available:
                print(f"Book '{book.title}' is already borrowed by another user.")
            else:
                book.available = False
                user.borrowed_books.add(book)
                print(f"Undo return: Book '{book.title}' re-borrowed by user '{user.name}'.")
        else:
            print("No action to undo.")
            
    def recommend_books(self, user_id):
        user = self.users.get(user_id)
        if not user:
            print(f"User with ID '{user_id}' not found.")
            return []
        recommendations =[]
        seen_genres = set()
        for borrowed_book in user.borrowed_books:
            genre = borrowed_book.genre
            if genre not in seen_genres:
                seen_genres.add(genre)
                recommendations.extend(self.author_graph.graph.get(genre, []))

        
        recommendations = [rec for rec in recommendations if rec != borrowed_book.genre]
        return list(set(recommendations))
