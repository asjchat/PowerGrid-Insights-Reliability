
"""
grid‑style interactive dashboard for U.S. distribution reliability

This Dash application reads the consolidated IEEE reliability dataset
produced from the CAIDI, SAIDI and SAIFI by state (2013–2023).
It provides an interactive USA map and a companion line chart.  Users
can filter by metric (CAIDI, SAIDI or SAIFI), category (All events,
Without major event days, Loss of supply removed) and year.  As the
selections change the map and charts update, and a short narrative
highlights key insights.  The narrative adopts a professional tone
similar to a grid Insights piece, helping the user interpret
variations across states and over time.

To run this dashboard locally:
    python grid_dashboard.py
Then open the displayed URL in your web browser.
"""

import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# ---- Style + copy constants ----
SUBTEXT_STYLE = {
    "textAlign": "center",
    "color": "#6c757d",
    "fontSize": "14px",
    "margin": "0 auto 12px",
    "maxWidth": "900px",
}

CARD_STYLE = {
    "border": "1px solid #e5e7eb",
    "borderRadius": "10px",
    "padding": "12px 14px",
    "margin": "8px 0",
    "boxShadow": "0 1px 2px rgba(0,0,0,0.05)",
    "backgroundColor": "white",
}

CONTAINER_STYLE = {
    "maxWidth": "900px",
    "margin": "0 auto 20px",
}

EXEC_SUMMARY_MD = """
**Executive summary**

- **SAIDI** (duration) is most sensitive to **storms/major events**, **crew response**, and **automation**.
- **SAIFI** (frequency) correlates strongly with **vegetation exposure**, **weather**, and **asset age**.
- Use the map to inspect a year’s conditions; click states to compare their **trends** on the right.
"""


# Load the consolidated dataset.  It is expected to live in the same
# directory as this script.  The dataset contains state names, years
# and nine metric columns (CAIDI/SAIDI/SAIFI × 3 categories).  We
# convert numeric columns on load.
DATA_PATH = "consolidated_ieee_data_by_state_year.csv"


def load_data(path: str) -> pd.DataFrame:
    """Load the reliability dataset and ensure numeric types."""
    df = pd.read_csv(path)
    numeric_cols = [c for c in df.columns if c not in ["State", "Year"]]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


df = load_data(DATA_PATH)

# Mapping of full state names to postal abbreviations required for
# Plotly's choropleth.  States not present (e.g., District of
# Columbia) fall back to their standard postal code.
STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}


def filter_data(df: pd.DataFrame, metric: str, category: str, year: int) -> pd.DataFrame:
    """
    Return a subset of the data for a given metric, category and year.

    Parameters
    ----------
    df: DataFrame
        The full reliability dataset
    metric: str
        One of 'CAIDI', 'SAIDI' or 'SAIFI'
    category: str
        One of 'All Events', 'Without Major Event Days' or
        'Loss of Supply Removed'
    year: int
        The year to filter on

    Returns
    -------
    DataFrame
        A subset with columns ['State', 'MetricValue'], where
        MetricValue is the selected metric/category for the specified
        year.
    """
    # Construct the column name based on metric and category
    cat_key_map = {
        "All Events": "All_Events",
        "Without Major Event Days": "Without_Major_Event_Days",
        "Loss of Supply Removed": "Loss_of_Supply_Removed",
    }
    col = f"{metric}_{cat_key_map[category]}"
    subset = df[df["Year"] == year][["State", col]].copy()
    subset.rename(columns={col: "MetricValue"}, inplace=True)
    return subset


