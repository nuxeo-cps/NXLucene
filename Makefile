.PHONY: clean check

SRC_DOCS := $(shell ls *.txt)

# Uncomment this line to produce HTML docs from all the available text files in
# this directory.
#HTML_DOCS := $(subst .txt,.html,${SRC_DOCS})
HTML_DOCS := README.html INSTALL.html

# In order to generate HTML docs, you will need to install
# Docutils (http://docutils.sourceforge.net/).
# For example on a Debian system:
# $ sudo apt-get install python-docutils
RST2HTML := rst2html \
#-t --stylesheet-path=nuxeo_doc.css \
--input-encoding=iso-8859-15 \
--output-encoding=iso-8859-15


doc: ${HTML_DOCS}

%.html: %.txt
	${RST2HTML} $< $@


check:
	pychecker2 *.py

clean:
	find . "(" -name "*~" -or  -name ".#*" -or -name "*.pyc" ")" -print0 | xargs -0 rm -f
	rm -f ChangeLog
	rm -rf build



