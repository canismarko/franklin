import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "franklin",
    version = read('VERSION'),
    author = "Mark Wolfman",
    author_email = "canismarko@gmail.com",
    description = "Retrieve scientific papers and manage associated citations.",
    license = "GPLv3",
    keywords = "",
    url = "https://github.com/canismarko/franklin",
    packages=['franklin'],
    long_description=read('README.rst'),
    install_requires=[
        'bibtexparser', 'requests',
    ],
    entry_points = {
        'console_scripts': ['fetch-doi=franklin.fetch_doi:main'],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
