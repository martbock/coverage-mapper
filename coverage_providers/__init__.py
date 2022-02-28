import hashlib
import json
import urllib.parse
from abc import ABC, abstractmethod
from pathlib import Path

import pyproj
import requests

from network_type import NetworkType


class CoverageProvider(ABC):
    def fetch_img(self, network_type: NetworkType,
                  bounding_box: dict[str, dict[str, float]],
                  size: dict[str, int], cache_img=True) -> Path:
        """
        Fetch the coverage image from the cellular network provider's map server.

        :param network_type: Type of cellular network that should be rendered.
        :param bounding_box: Latitude and longitude of top left and bottom right corners of the image.
        :param size: Image height and width in pixels. Should match the aspect ratio of the resulting map.
        :param cache_img: Use a cached image if present, avoiding downloading the image every time.
        :return: File path of the fetched coverage image.
        """
        path = self._create_filename(network_type, bounding_box, size)

        # Create directories if they don't already exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Avoid downloading a fresh copy of the image
        # if we already have one with the same parameters.
        if cache_img and path.is_file():
            return path

        top_left, bottom_right = self._transform_coordinates(bounding_box)

        params = {
            "bbox": ",".join(map(lambda x: str(x), top_left + bottom_right)),
            "size": f"{size['width']},{size['height']}",
            "dpi": "100",
            "format": "png24",
            "transparent": "true",
            "bboxSR": "3857",
            "imageSR": "3857",
            "layers": self._param_layers(network_type),
            "f": "image",
        }

        img = requests.get(
            self._base_url(),
            params=urllib.parse.urlencode(params, safe=",+"),
        ).content

        with open(path, "wb") as file:
            file.write(img)

        return path

    def _transform_coordinates(self, bounding_box: dict[str, dict[str, float]]
                               ) -> tuple[tuple[float, float], tuple[float, float]]:
        """
        Transform the coordinate system from latitude and longitude to Web Mercator.
        :param bounding_box: Latitude and longitude of top left and bottom right corners of the image.
        :return:
        """
        transformer = pyproj.Transformer.from_crs("epsg:4326", "epsg:3857")
        top_left = transformer.transform(
            bounding_box["min"]["latitude"],
            bounding_box["min"]["longitude"],
        )
        bottom_right = transformer.transform(
            bounding_box["max"]["latitude"],
            bounding_box["max"]["longitude"],
        )
        return top_left, bottom_right

    def _create_filename(self, network_type: NetworkType, bounding_box: dict[str, dict[str, float]],
                         size: dict[str, int]) -> Path:
        """
        Create a filename for the coverage image.

        The filename will include a MAC for network type, bounding box and image size. Thus, requesting the same
        coverage image twice can be avoided by caching the downloaded images.

        :param network_type: Type of cellular network that should be rendered.
        :param bounding_box: Latitude and longitude of top left and bottom right corners of the image.
        :param size: Image height and width in pixels. Should match the aspect ratio of the resulting map.
        :return: Path for the coverage image to be saved at.
        """
        operator_name = self.operator_name()
        json_data = json.dumps(dict(
            network_type=network_type,
            bounding_box=bounding_box,
            size=size,
        ), sort_keys=True)
        mac = hashlib.sha1(json_data.encode()).hexdigest()

        return Path(f"out/operators/coverage-{operator_name}-{mac}.png")

    @abstractmethod
    def _base_url(self) -> str:
        """
        :return: base URL of the map server.
        """
        pass

    @abstractmethod
    def _param_layers(self, network_type: NetworkType) -> str:
        """
        Get the "layers" parameter for the image query, depending on the network type.
        :param network_type: Type of cellular network that should be rendered.
        :return: Value for the "layers" parameter of the image query.
        """
        pass

    @abstractmethod
    def operator_name(self) -> str:
        """
        :return: Name of the cellular network operator.
        """
        pass
