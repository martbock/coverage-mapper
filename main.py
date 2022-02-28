import argparse
import sys

import pandas as pd

import renderer
from coverage_providers import CoverageProvider
from coverage_providers.telekom import CoverageProviderTelekom
from coverage_providers.vodafone import CoverageProviderVodafone
from network_type import NetworkType


def main():
    args = init_argparse().parse_args()

    location_data, signal_data, display_info_data = None, None, None

    if args.signal_strengths is not None:
        signal_data = pd.read_csv(args.signal_strengths, parse_dates=[0], infer_datetime_format=True)
        signal_data = signal_data.dropna(subset=["latitude", "longitude"])

    if args.location_updates is not None:
        location_data = pd.read_csv(args.location_updates, parse_dates=[0], infer_datetime_format=True)
        location_data = location_data.dropna(subset=["latitude", "longitude"])

    if args.display_info is not None:
        display_info_data = pd.read_csv(args.display_info, parse_dates=[0], infer_datetime_format=True)
        display_info_data = display_info_data.dropna(subset=["latitude", "longitude"])

    renderer.render(
        measurement_id=args.id,
        network_type=NetworkType[args.type.upper()] if args.type is not None else None,
        padding_degrees=args.padding_degrees,
        dpi=args.dpi,
        location_data=location_data,
        signal_data=signal_data,
        display_info_data=display_info_data,
        coverage_provider=get_coverage_provider(args.operator),
        aspect_ratio=args.aspect_ratio,
        file_type=args.file_type,
        title=args.title,
        vmin=args.vmin,
        vmax=args.vmax,
        plot_rsrq=args.rsrq,
        show_title=not args.hide_title,
    )


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS]",
        description="Generate coverage maps for measurement data."
    )

    parser.add_argument(
        "-i",
        "--id",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[None, *[t.name for t in NetworkType]],
        default=None,
        required="--signal-strengths" in sys.argv or "-s" in sys.argv or "--operator" in sys.argv or "-o" in sys.argv
    )

    parser.add_argument(
        "-p",
        "--padding-degrees",
        type=float,
        default=0.02,
    )

    parser.add_argument(
        "--aspect-ratio",
        type=float,
        default=16.0 / 9.0,
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=100,
    )

    parser.add_argument(
        "-l",
        "--location-updates",
        type=argparse.FileType("r"),
        default=None,
    )

    parser.add_argument(
        "-s",
        "--signal-strengths",
        type=argparse.FileType("r"),
        default=None,
    )

    parser.add_argument(
        "-d",
        "--display-info",
        type=argparse.FileType("r"),
        default=None,
    )

    parser.add_argument(
        "-o",
        "--operator",
        type=str,
        choices=[None, "Telekom", "Vodafone"],
        default=None,
    )

    parser.add_argument(
        "--hide-title",
        action='store_true',
        default=False,
    )

    parser.add_argument(
        "--title",
        type=str,
        default=None,
    )

    parser.add_argument(
        "--file-type",
        type=str,
        default="pdf",
    )

    parser.add_argument(
        "--vmin",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--vmax",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--rsrq",
        action='store_true',
        default=False,
    )

    return parser


def get_coverage_provider(operator: str) -> CoverageProvider or None:
    if operator == "Telekom":
        return CoverageProviderTelekom()
    elif operator == "Vodafone":
        return CoverageProviderVodafone()
    return None


if __name__ == "__main__":
    main()
