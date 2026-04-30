import os
import glob
import json
import base64
import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

CONFIG_DIR = ".github/kernel-config"
MANIFEST_URL_TEMPLATE = "https://android.googlesource.com/kernel/manifest/+/refs/heads/common-{branch}/default.xml?format=TEXT"

# Gather all kernel versions from config files
kernel_versions = set()
config_map = {}  # kernel_version -> config file
for config_path in glob.glob(os.path.join(CONFIG_DIR, "*.json")):
    with open(config_path) as f:
        data = json.load(f)
        for entry in data.get("include", []):
            ver = entry.get("kernel_version")
            if ver:
                kernel_versions.add(ver)
                config_map[ver] = os.path.basename(config_path)

# Map kernel_version to manifest branch name
def kernel_version_to_branch(ver):
    # e.g. 6.1.25-android14-2023-06 -> android14-6.1-2023-06
    m = None
    import re
    m = re.match(r"([\d.]+)-android(\d+)-(\d{4}-\d{2}|lts|exp)", ver)
    if m:
        kver, android, date = m.groups()
        return f"android{android}-{kver}-{date}"
    return None

manifest_details = defaultdict(lambda: defaultdict(dict))
# manifest_details[(name, path)][kernel_version] = {"tool": ..., "revision": ...}

for ver in sorted(kernel_versions):
    branch = kernel_version_to_branch(ver)
    if not branch:
        print(f"Could not parse branch for kernel version: {ver}")
        continue
    url = MANIFEST_URL_TEMPLATE.format(branch=branch)
    print(f"Fetching manifest for {ver} ({branch})")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch {url}")
        continue
    xml_content = base64.b64decode(resp.content).decode("utf-8")
    root = ET.fromstring(xml_content)
    for project in root.findall("project"):
        name = project.get("name")
        path = project.get("path", name)
        tool = project.get("tool", "")
        revision = project.get("revision", "")
        manifest_details[(name, path)][ver] = {"tool": tool, "revision": revision}

# Output detailed table
with open("manifest_resource_summary.md", "w") as f:
    f.write("| Resource Name | Path | Kernel Version | Tool | Revision |\n")
    f.write("|--------------|------|---------------|------|----------|\n")
    for (name, path), ver_map in sorted(manifest_details.items()):
        for ver, attrs in sorted(ver_map.items()):
            tool = attrs.get("tool", "")
            revision = attrs.get("revision", "")
            f.write(f"| `{name}` | `{path}` | `{ver}` | `{tool}` | `{revision}` |\n")

    # Optionally, add a summary for resources with differing tool/revision
    f.write("\n## Resources with differing tool or revision across kernel versions\n\n")
    for (name, path), ver_map in sorted(manifest_details.items()):
        tools = set(attrs.get("tool", "") for attrs in ver_map.values())
        revisions = set(attrs.get("revision", "") for attrs in ver_map.values())
        if len(tools) > 1 or len(revisions) > 1:
            f.write(f"- `{name}` (`{path}`):\n")
            for ver, attrs in sorted(ver_map.items()):
                tool = attrs.get("tool", "")
                revision = attrs.get("revision", "")
                f.write(f"    - {ver}: tool=`{tool}` revision=`{revision}`\n")

print("Summary written to manifest_resource_summary.md")
