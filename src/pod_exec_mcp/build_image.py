from __future__ import annotations

import shutil
import subprocess

IMAGE_NAME = "pod_exec_mcp_base"

CONTAINERFILE = """\
FROM docker.io/library/debian:trixie

RUN apt-get update && apt-get install -y \\
    bash \\
    ca-certificates \\
    coreutils \\
    curl \\
    file \\
    findutils \\
    gawk \\
    git \\
    grep \\
    gzip \\
    iproute2 \\
    iputils-ping \\
    jq \\
    less \\
    openssh-client \\
    procps \\
    psmisc \\
    ripgrep \\
    sed \\
    tar \\
    unzip \\
    wget \\
    which \\
    xz-utils \\
    zip \\
    && rm -rf /var/lib/apt/lists/*

CMD ["bash"]
"""


def main() -> None:
    if shutil.which("podman") is None:
        raise RuntimeError("Podman binary was not found in PATH")

    process = subprocess.Popen(
        ["podman", "build", "-t", IMAGE_NAME, "-f", "-", "."],
        stdin=subprocess.PIPE,
        text=True,
    )
    process.communicate(CONTAINERFILE)
    if process.returncode != 0:
        raise RuntimeError(
            f"Failed to build image '{IMAGE_NAME}' (exit code {process.returncode})"
        )
    print(f"Built image '{IMAGE_NAME}'")


if __name__ == "__main__":
    main()
