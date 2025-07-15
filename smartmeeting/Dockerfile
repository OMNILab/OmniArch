FROM registry.cn-hangzhou.aliyuncs.com/lacogito/ubuntu:24.04

# Set noninteractive mode
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Use Aliyun mirror for faster apt access in China
RUN sed -i 's|http://.*.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list

# Install system tools and add deadsnakes PPA
RUN apt-get update && apt-get install -y \
    software-properties-common curl \
    gcc g++ make \
    libfreetype6-dev libpng-dev libjpeg-dev \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3.11-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && python3.11 -m ensurepip --upgrade

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/root/.local/bin:$PATH"

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3.11 -

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to avoid virtualenv creation (optional)
RUN poetry config virtualenvs.create false

# Remove system pyparsing to avoid uninstall conflict
RUN apt-get remove -y python3-pyparsing python3-blinker || true

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Streamlit config
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

# Run the app
CMD ["poetry", "run", "streamlit", "run", "app.py"]
