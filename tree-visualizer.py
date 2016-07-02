#!/usr/bin/python

import sys
from math import ceil, floor
from way_cooler_client.way_cooler import *

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
        self.pack(fill=tk.BOTH, expand=True)
        self.make_root()

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
        parent_name = parent.name
        container_node = Node(text, [])
        parent.children.append(container_node)
        name = self.insert(parent_name, len(parent.children), text=text,
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

def update_app(tree):
    """Takes a json representation of the tree and lays it out
    in the view"""
    global app
    def recurse_add_container(json, parent):
        if not json:
            return
        if isinstance(json, list):
            for child in json:
                recurse_add_container(child, parent)
        elif isinstance(json, dict):
            for key in json.keys():
                if key.startswith("Output"):
                    parent = app.add_output()
                elif key.startswith("Workspace"):
                    # need to update json from rust side
                    parent = app.add_workspace(parent, key.split()[-1])
                elif key.startswith("Container"):
                    # need to update json from rust side
                    parent = app.add_container(parent, key.split()[-1])
                else:
                    app.add_view(parent, json[key])
                    continue
                recurse_add_container(json[key], parent)
        else:
            app.add_view(parent, json)
    recurse_add_container(tree, app._root)

def clear():
    global app;
    app.destroy()
    app = Application(master=root)

running = True
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = SOCKET_ROOT_PATH
    if path is None:
        print("Please either run from within Way-Cooler, or specify the socket",
        "path name as the first arg to this program")
        sys.exit(1)
wm = WayCooler(path)
tree = None
def update():
    global tree
    from time import sleep
    while running:
        sleep(.1)
        buffer = wm.tree_layout
        if buffer == tree:
            continue
        print("got: {}".format(buffer))
        tree = buffer
        clear()
        update_app(tree['Root'])
        app.configure(height=app.node_count() * 20)

from threading import Thread

update_thread = Thread(target=update).start()
app.mainloop()
running = False
