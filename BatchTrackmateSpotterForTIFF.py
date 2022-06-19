from fiji.util.gui import GenericDialogPlus
from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.tracking.sparselap import SparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking import LAPUtils
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
import fiji.plugin.trackmate.io.TmXmlWriter as TmXmlWriter
from ij import IJ
from os import listdir
from java.io import File
from os.path import isfile, join, splitext
import sys

gui = GenericDialogPlus("Batch Track Spotter")

gui.addDirectoryField("Select Directory containing .tiff files", "Select Directory")
gui.addNumericField("Radius", 0.4)
gui.addNumericField("Threshold", 1100)
gui.addCheckbox("Subpixel", True)
gui.addCheckbox("Median", True)
gui.addNumericField("Channel", 1)
gui.addNumericField("Max Frame Gap", 2)
gui.addNumericField("Max Distance", 1)
gui.addNumericField("Max Gap Distance", 0.4)

model = Model()
 
# Send all messages to ImageJ log window.
logger = Logger.IJ_LOGGER
model.setLogger(logger)

gui.showDialog()

def isTIFFFile(file):
	if not isfile(file):
		return False
	filename, extension = splitext(file)
	return extension.lower() == ".tiff" or extension.lower() == ".tif"

def createTrackMateSettingsForImage(img, data):
	"""
	Follows https://imagej.net/plugins/trackmate/scripting#A_full_example
	"""
	settings = Settings()
	settings.setFrom(img)
	settings.detectorFactory = LogDetectorFactory()
	settings.detectorSettings = {
	    'DO_SUBPIXEL_LOCALIZATION' : data.get("subpixel"),
	    'RADIUS' : data.get("radius"),
	    'TARGET_CHANNEL' : int(data.get("channel")),
	    'THRESHOLD' : data.get("threshold"),
	    'DO_MEDIAN_FILTERING' : data.get("median"),
	}
	logger.log("_____")
	logger.log(str(settings.detectorSettings))

	settings.trackerFactory = SparseLAPTrackerFactory()
	settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap() # almost good enough
	settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = True
	settings.trackerSettings['ALLOW_TRACK_MERGING'] = True
	
	qualityFilter = FeatureFilter('QUALITY', 30, True)
	settings.addSpotFilter(qualityFilter)

	# Add ALL the feature analyzers known to TrackMate. They will 
	# yield numerical features for the results, such as speed, mean intensity etc.
	settings.addAllAnalyzers()
	
	return settings

def saveToXML(data, model, settings):
	output_path = data.get("output_file").replace("\\", "/")
	logger.log("Start saving to " + output_path)
	outFile = File(output_path)
	writer = TmXmlWriter(outFile, logger)
	writer.appendModel(model)
	writer.appendSettings(settings)
	writer.writeToFile()

if gui.wasOKed():
	directory = gui.getNextString()
	data = {}
	data["directory"] = directory
	data["radius"] = gui.getNextNumber()
	data["threshold"] = gui.getNextNumber()
	data["channel"] = gui.getNextNumber()
	data["max_frame_gap"] = gui.getNextNumber()
	data["max_distance"] = gui.getNextNumber()
	data["max_gap_distance"] = gui.getNextNumber()
	checkboxes = gui.getCheckboxes()
	data["subpixel"] = checkboxes[0].state
	data["median"] = checkboxes[1].state
	# Creates a list of all xml files in the choosen directory
	tiff_files = [join(directory,f) for f in listdir(directory) if isTIFFFile(join(directory, f))]
	for tiff in tiff_files:
		filename, extension = splitext(tiff)
		data["output_file"] = filename + ".xml"
		tm_img =  IJ.openImage(tiff)
		settings = createTrackMateSettingsForImage(tm_img, data)
		trackmate = TrackMate(model, settings)
		if not trackmate.checkInput():
			sys.exit(str(trackmate.getErrorMessage()))
		if not trackmate.process():
		    sys.exit(str(trackmate.getErrorMessage()))
		saveToXML(data, model, settings)
	