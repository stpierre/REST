CWD := $(shell pwd)

.PHONY : container run stop restart venv test service start-service stop-service restart-service outputs clean

all:	test outputs run

container:	Dockerfile
	sudo docker build --rm -t stpierre/rest $(CWD)

run:	container
	sudo docker run -d -p 8000:8000 \
	    -v $(CWD)/local:/opt/reveal.js/local \
	    -v $(CWD)/index.html:/opt/reveal.js/index.html \
	    -v $(CWD)/images:/opt/reveal.js/images \
	    -v $(CWD)/outputs:/opt/reveal.js/outputs \
	    --name REST stpierre/rest

stop:
	sudo docker stop REST
	sudo docker rm REST

restart:	stop run

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
