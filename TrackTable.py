from fiji.plugin.trackmate.visualization.hyperstack import HyperStackDisplayer
from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import SelectionModel
from ij.io import DirectoryChooser
from ij.measure import ResultsTable
from java.io import File
import sys
from os import listdir
from os.path import isfile, join, splitext

class Track:
    
    def __init__(self, id, spots):
        self.id = id
        self.spots = []
        for spot in spots:
        	self.spots.append(spot)

    def get_id(self):
        return self.id

    def get_spot(self, id):
        if len(self.spots) <= id:
            return None
        return self.spots[id]

class TrackTable:

    def __init__(self, spot_analyzer):
        self.spot_analyzer = spot_analyzer
        self.tracks = []
        self.column_names = []
    	self.result_table = ResultsTable()

    def addTrack(self, track):
        self.tracks.append(track)

    def __tracks_to_rows(self):
        res = []
        column = 1
        tmp_row = [track.get_id() for track in self.tracks]
        res.append(tmp_row)
        while True:
            tmp_row = [track.get_spot(column) for track in self.tracks]
            # Stop if no row left to add i.e. no track has spots left
            if all([elem == None for elem in tmp_row]):
                break
            res.append(tmp_row)
            column = column + 1
        return res

    def __add_columns(self, rows):
        for track_id in rows[0]:
    		column_name = "Track ID: " + str(track_id)
    		self.column_names.append(column_name)
    		self.result_table.setColumn(column_name, [])

    def __add_row(self, row):
        self.result_table.incrementCounter()
        for column_index in range(0, len(row)):
            spot = row[column_index]
            column_name = self.column_names[column_index]
            if spot is None:
                self.result_table.addValue(column_name, "")
            else:
                feature = self.spot_analyzer(spot)
                self.result_table.addValue(column_name, str(feature))

    def to_results_table(self):
    	rows = self.__tracks_to_rows()
        self.__add_columns(rows)
        [self.__add_row(row) for row in rows[1:]]
    	return self.result_table

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

def analyse_spot(spot):
	#anzahl=spots.getNSpots(True)
	# TODO Write algorithm to analyse spots here.
	# Must return a single value as string
	return str(spot.getFeature("MEAN_INTENSITY01"))

def analyze_tracks(trackModel, fileName, output_file):
	trackTable = TrackTable(analyse_spot)
	track_ids = trackModel.trackIDs(True)
	for id in track_ids:
		track = Track(id, trackModel.trackSpots(id))
		trackTable.addTrack(track)
	result_table = trackTable.to_results_table()
	result_table.show("Tracks of file " + fileName)
	result_table.save(output_file)

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
    filename, extension = splitext(file.getAbsolutePath())
    output_file = filename + ".csv"
    model = reader.getModel()
    trackModel = model.getTrackModel()
    analyze_tracks(trackModel, xml_file, output_file)
    