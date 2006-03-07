.PHONY: clean check

check:
	pychecker2 *.py

clean:
	find . "(" -name "*~" -or  -name ".#*" -or -name "*.pyc" -or -name "#*" ")" -print0 | xargs -0 rm -f
	rm -f ChangeLog
	#cd tests ; make clean

