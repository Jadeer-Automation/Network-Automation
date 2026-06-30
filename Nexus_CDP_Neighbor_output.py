#!/usr/bin/env python3

import re
from datetime import datetime

#Show cdp neighbors detail output parsed on below file.
INPUT_FILE = "cdp_neighbors.txt"

# Read file
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = f.read()

# Get local switch hostname from CLI prompt
hostname = "Unknown_Switch"

match = re.search(
    r'^([A-Za-z0-9_.-]+)#\s*show\s+cdp\s+neighbors\s+detail',
    data,
    re.MULTILINE | re.IGNORECASE
)

if match:
    hostname = match.group(1)

# Split neighbors
entries = re.split(r'-{10,}', data)

neighbors = []

for entry in entries:

    device = re.search(r'Device ID:\s*(.+)', entry)
    if not device:
        continue
        
    ip = re.search(
        r'(?:IP address:|IPv4 Address:)\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',
        entry,
        re.MULTILINE
    )

    platform = re.search(r'Platform:\s*(.+?),', entry)

    capability = re.search(r'Capabilities:\s*(.+)', entry)

    local = re.search(r'Interface:\s*(.+?),', entry)

    remote = re.search(r'Port ID \(outgoing port\):\s*(.+)', entry)

    version = re.search(
        r'Version\s*:\s*(.*?)(?=Advertisement Version:|Duplex:|Management address|$)',
        entry,
        re.S
    )

    ver = ""
    if version:
        ver = " ".join(version.group(1).split())
        m = re.search(r'(\d+\.\d+\([^)]+\)|\d+\.\d+\.\d+\([^)]+\)|\d+\.\d+\(\d+\))', ver)
        if m:
            ver = m.group(1)

    neighbors.append({
        "device": device.group(1).strip(),
        "ip": ip.group(1).strip() if ip else "",
        "platform": platform.group(1).strip() if platform else "",
        "capability": capability.group(1).strip() if capability else "",
        "local": local.group(1).strip() if local else "",
        "remote": remote.group(1).strip() if remote else "",
        "version": ver
    })

rows = ""

for n in neighbors:
    rows += f"""
<tr>
<td>{n['device']}</td>
<td>{n['ip']}</td>
<td>{n['platform']}</td>
<td>{n['capability']}</td>
<td>{n['local']}</td>
<td>{n['remote']}</td>
<td>{n['version']}</td>
</tr>
"""

html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">

<title>CDP Neighbor Report</title>

<style>

body {{
font-family: Arial;
background:#f4f7fb;
margin:25px;
}}

.header {{
background:#0b5cab;
color:white;
padding:20px;
border-radius:8px;
}}

.summary {{
margin-top:15px;
padding:12px;
background:white;
border-radius:8px;
box-shadow:0 1px 4px rgba(0,0,0,.15);
}}

input {{
width:300px;
padding:8px;
margin-top:20px;
margin-bottom:15px;
font-size:14px;
}}

table {{
border-collapse:collapse;
width:100%;
background:white;
}}

th {{
background:#0b5cab;
color:white;
padding:10px;
position:sticky;
top:0;
}}

td {{
padding:8px;
border-bottom:1px solid #ddd;
}}

tr:nth-child(even){{
background:#f2f2f2;
}}

tr:hover {{
background:#d9edf7;
}}

</style>

<script>

function searchTable() {{

var input=document.getElementById("search");

var filter=input.value.toUpperCase();

var table=document.getElementById("cdpTable");

var tr=table.getElementsByTagName("tr");

for(var i=1;i<tr.length;i++){{

var show=false;

var td=tr[i].getElementsByTagName("td");

for(var j=0;j<td.length;j++){{

if(td[j]){{

if(td[j].innerHTML.toUpperCase().indexOf(filter)>-1){{

show=true;

}}

}}

}}

tr[i].style.display=show?"":"none";

}}

}}

</script>

</head>

<body>

<div class="header">
    <h2>Cisco Nexus CDP Neighbor Report</h2>

    <div style="margin-top:15px;font-size:16px;">
        <b>Hostname:</b> {hostname}<br>
        <b>Generated:</b> {datetime.now().strftime("%d-%b-%Y %H:%M:%S")}<br>
        <b>Total Neighbors:</b> {len(neighbors)}
    </div>
</div>

<div class="summary">

<b>Generated:</b> {datetime.now().strftime("%d-%b-%Y %H:%M:%S")}<br>

<b>Total Neighbors:</b> {len(neighbors)}

</div>

<input
type="text"
id="search"
onkeyup="searchTable()"
placeholder="Search...">

<table id="cdpTable">

<tr>

<th>Neighbor</th>

<th>Management IP</th>

<th>Platform</th>

<th>Capability</th>

<th>Local Interface</th>

<th>Remote Interface</th>

<th>Software Version</th>

</tr>

{rows}

</table>

</body>

</html>
"""

output_file = f"{hostname}_CDP_Report.html"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html)

print("HTML report created successfully.")
print(f"Output : {output_file}")