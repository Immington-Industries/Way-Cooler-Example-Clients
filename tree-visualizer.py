#!/usr/bin/python

from math import ceil, floor

try:
    # python 3
    import tkinter as tk
except ImportError:
    # python 2
    import Tkinter as tk

import ttk

class Node():
    def __init__(self, name, children):
        self.name = name
        self.children = children


class Application(ttk.Treeview):
    def __init__(self, master=None):
        ttk.Treeview.__init__(self, master)
        self.pack()
        self.make_root()
        # this is all test stuff, remove and replace with loop reading json


    def make_root(self):
        self.insert("", 0, "root", text="Root", open=True)
        self._root = Node("root", [])

    def add_output(self):
        next_output_num = len(self._root.children) + 1
        text = "Output %d" % next_output_num
        self.insert("root", next_output_num - 1, text, text=text, open=True)
        output_node = Node(text, [])
        self._root.children.append(output_node)
        return output_node

    def add_workspace(self, parent, workspace_name):
        text = "Workspace %s" % workspace_name
        # hacky, get the number from the parent
        parent_num = int(parent.name.split()[-1])
        workspace_node = Node(text, [])
        parent.children.append(workspace_node)
        self.insert("Output %d" % parent_num, len(parent.children), text, text=text,
                    open=True)
        return workspace_node

    def add_container(self, parent, layout_type):
        text = "Container w/ layout %s" % layout_type
        # hacky, get the name from the parent
        parent_name = parent.name.split()[-1]
        container_node = Node(text, [])
        parent.children.append(container_node)
        name = self.insert("Workspace %s" % parent_name, len(parent.children), text=text,
                    open=True)
        container_node.name = name
        return container_node

    def add_view(self, parent, view_name):
        text = "View: %s" % view_name
        parent_id = parent.name
        view_node = Node(text, None)
        parent.children.append(view_node)
        name = self.insert(parent_id, len(parent.children), text=text)
        view_node.name = name
        return view_node

    def node_count(self):
        def count_helper(node):
            if node.children is None:
                return 1
            return 1 + sum([count_helper(child) for child in node.children])
        return count_helper(self._root)



root = tk.Tk()
app = Application(master=root)
app.master.title("Tree visualization example")

def update_app():
    clear()
    output1 = app.add_output()
    output2 = app.add_output()
    app._workspace_1 = app.add_workspace(output1, "Web")
    app._workspace_2 = app.add_workspace(output2, "Work")
    app._container_1 = app.add_container(app._workspace_1, "horizontal")
    app._container_2 = app.add_container(app._workspace_1, "vertical")
    app._container_3 = app.add_container(app._workspace_2, "vertical")
    app.add_view(app._container_1, "Firefox")
    app.add_view(app._container_2, "Terminal")
    app.add_view(app._container_3, "Terminal")

def clear():
    global app;
    app.destroy()
    app = Application(master=root)

running = True
def update():
    from time import sleep
    while running:
        update_app()
        app.configure(height=app.node_count())
        sleep(1)

from threading import Thread

update_thread = Thread(target=update).start()
#app.after(100, update)
app.mainloop()
running = False
