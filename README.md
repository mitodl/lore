# LORE

## Getting Started
 You can either run this locally with a default sqlite database after
 installing the requirements.txt file, or if you have docker and
 prefer a cleaner environment, install docker-compose with `pip
 install docker-compose` and run `docker-compose up`.  This will
 setup a near production ready containerized development environment
 that runs migrations, with the django development server running on
 port 8070.

To run one off commands, like shell, you can run
`docker-compose run web python manage.py shell` or to create root
user, etc.

## Adding an application
To add an application to this, add it to the requirements file, add
its needed settings, include its URLs, and provide any needed template
overrides.
