#!/usr/bin/python

def main(args):
    pattern = "*.py"
    if args:
        assert len(args) == 1, args
        pattern = "*"+args[0]+"*.py"
    import unittest
    suite = unittest.defaultTestLoader.discover("test", pattern)
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    print args
    print "#=--!--=#" * 10
    main(args)

