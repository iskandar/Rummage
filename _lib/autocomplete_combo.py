import wx
import sys


class AutoCompleteCombo(object):
    def setup(self, choices, load_last=False):
        self.update_semaphore = False
        self.popped = False
        self.choices = None
        if sys.platform != "darwin":
            self.Bind(wx.EVT_KEY_UP, self.on_combo_key)
            self.Bind(wx.EVT_TEXT_ENTER, self.on_enter_key)
            self.Bind(wx.EVT_TEXT, self.on_text_change)
            self.Bind(wx.EVT_CHAR, self.on_char)
            self.Bind(wx.EVT_COMBOBOX, self.on_selected)
            self.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.on_popup)
            self.Bind(wx.EVT_COMBOBOX_CLOSEUP, self.on_dismiss)
        self.update_choices(choices, load_last)

    def tab_forward(self):
        self.Navigate(wx.NavigationKeyEvent.FromTab|wx.NavigationKeyEvent.IsForward)

    def tab_back(self):
        self.Navigate(wx.NavigationKeyEvent.FromTab|wx.NavigationKeyEvent.IsBackward)

    def update_choices(self, items, load_last=False):
        self.choices = items
        value = self.GetValue()
        self.Clear()
        self.AppendItems(items)
        if load_last:
            idx = self.GetCount() - 1
            if idx != -1:
                self.SetSelection(0)
        else:
            self.update_semaphore = True
            self.SetValue(value)

    def on_popup(self, event):
        self.popped = True
        event.Skip()

    def on_dismiss(self, event):
        self.popped = False
        event.Skip()

    def on_selected(self, event):
        self.update_semaphore = True
        event.Skip()

    def on_enter_key(self, event):
        self.tab_forward()
        event.Skip()

    def on_char(self, event):
        key = event.GetKeyCode()
        if key in [wx.WXK_DELETE, wx.WXK_BACK]:
            self.update_semaphore = True
        elif key == wx.WXK_TAB:
            if event.ShiftDown():
                self.tab_back()
            else:
                self.tab_forward()
        event.Skip()

    def on_combo_key(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_DOWN and not self.popped:
            self.Popup()
        event.Skip()

    def on_text_change(self, event):
        found = False
        if not self.update_semaphore:
            value = event.GetString()
            for choice in self.choices :
                if choice.startswith(value):
                    self.update_semaphore = True
                    self.SetValue(choice)
                    self.SetInsertionPoint(len(value))
                    self.SetMark(len(value), len(choice))
                    found = True
                    break
        else:
            self.update_semaphore = False
        if not found:
            event.Skip()