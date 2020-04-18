from datetime import datetime
from decimal import Decimal, getcontext
import pytz


from plotly.subplots import make_subplots
import plotly.graph_objects as go


getcontext().prec = 3

tz = pytz.timezone('Europe/Madrid')

x_dates = []
y_pm25 = []
y_pm10 = []
with open('hourly.csv', 'r') as csvfile:
    for line in csvfile:
        ts, pm25, pm10 = line.split(',')
        x_dates.append(datetime.fromtimestamp(int(ts), tz=tz))
        y_pm25.append(Decimal(pm25))
        y_pm10.append(Decimal(pm10))


pm25_limit = max(y_pm25)
pm25_zones =[
    ("#79bc6a", (0, 15)),
    ("#bbcf4c", (15, 30)),
    ("#eec20b", (30, 55)),
    ("#f29305", (55, 110)),
    ("#e8416f", (110, max(110, pm25_limit+10))),
]

pm10_limit = max(y_pm10)
pm10_zones =[
    ("#79bc6a", (0, 25)),
    ("#bbcf4c", (25, 50)),
    ("#eec20b", (50, 90)),
    ("#f29305", (90, 180)),
    ("#e8416f", (180, max(180, pm10_limit+10))),
]


def get_color(value, zones):
  for color, (lower, upper) in zones:
    if lower <= value < upper:
      return color



fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
pm25_row = 1
pm10_row = 2


for name, zones, row in (('PM 2.5 limit', pm25_zones, pm25_row), ('PM 10 limit', pm10_zones, pm10_row)):
    for color, (lower, upper) in zones:
        if pm10_limit > lower:
            fig.add_shape(
                type="rect",
                x0=x_dates[0],
                y0=lower,
                x1=x_dates[-1],
                y1=upper,
                name=name,
                line_width=0,
                fillcolor=color,
                opacity=0.3,
                layer="below",
                row=row, col=1
            )

fig.add_trace(go.Scatter(x=x_dates, y=y_pm25, mode='lines', name='PM 2.5'), row=pm25_row, col=1)
fig.add_trace(go.Scatter(x=x_dates, y=y_pm10, mode='lines', name='PM 10'), row=pm10_row, col=1)

layout = {
  "title": "μg/m3 average per hour",
  "hovermode": "x unified",
  "xaxis": {
    "type": "date",
    "rangeslider": {},
    "rangeselector": {"buttons": [
        {
          "step": "day",
          "count": 7,
          "label": "1w",
          "stepmode": "backward"
        },
        {
          "step": "month",
          "count": 1,
          "label": "1m",
          "stepmode": "backward"
        },
        {
          "step": "month",
          "count": 6,
          "label": "6m",
          "stepmode": "backward"
        },
        {
          "step": "year",
          "count": 1,
          "label": "YTD",
          "stepmode": "todate"
        },
        {
          "step": "year",
          "count": 1,
          "label": "1y",
          "stepmode": "backward"
        },
        {"step": "all"}
      ]}
  },
}
fig.update_layout(layout)

chart_html = fig.to_html("index.html", include_plotlyjs="cdn", full_html=False)


doc_html = f"""\
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Air Quality</title>
        <meta name="description" content="Air Quality Monitoring Station">
        <meta name="author" content="Jorge Barata">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel='shortcut icon' type='image/x-icon' href='favicon.png' />
        <style>
            body {{
                font-family: "Open Sans", verdana, arial, sans-serif;
                color: #2A3F57;
            }}
            main {{
              margin-right: auto;
              margin-left: auto;
              max-width: 960px;
            }}
            footer {{
                text-align: center;
            }}
            h1 img {{
                height: 1em;
                vertical-align: text-bottom;
                padding-right: 0.5em;
            }}
            th, td {{
                padding: 0 20px;
                font-size: 90%;
            }}
            big {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <main>
        <h1><img src="airquality.svg">Air Quality</h1>

        <table>
        <tbody>
        <tr>
        <th><abbr title="Fine particulate matter with a diameter smaller than 2.5 micrometers (μm)">PM<sub>2.5</sub></abbr></th>
        <th><abbr title="Coarse particulate matter with a diameter between 2.5 and 10 micrometers (μm)">PM<sub>10</sub></abbr></th>
        <th>Last update</th>
        </tr>
        <tr>
        <td style="color:{ get_color(y_pm25[-1], pm25_zones) };"><big>{y_pm25[-1]}</big></td>
        <td style="color:{ get_color(y_pm10[-1], pm10_zones) };"><big>{y_pm10[-1]}</big></td>
        <td>{ datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M:%S") }</td>
        </tr>
        </tbody>
        </table>


        {chart_html}


<h2>Air Quality in Madrid</h2>
<ul>
  <li><a href="https://idem.madrid.org/visor/?v=calidadaire&ZONE=430000,4485000,8" target="_blank">Comunidad de Madrid</a></li>
  <li><a href="https://www.eltiempo.es/calidad-aire/madrid" target="_blank">El Tiempo</a></li>
</ul>
<br/>

<h2> European Union: CAQI Air quality index </h2>
<table style="text-align:center;">

<tbody><tr>
<th>Qualitative name</th>
<th colspan="2">Hourly concentration (μg/m<sup>3)</sup>
</th></tr>
<tr>
<th></th>
<th>PM<sub>2.5</sub>
<th>PM<sub>10</sub></th>
</th></tr>
<tr>
<td style="background:#79bc6a;">Very low</td>
<td>0–15</td>
<td>0–25</td>
</tr>
<tr>
<td style="background:#bbcf4c;">Low</td>
<td>15–30</td>
<td>25–50</td>
</tr>
<tr>
<td style="background:#eec20b;">Medium</td>
<td>30–55</td>
<td>50–90</td>
</tr>
<tr>
<td style="background:#f29305;">High</td>
<td>55–110</td>
<td>90–180</td>
</tr>
<tr>
<td style="background:#e8416f;">Very high</td>
<td>&gt;110</td>
<td>&gt;180</td>
</tr>
</tbody>
</table>

<p><a href="https://www.airqualitynow.eu/download/CITEAIR-Comparing_Urban_Air_Quality_across_Borders.pdf">Source</a></p>
<br/>

<h2> WHO Air quality guideline values for PM</h2>

<table>
<tbody>
<tr>
<th>Timerange</th>
<th colspan="2">Safety levels (μg/m<sup>3)</th>
</tr>
<tr>
<th></th>
<th>PM<sub>2.5</sub></th>
<th>PM<sub>10</sub></th>
</tr>
<tr>
<td>Annual mean</td>
<td>&lt;10</td>
<td>&lt;20</td>
</tr>
<tr>
<td>24-hour mean</td>
<td>&lt;25</td>
<td>&lt;50</td>
</tr>
</tbody>
</table>



<p><a href="https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health">Source</a></p>


        <footer>
        <small>Work In Progress | Made by <a href="http://jorgebg.com">Jorge Barata</a> | <a href="https://github.com/jorgebg/airquality">Source Code</a></small>
        </footer>
        </main>
    </body>
</html>
"""

with open("index.html", 'w') as f:
    f.write(doc_html)
