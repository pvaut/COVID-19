import math
from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.stats import spearmanr


def expand_range(value_range: Tuple[float, float], factor: float) -> Tuple[float, float]:
    mn, mx = value_range
    if (mn is None) or (mx is None):
        return value_range
    diff = mx - mn
    return mn - factor * diff, mx + factor * diff


def wrap_label_multiline(label: str) -> str:
    return label.replace(' (', '\n(')


class ColorCategoryManager:
    """Attaches a unique color to each categorical value"""

    color_list = ['maroon', 'lightseagreen', 'forestgreen', 'darkorange', 'purple', 'saddlebrown']

    def __init__(self):
        self._cat_idx = {}
        self._cat_count = 0

    def register_category_value(self, cat_value: str):
        if cat_value not in self._cat_idx:
            assert self._cat_count < len(ColorCategoryManager.color_list)
            self._cat_idx[cat_value] = ColorCategoryManager.color_list[self._cat_count]
            print(f'COLOR: {cat_value} => { self._cat_idx[cat_value]}')
            self._cat_count += 1

    def get_color(self, cat_value: str) -> str:
        assert cat_value in self._cat_idx
        return self._cat_idx[cat_value]


class CorrelationValue:
    """A single correlation value and associated p value"""

    def __init__(self, corr_info: Tuple[float, float]):
        self._r, self._p = corr_info

    def get_r(self) -> float:
        return self._r

    def get_p(self) -> float:
        return self._p

    def get_signif_color_fraction(self) -> float:
        """Returns a value between 0 and 1 that can be used for visual color coding of the significance"""
        # @todo: improve & parametrize this currently fairly arbitrary choice
        return min(1.0, -math.log10(self._p) / 15) ** 2


class CorrelationFactor:
    """A single factor that is used in either the X or Y dimension of the correlation gallery"""

    def __init__(self, id : str, name: str):
        self._id = id
        self._name = name
        self._range_min = None
        self._range_max = None

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def add_value(self, val: float):
        if val is None:
            return
        if self._range_min is None:
            self._range_min = val
        else:
            self._range_min = min(self._range_min, val)
        if self._range_max is None:
            self._range_max = val
        else:
            self._range_max = max(self._range_max, val)

    def get_range(self) -> Tuple[float, float]:
        return self._range_min, self._range_max


class CorrelationDataPoint:
    """A single data point in the list of data points driving the correlation gallery"""

    def __init__(self, id: str, name: str, size_fraction: float, color_cat: str):
        self._id = id
        self._name = name
        self._size_fraction = size_fraction
        self._color_cat = color_cat
        self._values_dimx = {}
        self._values_dimy = {}

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_size_fraction(self) -> float:
        return self._size_fraction

    def get_color_cat(self) -> str:
        return self._color_cat

    def set_value_dimx(self, factor_id: str, value: float):
        self._values_dimx[factor_id] = value

    def set_value_dimy(self, factor_id: str, value: float):
        self._values_dimy[factor_id] = value

    def get_value_dimx(self, factor_id: str) -> float:
        return self._values_dimx[factor_id]

    def get_value_dimy(self, factor_id: str) -> float:
        return self._values_dimy[factor_id]


