# Use a smaller base image
FROM python:3.10-slim AS builder

# Install git and any dependencies, then clean up
RUN apt update && apt upgrade -y && apt install git -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies without caching
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -U -r /requirements.txt

# Start a new stage to minimize the final image size
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy only the installed dependencies and the application files from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .

# Set the command to run the bot
CMD ["python", "bot.py"]
