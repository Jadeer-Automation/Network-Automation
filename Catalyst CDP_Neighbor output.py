import re
import os
from datetime import datetime

##Show cdp neighbors detail output parsed on below file.

INPUT_FILE = "cdp_output.txt"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()
# Extract hostname from CLI prompt
hostname = "Unknown_Switch"

first_line = text.splitlines()[0].strip()

match = re.search(r'^([^#]+)#', first_line)

if match:
    hostname = match.group(1).strip()

print(f"Hostname: {hostname}")

# Split each neighbor section
sections = re.split(r'-{10,}', text)

neighbors = []

for sec in sections:

    if "Device ID:" not in sec:
        continue

    neighbor = {}

    patterns = {
        "Device ID": r"Device ID:\s*(.+)",
        "IP Address": r"IP address:\s*([\d\.]+)",
        "Platform": r"Platform:\s*([^,]+)",
        "Capabilities": r"Capabilities:\s*(.+)",
        "Local Interface": r"Interface:\s*([^,]+)",
        "Remote Interface": r"Port ID \(outgoing port\):\s*(.+)",
        "Holdtime": r"Holdtime\s*:\s*(\d+)",
        "Version": r"Version\s*:\n(.*?)Advertisement",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, sec, re.S)
        if match:
            value = match.group(1).strip().replace("\n", "<br>")
            neighbor[key] = value
        else:
            neighbor[key] = "-"

    neighbors.append(neighbor)

switches = sum(
    1 for n in neighbors
    if "Switch" in n["Capabilities"]
)

routers = sum(
    1 for n in neighbors
    if "Router" in n["Capabilities"]
)

phones = sum(
    1 for n in neighbors
    if "Phone" in n["Capabilities"]
)

aps = sum(
    1 for n in neighbors
    if "Trans-Bridge" in n["Capabilities"] or "Wlan" in n["Capabilities"]
)

html = f"""
<!DOCTYPE html>
<html>
<head>

<title>CDP Neighbor Report</title>

<style>

body{{
font-family:Arial;
background:#f4f4f4;
margin:30px;
}}

h1{{
color:#0B3C5D;
}}

.summary{{
display:flex;
gap:20px;
margin-bottom:25px;
}}

.card{{
background:white;
padding:15px;
border-radius:8px;
box-shadow:0 2px 8px gray;
width:180px;
text-align:center;
}}

table{{
width:100%;
border-collapse:collapse;
background:white;
}}

th{{
background:#0B3C5D;
color:white;
padding:10px;
}}

td{{
padding:8px;
border:1px solid #ddd;
vertical-align:top;
}}

tr:nth-child(even){{
background:#f2f2f2;
}}

.search{{
margin-bottom:20px;
padding:8px;
width:300px;
}}

</style>

<script>

function searchTable() {{

var input=document.getElementById("search");

var filter=input.value.toUpperCase();

var table=document.getElementById("cdptable");

var tr=table.getElementsByTagName("tr");

for (var i=1;i<tr.length;i++){{

var found=false;

var td=tr[i].getElementsByTagName("td");

for(var j=0;j<td.length;j++){{

if(td[j].innerHTML.toUpperCase().indexOf(filter)>-1){{

found=true;

}}

}}

tr[i].style.display=found?"":"none";

}}

}}

</script>

</head>

<body>

<h1>Cisco CDP Neighbor Report - {hostname}</h1>

<p>Generated: {datetime.now()}</p>

<div class="summary">

<div class="card">
<h2>{len(neighbors)}</h2>
Total Neighbors
</div>

<div class="card">
<h2>{switches}</h2>
Switches
</div>

<div class="card">
<h2>{routers}</h2>
Routers
</div>

<div class="card">
<h2>{phones}</h2>
Phones
</div>

<div class="card">
<h2>{aps}</h2>
Access Points
</div>

</div>

<input
class="search"
type="text"
id="search"
onkeyup="searchTable()"
placeholder="Search...">

<table id="cdptable">

<tr>

<th>Neighbor</th>

<th>IP Address</th>

<th>Platform</th>

<th>Capabilities</th>

<th>Local Interface</th>

<th>Remote Interface</th>

<th>Holdtime</th>

<th>Version</th>

</tr>

"""

for n in neighbors:

    html += f"""

<tr>

<td>{n['Device ID']}</td>

<td>{n['IP Address']}</td>

<td>{n['Platform']}</td>

<td>{n['Capabilities']}</td>

<td>{n['Local Interface']}</td>

<td>{n['Remote Interface']}</td>

<td>{n['Holdtime']}</td>

<td>{n['Version']}</td>

</tr>

"""

html += """

</table>

</body>

</html>

"""

if match:
    hostname = match.group(1)

OUTPUT_FILE = f"{hostname}_CDP_Report.html"
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Report generated successfully: {OUTPUT_FILE}")