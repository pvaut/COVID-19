import csv
import math
from typing import List, Optional
import itertools
from pathlib import Path
from util import smart_string_to_float
from constants import DATA_DIR

"""
Loads country indicator data from file downloads from https://data.worldbank.org/indicator.
These classes directly read the format as downloaded from that site
"""


default_transformer = {
    'TransformValue': lambda x: x,
    'TransformTitle': lambda x: x,
}

log_transformer = {
    'TransformValue': lambda x: math.log10(x) if x is not None else None,
    'TransformTitle': lambda x: f'log10 {x}',
}

# Used to tweak some of the indicator data set (e.g. shorten a title, apply a log transform
transformers = {
    'NY.GDP.PCAP.CD': log_transformer,
    'EN.POP.DNST': log_transformer,
    'EN.ATM.PM25.MC.M3': {
        'TransformValue': lambda x: x,
        'TransformTitle': lambda x: 'PM2.5 air poll., mean ann. exp. (micrograms per m3)',
    }
}

class GeoRegionsIndicator:
    """Loads a single indicator from the source folder"""

    def __init__(self, id: str):
        indicator_dir = f'{DATA_DIR}/ref_data/{id}'
        p = Path(indicator_dir)
        # Figure out what are the files to look for in the folder
        filename_datafile = None
        filename_metadata = None
        for item in p.iterdir():
            if item.name.startswith('API'):
                filename_datafile = item.name
            if item.name.startswith('Metadata_Indicator'):
                filename_metadata = item.name
        assert filename_datafile
        assert filename_metadata

        # Load & parse the metadata
        with open(f'{indicator_dir}/{filename_metadata}') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=',')
            data = [row for row in csv_reader]
            assert(len(data) == 1)
            self._indicator_code = data[0]['\ufeff"INDICATOR_CODE"']
            self._indicator_name = data[0]['INDICATOR_NAME']

        # Load the transformer, and apply it to the indicator name
        transformer = default_transformer
        if self._indicator_code in transformers:
            transformer = transformers[self._indicator_code]
        self._indicator_name = transformer['TransformTitle'](self._indicator_name)

        # Load the actual data
        with open(f'{indicator_dir}/{filename_datafile}') as csvfile:
            csv_reader = csv.reader(itertools.islice(csvfile, 4, None), delimiter=',')
            header = next(csv_reader)
            data = [row for row in csv_reader]
        self._total_region_count = len(data)

        # Look for the most recent year that contains data for the maximum number of regions
        # This year will be used to fetch the indicator data
        max_datapoints_count = 0
        max_datapoints_colnr = None
        for col_nr in range(4, len(header) - 1):
            datapoints_count = 0
            for row in data:
                if row[col_nr]:
                    datapoints_count += 1
            if datapoints_count >= max_datapoints_count:
                max_datapoints_count = datapoints_count
                max_datapoints_colnr = col_nr
        assert max_datapoints_colnr
        assert max_datapoints_count > 0
        self._used_year = header[max_datapoints_colnr]
        self._datapoint_count = max_datapoints_count
        self._indicator_name += f'\n({self._used_year})'

        # Build the regions data using the chosen year, applying the transformation
        transform_value = transformer['TransformValue']
        self._regions = [{
            'Name': row[0],
            'Code': row[1],
            'Value': transform_value(smart_string_to_float(row[max_datapoints_colnr]))
        } for row in data]

        # Build an index for faster lookup
        self._regions_idx = {region['Code']: region for region in self._regions}

    def get_id(self) -> str:
        return self._indicator_code

    def get_name(self) -> str:
        return self._indicator_name

    def get_region_value(self, region_code: str) -> Optional[float]:
        if region_code not in self._regions_idx:
            return None
        return self._regions_idx[region_code]['Value']

    def log_dump(self):
        print(f'INDICATOR {self._indicator_code}; Year={self._used_year}; Data points={self._datapoint_count}')


def load_all_georegions_indicators() -> List[GeoRegionsIndicator]:
    """Loads all indicator folders in a predefined directory
       Indicator folders can be downloaded from https://data.worldbank.org/indicator"""
    indicators = []
    for item in Path(f'{DATA_DIR}/ref_data').iterdir():
        if item.name.startswith('API'):
            indicator = GeoRegionsIndicator(item.name)
            indicator.log_dump()
            indicators.append(indicator)
    return indicators
