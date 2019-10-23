import os
from setuptools import setup, find_packages
import versioneer


if __name__ == "__main__":

    def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    meta = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, 'haskpy', '_meta.py')) as fp:
        exec(fp.read(), meta)


    setup(
        name         = "haskpy",
        version      = versioneer.get_version(),
        author       = meta["__author__"],
        author_email = meta["__contact__"],
        description  = "Functions and classes inspired by Haskell and Hask category",
        url          = "https://github.com/jluttine/HaskPy",
        cmdclass     = versioneer.get_cmdclass(),
        packages     = find_packages(),
        install_requires = [
            "attrs",
        ],
        extras_require = {
            "dev": [
                "versioneer",
                "pytest",
                "hypothesis",
            ],
        },
        keywords     = [
            "functional programming",
            "category theory",
            "Hask category",
            "Haskell",
            "functor",
            "monad",
        ],
        classifiers = [
            "Programming Language :: Python :: 3 :: Only",
            "Development Status :: 1 - Planning",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: {0}".format(meta["__license__"]),
            "Operating System :: OS Independent",
            "Topic :: Scientific/Engineering",
            "Topic :: Software Development :: Libraries",
        ],
        long_description = read('README.md'),
        long_description_content_type = "text/markdown",
    )
