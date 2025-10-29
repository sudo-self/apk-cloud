FROM ubuntu:22.04

WORKDIR /app

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    git \
    xz-utils \
    zip \
    libglu1-mesa \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git /opt/flutter
ENV PATH="$PATH:/opt/flutter/bin"

# Install Android SDK
RUN mkdir -p /opt/android-sdk/cmdline-tools
RUN wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O /tmp/cmdline-tools.zip && \
    unzip -q /tmp/cmdline-tools.zip -d /opt/android-sdk/cmdline-tools && \
    mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest && \
    rm /tmp/cmdline-tools.zip

ENV ANDROID_HOME=/opt/android-sdk
ENV PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"

# Accept licenses and install Android packages
RUN yes | sdkmanager --licenses
RUN sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"

# Pre-download Flutter dependencies
RUN flutter precache

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create builds directory
RUN mkdir -p builds

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start the app
CMD ["python3", "app.py"]
