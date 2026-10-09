FROM mcr.microsoft.com/devcontainers/base:jammy

# Install prerequisite packages for Spack
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        build-essential ca-certificates coreutils curl environment-modules \
        gfortran git gpg lsb-release python3 python3-distutils python3-venv python3-pip \
        unzip zip bzip2 xz-utils patch file gnupg2 make tar gzip zstd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone Spack directly from the official repository
ENV SPACK_ROOT=/opt/spack
RUN git clone -c feature.manyFiles=true --depth=2 https://github.com/spack/spack.git ${SPACK_ROOT}

# Initialize Spack in the bash profile
RUN echo "source ${SPACK_ROOT}/share/spack/setup-env.sh" >> /home/vscode/.bashrc

# Grant permissions to the standard devcontainer user
RUN chown -R vscode:vscode ${SPACK_ROOT}

ENV PATH="${SPACK_ROOT}/bin:${PATH}"
