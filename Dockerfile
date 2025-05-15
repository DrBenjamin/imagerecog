FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBIAN_PRIORITY=high

# Install system dependencies (no system wxWidgets)
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install \
    xvfb xterm xdotool scrot imagemagick sudo mutter x11vnc \
    build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev \
    libxmlsec1-dev libffi-dev liblzma-dev net-tools netcat-openbsd software-properties-common \
    libgtk-3-dev libgtk2.0-dev libgdk-pixbuf2.0-dev libgl1-mesa-dev \
    freeglut3-dev libsm-dev libxrender-dev libxext-dev libxtst-dev libjpeg-dev libtiff-dev \
    libpng-dev libnotify-dev libsdl1.2-dev pkg-config \
    libwebkit2gtk-4.0-dev novnc xdg-utils epiphany-browser w3m && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installing Python 3.10 and pip (skip pyenv for faster builds)
RUN apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3-pip && \
    ln -sf /usr/bin/python3.10 /usr/local/bin/python && \
    ln -sf /usr/bin/pip3 /usr/local/bin/pip

RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir "wxPython==4.2.2"

# Setting user
ENV USERNAME=ben
ENV HOME=/home/$USERNAME
RUN useradd -m -s /bin/bash -d $HOME $USERNAME
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Switching to the correct user
USER ben
WORKDIR $HOME

# Cloning Dateiablage repository from branch v0.2.0
# Forcing Docker not to use cache for repository clone step
RUN --mount=type=cache,target=/var/cache/apt \
    rm -rf $HOME/Dateiablage && \
    git clone --branch v0.2.0 https://github.com/DrBenjamin/BenBox.git $HOME/Dateiablage

# Setting up working directory for Dateiablage
WORKDIR $HOME/Dateiablage

# Adding entrypoint.sh to the image as root, before switching to USER ben
USER root
COPY entrypoint.sh /home/ben/Dateiablage/entrypoint.sh
RUN chmod +x /home/ben/Dateiablage/entrypoint.sh

# Installing Miniforge (conda-forge based) as root, with architecture detection
USER root
ENV CONDA_DIR=/opt/conda
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        MINIFORGE_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        MINIFORGE_URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    curl -sSL $MINIFORGE_URL -o miniforge.sh && \
    bash miniforge.sh -b -p $CONDA_DIR && \
    rm miniforge.sh && \
    $CONDA_DIR/bin/conda clean -afy
ENV PATH="$CONDA_DIR/bin:$PATH"

# Switching back to the correct user
USER ben

# Copying environment.yml and creating conda environment
COPY --chown=ben:ben environment.yml /home/ben/Dateiablage/environment.yml
WORKDIR /home/ben/Dateiablage

# Updating permissions for conda envs and pkgs directories
USER root
RUN mkdir -p /opt/conda/envs && chmod -R 777 /opt/conda/envs && \
    mkdir -p /opt/conda/pkgs && chmod -R 777 /opt/conda/pkgs

USER ben
RUN conda env create -f environment.yml && conda clean -afy

# Setting conda environment variables
ENV CONDA_DEFAULT_ENV=benbox
ENV PATH="/opt/conda/envs/benbox/bin:$PATH"

# Installing wxPython dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir "wxPython==4.2.2"

# Building the Dateiablage app using PyInstaller (inside conda env)
RUN conda run -n benbox python -m pip install --no-cache-dir pyinstaller
RUN conda run -n benbox python -m PyInstaller --noconfirm --clean Dateiablage.py

ARG DISPLAY_NUM=1
ARG HEIGHT=768
ARG WIDTH=1024
ENV DISPLAY_NUM=$DISPLAY_NUM
ENV HEIGHT=$HEIGHT
ENV WIDTH=$WIDTH

# Installing noVNC and websockify as root (fixing permissions)
USER root
RUN git clone --branch v1.5.0 https://github.com/novnc/noVNC.git /opt/noVNC && \
    git clone --branch v0.12.0 https://github.com/novnc/websockify /opt/noVNC/utils/websockify && \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html

# Fixing noVNC path and ensuring DISPLAY is set for all processes
ENV PATH="/opt/noVNC/utils:${PATH}"
ENV DISPLAY=:1

# Switching back to the correct user
USER ben

# Installing MinIO mc CLI to $HOME/minio-binaries and add to PATH
RUN curl -sSL https://dl.min.io/client/mc/release/linux-amd64/mc \
    --create-dirs \
    -o /home/ben/minio-binaries/mc && \
    chmod +x /home/ben/minio-binaries/mc

ENV PATH="$PATH:/home/ben/minio-binaries"

# Setting entrypoint to run Streamlit app using conda
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "benbox", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
