FROM python:3.9.5

# Set pip to have no saved cache
ENV PIP_NO_CACHE_DIR=false \
    POETRY_VIRTUALENVS_CREATE=false

# Create the working directory
WORKDIR /bot

# Copy the source code in last to optimize rebuilding the image
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["-m", "bot"]