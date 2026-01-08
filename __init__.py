from qgis.core import QgsApplication
from .provider import GeoJSONSQLProvider

class GeoJSONSQLPlugin:
    def __init__(self):
        self.provider = None

    def initProcessing(self):
        """Called when Processing is initialized (headless or GUI mode)."""
        self.provider = GeoJSONSQLProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        """Called only in GUI mode – we can safely call initProcessing here too."""
        self.initProcessing()

    def unload(self):
        """Remove the provider when the plugin is unloaded."""
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

def classFactory(iface):
    """Required entry point – returns the plugin object."""
    return GeoJSONSQLPlugin()