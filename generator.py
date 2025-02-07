import datetime

import game

header = """
<!DOCTYPE html>
  <header>
    <link rel="stylesheet" href="nvl.css">
  </header>
  <body>
    <script src="nvl.js"></script> 
    <h1>NVL Season 24/25</h1>
    <table id="nvlTable">
      <thead>
        <tr>
          <th onclick="sortTable(0)">Date</th>
          <th onclick="sortTable(1)">Time</th>
          <th onclick="sortTable(2)">ID</th>
          <th onclick="sortTable(3)">Division</th>
          <th onclick="sortTable(5)" colspan='7'>Teams & Results</th>
          <th onclick="sortTable(7)">Venue</th>
          <th onclick="sortTable(8)">Ref 1</th>
          <th onclick="sortTable(9)">Ref 2</th>
        </tr>
      </thead>
      <tbody>
"""

def generate_html(games):
    body = ""
    # for g in sorted(games, key=lambda x: x.timestamp):
    for g in sorted(games, key=lambda x: (x.timestamp, x.division, x.number)):
        body += g.as_table_row()

    footer = f"""
          </tbody>
        </table>
        {len(games)} rows - {str(datetime.datetime.now())}
      </body>
    </html>      
    """

    print("Saving calendar...")
    with open("calendar.html", "w") as f:
        f.write(header)
        f.write(body)
        f.write(footer)
