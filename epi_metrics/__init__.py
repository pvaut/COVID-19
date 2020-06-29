from epi_metrics.total_cases_frac import TotalCasesFrac
from epi_metrics.total_deaths_frac import TotalDeathsFrac
from epi_metrics.frac_deaths_cases import FracDeathsToCases
from epi_metrics.max_cases_rate import MaxCasesRate
from epi_metrics.max_deaths_rate import MaxDeathsRate

"""Factory list of all metrics that will be calculated on epi data"""
epi_metrics_list = [
    FracDeathsToCases,
    MaxDeathsRate,
    TotalDeathsFrac,
    MaxCasesRate,
    TotalCasesFrac,
]

def get_epi_metrics_list():
    return epi_metrics_list

def calc_all_metrics(world_epi_data):
    """Calculate a range of aggregating metrics, and add them to the data"""
    for country in world_epi_data.get_all_countries():
        for metric in epi_metrics_list:
            value = metric.calc(country.get_data())
            country.add_metric(metric.get_id(), value)