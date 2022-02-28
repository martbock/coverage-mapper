import argparse

import pandas as pd


def main():
    args = init_argparse().parse_args()

    cell_df = pd.read_csv(args.cell_info, parse_dates=[0], infer_datetime_format=True)
    signal_df = pd.read_csv(args.signal_strengths, parse_dates=[0], infer_datetime_format=True)
    loc_df = pd.read_csv(args.location_updates)

    data = []

    for i, r in loc_df.iterrows():
        similar = cell_df.loc[
            (cell_df["latitude"] == r["latitude"])
            & (cell_df["longitude"] == r["longitude"])
            & (cell_df["altitude"] == r["altitude"])
            & (cell_df["speed"] == r["speed"])
            & (cell_df["locationAccuracy"] == r["locationAccuracy"])
            ]

        data.append([
            similar.iloc[0]["time"] if len(similar) > 0 else None,
            r["latitude"],
            r["longitude"],
            r["altitude"],
            r["speed"],
            r["locationAccuracy"],
        ])

    df = pd.DataFrame(data, columns=["time", "latitude", "longitude", "altitude", "speed", "locationAccuracy"])

    for i, r in df.iterrows():
        if r["time"] is not pd.NaT:
            continue
        similar = signal_df.loc[
            (signal_df["latitude"] == r["latitude"])
            & (signal_df["longitude"] == r["longitude"])
            & (signal_df["altitude"] == r["altitude"])
            & (signal_df["speed"] == r["speed"])
            & (signal_df["locationAccuracy"] == r["locationAccuracy"])
            ]
        if len(similar) > 0:
            df.at[i, "time"] = similar.iloc[0]["time"]
        else:
            before = df.iloc[i - 1]["time"]
            after = df.iloc[i + 1]["time"]
            average = before + (after - before) / 2
            df.at[i, "time"] = average
            print(f"WARNING: Guessed the timestamp {average}")

    df.to_csv(args.out, date_format="%Y-%m-%dT%H:%M:%S.%f", index=False)


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS]",
        description="Generate coverage maps for measurement data."
    )

    parser.add_argument(
        "-l",
        "--location-updates",
        type=argparse.FileType("r"),
        required=True,
    )

    parser.add_argument(
        "-c",
        "--cell-info",
        type=argparse.FileType("r"),
        required=True,
    )

    parser.add_argument(
        "-s",
        "--signal-strengths",
        type=argparse.FileType("r"),
        required=True,
    )

    parser.add_argument(
        "-o",
        "--out",
        type=argparse.FileType("w"),
        required=True,
    )

    return parser


if __name__ == '__main__':
    main()
