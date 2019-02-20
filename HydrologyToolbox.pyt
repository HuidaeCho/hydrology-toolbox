############################################################################
# Name:    Hydrology Toolbox for ArcGIS Pro
# Purpose: Calculates flow accumulation, and delineates stream network and
#          watersheds.
# Author:  Huidae Cho
# Since:   November 8, 2018
#
# Copyright (C) 2018, Huidae Cho <https://idea.isnew.info>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#############################################################################

import arcpy
import re


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Hydrology Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [
                FlowAccumulation,
                StreamNetworkDelineation,
                WatershedDelineation,
                LongestFlowPath,
        ]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        return


class FlowAccumulation(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Flow Accumulation"
        self.description = "Run fill, flow direction, and flow accumulation"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        elev = arcpy.Parameter(
                displayName="Elevation",
                name="elevation",
                datatype="GPRasterLayer",
                parameterType="Required",
                direction="Input")
        fill = arcpy.Parameter(
                displayName="Filled Elevation",
                name="filled",
                datatype="DERasterDataset",
                parameterType="Required",
                direction="Output")
        fdir = arcpy.Parameter(
                displayName="Flow Direction",
                name="flow_direction",
                datatype="DERasterDataset",
                parameterType="Required",
                direction="Output")
        facc = arcpy.Parameter(
                displayName="Flow Accumulation",
                name="flow_accumulation",
                datatype="DERasterDataset",
                parameterType="Required",
                direction="Output")
        params = [elev, fill, fdir, facc]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        elev = parameters[0].valueAsText
        fill = parameters[1].valueAsText
        fdir = parameters[2].valueAsText
        facc = parameters[3].valueAsText

        outFill = arcpy.sa.Fill(elev)
        outFill.save(fill)

        outFlowDirection = arcpy.sa.FlowDirection(fill)
        outFlowDirection.save(fdir)

        outFlowAccumulation = arcpy.sa.FlowAccumulation(fdir)
        outFlowAccumulation.save(facc)
        return


class StreamNetworkDelineation(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Stream Network Delineation"
        self.description = "Delineate stream networks from flow accumulation"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        facc = arcpy.Parameter(
                displayName="Flow Accumulation",
                name="flow_accumulation",
                datatype="GPRasterLayer",
                parameterType="Required",
                direction="Input")
        thresh = arcpy.Parameter(
                displayName="Stream Threshold",
                name="stream_threshold",
                datatype="GPLong",
                parameterType="Required",
                direction="Input")
        streamRast = arcpy.Parameter(
                displayName="Stream Raster",
                name="stream_raster",
                datatype="DERasterDataset",
                parameterType="Required",
                direction="Output")
        streamVect = arcpy.Parameter(
                displayName="Stream Vector",
                name="stream_vector",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Output")
        params = [facc, thresh, streamRast, streamVect]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        facc = parameters[0].valueAsText
        thresh = parameters[1].value
        streamRast = parameters[2].valueAsText
        streamVect = parameters[3].valueAsText

        outStreamRast = arcpy.sa.Con(arcpy.Raster(facc) >= thresh, 1, 0)
        outStreamRast.save(streamRast)

        arcpy.RasterToPolyline_conversion(streamRast, streamVect)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprxMap = aprx.listMaps("Map")[0]
        aprxMap.addDataFromPath(streamVect)
        return


class WatershedDelineation(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Watershed Delineation"
        self.description = "Delineate watersheds from flow direction and outlets"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        fdir = arcpy.Parameter(
                displayName="Flow Direction",
                name="flow_direction",
                datatype="GPRasterLayer",
                parameterType="Required",
                direction="Input")
        outlets = arcpy.Parameter(
                displayName="Outlets",
                name="outlets",
                datatype="GPFeatureRecordSetLayer",
                parameterType="Required",
                direction="Input")
        watershedRast = arcpy.Parameter(
                displayName="Watershed Raster",
                name="watershed_raster",
                datatype="DERasterDataset",
                parameterType="Required",
                direction="Output")
        watershedVect = arcpy.Parameter(
                displayName="Watershed Vector",
                name="watershed_vector",
                datatype="DEFeatureClass",
                parameterType="Required",
                direction="Output")
        params = [fdir, outlets, watershedRast, watershedVect]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fdir = parameters[0].valueAsText
        outlets = parameters[1].valueAsText
        watershedRast = parameters[2].valueAsText
        watershedVect = parameters[3].valueAsText

        arcpy.env.extent = "MAXOF"
        outletsOidFieldName = arcpy.Describe(outlets).OIDFieldName
        outWatershed = arcpy.sa.Watershed(fdir, outlets, outletsOidFieldName)
        outWatershed.save(watershedRast)

        arcpy.RasterToPolygon_conversion(watershedRast, watershedVect)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        aprxMap = aprx.listMaps("Map")[0]
        aprxMap.addDataFromPath(watershedVect)
        return
        
class LongestFlowPath(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Longest Flow Path"
        self.description = "This tool creates the longest flow path for multiple watersheds."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        fdir = arcpy.Parameter(
                displayName="Flow Direction",
                name="flow_direction",
                datatype="GPRasterLayer",
                parameterType="Required",
                direction="Input")
        outlets = arcpy.Parameter(
                displayName="Outlets",
                name="outlets",
                datatype="GPFeatureRecordSetLayer",
                parameterType="Required",
                direction="Input")
        output_path = arcpy.Parameter(
                displayName="Output Folder Path",
                name="output_path",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        output_prefix = arcpy.Parameter(
                displayName="Output Prefix",
                name="output_prefix",
                datatype="GPString",
                parameterType="Required",
                direction="Input")          
        params = [fdir, outlets, output_path, output_prefix]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fdir = parameters[0].valueAsText
        outlets = parameters[1].valueAsText
        output_path = parameters[2].value
        output_prefix = parameters[3].value

        output_path = re.sub(r'\\+$', '', output_path) + '\\'
    
        arcpy.env.extent = "MAXOF"
        wsheds = arcpy.sa.Watershed(fdir, outlets, 'OBJECTID')
        wsheds.save(output_path + output_prefix + 'wsheds.tif')
    
        with arcpy.da.SearchCursor(outlets, ['OID@']) as cur:
            for row in cur:
                oid = row[0]
    
                wshed = arcpy.sa.ExtractByAttributes(wsheds, 'VALUE = {}'.format(oid))
                wshed.save(output_path + output_prefix + 'wshed_{}.tif'.format(oid))
    
                wshed_fdir = arcpy.sa.ExtractByMask(fdir, wshed)
                wshed_fdir.save(output_path + output_prefix + 'wshed_fdir_{}.tif'.format(oid))
    
                wshed_uplen = arcpy.sa.FlowLength(wshed_fdir, "UPSTREAM")
                wshed_uplen.save(output_path + output_prefix + 'wshed_uplen_{}.tif'.format(oid))
    
                wshed_dnlen = arcpy.sa.FlowLength(wshed_fdir, "DOWNSTREAM")
                wshed_dnlen.save(output_path + output_prefix + 'wshed_dnlen_{}.tif'.format(oid))
    
                wshed_updnlen = wshed_uplen + wshed_dnlen
                wshed_updnlen.save(output_path + output_prefix + 'wshed_updnlen_{}.tif'.format(oid))
    
                wshed_lfp = arcpy.sa.Con(wshed_updnlen >= int(wshed_updnlen.maximum), 1, 0)
                wshed_lfp.save(output_path + output_prefix + 'wshed_lfp_{}.tif'.format(oid))
    
                arcpy.RasterToPolyline_conversion(wshed_lfp, output_path + output_prefix + 'wshed_lfp_{}.shp'.format(oid))
        return
