from distutils.core import setup
import py2exe
import sys

sys.argv.append("py2exe")

setup(windows=['Main.py'],
     options = {'py2exe': {'optimize': 2, 'bundle_files':1} },
     zipfile=None)

#setup(console=['Main.py'])
