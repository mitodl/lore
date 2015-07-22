FROM ubuntu:trusty
MAINTAINER ODL DevOps <mitx-devops@mit.edu>


# Add package files
ADD requirements.txt /tmp/requirements.txt
ADD test_requirements.txt /tmp/test_requirements.txt
ADD doc_requirements.txt /tmp/doc_requirements.txt
ADD apt.txt /tmp/apt.txt
WORKDIR /tmp

# Install base packages
RUN apt-get update
RUN apt-get install -y $(grep -vE "^\s*#" apt.txt  | tr "\n" " ")
RUN pip install pip --upgrade

# Install project packages
RUN pip install -r requirements.txt
RUN pip install -r test_requirements.txt
RUN pip install -r doc_requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install -r test_requirements.txt

# Add, and run as, non-root user.
RUN adduser --disabled-password --gecos "" mitodl

# Add project
ADD . /src
WORKDIR /src
RUN chown -R mitodl:mitodl /src

# Link nodejs to node since npm expects node
RUN ln -s /usr/bin/nodejs /usr/bin/node

# Install development packages globally for things like
# bower.
RUN mkdir /node
ADD package.json /node/package.json
RUN cd /node && npm install

# Install productions deps for runtime items like jsx
RUN npm install --production
ENV PATH /src/node_modules/.bin:/node/node_modules/.bin:$PATH

# Set pip cache folder, as it is breaking pip when it is on a shared volume
ENV XDG_CACHE_HOME /tmp/.cache

# Gather static
RUN ./manage.py collectstatic --noinput

USER mitodl

# Set and expose port for uwsgi config
EXPOSE 8070
ENV PORT 8070
CMD if [ -n "$WORKER" ]; then celery -A lore worker; else uwsgi uwsgi.ini; fi
