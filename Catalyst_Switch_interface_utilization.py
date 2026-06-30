import re
import os
import pandas as pd
from datetime import datetime

all_data = []

# Process all TXT files
for filename in os.listdir("."):

    if not filename.lower().endswith(".txt"):
        continue

    with open(filename, "r", encoding="utf-8") as f:
        output = f.read()

    # Get hostname from prompt
    hostname_match = re.search(
        r'^\s*([A-Za-z0-9._-]+)[#>]',
        output,
        re.MULTILINE
    )

    if hostname_match:
        device_name = hostname_match.group(1)
    else:
        device_name = filename.replace(".txt", "")

    # Find UP/UP interfaces
    interfaces = re.findall(
        r'(\S+) is up, line protocol is up(.*?)'
        r'5 minute input rate (\d+) bits/sec.*?'
        r'5 minute output rate (\d+) bits/sec',
        output,
        re.DOTALL
    )

    for iface, block, in_rate, out_rate in interfaces:

        desc_match = re.search(r'Description:\s*(.*)', block)
        description = desc_match.group(1).strip() if desc_match else "No Description"

        bw_match = re.search(r'BW (\d+) Kbit', block)
        bandwidth_kbit = int(bw_match.group(1)) if bw_match else 0

        bandwidth_mbps = round(bandwidth_kbit / 1000, 2)

        in_rate = int(in_rate)
        out_rate = int(out_rate)

        input_mbps = round(in_rate / 1000000, 2)
        output_mbps = round(out_rate / 1000000, 2)

        if bandwidth_kbit > 0:
            input_util = round((in_rate / (bandwidth_kbit * 1000)) * 100, 2)
            output_util = round((out_rate / (bandwidth_kbit * 1000)) * 100, 2)
        else:
            input_util = 0
            output_util = 0

        max_util = max(input_util, output_util)

        if max_util >= 80:
            severity = "Critical"
        elif max_util >= 50:
            severity = "High"
        elif max_util >= 20:
            severity = "Medium"
        elif max_util > 0:
            severity = "Low"
        else:
            severity = "No Traffic"

        all_data.append([
            device_name,
            iface,
            description,
            bandwidth_mbps,
            input_mbps,
            output_mbps,
            input_util,
            output_util,
            severity,
            max_util
        ])

# Create DataFrame
df = pd.DataFrame(
    all_data,
    columns=[
        "Device",
        "Interface",
        "Description",
        "Bandwidth_Mbps",
        "Input_Mbps",
        "Output_Mbps",
        "Input_Util_%",
        "Output_Util_%",
        "Severity",
        "Max_Util_%"
    ]
)

# Sort
df = df.sort_values(
    by=["Device", "Max_Util_%"],
    ascending=[True, False]
)

# Console Output
print("\n========== INTERFACE UTILIZATION REPORT ==========\n")

for device in sorted(df["Device"].unique()):

    print("=" * 70)
    print(f"Device: {device}")
    print("=" * 70)

    device_df = df[df["Device"] == device]

    print(
        device_df[
            [
                "Interface",
                "Description",
                "Bandwidth_Mbps",
                "Input_Mbps",
                "Output_Mbps",
                "Input_Util_%",
                "Output_Util_%",
                "Severity",
                "Max_Util_%"
            ]
        ].to_string(index=False)
    )

    print()

# Save CSV
df.to_csv("All_Switch_Interface_Report.csv", index=False)

# Build HTML
html = f"""
<html>
<head>
<title>Interface Utilization Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 20px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 30px;
}}

th {{
    background-color: #003366;
    color: white;
    padding: 8px;
}}

td {{
    border: 1px solid #cccccc;
    padding: 8px;
}}

h2 {{
    background-color: #003366;
    color: white;
    padding: 8px;
}}

.critical {{ background-color: #ff4d4d; color: white; }}
.high {{ background-color: #ff9933; }}
.medium {{ background-color: #ffff66; }}
.low {{ background-color: #ccffcc; }}
.notraffic {{ background-color: #e0e0e0; }}

</style>
</head>
<body>

<h1>Interface Utilization Report</h1>
<p>Generated: {datetime.now()}</p>
"""

for device in sorted(df["Device"].unique()):

    html += f"<h2>{device}</h2>"

    html += """
    <table>
    <tr>
        <th>Interface</th>
        <th>Description</th>
        <th>Bandwidth</th>
        <th>Input Mbps</th>
        <th>Output Mbps</th>
        <th>Input Util %</th>
        <th>Output Util %</th>
        <th>Severity</th>
    </tr>
    """

    device_df = df[df["Device"] == device]

    for _, row in device_df.iterrows():

        css = row["Severity"].lower().replace(" ", "")

        html += f"""
        <tr class="{css}">
            <td>{row['Interface']}</td>
            <td>{row['Description']}</td>
            <td>{row['Bandwidth_Mbps']}</td>
            <td>{row['Input_Mbps']}</td>
            <td>{row['Output_Mbps']}</td>
            <td>{row['Input_Util_%']}</td>
            <td>{row['Output_Util_%']}</td>
            <td>{row['Severity']}</td>
        </tr>
        """

    html += "</table>"

html += """
</body>
</html>
"""

html_file = f"{device_name}_Interface_Utilization_Report.html"
csv_file = f"{device_name}_Interface_Utilization_Report.csv"

with open(html_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"CSV report saved: {csv_file}")
print(f"HTML report saved: {html_file}")