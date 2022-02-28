from pathlib import Path

import matplotlib.axes
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tilemapbase
from PIL import Image, ImageEnhance, ImageChops
from matplotlib.axes import Subplot
from matplotlib.figure import Figure
from tilemapbase import Extent

from coverage_providers import CoverageProvider
from network_type import NetworkType

tilemapbase.start_logging()
tilemapbase.init(create=True)


def render(measurement_id: str,
           network_type: NetworkType or None,
           padding_degrees: float,
           dpi: int,
           location_data: pd.DataFrame or None,
           signal_data: pd.DataFrame or None,
           display_info_data: pd.DataFrame or None,
           coverage_provider: CoverageProvider or None,
           aspect_ratio: float,
           file_type: str,
           title: str or None,
           vmin: int or None,
           vmax: int or None,
           plot_rsrq: bool,
           show_title: bool = True):
    if location_data is not None:
        bounding_box_data = location_data
    elif signal_data is not None:
        bounding_box_data = signal_data
    elif display_info_data is not None:
        bounding_box_data = display_info_data
    else:
        raise ValueError("At least one location data set is required.")

    bounding_box = _get_bounding_box(bounding_box_data[["latitude", "longitude"]], padding_degrees)
    extent = _create_extent(bounding_box, aspect_ratio)
    tile_provider = tilemapbase.tiles.Carto_Light

    fig, ax = plt.subplots(figsize=(10 * (dpi / 90), 4 * (dpi / 90)), dpi=dpi, facecolor="White")
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    plotter = tilemapbase.Plotter(extent, tile_provider, width=3 * dpi)
    plotter.plot(ax, tile_provider)

    if location_data is not None:
        _plot_location_updates(ax, location_data)

    if signal_data is not None:
        _scatter_signal_strength(network_type=network_type, signal_data=signal_data, fig=fig, ax=ax,
                                 vmin=vmin, vmax=vmax, plot_rsrq=plot_rsrq)

    if display_info_data is not None:
        _plot_display_info(ax=ax, location_data=location_data, display_info_data=display_info_data)

    if coverage_provider is not None:
        _render_operator_map(coverage_provider=coverage_provider, network_type=network_type, ax=ax,
                             bounding_box=bounding_box, aspect_ratio=aspect_ratio, extent=extent)

    if show_title:
        plt.title(_get_title(title, network_type, coverage_provider, signal_data, plot_rsrq))

    path = _create_filename(measurement_id=measurement_id, coverage_provider=coverage_provider,
                            network_type=network_type, dpi=dpi, file_type=file_type, plot_rsrq=plot_rsrq,
                            name="override" if display_info_data is not None else "coverage")
    path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(
        path,
        format=file_type,
        dpi=dpi,
        bbox_inches="tight",
        transparent=True,
    )


def _get_title(title: str or None, network_type: NetworkType or None, coverage_provider: CoverageProvider or None,
               signal_data: pd.DataFrame or None, plot_rsrq: bool) -> str:
    if title is not None:
        return title

    s = ""

    if network_type is not None:
        s += f"{network_type.name} "

    if signal_data is None:
        s += "Dead Spots "
    elif plot_rsrq:
        s += "Signal Quality "
    else:
        s += "Signal Strength "

    if coverage_provider is not None:
        s += f"({coverage_provider.operator_name()})"

    return s.strip()


def _plot_location_updates(ax: Subplot, location_data: pd.DataFrame):
    projected_loc = _project_coordinates(location_data)
    ax.plot(
        projected_loc["longitude"],
        projected_loc["latitude"],
        color="darkgray",
        linewidth=1,
        zorder=1
    )


def _create_extent(bounding_box, aspect_ratio: float):
    extent = tilemapbase.Extent.from_lonlat(
        bounding_box["min"]["longitude"],
        bounding_box["max"]["longitude"],
        bounding_box["min"]["latitude"],
        bounding_box["max"]["latitude"],
    )
    extent = extent.to_aspect(aspect_ratio)
    return extent


def _project_coordinates(df) -> dict[str, list]:
    projected = dict(latitude=[], longitude=[])
    for i, row in df.iterrows():
        [long, lat] = tilemapbase.project(row["longitude"], row["latitude"])
        projected["longitude"].append(long)
        projected["latitude"].append(lat)
    return projected


def _scatter_signal_strength(network_type: NetworkType, signal_data: pd.DataFrame, fig: Figure, ax: Subplot,
                             vmin: int or None, vmax: int or None, plot_rsrq: bool):
    df = signal_data.loc[signal_data["networkType"] == network_type]
    projected = _project_coordinates(df)

    if plot_rsrq and network_type == NetworkType.LTE:
        c = df["rsrq"]
    elif plot_rsrq and network_type == NetworkType.NR:
        c = df["ssRsrq"]
    else:
        c = df["dbm"]

    scatter = ax.scatter(
        x=projected["longitude"],
        y=projected["latitude"],
        linewidth=5,
        marker=".",
        c=c,
        cmap="rainbow_r",
        vmin=_get_vmin(signal_data, network_type, vmin, plot_rsrq),
        vmax=_get_vmax(signal_data, network_type, vmax, plot_rsrq),
        zorder=3,
    )

    color_bar = fig.colorbar(scatter)
    color_bar.ax.set_ylabel(_get_axis_name(network_type, plot_rsrq))