def compute_insights(subset: pd.DataFrame, metric: str, category: str) -> str:
    """
    Generate a narrative insight string for the selected subset.

    The narrative highlights which state has the highest and lowest
    values and quantifies the gap.  It adopts a concise, analytic tone.
    """
    if subset.empty:
        return "No data available for the selected filters."
    max_row = subset.loc[subset["MetricValue"].idxmax()]
    min_row = subset.loc[subset["MetricValue"].idxmin()]
    gap = max_row["MetricValue"] - min_row["MetricValue"]
    metric_label = {
        "CAIDI": "average restoration time (CAIDI)",
        "SAIDI": "total outage duration (SAIDI)",
        "SAIFI": "outage frequency (SAIFI)",
    }[metric]
    category_desc = {
        "All Events": "including major events",
        "Without Major Event Days": "excluding major event days",
        "Loss of Supply Removed": "excluding loss of supply",
    }[category]
    insight = (
        f"The highest {metric_label} {category_desc} in the selected year occurs in {max_row['State']} "
        f"({max_row['MetricValue']:.1f}), while the lowest is in {min_row['State']} "
        f"({min_row['MetricValue']:.1f}). This represents a gap of {gap:.1f}."
    )
    return insight


def make_map_figure(subset: pd.DataFrame, metric: str) -> px.choropleth:
    """Create a choropleth map of the USA for the given metric subset."""
    subset = subset.copy()
    subset["StateCode"] = subset["State"].map(STATE_ABBREV).fillna(subset["State"])
    color_continuous_scale = {
        "CAIDI": "Blues",
        "SAIDI": "Greens",
        "SAIFI": "Reds",
    }[metric]
    fig = px.choropleth(
        subset,
        locations="StateCode",
        locationmode="USA-states",
        color="MetricValue",
        hover_name="State",
        color_continuous_scale=color_continuous_scale,
        scope="usa",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(title=metric),
    )
    return fig


