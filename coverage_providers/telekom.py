from coverage_providers import CoverageProvider
from network_type import NetworkType


class CoverageProviderTelekom(CoverageProvider):
    def operator_name(self) -> str:
        return "Telekom"

    def _base_url(self) -> str:
        return "https://t-map.telekom.de/arcgis/rest/services/public/coverage/MapServer/export"

    def _param_layers(self, network_type: NetworkType) -> str:
        if network_type == NetworkType.NR:
            return "show:6"
        elif network_type == NetworkType.LTE:
            return "show:3"
        elif network_type == NetworkType.GSM:
            return "show:5"
        raise ValueError("Unknown network type")
