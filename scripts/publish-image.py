#!/usr/bin/env python3
"""Publish a commit once; re-runs verify and reuse its existing image."""
import json
import os
import re
import subprocess


def main():
    repository = os.environ["IMAGE_REPOSITORY"]
    sha = os.environ["GITHUB_SHA"]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise SystemExit("An immutable image requires a full source commit SHA.")
    image = f"{repository}:{sha}"
    pull = subprocess.run(["docker", "pull", image], capture_output=True, text=True)
    if pull.returncode:
        output = pull.stdout + pull.stderr
        missing = ("manifest unknown" in output or "no such manifest" in output
                   or f'Error response from daemon: failed to resolve reference "{image}": {image}: not found' in output.splitlines())
        if not missing:
            raise SystemExit("Cannot establish whether the commit image exists; refusing to overwrite it.")
        subprocess.run(["docker", "build", "--file", os.environ.get("DOCKERFILE", "Dockerfile"),
                        "--label", "org.opencontainers.image.revision=" + sha,
                        "--label", "org.opencontainers.image.source=https://github.com/" + os.environ["GITHUB_REPOSITORY"],
                        "--tag", image, "."], check=True)
        subprocess.run(["docker", "push", image], check=True)
    else:
        print("Reusing the published commit image.")
    metadata = json.loads(subprocess.check_output(["docker", "image", "inspect", image], text=True))[0]
    if (metadata.get("Config", {}).get("Labels") or {}).get("org.opencontainers.image.revision") != sha:
        raise SystemExit("Image revision label does not match the source commit.")
    digests = {item.split("@", 1)[1] for item in metadata.get("RepoDigests", [])
               if item.startswith(repository + "@")}
    if len(digests) != 1:
        raise SystemExit("Expected exactly one published image digest.")
    digest = digests.pop()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise SystemExit("Invalid registry image digest.")
    reference = f"{image}@{digest}"
    with open(os.environ["GITHUB_OUTPUT"], "a") as output:
        output.write(f"reference={reference}\n")
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
        summary.write(f"Published image: `{reference}`\n")


if __name__ == "__main__":
    main()
