# CoverageMapper

CoverageMapper is an open-source tool to visualize cellular radio network
coverage measurements along with a network operator's claimed coverage.

![Example Usage](.example/coverage-Telekom-NR-100.png)

## Supported Network Operators

Currently, the following network operators are supported:

- Deutsche Telekom
- Vodafone

## Command Line Options

The following command line options can be used to customize the rendered maps.
`--id` is used to create a subfolder where rendered images are stored
(`./out/this-is-my-id`).

```sh
python main.py --help
usage: main.py [OPTIONS]

Generate coverage maps for measurement data.

optional arguments:
  -h, --help            show this help message and exit
  -i ID, --id ID
  -t {None,NR,LTE,GSM}, --type {None,NR,LTE,GSM}
  -p PADDING_DEGREES, --padding-degrees PADDING_DEGREES
  --aspect-ratio ASPECT_RATIO
  --dpi DPI
  -l LOCATION_UPDATES, --location-updates LOCATION_UPDATES
  -s SIGNAL_STRENGTHS, --signal-strengths SIGNAL_STRENGTHS
  -d DISPLAY_INFO, --display-info DISPLAY_INFO
  -o {None,Telekom,Vodafone}, --operator {None,Telekom,Vodafone}
  --hide-title
  --title TITLE
  --file-type FILE_TYPE
  --vmin VMIN
  --vmax VMAX
  --rsrq
```

## Installation

Use a virtual Python environment to install the [required dependencies](requirements.txt).
Python 3.8 should work fine, while Python 3.9 does not work at the moment.

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Additionally, you have to install [PROJ](https://proj.org/). For details, have a
look at their [installation instructions](https://proj.org/install.html). For
macOS, simply install PROJ with:

```sh
brew install proj
```

## Example Usage

```sh
python main.py \
    --id stuttgart \
    --type NR \
    --operator Telekom \
    --aspect-ratio 1.78 \
    --padding-degrees 0.025 \
    --file-type png \
    --location-updates ./data/LOCATION_UPDATE.csv \
    --signal-strengths ./data/SIGNAL_STRENGTH.csv
```

![Example Usage (RSRP)](.example/coverage-Telekom-NR-100.png)

```sh
python main.py \
    --id stuttgart \
    --rsrq \
    --type NR \
    --operator Telekom \
    --aspect-ratio 1.78 \
    --padding-degrees 0.025 \
    --file-type png \
    --location-updates ./data/LOCATION_UPDATE.csv \
    --signal-strengths ./data/SIGNAL_STRENGTH.csv
```

![Example Usage (RSRQ)](.example/coverage-Telekom-NR-rsrq-100.png)

```sh
python main.py \
    --id stuttgart \
    --type NR \
    --operator Telekom \
    --aspect-ratio 1.78 \
    --padding-degrees 0.025 \
    --file-type png \
    --location-updates ./data/LOCATION_UPDATE.csv \
    --display-info ./data/DISPLAY_INFO.csv
```

![Example Usage (Display Info)](.example/override-Telekom-NR-100.png)