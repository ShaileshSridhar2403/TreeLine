#!/usr/bin/env python3

#******************************************************************************
# treenode.py, provides a class to store tree node data
#
# TreeLine, an information storage program
# Copyright (C) 2017, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#******************************************************************************

import uuid
import treespot


class TreeNode:
    """Class to store tree node data and the tree's linked structure.

    Stores a data dict, lists of children and a format name string.
    Provides methods to get info on the structure and the data.
    """
    def __init__(self, formatRef, fileData=None):
        """Initialize a tree node.

        Arguments:
            formatRef -- a ref to this node's format info
            fileData -- a dict with uid, data, child refs & parent refs
        """
        self.formatRef = formatRef
        if not fileData:
            fileData = {}
        self.uId = fileData.get('uid', uuid.uuid1().hex)
        self.data = fileData.get('data', {})
        self.tmpChildRefs = fileData.get('children', [])
        self.childList = []
        self.spotRefs = set()

    def assignRefs(self, nodeDict):
        """Add actual refs to child nodes.

        Arguments:
            nodeDict -- all nodes stored by uid
        """
        self.childList = [nodeDict[uid] for uid in self.tmpChildRefs]
        self.tmpChildRefs = []

    def generateSpots(self, parentSpot):
        """Recursively generate spot references for this branch.

        Arguments:
            parentSpot -- the parent spot reference
        """
        spot = treespot.TreeSpot(self, parentSpot)
        self.spotRefs.add(spot)
        for child in self.childList:
            child.generateSpots(spot)

    def parents(self):
        """Return a set of parent nodes for this node.

        None is included for top level nodes.
        """
        return {spot.parentSpot.nodeRef if spot.parentSpot else None
                for spot in self.spotRefs}

    def fileData(self):
        """Return the file data dict for this node.
        """
        children = [node.uId for node in self.childList]
        fileData = {'format': self.formatRef.name, 'uid': self.uId,
                    'data': self.data, 'children': children}
        return fileData

    def title(self):
        """Return the title string for this node.
        """
        return self.formatRef.formatTitle(self)

    def setTitle(self, title):
        """Change this node's data based on a new title string.

        Return True if successfully changed.
        """
        if title == self.title():
            return False
        return self.formatRef.extractTitleData(title, self.data)

    def output(self, plainText=False, keepBlanks=False):
        """Return a list of formatted text output lines.

        Arguments:
            plainText -- if True, remove HTML markup from fields and formats
            keepBlanks -- if True, keep lines with empty fields
        """
        return self.formatRef.formatOutput(self, plainText, keepBlanks)