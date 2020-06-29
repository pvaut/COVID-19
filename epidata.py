import datetime
import csv
from typing import Dict, List, Tuple, Optional, Callable
from constants import DATA_DIR, START_DATE, SECONDS_IN_DAY


GET_DAILY_CASES = lambda x: x.daily_cases
GET_DAILY_CASES_FRACTION = lambda x: x.daily_cases_fraction
GET_DAILY_DEATHS = lambda x: x.daily_deaths
GET_DAILY_DEATHS_FRACTION = lambda x: x.daily_deaths_fraction


class DateEpiData:
    """A single data point in an epi data time series"""

    def __init__(self, row: Dict[str, str]):
        """Loads tbe data point from the source file record values"""
        self.date_string = row['dateRep']
        self.day = int(row['day'])
        self.month = int(row['month'])
        self.year = int(row['year'])
        self.date = datetime.datetime(self.year, self.month, self.day)
        self.daily_cases = int(row['cases'])
        self.daily_deaths = int(row['deaths'])
        self.elapsed_days = round((self.date - START_DATE).total_seconds() / SECONDS_IN_DAY)
        self.daily_cases_fraction = None
        self.daily_deaths_fraction = None


class EpiDataSeries:
    """An epi data time series"""
    def __init__(self):
        self.data_points: List[DateEpiData] = []
        self._total_cases: Optional(int) = None

    def add_data_point(self, data_point: DateEpiData):
        self.data_points.append(data_point)

    def process(self, population_size: float):
        if population_size:
            for point in self.data_points:
                point.daily_cases_fraction = point.daily_cases / population_size
                point.daily_deaths_fraction = point.daily_deaths / population_size
        self.data_points.sort(key=lambda date: date.elapsed_days)
        assert self.data_points[0].elapsed_days >= 0
        self._total_cases = sum([pt.daily_cases for pt in self.data_points])

    def get_total_cases(self) -> int:
        return self._total_cases

    def get_timeseries(self, aspect_getter) -> List[Tuple[datetime.datetime, float]]:
        return [(point.date, aspect_getter(point)) for point in self.data_points]

    def log_dump(self):
        for date in self.data_points:
            print(f'{date.elapsed_days} {date.date_string} {date.cases} {date.deaths}')


class CountryEpiData:
    """Epi data for a single country"""

    def __init__(self, country_code: str, country_name: str, continent: str, population_size: float):
        if not(population_size):
            print(f'WARNING: {country_name} does not have population size')
        self._country_code = country_code
        self._country_name = country_name
        self._continent = continent
        self._population_size = population_size
        self._data: EpiDataSeries = EpiDataSeries()
        self._metrics = {}

    def get_code(self) -> str:
        return self._country_code

    def get_name(self) -> str:
        return self._country_name

    def get_continent(self) -> str:
        return self._continent

    def get_population_size(self) -> float:
        return self._population_size

    def add_data_row(self, row: Dict[str, str]):
        self._data.add_data_point(DateEpiData(row))

    def finalise_load(self):
        self._data.process(self._population_size)

    def get_data(self) -> EpiDataSeries:
        return self._data

    def has_population_size(self) -> bool:
        return (self._population_size != None) and (self._population_size > 0)

    def add_metric(self, id: str, value: float):
        self._metrics[id] = value

    def get_metric(self, id: str) -> float:
        assert id in self._metrics
        return self._metrics[id]

    def log_dump(self):
        print(f'COUNTRY CODE={self._country_code}; NAME={self._country_name}; POPULATION={self._population_size}')
        self._data.log_dump()


class WorldEpiData:
    """Epi data for all countries"""

    def __init__(self, data_file_name: str):
        self.countries: List[CountryEpiData] = []
        self.countries_idx: Dict[str, CountryEpiData] = dict()

        # load the data from the source file
        with open(f'{DATA_DIR}/{data_file_name}.csv') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=',')
            for row in csv_reader:
                country_code = row['countryterritoryCode']
                if country_code not in self.countries_idx:
                    country = CountryEpiData(
                        country_code,
                        row['countriesAndTerritories'],
                        row['continentExp'],
                        int(row['popData2019']) if row['popData2019'] else None
                    )
                    self.countries_idx[country_code] = country
                    self.countries.append(country)
                self.countries_idx[country_code].add_data_row(row)
        for country in self.countries:
            country.finalise_load()

    def apply_filter(self, filter: Callable[[str], bool], reason: str):
        accepted = []
        rejected = []
        for country in self.countries:
            if filter(country):
                accepted.append(country)
            else:
                rejected.append(country)
        self.countries = accepted
        print(f'COUNTRY FILTER STEP: {reason}; Removed:{[r.get_name() for r in rejected]}')

    def filter_min_total_cases(self, min_total_cases: int):
        self.apply_filter(
            lambda country: country.get_data().get_total_cases() >= min_total_cases,
            f'Minimum total cases: {min_total_cases}'
        )


    def filter_min_population_size(self, min_size: int):
        self.apply_filter(
            lambda country: country.has_population_size() and (country.get_population_size() >= min_size),
            f'Minimum population: {min_size}'
        )

    def filter_continent(self, continent: str):
        self.apply_filter(
            lambda c: c.get_continent() == continent,
            f'Restrict to continent {continent}'
        )

    def get_country(self, country_code: str) -> CountryEpiData:
        if country_code not in self.countries_idx:
            raise Exception(f'Invalid country code {country_code}')
        return self.countries_idx[country_code]

    def get_all_countries(self) -> List[CountryEpiData]:
        return self.countries
