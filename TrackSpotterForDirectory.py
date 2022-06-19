from fiji.plugin.trackmate.visualization.hyperstack import HyperStackDisplayer
from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import SelectionModel
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from ij.io import DirectoryChooser
from java.io import File
import sys
from os import listdir
from os.path import isfile, join, splitext

# Open interactive DirectoryChooser window
dc = DirectoryChooser("Choose a directory")

# Create logger to output things
logger = Logger.IJ_LOGGER

# read choosen directory path
directory = dc.getDirectory()

def isXMLFile(file):
	"""
	Checks whether a specific file is indeed a xml file
	"""
	if not isfile(file):
		return False
	filename, extension = splitext(file)
	return extension == ".xml"

def analyse_spots(spots):

	#anzahl=spots.getNSpots(True)
	# TODO Write algorithm to analyse spots here
	result_string = ""
	for spot in spots.iterable(True):
		feature = str(spot.getFeature("MEAN_INTENSITY01"))
		result_string = result_string + feature + ", "
	logger.log(result_string)
		

# Creates a list of all xml files in the choosen directory
xmls = [f for f in listdir(directory) if isXMLFile(join(directory, f))]

# Expands all xml files to absolute path so that they can be opened
xml_files = [join(directory, f) for f in xmls]

# extract spots in each xml file in choosen directory and invokes 'analyse_spots' for each file
for xml_file in xml_files:
	logger.log("Currently analysed file: " + xml_file)
	file = File(xml_file)
	reader = TmXmlReader(file)
	if not reader.isReadingOk():
		continue
	model = reader.getModel()
	spots = model.getSpots()
	analyse_spots(spots)