import os
from setuptools import setup, find_packages


if __name__ == "__main__":

    def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

    meta = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, 'haskpy', '_meta.py')) as fp:
        exec(fp.read(), meta)

    setup(
        name="haskpy",
        author=meta["__author__"],
        author_email=meta["__contact__"],
        description="Utilities inspired by Haskell and Hask category",
        project_urls={
            "Homepage": "https://github.com/jluttine/haskpy",
            "Download": "https://pypi.org/project/haskpy/",
            "Documentation": "https://jluttine.github.io/haskpy/",
            "Bug reports": "https://github.com/jluttine/haskpy/issues",
            "Contributing": "https://github.com/jluttine/haskpy/pulls",
            "Forum": "https://github.com/jluttine/haskpy/discussions",
        },
        packages=find_packages(),
        use_scm_version=True,
        setup_requires=[
            "setuptools_scm",
        ],
        install_requires=[
            "attrs",
            "importlib_metadata",
            "hypothesis",
        ],
        extras_require={
            "dev": [
                "pytest",
            ],
            "doc": [
                "sphinx",
                "numpydoc",
            ],
        },
        keywords=[
            "functional programming",
            "category theory",
            "Hask category",
            "Haskell",
            "functor",
            "applicative",
            "monad",
            "monoid",
        ],
        classifiers=[
            "Programming Language :: Python :: 3 :: Only",
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: {0}".format(meta["__license__"]),
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3 :: Only",
            "Topic :: Scientific/Engineering",
            "Topic :: Software Development :: Libraries",
        ],
        long_description=read('README.md'),
        long_description_content_type="text/markdown",
    )
