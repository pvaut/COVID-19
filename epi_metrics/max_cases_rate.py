from epidata import EpiDataSeries, GET_DAILY_CASES_FRACTION
import math
from util import moving_timewindow_average


class MaxCasesRate:

    @staticmethod
    def get_id() -> str:
        return 'MaxCasesRate'

    @staticmethod
    def get_description() -> str:
        return 'Max cases rate (14-days window, log10)'

    @staticmethod
    def calc(epidata_series: EpiDataSeries):
        time_series = epidata_series.get_timeseries(GET_DAILY_CASES_FRACTION)
        smoothed_time_series = moving_timewindow_average(time_series, 7)
        max_point = max(smoothed_time_series, key=lambda pt: pt[1])
        return math.log10(max_point[1])
