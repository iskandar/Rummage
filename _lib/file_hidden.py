#!/usr/bin/python

import contextlib
import ctypes
from os.path import expanduser, basename
import sys

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"

if _PLATFORM == "osx":
    import Foundation
elif _PLATFORM == "windows":
    import ctypes

_OSX_FOUNDATION_NOT_LOADED = 0
_OSX_USE_FOUNDATION = 1
_OSX_USE_CORE_FOUNDATION = 2
_OSX_FOUNDATION_METHOD = _OSX_FOUNDATION_NOT_LOADED


def platform_not_implemented(path):
    raise NotImplementedError


if _PLATFORM == "windows":
    def is_win_hidden(path):
        attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
        return attrs != -1 and bool(attrs & 2)
else:
    is_win_hidden = platform_not_implemented


def is_nix_hidden(path):
    f = basename(path)
    return f.startswith('.') and f != ".."


def _test(fn):
    path = expanduser("~/Library")
    is_osx_hidden(path)
    # print "OSX Hidden Method: %d, Test Path: %s, Result: %s"  % (_OSX_FOUNDATION_METHOD, path, str(fn(path)))


if _PLATFORM == "osx":
    # http://stackoverflow.com/questions/284115/cross-platform-hidden-file-detection
    try:
        import Foundation

        def is_osx_hidden(path):
            pool = Foundation.NSAutoreleasePool.alloc().init()
            hidden = (
                is_nix_hidden(path) or
                Foundation.NSURL.fileURLWithPath_(path).getResourceValue_forKey_error_(
                    None, Foundation.NSURLIsHiddenKey, None
                )[1]
            )
            del pool
            return hidden

        _OSX_FOUNDATION_METHOD = _OSX_USE_FOUNDATION
        _test(is_osx_hidden)
    except:
        _OSX_FOUNDATION_METHOD = _OSX_FOUNDATION_NOT_LOADED
        pass

if _PLATFORM == "osx" and _OSX_FOUNDATION_METHOD == _OSX_FOUNDATION_NOT_LOADED:
    # http://stackoverflow.com/questions/284115/cross-platform-hidden-file-detection
    try:
        # Setup OSX access to CoreFoundatin for hidden file detection
        cf = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
        cf.CFShow.argtypes = [ctypes.c_void_p]
        cf.CFShow.restype = None
        cf.CFRelease.argtypes = [ctypes.c_void_p]
        cf.CFRelease.restype = None
        cf.CFURLCreateFromFileSystemRepresentation.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.c_int
        ]
        cf.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
        cf.CFURLCopyResourcePropertyForKey.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p
        ]
        cf.CFURLCopyResourcePropertyForKey.restype = ctypes.c_int
        cf.CFBooleanGetValue.argtypes = [ctypes.c_void_p]
        cf.CFBooleanGetValue.restype = ctypes.c_int

        # This one is a static CFStringRef.
        kCFURLIsHiddenKey = ctypes.c_void_p.in_dll(cf, 'kCFURLIsHiddenKey')

        @contextlib.contextmanager
        def cfreleasing(stuff):
            try:
                yield
            finally:
                for thing in stuff:
                    cf.CFRelease(thing)


        def is_osx_hidden(path):
            # Convert file name to bytes
            if not isinstance(path, bytes):
                path = path.encode('UTF-8')

            stuff = []
            with cfreleasing(stuff):
                url = cf.CFURLCreateFromFileSystemRepresentation(None, path, len(path), False)
                stuff.append(url)
                val = ctypes.c_void_p(0)
                ret = cf.CFURLCopyResourcePropertyForKey(
                    url, kCFURLIsHiddenKey, ctypes.addressof(val), None
                )
                if ret:
                    result = cf.CFBooleanGetValue(val)
                    stuff.append(val)
                    return True if result else False
                raise OSError('CFURLCopyResourcePropertyForKey failed')

        _OSX_FOUNDATION_METHOD = _OSX_USE_CORE_FOUNDATION
        _test(is_osx_hidden)
    except:
        is_osx_hidden = is_nix_hidden
        _OSX_FOUNDATION_METHOD = _OSX_FOUNDATION_NOT_LOADED


if _PLATFORM != "osx":
    is_osx_hidden = platform_not_implemented


def is_hidden(path):
    if _PLATFORM == "windows":
        return is_win_hidden(path)
    elif _PLATFORM == "osx":
        if is_nix_hidden(path):
            return True
        elif _OSX_FOUNDATION_METHOD != _OSX_FOUNDATION_NOT_LOADED:
            return is_osx_hidden(path)
        return False
    else:
        return is_nix_hidden(path)


if __name__ == '__main__':
    import sys
    for arg in sys.argv[1:]:
        filename = expanduser(arg)
        print('{}: {}'.format(filename, is_hidden(filename)))