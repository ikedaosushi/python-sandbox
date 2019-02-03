FROM python:3.7.2

# Setting
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PIPENV_DONT_USE_PYENV=True

# Install PyPI packages
ADD Pipfile* /tmp/
RUN cd /tmp && \
    pip install -U pip && \
    pip install pipenv && \
    pipenv install --system --ignore-pipfile --deploy