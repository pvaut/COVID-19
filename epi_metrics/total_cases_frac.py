from epidata import EpiDataSeries, GET_DAILY_CASES_FRACTION
import math

class TotalCasesFrac:

    @staticmethod
    def get_id() -> str:
        return 'TotCasesFrac'

    @staticmethod
    def get_description() -> str:
        return 'Total cases (population %, log10)'

    @staticmethod
    def calc(epidata_series: EpiDataSeries):
        time_series = epidata_series.get_timeseries(GET_DAILY_CASES_FRACTION)
        total = math.log10(100 * sum([pt[1] for pt in time_series]))
        if total == 0:
            return None
        return total
