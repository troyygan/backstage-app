#!/usr/bin/env python3
"""Request dev validation and a reviewed release in the workload repository."""
import json
import os
import re
import urllib.error
import urllib.request


def main():
    app = os.environ["RELEASE_APP"]
    repository = os.environ["IMAGE_REPOSITORY"]
    sha = os.environ["GITHUB_SHA"]
    image = os.environ["RELEASE_IMAGE"]
    run_id = os.environ["GITHUB_RUN_ID"]
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise SystemExit("Only main may request a workload release.")
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or not re.fullmatch(r"[0-9]+", run_id):
        raise SystemExit("Invalid source workflow identity.")
    if not re.fullmatch(re.escape(repository + ":" + sha) + r"@sha256:[0-9a-f]{64}", image):
        raise SystemExit("Release requires this commit and an exact image digest.")
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        raise SystemExit("Configure WORKLOADS_DISPATCH_TOKEN before requesting a release.")
    request = urllib.request.Request(
        "https://api.github.com/repos/troyygan/homelab-workloads/actions/workflows/custom-app-release.yml/dispatches",
        data=json.dumps({"ref": "main", "inputs": {
            "app": app, "source_sha": sha, "image": image, "source_run_id": run_id,
        }}).encode(),
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json",
                 "X-GitHub-Api-Version": "2022-11-28"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 204:
                raise SystemExit("Unexpected release request response.")
    except urllib.error.HTTPError as error:
        raise SystemExit(f"Workload release request failed (HTTP {error.code}).") from None
    except urllib.error.URLError:
        raise SystemExit("Workload release request could not reach GitHub.") from None
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
        summary.write("\nRequested isolated dev validation in `homelab-workloads`. "
                      "A release PR is opened only after validation and cleanup pass. "
                      "Review and merge that PR to deploy core.\n")


if __name__ == "__main__":
    main()
