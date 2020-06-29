from epidata import EpiDataSeries, GET_DAILY_DEATHS_FRACTION, GET_DAILY_CASES_FRACTION


class FracDeathsToCases:

    @staticmethod
    def get_id() -> str:
        return 'DeathsToCasesFrac'

    @staticmethod
    def get_description() -> str:
        return 'Deaths to Cases (%)'

    @staticmethod
    def calc(epidata_series: EpiDataSeries):
        total_deaths = sum([pt[1] for pt in epidata_series.get_timeseries(GET_DAILY_DEATHS_FRACTION)])
        total_cases = sum([pt[1] for pt in epidata_series.get_timeseries(GET_DAILY_CASES_FRACTION)])
        return 100 * total_deaths / total_cases
