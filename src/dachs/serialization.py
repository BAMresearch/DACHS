# -*- coding: utf-8 -*-
# serialization.py

"""
Utility function to serialize data and meta classes for export, to a HDF5 file, for example.
"""

__author__ = "Ingo Breßler"
__contact__ = "dev@ingobressler.net"
__license__ = "GPLv3+"
__date__ = "2023/02/07"
__status__ = "beta"

import pprint
from pathlib import Path, PurePosixPath

import graphviz


def dumpKV(objlst: object, prefix: PurePosixPath = None, lvl: int = 0):
    """Serializes the given hierarchical DACHS structure as key-value pairs (a dict).

    :param objlst: A hierarchical instance for traversal.
    :param prefix: Optional, a word to prepend to all generated keys, a top-level name.
        It is replaced by the *ID* attribute if available.
    :param lvl: The current level of invocation, tracks the recursion depth for debugging.
    """
    # handle unnamed lists by default, catch single objects here
    if type(objlst) not in (list, tuple):
        prefix = getattr(objlst, "ID", prefix)
        objlst = (objlst,)
    pathlst = {}
    # indent = "".join(["  " for _ in range(lvl)])
    for idx, obj in enumerate(objlst):
        idx = getattr(obj, "ID", idx)
        # print(indent, "=>", idx, obj)
        subpath = PurePosixPath(prefix)
        if len(objlst) > 1:  # we have more than one item
            subpath /= str(idx)
        if hasattr(obj, "_storeKeys"):
            for mem in getattr(obj, "_storeKeys", ()):
                # print(indent, "->", mem, len(objlst))
                items = {(subpath / m): v for m, v in dumpKV(getattr(obj, mem), mem, lvl + 1).items()}
                pathlst.update(items)
        else:
            pathlst.update({subpath: obj})
    return pathlst


def buildGraph2(obj: object, path: PurePosixPath = None, lvl: int = 0, dbg: bool = False):
    indent = "".join(["  " for _ in range(lvl)])
    if dbg:
        print(indent, f"{obj=}")
        print(indent, f"path called:  '{path}'")
    if not path:
        path = getattr(obj, "ID", None)
    path = PurePosixPath(path) if path else PurePosixPath("")
    if dbg:
        print(indent, f"path from id: '{path}', {type(obj)}")

    graph = graphviz.Digraph(str(path), format="svg", graph_attr=dict(rankdir="LR"))
    nodeLbl = f"{path.name}({type(obj).__name__})"
    nodeName = f"{path}"
    if dbg:
        print(indent, f"{nodeName=}, {nodeLbl=}")
    graph.node(nodeName, label=nodeLbl)

    # find any children to traverse
    children = [(storeKey, getattr(obj, storeKey)) for storeKey in getattr(obj, "_storeKeys", [])]
    if not len(children) and type(obj) in (list, tuple):
        children = list(enumerate(obj))
    # translate children path names from type names to their stored ID
    children = [(getattr(child, "ID", num), child) for num, child in children]
    if dbg:
        print(f"{children=}")
    # if not len(children):  # or lvl > 1:
    # on a leaf: return the object itself
    #    return {path: obj}, graph
    pathlst = {path: obj}  # TODO: for McHDF storage, filter the resulting list to remove dachs types
    for name, child in children:
        if dbg:
            print(indent, "=>", name)
        subpath = path / str(name)
        items, subgraph = buildGraph2(child, subpath, lvl + 1, dbg=dbg)
        if dbg:
            print(indent, "->", items)
        pathlst.update(items)
        graph.subgraph(subgraph)
        if dbg:
            print(
                indent,
                f"  edge: '{nodeName}' -> '{subpath}'",
            )
        graph.edge(nodeName, str(subpath))
    return pathlst, graph


def graphKV(paths):
    docsPath = Path("dist/docs/reference/autosummary")
    pprint.pprint(paths, width=120)
    nodes = {
        PurePosixPath(*path.parts[: i + 1]): type(paths[PurePosixPath(*path.parts[: i + 1])])
        for path in paths
        for i in range(len(path.parts))
    }
    edges = {
        (PurePosixPath(*path.parts[: i + 1]), PurePosixPath(*path.parts[: i + 2]))
        for path in paths
        for i in range(len(path.parts) - 1)
    }
    graph = graphviz.Digraph("test", format="svg", graph_attr=dict(rankdir="LR"))
    for nodepath, nodetype in nodes.items():
        print("node", nodepath, type(nodepath), nodetype)
        lbl = f"{nodepath.name}({nodetype.__name__})"
        url, color = "", ""
        if nodetype.__module__.startswith("dachs."):
            url = docsPath / (".".join((nodetype.__module__, nodetype.__name__)) + ".html")
            color = "blue"
        graph.node(str(nodepath), label=lbl, URL=str(url), fontcolor=color)
    for tail, head in edges:
        graph.edge(str(tail), str(head))
    # print("NODES", nodes)
    # print("EDGES", edges)
    # print("Types found in 2nd serialized data:", {type(value) for path, value in paths.items()})
    # path = list(paths.keys())[-5]
    # print("    ", path.parts)
    # nodesAll = {}
    # edgesAll = set()
    # for lvl, (tail, head) in enumerate(zip(iter(path.parts[:-1]), iter(path.parts[1:]))):
    #     partialPath = PurePosixPath(*path.parts[:lvl+2])
    #     print("      ", (tail, head), type(paths[partialPath]))
    #     graph.edge(tail, head)
    # to avoid duplicate calls to edge() or node():
    #       make a dict mapping node names to labels (or objects)
    #       and make a set with node name pairs (tuples) for each edge
    #       in a final step, build the graph from that structures
    graph.render(graph.name, cleanup=True)


def buildGraph(objlst: object, prefix: PurePosixPath = None, lvl: int = 0):
    """Renders the given hierarchical DACHS structure to a SVG."""
    # handle unnamed lists by default, catch single objects here
    if type(objlst) not in (list, tuple):
        prefix = getattr(objlst, "ID", prefix)
        objlst = (objlst,)
    nodes = []
    digraph = graphviz.Digraph(prefix, format="svg", graph_attr=dict(rankdir="LR"))
    indent = "".join(["  " for _ in range(lvl)])
    for idx, obj in enumerate(objlst):
        idx = getattr(obj, "ID", idx)
        print(indent, f"=> idx: '{idx}', type: '{type(obj)}', obj:", obj)
        subpath = PurePosixPath(prefix)
        if len(objlst) > 1:  # we have more than one item
            subpath /= str(idx)
        lbl = f"{subpath.name}({type(obj).__name__})"
        nodes.append(f"{str(subpath)}")
        print(indent, "name:", nodes[-1], f"{lbl=}")
        digraph.node(nodes[-1], label=lbl)
        if hasattr(obj, "_storeKeys"):
            if lvl > 1:
                continue
            for mem in getattr(obj, "_storeKeys", ()):
                print(indent, "->", mem, len(objlst), subpath)  # should be combined below: subpath/mem
                subgraph, subnodes = buildGraph(getattr(obj, mem), mem, lvl + 1)
                digraph.subgraph(subgraph)
                for n in subnodes:
                    digraph.edge(nodes[-1], n)
        else:
            pass
        # pathlst.update({subpath: obj})
    return digraph, nodes
