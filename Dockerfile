FROM ubuntu:22.04

WORKDIR /app


ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV PORT=8080


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


RUN git clone https://github.com/flutter/flutter.git /opt/flutter -b stable
ENV PATH="$PATH:/opt/flutter/bin"

RUN mkdir -p /opt/android-sdk/cmdline-tools
RUN wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -O /tmp/cmdline-tools.zip && \
    unzip -q /tmp/cmdline-tools.zip -d /opt/android-sdk/cmdline-tools && \
    mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest && \
    rm /tmp/cmdline-tools.zip

ENV ANDROID_HOME=/opt/android-sdk
ENV PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"


RUN yes | sdkmanager --licenses && \
    sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.2"


RUN flutter precache


COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


COPY . .


RUN mkdir -p builds


EXPOSE 8080


CMD exec python3 app.py
