FROM python:3.10

# Update and install git in a single RUN command
RUN apt update && apt upgrade -y && apt install git -y && rm -rf /var/lib/apt/lists/*

# Install Python dependencies without caching
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -U -r /requirements.txt

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Command to run the bot
CMD ["python", "bot.py"]