class CorrelationGallery:
    """Aanalyses the correlation for a number of factors, organised in a cross table with X and Y dimension factors"""

    def __init__(self):
        self._dimx_factors = []
        self._dimy_factors = []
        self._dimx_factors_idx = {}
        self._dimy_factors_idx = {}
        self._datapoints = []
        self._datapoints_idx = {}
        self._color_cat_manager = ColorCategoryManager()
        self._corr_matrix = None

    def add_dimx_factor(self, correlation_factor: CorrelationFactor):
        assert correlation_factor.get_id() not in self._dimx_factors_idx
        self._dimx_factors.append(correlation_factor)
        self._dimx_factors_idx[correlation_factor.get_id()] = correlation_factor

    def add_dimy_factor(self, correlation_factor: CorrelationFactor):
        assert correlation_factor.get_id() not in self._dimy_factors_idx
        self._dimy_factors.append(correlation_factor)
        self._dimy_factors_idx[correlation_factor.get_id()] = correlation_factor

    def add_datapoint(self, point_id: str, name: str, size_frac: float, color_cat: str):
        assert point_id not in self._datapoints_idx
        datapoint = CorrelationDataPoint(point_id, name, size_frac, color_cat)
        self._datapoints.append(datapoint)
        self._datapoints_idx[point_id] = datapoint
        self._color_cat_manager.register_category_value(color_cat)

    def add_dimx_value(self, point_id: str, factor_id: str, value: float):
        assert point_id in self._datapoints_idx
        assert factor_id in self._dimx_factors_idx
        datapoint = self._datapoints_idx[point_id]
        datapoint.set_value_dimx(factor_id, value)
        self._dimx_factors_idx[factor_id].add_value(value)

    def add_dimy_value(self, point_id: str, factor_id: str, value: float):
        assert point_id in self._datapoints_idx
        datapoint = self._datapoints_idx[point_id]
        datapoint.set_value_dimy(factor_id, value)
        self._dimy_factors_idx[factor_id].add_value(value)

    def calc_correlations(self):
        self._corr_matrix = []
        for ix, fac_x in enumerate(self._dimx_factors):
            corr_row = []
            self._corr_matrix.append(corr_row)
            for iy, fac_y in enumerate(self._dimy_factors):
                series_x = []
                series_y = []
                for pt in self._datapoints:
                    val_x = pt.get_value_dimx(fac_x.get_id())
                    val_y = pt.get_value_dimy(fac_y.get_id())
                    if (val_x is not None) and (val_y is not None):
                        series_x.append(val_x)
                        series_y.append(val_y)
                corr_row.append(CorrelationValue(spearmanr(series_x, series_y)))

    def sort_dimx_by_significance(self, dimy_factor: str):
        assert self._corr_matrix
        assert dimy_factor in self._dimy_factors_idx
        dimy_nr = [fc.get_id() for fc in self._dimy_factors].index(dimy_factor)
        staging = list(zip(self._dimx_factors, self._corr_matrix))
        staging.sort(key=lambda pt: pt[1][dimy_nr].get_p())
        self._dimx_factors, self._corr_matrix = list(zip(*staging))

    def create_chart(self, show_labels: bool=False, color_by_significance: bool=False):
        fig = plt.figure()
        color_map = cm.get_cmap('gist_heat')
        plt.axis('off')
        plt.rc('axes', edgecolor='darkgrey')
        dimx_count = len(self._dimx_factors)
        dimy_count = len(self._dimy_factors)
        if color_by_significance:
            assert self._corr_matrix

        # draw all scatterplot cells
        for ix, fac_x in enumerate(self._dimx_factors):
            for iy, fac_y in enumerate(self._dimy_factors):
                plt.rc('font', size=10)
                ax = fig.add_axes([
                    0.1 + ix / (dimx_count + 1),
                    0.1 + iy / (dimy_count + 1),
                    1 / (dimx_count + 1),
                    1 / (dimy_count + 1)
                ])
                ax.tick_params(axis='x', colors='grey', labelsize=8)
                ax.tick_params(axis='y', colors='grey', labelsize=8)
                if color_by_significance:
                    ax.patch.set_facecolor(color_map(1 - self._corr_matrix[ix][iy].get_signif_color_fraction()))
                if iy == 0:
                    ax.set_xlabel(wrap_label_multiline(fac_x.get_name()))
                else:
                    plt.xticks([], [])

                if ix == 0:
                    ax.set_ylabel(wrap_label_multiline(fac_y.get_name()))
                else:
                    plt.yticks([], [])

                series_x = []
                series_y = []
                series_size = []
                series_label = []
                series_color = []
                for pt in self._datapoints:
                    val_x = pt.get_value_dimx(fac_x.get_id())
                    val_y = pt.get_value_dimy(fac_y.get_id())
                    if (val_x is not None) and (val_y is not None):
                        series_x.append(val_x)
                        series_y.append(val_y)
                        series_label.append(pt.get_name())
                        series_size.append(6 + 60 * math.sqrt(pt.get_size_fraction()))
                        series_color.append(self._color_cat_manager.get_color(pt.get_color_cat()))
                ax.scatter(
                    series_x,
                    series_y,
                    s=series_size,
                    color=series_color,
                    alpha=0.5
                )
                plt.xlim(expand_range(fac_x.get_range(), 0.15))
                plt.ylim(expand_range(fac_y.get_range(), 0.15))
                if show_labels:
                    plt.rc('font', size=5)
                    for scatter_pt in zip(series_x, series_y, series_label):
                        ax.annotate(scatter_pt[2], (scatter_pt[0], scatter_pt[1]))

        # Draw correlation values on top of cells
        if self._corr_matrix:
            ax = fig.add_axes([0, 0, 1, 1])
            ax.patch.set_facecolor('none')
            for ix, fac_x in enumerate(self._dimx_factors):
                for iy, fac_y in enumerate(self._dimy_factors):
                    corr = self._corr_matrix[ix][iy]
                    r_formatted = "{:.4f}".format(corr.get_r())
                    p_formatted = "{:.6f}".format(corr.get_p())
                    plt.text(
                        0.1025 + ix / (dimx_count + 1),
                        0.0875 + (iy + 1) / (dimy_count + 1),
                        f'r={r_formatted} p={p_formatted}',
                        fontsize=8,
                        alpha=0.6
                    )

        plt.show()
