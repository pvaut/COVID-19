from epidata import EpiDataSeries, GET_DAILY_DEATHS_FRACTION
import math

class TotalDeathsFrac:

    @staticmethod
    def get_id() -> str:
        return 'TotDeathsFrac'

    @staticmethod
    def get_description() -> str:
        return 'Total deaths (population %, log10)'

    @staticmethod
    def calc(epidata_series: EpiDataSeries):
        time_series = epidata_series.get_timeseries(GET_DAILY_DEATHS_FRACTION)
        total = sum([pt[1] for pt in time_series])
        if total == 0:
            return None
        return math.log10(100 * total)
