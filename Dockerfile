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

# Install node packages and add to PATH
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install -g --prefix /node
ENV PATH /node/lib/node_modules/lore/node_modules/.bin:$PATH

# Set pip cache folder, as it is breaking pip when it is on a shared volume
ENV XDG_CACHE_HOME /tmp/.cache

EXPOSE 8070

USER mitodl
CMD uwsgi uwsgi.ini
