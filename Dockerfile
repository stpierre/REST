FROM fedora:24

# install npm and git. other packages are required by some node.js deps
RUN dnf -y install \
    bzip2 \
    findutils \
    git \
    npm \
    spawn \
    tar \
    wget

# install reveal.js and the presentation
WORKDIR /opt
RUN git clone https://github.com/hakimel/reveal.js.git && \
    rm -rf /opt/reveal.js/index.html

WORKDIR /opt/reveal.js
RUN npm install -g grunt-cli && npm install
RUN sed -i "s/port: port/port: port,\n\t\t\t\t\thostname: \'\'/g" Gruntfile.js
RUN wget -O /opt/reveal.js/js/jquery.min.js \
    https://code.jquery.com/jquery-3.1.0.min.js
RUN wget -O /opt/reveal.js/css/bootstrap.min.css \
    https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css
RUN wget -O /opt/reveal.js/js/bootstrap.min.js \
    https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js

VOLUME /opt/reveal.js/local
VOLUME /opt/reveal.js/index.html
VOLUME /opt/reveal.js/images

EXPOSE 8000

CMD ["grunt", "-d", "serve"]
