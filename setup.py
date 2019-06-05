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
    version = "0.1",
    author = "Mark Wolfman",
    author_email = "canismarko@gmail.com",
    description = ("Retrieve scientific papers and manage associated citations.",),
    license = "GPLv3",
    keywords = "",
    url = "https://github.com/canismarko/franklin",
    packages=['franklin'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "LICENSE :: OSI APPROVED :: GNU GENERAL PUBLIC LICENSE V3 (GPLV3)",
    ],
)