def _get_vmin(signal_data: pd.DataFrame, network_type: NetworkType, vmin: int or None, plot_rsrq: bool):
    if vmin is not None:
        return vmin
    if plot_rsrq and network_type == NetworkType.LTE:
        return signal_data["rsrq"].min()
    if plot_rsrq and network_type == NetworkType.NR:
        return signal_data["ssRsrq"].min()
    return signal_data["dbm"].min()


def _get_vmax(signal_data: pd.DataFrame, network_type: NetworkType, vmax: int or None, plot_rsrq: bool):
    if vmax is not None:
        return vmax
    if plot_rsrq and network_type == NetworkType.LTE:
        return signal_data["rsrq"].max()
    if plot_rsrq and network_type == NetworkType.NR:
        return signal_data["ssRsrq"].max()
    return signal_data["dbm"].max()


def _get_axis_name(network_type: NetworkType, plot_rsrq: bool):
    if network_type == NetworkType.GSM:
        return "RSSI in dBm"
    if plot_rsrq and (network_type == NetworkType.LTE or network_type == NetworkType.NR):
        return "RSRQ in dB"
    if network_type == NetworkType.LTE or network_type == NetworkType.NR:
        return "RSRP in dBm"
    return "???"


def _plot_display_info(ax: Subplot, location_data: pd.DataFrame, display_info_data: pd.DataFrame):
    projected = _project_coordinates(display_info_data)
    ax.scatter(
        x=projected["longitude"],
        y=projected["latitude"],
        color="gray",
        s=8,
    )

    for i, display_info in display_info_data.iterrows():
        df = location_data.loc[(location_data["time"] >= display_info["time"])]
        projected = _project_coordinates(df)

        name = display_info["overrideNetworkType"]
        if name == "NONE":
            name = display_info["networkType"]

        ax.plot(
            projected["longitude"],
            projected["latitude"],
            linewidth=3,
            color=_map_override_network_type(display_info["overrideNetworkType"], display_info["networkType"]),
            zorder=i + 1,
            label=name,
        )
    _legend_without_duplicate_labels(ax)


def _legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    unique = sorted(unique, key=lambda x: x[1])
    ax.legend(*zip(*unique))


def _map_override_network_type(override: str, connected: str) -> str:
    if override == "NR_NSA_MMWAVE":
        return "darkblue"
    elif override == "NR_NSA":
        return "royalblue"
    elif override == "LTE_ADVANCED_PRO":
        return "darkorange"
    elif override == "LTE_CA":
        return "gold"
    elif override == "NONE" and connected == "LTE":
        return "springgreen"
    elif override == "EDGE":
        return "firebrick"
    else:
        return "orange"


def _render_operator_map(coverage_provider: CoverageProvider, network_type: NetworkType,
                         ax: matplotlib.axes.Subplot, bounding_box: dict[str, dict[str, float]],
                         aspect_ratio: float, extent: Extent):
    coverage_img_path = coverage_provider.fetch_img(
        network_type=network_type,
        bounding_box=bounding_box,
        size={
            "height": 2000,
            "width": 2000 * aspect_ratio,
        },
    )

    img = Image.open(coverage_img_path).convert("LA")
    img = ImageChops.invert(img)
    img = ImageEnhance.Contrast(img).enhance(100)
    img = img.convert('RGBA')

    data = np.array(img)
    red, green, blue, alpha = data.T
    black_areas = (red == 0) & (blue == 0) & (green == 0)
    data[..., :-1][black_areas.T] = (248, 113, 113)
    img = Image.fromarray(data)

    ax.imshow(img, extent=[extent.xmin, extent.xmax, extent.ymax, extent.ymin], cmap=cm.Greys, alpha=0.6)


def _get_bounding_box(lat_long_df: pd.DataFrame, padding_degrees: float) -> dict[str, dict[str, float]]:
    """
    Get the map bounding box by searching for minimum and maximum latitude and longitude
    and adding a padding around them.

    :param lat_long_df: DataFrame with latitude and longitude measurements.
    :param padding_degrees: Amount of padding in degrees.
    :return:
    """
    return {
        "min": {
            "latitude": lat_long_df["latitude"].min() - padding_degrees,
            "longitude": lat_long_df["longitude"].min() - padding_degrees,
        },
        "max": {
            "latitude": lat_long_df["latitude"].max() + padding_degrees,
            "longitude": lat_long_df["longitude"].max() + padding_degrees,
        }
    }


def _create_filename(measurement_id: str, name: str, dpi: int, file_type: str, plot_rsrq: bool,
                     coverage_provider: CoverageProvider or None, network_type: NetworkType or None) -> Path:
    s = f"out/graphs/{measurement_id}/{name}-"

    if coverage_provider is not None:
        s += f"{coverage_provider.operator_name()}-"

    if network_type is not None:
        s += f"{network_type}-"

    if plot_rsrq:
        s += f"rsrq-"

    s += f"{dpi}.{file_type}"

    return Path(s)
