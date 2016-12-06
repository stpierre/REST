CWD := $(shell pwd)

.PHONY : run venv test service start-service stop-service restart-service outputs clean

all:	test outputs run

run:	test
	python -mSimpleHTTPServer

test:	venv
	. venv/bin/activate
	./service.py

venv:	venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate && pip install -r requirements.txt

service:	venv
	. venv/bin/activate; FLASK_APP=service.py flask run

start-service:
	. venv/bin/activate; FLASK_APP=service.py flask run & echo $$! > service.pid; while ! echo | nc localhost 5000; do sleep 1; done

stop-service:
	kill `cat service.pid` && rm service.pid

restart-service:	stop-service start-service

outputs:	venv start-service
	./output_preprocessor.py --output outputs index.html; $(MAKE) stop-service; rm -rf outputs/*.cookies

clean:
	rm -rf venv
	rm -rf outputs/*.txt
	rm -rf outputs/*.cookies
