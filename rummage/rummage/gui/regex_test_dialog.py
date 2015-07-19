"""
Regex Test dialog.

Licensed under MIT
Copyright (c) 2013 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import wx
import traceback
import sys
from . import gui
from ..rumcore import backrefs as bre
from ..localization import _
from .. import data


class RegexTestDialog(gui.RegexTestDialog):

    """Regex test dialog."""

    def __init__(self, parent, regex_support=False):
        """Init Regex Test Dialog object."""

        super(RegexTestDialog, self).__init__(None)
        self.SetIcon(data.get_image('rummage_64.png').GetIcon())
        self.parent = parent
        self.regex_support = regex_support

        # Ensure OS selectall shortcut works in text inputs
        self.set_keybindings(
            [(wx.ACCEL_CMD if sys.platform == "darwin" else wx.ACCEL_CTRL, ord('A'), self.on_textctrl_selectall)]
        )

        self.m_case_checkbox.SetValue(parent.m_case_checkbox.GetValue() if parent else False)
        self.m_dotmatch_checkbox.SetValue(parent.m_dotmatch_checkbox.GetValue() if parent else False)
        self.m_unicode_checkbox.SetValue(parent.m_unicode_checkbox.GetValue() if parent else False)
        if self.regex_support:
            self.m_bestmatch_checkbox.SetValue(parent.m_bestmatch_checkbox.GetValue() if parent else False)
            self.m_enhancematch_checkbox.SetValue(parent.m_enhancematch_checkbox.GetValue() if parent else False)
            self.m_word_checkbox.SetValue(parent.m_word_checkbox.GetValue() if parent else False)
            self.m_reverse_checkbox.SetValue(parent.m_reverse_checkbox.GetValue() if parent else False)
            self.m_bestmatch_checkbox.Show()
            self.m_enhancematch_checkbox.Show()
            self.m_word_checkbox.Show()
            self.m_reverse_checkbox.Show()
        self.regex_event_code = -1
        self.testing = False
        self.init_regex_timer()
        self.start_regex_timer()

        self.m_regex_text.SetValue(parent.m_searchfor_textbox.GetValue() if parent else "")
        self.m_replace_text.SetValue(parent.m_replace_textbox.GetValue() if parent else "")

        self.localize()

        # Ensure good sizing of frame
        best = self.m_tester_panel.GetBestSize()
        current = self.m_tester_panel.GetSize()
        offset = best[1] - current[1]
        mainframe = self.GetSize()
        self.SetSize(wx.Size(mainframe[0], mainframe[1] + offset + 15))
        self.SetMinSize(self.GetSize())

    def localize(self):
        """Localize dialog."""

        self.SetTitle(_("Regex Tester"))
        self.m_use_regex_button.SetLabel(_("Use"))
        self.m_close_button.SetLabel(_("Close"))
        self.m_case_checkbox.SetLabel(_("Search case-sensitive"))
        self.m_dotmatch_checkbox.SetLabel(_("Dot matches newline"))
        self.m_unicode_checkbox.SetLabel(_("Use Unicode properties"))
        self.m_bestmatch_checkbox.SetLabel(_("Best fuzzy match"))
        self.m_enhancematch_checkbox.SetLabel(_("Improve fuzzy fit"))
        self.m_word_checkbox.SetLabel(_("Unicode word break"))
        self.m_reverse_checkbox.SetLabel(_("Reverse match"))
        self.m_test_text.GetContainingSizer().GetStaticBox().SetLabel(_("Text"))
        self.m_test_replace_text.GetContainingSizer().GetStaticBox().SetLabel(_("Result"))
        main_sizer = self.m_tester_panel.GetSizer()
        main_sizer.GetItem(2).GetSizer().GetStaticBox().SetLabel(_("Regex Input"))
        self.m_find_label.SetLabel(_("Find"))
        self.m_replace_label.SetLabel(_("Replace"))
        self.Fit()

    def init_regex_timer(self):
        """Init the update Timer object]."""

        self.regex_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.regex_event, self.regex_timer)

    def regex_expand(self, m, replace):
        """Regex module expand."""

        return m.expand(replace)

    def start_regex_timer(self):
        """Start update timer."""

        if not self.regex_timer.IsRunning():
            self.regex_timer.Start(500)

    def stop_regex_timer(self):
        """Stop update timer."""

        if self.regex_timer.IsRunning():
            self.regex_timer.Stop()

    def regex_event(self, event):
        """Event for regex."""

        if self.regex_event_code == 0:
            if not self.testing:
                self.test_regex()
                self.regex_event_code -= 1
            else:
                event.Skip()
        else:
            if self.regex_event_code > 0:
                self.regex_event_code = 0
            event.Skip()

    def set_keybindings(self, keybindings):
        """Set keybindings for frame."""

        tbl = []
        for binding in keybindings:
            keyid = wx.NewId()
            self.Bind(wx.EVT_MENU, binding[2], id=keyid)
            tbl.append((binding[0], binding[1], keyid))

        if len(keybindings):
            self.SetAcceleratorTable(wx.AcceleratorTable(tbl))

    def on_textctrl_selectall(self, event):
        """Selectall content of textctrl."""

        text = self.FindFocus()
        if isinstance(text, wx.TextCtrl):
            text.SelectAll()
        event.Skip()

    def on_close(self, event):
        """Enable parent Rummage Dialog "Test Regex" button on close."""

        self.stop_regex_timer()
        event.Skip()

    def on_use(self, event):
        """Copy regex to parent Rummage Dialog search input."""

        self.parent.m_searchfor_textbox.SetValue(self.m_regex_text.GetValue())
        self.parent.m_replace_textbox.SetValue(self.m_replace_text.GetValue())
        self.parent.m_regex_search_checkbox.SetValue(True)
        self.parent.m_unicode_checkbox.SetValue(self.m_unicode_checkbox.GetValue())
        self.parent.m_case_checkbox.SetValue(self.m_case_checkbox.GetValue())
        self.parent.m_dotmatch_checkbox.SetValue(self.m_dotmatch_checkbox.GetValue())
        if self.regex_support:
            self.parent.m_bestmatch_checkbox.SetValue(self.m_bestmatch_checkbox.GetValue())
            self.parent.m_enhancematch_checkbox.SetValue(self.m_enhancematch_checkbox.GetValue())
            self.parent.m_word_checkbox.SetValue(self.m_word_checkbox.GetValue())
            self.parent.m_reverse_checkbox.SetValue(self.m_reverse_checkbox.GetValue())
        self.Close()

    def on_cancel(self, event):
        """Close dialog."""

        self.Close()

    def test_regex(self):
        """Test and highlight search results in content buffer."""

        if self.regex_support:
            import regex

        if not self.testing:
            self.testing = True
            if self.m_regex_text.GetValue() == "":
                self.m_test_text.SetStyle(
                    0,
                    self.m_test_text.GetLastPosition(),
                    wx.TextAttr(colText=wx.Colour(0, 0, 0), colBack=wx.Colour(255, 255, 255))
                )
                self.testing = False
                return

            if self.regex_support:
                flags = regex.VERSION1 | regex.MULTILINE
                if self.m_dotmatch_checkbox.GetValue():
                    flags |= regex.DOTALL
                if not self.m_case_checkbox.GetValue():
                    flags |= regex.IGNORECASE
                if self.m_unicode_checkbox.GetValue():
                    flags |= regex.UNICODE
                else:
                    flags |= regex.ASCII
                if self.m_bestmatch_checkbox.GetValue():
                    flags |= regex.BESTMATCH
                if self.m_enhancematch_checkbox.GetValue():
                    flags |= regex.ENHANCEMATCH
                if self.m_word_checkbox.GetValue():
                    flags |= regex.WORD
                if self.m_reverse_checkbox.GetValue():
                    flags |= regex.REVERSE
            else:
                flags = bre.MULTILINE
                if not self.m_case_checkbox.GetValue():
                    flags |= bre.IGNORECASE
                if self.m_dotmatch_checkbox.GetValue():
                    flags |= bre.DOTALL
                if self.m_unicode_checkbox.GetValue():
                    flags |= bre.UNICODE

            try:
                if self.regex_support:
                    test = regex.compile(self.m_regex_text.GetValue(), flags)
                else:
                    test = bre.compile_search(self.m_regex_text.GetValue(), flags)
            except Exception:
                self.testing = False
                return

            replace_test = None
            try:
                rpattern = self.m_replace_text.GetValue()
                if rpattern:
                    if self.regex_support:
                        replace_test = lambda m, replace=rpattern: self.regex_expand(m, replace)
                    else:
                        replace_test = bre.compile_replace(test, self.m_replace_text.GetValue())
            except Exception:
                pass

            try:
                text = self.m_test_text.GetValue()

                # Reset Colors
                self.m_test_text.SetStyle(
                    0,
                    self.m_test_text.GetLastPosition(),
                    wx.TextAttr(colText=wx.Colour(0, 0, 0), colBack=wx.Colour(255, 255, 255))
                )

                new_text = []
                offset = 0
                for m in test.finditer(text):
                    try:
                        if replace_test:
                            new_text.append(text[offset:m.start(0)])
                            new_text.append(replace_test(m))
                            offset = m.end(0)
                    except Exception:
                        replace_test = None
                    self.m_test_text.SetStyle(
                        m.start(0),
                        m.end(0),
                        wx.TextAttr(colBack=wx.Colour(0xFF, 0xCC, 0x00))
                    )
                if replace_test:
                    new_text.append(text[offset:])
                self.m_test_replace_text.SetValue(''.join(new_text))

            except Exception:
                print(str(traceback.format_exc()))
            self.testing = False

    def regex_start_event(self, event):
        """Regex start event."""

        self.regex_event_code += 1
        event.Skip()

    def on_test_changed(self, event):
        """On test change event."""

        if not self.testing:
            self.regex_start_event(event)
        else:
            event.Skip()

    on_replace_changed = regex_start_event

    on_regex_changed = regex_start_event

    on_case_toggle = regex_start_event

    on_dot_toggle = regex_start_event

    on_unicode_toggle = regex_start_event
