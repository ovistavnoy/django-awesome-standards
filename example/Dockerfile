# Python version
FROM python:3.7
ENV PYTHONUNBUFFERED=1

WORKDIR /code/

# Install gettext to compile tranlations
RUN apt-get update && apt-get install -y gettext

# Install pipenv
RUN pip install --upgrade pip && pip install pipenv

# Copy pipfile and install it as a system packages
COPY ./Pipfile ./Pipfile.lock /code/

# No need in virtualenv as we are already inside container
RUN pipenv install --dev --system

# Copy project files only here, because we don't want to reinstall
# requirements each time file is changed.
COPY ./ /code/
