from qgis.core import QgsProcessingProvider
from .geojson_insert_algorithm import GeoJSONToInsertOnlySQL

class GeoJSONSQLProvider(QgsProcessingProvider):

    def loadAlgorithms(self):
        self.addAlgorithm(GeoJSONToInsertOnlySQL())

    def id(self):
        return 'geojson_sql'

    def name(self):
        return 'GeoJSON SQL Tools'

    def icon(self):
        return self.algorithms()[0].icon()