FROM python:3.8

# Set pip to have no saved cache
ENV PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_CREATE=false

# Create the working directory
WORKDIR /bot

# Create volumes so that data can be binded from host
VOLUME /bot/data /bot/logs

# Copy the source code in last to optimize rebuilding the image
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["-m", "bot"]