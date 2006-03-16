# NXLucene doc Makefile
# $Id: $
# to build api documentation you need python docutils and epydoc
#
.PHONY: all epydoc clean

all: epydoc

epydoc:
	python build_doc --html -o api -n NXLucene -u http://nxlucene.nuxeo.org ../src/nxlucene/ 

clean:
	rm -rf ./api/*
	find . "(" -name "*~" -or  -name ".#*" -or  -name "#*#" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f
