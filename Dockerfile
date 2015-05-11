FROM ubuntu:trusty
MAINTAINER ODL DevOps <mitx-devops@mit.edu>

WORKDIR /src/

# Add project
ADD . /src

# Install base packages
RUN apt-get update
RUN apt-get install -y $(grep -vE "^\s*#" apt.txt  | tr "\n" " ")
RUN pip install pip --upgrade


# Install project packages
RUN pip install -r requirements.txt

EXPOSE 8070

CMD uwsgi uwsgi.ini