def make_line_figure(df: pd.DataFrame, metric: str, category: str, states: list[str]) -> px.line:
    """
    Create a line chart showing the selected metric over time for one or
    more states.  If no states are selected, display the national
    average instead.
    """
    cat_key_map = {
        "All Events": "All_Events",
        "Without Major Event Days": "Without_Major_Event_Days",
        "Loss of Supply Removed": "Loss_of_Supply_Removed",
    }
    col = f"{metric}_{cat_key_map[category]}"
    if states:
        data = df[df["State"].isin(states)][["State", "Year", col]].dropna()
    else:
        # Show national average across all states
        data = df.groupby("Year")[col].mean().reset_index()
        data["State"] = "National average"
    fig = px.line(
        data,
        x="Year",
        y=col if states else col,
        color="State",
        markers=True,
    )
    y_label = {
        "CAIDI": "Minutes per interruption",
        "SAIDI": "Minutes per year",
        "SAIFI": "Interruptions per year",
    }[metric]
    fig.update_layout(
        yaxis_title=y_label,
        xaxis_title="Year",
        legend_title="State",
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1(
            "U.S. Distribution Reliability Dashboard",
            style={"textAlign": "center", "marginTop": 20},
        ),
        html.P(
            "Explore how distribution reliability has evolved across the United States. "
            "Select a reliability metric (CAIDI, SAIDI or SAIFI) and a category to display a choropleth map. "
            "Use the year slider to examine conditions for any year from 2013 to 2023. "
            "Click on states in the map to compare their trends over time. The narrative below provides a brief analytic insight for your current selection.",
            style={"textAlign": "center", "maxWidth": "900px", "margin": "auto", "paddingBottom": "20px"},
        ),
        html.Div([
            html.Div([
                html.P("Key metrics and documentation", style=SUBTEXT_STYLE),
                html.Details([
                    html.Summary("Executive Summary"),
                    dcc.Markdown(EXEC_SUMMARY_MD)
                ], style={**CARD_STYLE}),
                html.Details([
                    html.Summary("Metrics Definitions"),
                    html.Div([
                        html.P([html.Strong("SAIDI"), ": System Average Interruption Duration Index. Average total outage duration per customer per year. Minutes per customer."], style={"marginBottom": "8px"}),
                        html.P([html.Strong("SAIFI"), ": System Average Interruption Frequency Index. Average number of interruptions per customer per year. Interruptions per customer."], style={"marginBottom": "8px"}),
                        html.P([html.Strong("CAIDI"), ": Customer Average Interruption Duration Index. Average time to restore service per interruption. Equals SAIDI divided by SAIFI. Minutes per interruption."]),
                    ], style={"marginTop": "10px"})
                ], style={**CARD_STYLE}),
            ], style=CONTAINER_STYLE)
        ]),

        html.Div(
            [
                html.Div(
                    [
                        html.Label("Select Metric"),
                        dcc.Dropdown(
                            id="metric-dropdown",
                            options=[
                                {"label": "Average restoration time (CAIDI)", "value": "CAIDI"},
                                {"label": "Total outage duration (SAIDI)", "value": "SAIDI"},
                                {"label": "Outage frequency (SAIFI)", "value": "SAIFI"},
                            ],
                            value="CAIDI",
                            clearable=False,
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block", "padding": "0 20px"},
                ),
                html.Div(
                    [
                        html.Label("Select Category"),
                        dcc.Dropdown(
                            id="category-dropdown",
                            options=[
                                {"label": "All Events (with major events)", "value": "All Events"},
                                {"label": "Without Major Event Days", "value": "Without Major Event Days"},
                                {"label": "Loss of Supply Removed", "value": "Loss of Supply Removed"},
                            ],
                            value="All Events",
                            clearable=False,
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block", "padding": "0 20px"},
                ),
                html.Div(
                    [
                        html.Label("Select Year"),
                        dcc.Slider(
                            id="year-slider",
                            min=int(df["Year"].min()),
                            max=int(df["Year"].max()),
                            step=1,
                            value=int(df["Year"].min()),
                            marks={int(y): str(y) for y in sorted(df["Year"].unique())},
                            tooltip={"always_visible": True, "placement": "bottom"},
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block", "padding": "0 20px"},
                ),
            ],
            style={"display": "flex", "justifyContent": "center", "paddingBottom": "20px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id="map-graph"),
                    ],
                    style={"width": "60%", "display": "inline-block", "verticalAlign": "top"},
                ),
                html.Div(
                    [
                        dcc.Graph(id="line-graph"),
                    ],
                    style={"width": "40%", "display": "inline-block", "verticalAlign": "top"},
                ),
            ],
            style={"width": "100%", "display": "flex"},
        ),
        html.Div(
            [
                html.H4("Analytic Insight", style={"paddingTop": "20px"}),
                html.Div(id="insight-text", style={"fontSize": "16px", "lineHeight": "1.4", "maxWidth": "900px", "margin": "auto"}),
            ],
            style={"paddingTop": "20px", "textAlign": "center"},
        ),
    ],
    style={"fontFamily": "Arial, sans-serif", "padding": "20px"},
)


@app.callback(
    Output("map-graph", "figure"),
    Output("insight-text", "children"),
    Input("metric-dropdown", "value"),
    Input("category-dropdown", "value"),
    Input("year-slider", "value"),
)
def update_map(metric: str, category: str, year: int):
    """Update the map and insight when controls change."""
    subset = filter_data(df, metric, category, year)
    fig = make_map_figure(subset, metric)
    insight = compute_insights(subset, metric, category)
    return fig, insight


@app.callback(
    Output("line-graph", "figure"),
    Input("metric-dropdown", "value"),
    Input("category-dropdown", "value"),
    Input("map-graph", "clickData"),
)
def update_line(metric: str, category: str, click_data):
    """
    Update the line chart based on the selected state(s).  If the user
    clicks on one or more states in the map, the line chart shows those
    states.  Otherwise it displays the national average.
    """
    states: list[str] = []
    if click_data and "points" in click_data:
        # Extract state names from the hover text of clicked points
        states = [pt.get("hovertext") for pt in click_data.get("points", [])]
    fig = make_line_figure(df, metric, category, states)
    return fig


if __name__ == "__main__":
    app.run(debug=True)

