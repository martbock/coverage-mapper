from coverage_providers import CoverageProvider
from network_type import NetworkType


class CoverageProviderVodafone(CoverageProvider):
    def operator_name(self) -> str:
        return "Vodafone"

    def _base_url(self) -> str:
        return "https://netmap.vodafone.de/arcgis/rest/services/CoKart/netzabdeckung_mobilfunk_4x/MapServer/export"

    def _param_layers(self, network_type: NetworkType) -> str:
        if network_type == NetworkType.NR:
            return "show:123"
        elif network_type == NetworkType.LTE:
            return "show:111"
        elif network_type == NetworkType.GSM:
            return "show:119"
        raise ValueError("Unknown network type")
