# Makefile of FunkLoad WebLucene tests
.PHONY: clean all start stop restart status
.PHONY:	test bench
.PHONY:	start_monitor stop_monitor restart_monitor

FLRUNTEST := fl-run-test -vv
FLRUNBENCH := fl-run-bench
FLBUILDREPORT :=  fl-build-report --html -o reports
MONCTL := fl-monitor-ctl monitor.conf

ifdef URL
# FunkLoad options
	FLOPS = -u $(URL)
else
	FLOPS =
endif

all: test

# testing
test:
	$(MONCTL) start

	$(FLRUNTEST) test_WebLucene.py

	$(MONCTL) stop

bench:
	$(MONCTL) start

	$(FLRUNBENCH) test_WebLucene.py WebLucene.test_simple_document_indexation
	$(FLRUNBENCH) test_WebLucene.py WebLucene.test_simple_search

	$(FLBUILDREPORT) weblucene-bench.xml

	$(MONCTL) stop


# Benching

# monitor ctl
start_monitor:
	$(MONCTL) start

stop_monitor:
	-$(MONCTL) stop

restart_monitor:
	-$(MONCTL) restart

# misc
status:
	-$(MONCTL) status;

stop: stop_monitor

start: start_monitor

restart: restart_monitor

clean:
	-find . "(" -name "*~" -or  -name ".#*" -or -name "*.log" -or -name "*.pyc" -or -name "*.xml" -or -name "*bak*" ")" -print0 | xargs -0 rm -f
