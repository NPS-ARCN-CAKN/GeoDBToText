# Python script to be associated with an ArcToolbox.
# Exports each featureclass in the submitted geodatabase to  human and machine readable text and JSON files.
# Export files are created in the same directory as the input geodatabase

#Written by Scott D. Miller
#National Park Service, Arctic and Central Alaska Inventory and Monitoring programs
#2019-06-15

# Imports
import arcpy
import os
import csv


# Input parameters
GeoDB = arcpy.GetParameterAsText(0) # The input geodatabase (Workspace)
DatasetTitle = arcpy.GetParameterAsText(1) # The output geodatabase
Attribution = arcpy.GetParameterAsText(2) # Attribution (citation) for the dataset
Abstract = arcpy.GetParameterAsText(3) # Abstract
TermsOfUse = arcpy.GetParameterAsText(4) # Terms of use. Non-sensitive government data is public domain
DatasetContact = arcpy.GetParameterAsText(5) # Contact for the dataset
Delimiter = arcpy.GetParameterAsText(6) # Fields delimiter. A pipe was chosen to avoid ambiguity with the commas in the WKT geometry data. You can change it back to a comma or whatever you want here.

# set the workspace
arcpy.env.workspace = GeoDB

# Function to export a featureclass as a json file
def ExportJSON(FeatureClass):
    try:
        # This will be the output json file
        JsonFile = os.path.dirname(arcpy.env.workspace) + '\\' + FeatureClass + '.json'
        
        # If the json file exists already then delete it 
        if os.path.exists(JsonFile):
            arcpy.AddMessage("File exists: " + JsonFile + '. Deleted')
            os.remove(JsonFile)

        # Export the FeatureClass
        arcpy.AddMessage("Exporting " + JsonFile)
        arcpy.FeaturesToJSON_conversion(FeatureClass, JsonFile, "NOT_FORMATTED")
    except Exception as e:
        arcpy.AddMessage('Export failed for FeatureClass: ' + FeatureClass + ' ' + str(e))

# Function to export a featureclass as a comma separated values text file
def ExportCSV(FeatureClass):
    try:
   
        # This will be the output CSV file
        CSVFile = os.path.dirname(arcpy.env.workspace) + '/' + FeatureClass + '.csv'
        # if the CSV file exists already then delete it 
        if os.path.exists(CSVFile):
            arcpy.AddMessage("File exists: " + CSVFile + '. Deleted')
            os.remove(CSVFile)
        CSVFile = open(CSVFile,'a')  
        
        # Get the field names into the first row of the CSV file
        fields = arcpy.ListFields(FeatureClass)
        field_names =  [field.name for field in fields]
        field_names.insert(0,"Shape@WKT")
        FieldNames = ""
        for Field in field_names:
            FieldNames = FieldNames + Delimiter + Field
        
        # Add some metadata to the file
        CSVFile.write(DatasetTitle + "\n")
        CSVFile.write(Abstract + "\n")
        CSVFile.write(Attribution + "\n")
        CSVFile.write("Spatial reference: " + arcpy.Describe(FeatureClass).spatialReference.exportToString()  + "\n")
        CSVFile.write(TermsOfUse + "\n")
        CSVFile.write("This file is a human and machine readable equivalent of the layer " + FeatureClass + " exported from the ESRI personal geodatabase " + os.path.basename(GeoDB) + " and was generated to back up and archive the parent dataset for posterity in a non-proprietary text format in case the parent geodatabase format should become unsupported or outmoded. This file was not intended for day to day analytical work. Where possibe use the parent geodatabase.\n")
        CSVFile.write("Dataset contact: " + DatasetContact + " \n")
        CSVFile.write("Note: Row field values are separated by a pipe character | to avoid software confusion with the commas commonly found in WKT representations of geometry.")
        CSVFile.write("\n")

        # remove the leftmost delimiter and write the data line to the file
        CSVFile.write(FieldNames.lstrip(FieldNames[:1]) + '\n')

        # loop through the data rows and output to CSV
        for row in arcpy.da.SearchCursor(FeatureClass,field_names):
            i = 0
            while i < len(fields):
                CSVFile.write(str(row[i]) + Delimiter)
                i += 1
            CSVFile.write('\n')
        del row
        CSVFile.close
    except Exception as e:
        arcpy.AddMessage('Export failed for FeatureClass: ' + FeatureClass + ' ' + str(e))

# loop through all the feature classes in the geodatabase and export them to json files
try:
    FeatureClasses = arcpy.ListFeatureClasses()
    for FeatureClass in FeatureClasses:
        arcpy.AddMessage("Processing " + FeatureClass)
        ExportCSV(FeatureClass)
        ExportJSON(FeatureClass)
except Exception as e:
    arcpy.AddMessage('Error: ' + str(e))