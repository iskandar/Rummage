"""
Load Search Dialog

Licensed under MIT
Copyright (c) 2013 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import wx
import wx.lib.mixins.listctrl as listmix
from wx.lib.embeddedimage import PyEmbeddedImage

from _lib.settings import Settings

import _gui.gui as gui
from _gui.sorted_columns import up_arrow, down_arrow


glass = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAA"
    "CXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH3QcDFTYBJhcW1wAAAB1pVFh0Q29tbWVudAAA"
    "AAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAACBElEQVQ4y5XTT0jTYRgH8O/zvL8/UzZHtUNh"
    "0mooUw+BlxAjJJAlXSYInaRYpzoHgdi9Lt1LrBEEJRNzSH+lVgRRtzzEjGo2gjXdUpn7tfj9"
    "9ns6xGDQ/uD39LzvCx9enud9CQ0yd/eeBscx/YH9vycnoi5ahOoXM4lFOrJRmBGmiGZ6Ou2K"
    "taUb5oPYxfOzbYHbs3EPQ1a6enpHQv39crDLQyWrgtX372Btbz27EJs60wjgWqGUuql1h0e8"
    "PX1wSaNNy4XP68Xw6THpCByKxOfil5sCt5aeepj4krPvMMoOZNOqomA5SG9W4DOIOoMD0A0z"
    "1gjQAMDc2Q6LZsBRHlRB5IDAUCAQ8rs2RBlgo6O36Q1Uly+rwQWLI0IKQgogBoiRK/8bArt2"
    "rikwFT37i5lTnlKeWFOilAIrBV3XYZMukvsCBuZbNpGAc2bx2w/18zMp1xZTV1B/SqiufyR3"
    "J78ePBq60fYdJOYfHQC5DzWiIWbFrFQ1vbbmTyaTltK0k69SK6stgVqWFpcDROTPZDLWwkJi"
    "mYiGAEoPj0cGr09fddsC9ZmITp4qFgqvRQRE9OHN29SJ+nPVDkinP33v6wuHbNs+7rpudzB4"
    "zMhm11/+18SWH4boCjMXAaDqONOjo2PjewKev3iyQcx3RAQigopVfrwnAABCgwPXROSrQCCQ"
    "+7X9v8GZwN0bJSSNAAAAAElFTkSuQmCC")


class MixinSortPanel(listmix.ColumnSorterMixin, listmix.ListRowHighlighter):
    def setup(self, c):
        self.column_count = c
        self.itemDataMap = {}
        self.images = wx.ImageList(16, 16)
        self.glass = self.images.Add(glass.GetBitmap())
        self.sort_up = self.images.Add(up_arrow.GetBitmap())
        self.sort_down = self.images.Add(down_arrow.GetBitmap())
        self.SetImageList(self.images, wx.IMAGE_LIST_SMALL)
        listmix.ColumnSorterMixin.__init__(self, self.column_count)
        listmix.ListRowHighlighter.__init__(self, (0xEE, 0xEE, 0xEE))

    def reset_item_map(self):
        self.itemDataMap = {}

    def set_item_map(self, idx, *args):
        self.itemDataMap[idx] = tuple([a for a in args])

    def init_sort(self):
        self.SortListItems(col=0, ascending=1)
        self.RefreshRows()

    def GetListCtrl(self):
        return self

    def GetSortImages(self):
        return self.sort_down, self.sort_up

    def get_map_item(self, idx, col=0):
        return self.itemDataMap[idx][col]

    def OnSortOrderChanged(self):
        self.RefreshRows()


def extend(instance, extension):
    instance.__class__ = type(
        '%s_extended_with_%s' % (instance.__class__.__name__, extension.__name__),
        (instance.__class__, extension),
        {}
    )


def extend_list(l, c):
    extend(l, MixinSortPanel)
    l.setup(c)


class LoadSearchDialog(gui.LoadSearchDialog):
    def __init__(self, parent):
        super(LoadSearchDialog, self).__init__(parent)

        self.search = None
        self.is_regex = None

        self.reset_table()
        extend_list(self.m_search_list, 3)

        best = self.m_load_panel.GetBestSize()
        current = self.m_load_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

        self.load_searches()
        self.m_search_list.SetFocus()

    def load_searches(self):
        count = 0
        for x in Settings.get_search():
            search_type = "Regex" if x[2] else "Text"
            self.m_search_list.InsertStringItem(count, x[0])
            self.m_search_list.SetStringItem(count, 1, x[1])
            self.m_search_list.SetStringItem(count, 2, search_type)
            self.m_search_list.SetItemData(count, count)
            self.m_search_list.SetItemImage(count, 0)
            self.m_search_list.set_item_map(count, x[0], x[1], search_type)
            count += 1
        if count:
            self.column_resize(self.m_search_list, count)
        self.m_search_list.init_sort()

    def on_load(self, event):
        item = self.m_search_list.GetFirstSelected()
        if item == -1:
            return
        idx = self.m_search_list.GetItemData(item)
        self.search = self.m_search_list.get_map_item(idx, col=1)
        self.is_regex = self.m_search_list.get_map_item(idx, col=2) == "Regex"
        self.Close()

    def get_search(self):
        return self.search, self.is_regex

    def column_resize(self, obj, count, minimum=100):
        for i in range(0, count):
            obj.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            if obj.GetColumnWidth(i) < minimum:
                obj.SetColumnWidth(i, minimum)

    def reset_table(self):
        self.m_search_list.ClearAll()
        self.m_search_list.InsertColumn(0, "Name")
        self.m_search_list.InsertColumn(1, "Search")
        self.m_search_list.InsertColumn(2, "Type")
        wx.GetApp().Yield()

    def on_delete(self, event):
        item = self.m_search_list.GetFirstSelected()
        if item == -1:
            return
        idx = self.m_search_list.GetItemData(item)
        Settings.delete_search(idx)
        self.m_search_list.reset_item_map()
        self.reset_table()
        self.load_searches()

    def on_cancel(self, event):
        self.Close()
