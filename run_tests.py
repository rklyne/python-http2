#!/usr/bin/python

import unittest
suite = unittest.defaultTestLoader.discover("test", "*.py")
unittest.TextTestRunner().run(suite)


