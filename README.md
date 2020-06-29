
# COVID-19 - Indicator correlator

This program performs a visual correlation analysis between two sets of factors, each of them present at a country level:
 1. Epidemiological metrics derived from https://data.europa.eu/euodp/en/data/dataset/covid-19-coronavirus-data
 2. Indicator data, downloaded from https://data.worldbank.org
 
 New epi metrics can be added using a simple factory model. New indicator data can be added by downloading additional indicators from https://data.worldbank.org, and adding it as a folder to `data/ref_data`.
 
 For now, choices (such as filters on countries) must be set via code in `main.py`.
 
 IMPORTANT NOTE: This program is intended as an exploratory analysis tool only. Keep in mind that correlation does not mean causality! 
 
 Example visualisations:
 
