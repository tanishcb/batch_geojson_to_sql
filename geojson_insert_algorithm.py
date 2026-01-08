from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterString,
    QgsProcessingParameterNumber,
    QgsProcessingException
)
from qgis.PyQt.QtGui import QIcon
import os
import subprocess
import sys

class GeoJSONToInsertOnlySQL(QgsProcessingAlgorithm):

    INPUT_DIR = 'INPUT_DIR'
    OUTPUT_DIR = 'OUTPUT_DIR'
    SCHEMA = 'SCHEMA'
    SRID = 'SRID'
    GEOM_COL = 'GEOM_COL'
    ENCODING = "ENCODING"

    def name(self):
        return 'geojson_to_insert_only_sql'

    def displayName(self):
        return 'GeoJSON → INSERT-only SQL (Schema / SRID / Geometry)'

    def group(self):
        return 'Database Tools'

    def groupId(self):
        return 'database_tools'

    def icon(self):
        return QIcon(os.path.join(os.path.dirname(__file__), 'icon.svg'))

    def shortHelpString(self):
        return (
            "Converts GeoJSON files into INSERT-only PostGIS SQL files.\n\n"
            "• Keeps only INSERT INTO statements\n"
            "• Supports schema-qualified tables\n\n"
            "Requires GDAL (ogr2ogr)\n\n"
            "@Developed By Tanish"
        )

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterFolderDestination(
            self.INPUT_DIR, 'Input GeoJSON Folder'))

        self.addParameter(QgsProcessingParameterFolderDestination(
            self.OUTPUT_DIR, 'Output SQL Folder'))

        self.addParameter(QgsProcessingParameterString(
            self.SCHEMA, 'Target Schema', defaultValue='gis'))

        self.addParameter(QgsProcessingParameterNumber(
            self.SRID, 'SRID',
            QgsProcessingParameterNumber.Integer, defaultValue=4326))

        self.addParameter(QgsProcessingParameterString(
            self.GEOM_COL, 'Geometry Column Name', defaultValue='the_geom'))

        self.addParameter(QgsProcessingParameterString(
            self.ENCODING, 'Client Encoding', defaultValue='UTF-8'))

    def processAlgorithm(self, parameters, context, feedback):

        input_dir = self.parameterAsString(parameters, self.INPUT_DIR, context)
        output_dir = self.parameterAsString(parameters, self.OUTPUT_DIR, context)
        schema = self.parameterAsString(parameters, self.SCHEMA, context)
        srid = self.parameterAsInt(parameters, self.SRID, context)
        geom_col = self.parameterAsString(parameters, self.GEOM_COL, context)
        encoding = self.parameterAsString(parameters, self.ENCODING, context)

        if not os.path.isdir(input_dir):
            raise QgsProcessingException("Invalid input directory")

        os.makedirs(output_dir, exist_ok=True)
        temp_dir = os.path.join(output_dir, "_temp_sql")
        os.makedirs(temp_dir, exist_ok=True)

        files = [f for f in os.listdir(input_dir) if f.lower().endswith(".geojson")]
        if not files:
            raise QgsProcessingException("No GeoJSON files found in input folder")
        total = len(files)

        for idx, file in enumerate(files):

            feedback.setProgress(int((idx / total) * 100))
            feedback.pushInfo(f"Processing: {file}")

            geojson_path = os.path.join(input_dir, file)
            table_name = os.path.splitext(file)[0].lower()
            qualified_table = f"{schema}.{table_name}"

            temp_sql = os.path.join(temp_dir, f"{table_name}.sql")
            final_sql = os.path.join(output_dir, f"{table_name}.sql")
           
            cmd = [
                "ogr2ogr",
                "-f", "PGDump",
                temp_sql,
                geojson_path,
                "-nln", qualified_table,
                "-nlt", "GEOMETRY",
                "-lco", f"GEOMETRY_NAME={geom_col}",
                "-lco", f"SRID={srid}",
                "-lco", "ADD_CONSTRAINTS=NO",
                "-lco", "SPATIAL_INDEX=NO",
                "--config", "PGCLIENTENCODING", encoding
            ]

            run_kwargs = {"check": True}
            if sys.platform.startswith("win"):
                run_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            subprocess.run(cmd, **run_kwargs)

            with open(temp_sql, "r", encoding="utf-8") as src, \
                 open(final_sql, "w", encoding="utf-8") as dst:
                for line in src:
                    if line.lstrip().upper().startswith("INSERT INTO"):
                        dst.write(line)

        feedback.setProgress(100)
        feedback.pushInfo("✅ Conversion completed successfully")
        return {}
    def createInstance(self):
        return GeoJSONToInsertOnlySQL()