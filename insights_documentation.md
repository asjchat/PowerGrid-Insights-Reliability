# Grid Insights Dashboard Documentation

## Data Sources

The primary source for outage and reliability data is the U.S. Energy Information Administration (EIA), specifically the [Annual Electric Power Industry Report](https://www.eia.gov/electricity/annual/).  
The dataset includes state-level measures of electric reliability as reported by utilities and compiled by EIA. Key indices are SAIDI, SAIFI, and CAIDI, which are widely adopted in reliability engineering.

## Metrics

- **SAIDI (System Average Interruption Duration Index)**: Average total duration of interruptions experienced by a customer in a year, in minutes per customer.  
- **SAIFI (System Average Interruption Frequency Index)**: Average number of interruptions experienced by a customer in a year, in interruptions per customer.  
- **CAIDI (Customer Average Interruption Duration Index)**: Average duration of an interruption per customer, equal to SAIDI divided by SAIFI. Expressed in minutes per interruption.

These metrics are reported by state and aggregated to produce national averages.  

## Statistical Methodology

1. **Correlation Analysis**  
   - Pearson correlation coefficients were calculated between SAIDI, SAIFI, and CAIDI across the period 2013–2023.  
   - Results show strong associations: SAIDI and CAIDI correlation ≈ 0.92; SAIDI and SAIFI correlation ≈ 0.59.  
   - Interpretation: states with longer average outage durations often also experience higher interruption frequencies or longer restoration times.

2. **Trend Estimation**  
   - Linear regression slopes were calculated for each state to capture changes over time.  
   - For example, Rhode Island, South Carolina, and South Dakota displayed negative slopes in CAIDI and SAIDI, indicating reduced outage durations over the decade.  
   - Louisiana exhibited positive slopes in CAIDI (+69.8 minutes per year) and SAIDI (+218.7 minutes per year), reflecting upward trends in those indices.

3. **Variability Assessment**  
   - Standard deviation of SAIDI was computed year-over-year to highlight sensitivity to extreme weather.  
   - For instance, standard deviation ranged from ~156 minutes (2015) to ~855 minutes (2021).  

## Project Context

The Grid Insights Dashboard was designed to:  
- Visualize national and state-level reliability patterns across 2013–2023.  
- Integrate written insights with interactive charts to give stakeholders both quantitative and narrative understanding.  
- Provide contextual explanations for spikes and variability, especially those linked to weather events (e.g., Hurricanes Harvey, Irma, Maria in 2017, and the Texas winter storm in 2021).  

## Scope and Limitations

- Data reflects reported values from utilities; reporting practices and definitions may vary slightly across jurisdictions.  
- Extreme weather significantly influences reliability indices and can cause year-to-year volatility.  
- The dashboard focuses on historical patterns and does not provide predictive modeling.  
- Outage causes are not separately categorized (e.g., equipment failure vs. natural disasters).  

## Interpretation Guidance

- Improvements in infrastructure, grid hardening, and system automation are often reflected in declining trends in SAIDI, SAIFI, and CAIDI.  
- Strong correlations across the indices imply that targeted investments can improve multiple aspects of reliability simultaneously.  
- States differ in geography, weather exposure, and grid infrastructure, all of which shape the observed reliability metrics.  

---

_Last updated: 2025_  
