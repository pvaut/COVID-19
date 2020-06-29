import math
from typing import Optional, List, Tuple
import datetime
from constants import SECONDS_IN_DAY


def smart_string_to_int(source_str: str) -> Optional[int]:
    return int(source_str) if source_str else None


def smart_string_to_float(source_str: str) -> Optional[float]:
    return float(source_str) if source_str else None


def moving_timewindow_average(
        timeseries: List[Tuple[datetime.datetime, float]], half_window: float
) -> List[Tuple[datetime.datetime, float]]:
    result = []
    # @todo: This is a temporary, inefficient implementation relying on a nested loop. Can be optimized
    # but keep in mind that the time series is not necessarily consecutive
    for point in timeseries:
        sum = 0
        count = 0
        for pt2 in timeseries:
            diff_days = math.fabs((point[0] - pt2[0]).total_seconds() / SECONDS_IN_DAY)
            if diff_days <= half_window:
                sum += pt2[1]
                count += 1
        result.append((point[0], sum / count if count > 0 else None))
    return result
