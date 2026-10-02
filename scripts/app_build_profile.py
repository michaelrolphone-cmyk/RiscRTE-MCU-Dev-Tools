"""Select an app ELF profile by immutable manifest version evidence."""

SUPPORTED_PROFILES = {"unstripped", "strip-unneeded"}


def select_build_profile(manifest, release_baseline):
    if not isinstance(manifest, dict) or not isinstance(release_baseline, dict):
        raise ValueError("Invalid manifest or release baseline")
    app_id = manifest.get("file_name", "")
    if not isinstance(app_id, str) or not app_id.endswith(".elf"):
        raise ValueError("Manifest artifact must name an ELF")
    app_id = app_id[:-4]
    matches = [row for row in release_baseline.get("apps", [])
               if isinstance(row, dict) and row.get("id") == app_id]
    if len(matches) != 1:
        raise ValueError("Release baseline must contain one profile for " + app_id)
    row = matches[0]
    if row.get("file_name") != manifest.get("file_name"):
        raise ValueError("Release baseline artifact does not match manifest")
    if row.get("version") != manifest.get("version"):
        raise ValueError("Build profile version does not match manifest: " + app_id)
    profile = row.get("build_profile")
    if profile not in SUPPORTED_PROFILES:
        raise ValueError("Unsupported published build profile for " + app_id)
    return profile


def build_profile_arguments(profile):
    if profile == "unstripped":
        return []
    if profile == "strip-unneeded":
        return ["--strip-unneeded"]
    raise ValueError("Unsupported published build profile")
