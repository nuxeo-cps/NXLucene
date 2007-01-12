# NXLucene doc Makefile
# $Id$
# to build api documentation you need python docutils and epydoc
#
.PHONY: all epydoc clean

all: epydoc

epydoc:
	export LD_LIBRARY_PATH='../src/PyLucene/gcj'
	export PYTHONPATH='../src/PyLucene/python'
	python build_doc --html -o api -n NXLucene -u http://nxlucene.nuxeo.org ../src/nxlucene/ 

clean:
	rm -rf ./api/*
	find . "(" -name "*~" -or  -name ".#*" -or  -name "#*#" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f
