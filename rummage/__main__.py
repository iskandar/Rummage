"""
Rummage (main).

Licensed under MIT
Copyright (c) 2011 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import argparse
import sys
from rummage.gui.settings import Settings
from rummage.gui.rummage_app import set_debug_mode, RummageApp, RummageFrame, RegexTestDialog
from rummage import version


def parse_arguments():
    """Parse the arguments."""

    parser = argparse.ArgumentParser(prog=version.__app__, description='A python grep like tool.')
    # Flag arguments
    parser.add_argument('--version', action='version', version=('%(prog)s ' + version.__version__))
    parser.add_argument('--debug', '-d', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--searchpath', '-s', nargs=1, default=None, help="Path to search.")
    parser.add_argument('--regextool', '-r', action='store_true', default=False, help="Open just the regex tester.")
    return parser.parse_args()


def run():
    """Configure environment, start the app, and launch the appropriate frame."""

    args = parse_arguments()

    Settings.load_settings(args.debug)

    if args.debug:
        set_debug_mode(True)

    if Settings.get_single_instance():
        app = RummageApp(redirect=True, single_instance_name="Rummage", pipe_name=Settings.get_fifo())
    else:
        app = RummageApp(redirect=True)

    if not Settings.get_single_instance() or (Settings.get_single_instance() and app.is_instance_okay()):
        if args.regextool:
            RegexTestDialog(None, False, False, stand_alone=True).Show()
        else:
            RummageFrame(
                None,
                args.searchpath[0] if args.searchpath is not None else None,
                debug_mode=args.debug
            ).Show()
    app.MainLoop()


def main():
    """Main entry point."""

    sys.exit(run())


if __name__ == "__main__":
    main()