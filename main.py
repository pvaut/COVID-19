from epidata import WorldEpiData
from epi_metrics import calc_all_metrics, get_epi_metrics_list
from georegions_indicators import load_all_georegions_indicators
from correlation_gallery import CorrelationGallery, CorrelationFactor


# Load the COVID-19 epi data
world_epi_data = WorldEpiData('COVID-19_cases_worldwide')


# Apply some filters
world_epi_data.filter_continent('Africa')
world_epi_data.filter_min_population_size(100000)
world_epi_data.filter_min_total_cases(200)


# Calculate all defined aggregation metrics on the epi data
calc_all_metrics(world_epi_data)


# Load all country indicators
# (these are direct dumps of https://data.worldbank.org/indicator, to be put as separate folders in data/ref_data)
indicators = load_all_georegions_indicators()


# Initiate the correlation gallery, showing a grid of correlations between
#   1. The country indicators
#   2. The epi metrics
corr_gallery = CorrelationGallery()


# Load the indicators as X axis factors
for indicator in indicators:
    corr_gallery.add_dimx_factor(CorrelationFactor(
        id=indicator.get_id(),
        name=indicator.get_name()
    ))


# Load the epi metrics as Y axis factors
for epi_metric in get_epi_metrics_list():
    corr_gallery.add_dimy_factor(CorrelationFactor(
        id=epi_metric.get_id(),
        name=epi_metric.get_description()
    ))


# Determine the maximum population size (used to scale the points in the correlation scatter plot points)
max_population = max([
    ctry.get_population_size()
    for ctry in world_epi_data.get_all_countries()
])


# Load all the country data points used for the correlation analysis,
# and set the values for both the epi metrics & indicator factors
for country in world_epi_data.get_all_countries():
    point_id = country.get_code()
    # Add the data point
    corr_gallery.add_datapoint(
        point_id=point_id,
        name=country.get_name(),
        size_frac=country.get_population_size() / max_population,
        color_cat=country.get_continent()
    )
    # Set the X values (indicators)
    for indicator in indicators:
        corr_gallery.add_dimx_value(
            point_id=point_id,
            factor_id=indicator.get_id(),
            value=indicator.get_region_value(point_id)
        )
    # Set the Y values (epi metrics)
    for epi_metric in get_epi_metrics_list():
         corr_gallery.add_dimy_value(
             point_id=point_id,
             factor_id=epi_metric.get_id(),
             value=country.get_metric(epi_metric.get_id())
         )


# Perform the calculations & create the plot
corr_gallery.calc_correlations()
corr_gallery.sort_dimx_by_significance(dimy_factor='TotCasesFrac')
corr_gallery.create_chart(show_labels=False, color_by_significance=True)
