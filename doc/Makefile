# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS  = -n -W
SPHINXBUILD = sphinx-build
SOURCEDIR   = source
BUILDDIR    = build
# Fix copyright year issue on NixOS. See:
# https://github.com/sphinx-doc/sphinx/issues/3451#issuecomment-373708110
SOURCE_DATE_EPOCH = $(shell git log -1 --format=%ct)

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
