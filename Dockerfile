FROM python:3.10

# Update, upgrade and install Git in one layer
RUN apt update && apt upgrade -y && apt install -y git

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Start the bot
CMD ["python", "bot.py"]
