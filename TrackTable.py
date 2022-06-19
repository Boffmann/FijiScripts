from fiji.plugin.trackmate.visualization.hyperstack import HyperStackDisplayer
from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import SelectionModel
from fiji.util.gui import GenericDialogPlus
from ij.gui import GenericDialog
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

def get_xmls_to_analyze(path):
    path_file = File(path)
    if path_file.isDirectory():
        # Creates a list of all xml files in the choosen path
        xmls = [f for f in listdir(path) if isXMLFile(join(path, f))]
        # Expands all xml files to absolute path so that they can be opened
        return [join(path, f) for f in xmls]
    else:
        if isXMLFile(path):
            return [path]
        else:
            gui = GenericDialog("ERROR")
            gui.addMessage("Selected file is not a xml file")
            gui.showDialog()

def create_table_for(trackModel):
	trackTable = TrackTable(analyse_spot)
	track_ids = trackModel.trackIDs(True)
	for id in track_ids:
		track = Track(id, trackModel.trackSpots(id))
		trackTable.addTrack(track)
	return trackTable.to_results_table()

# Create a GUI window and add required fields
gui = GenericDialogPlus("TrackTable to CSV")
gui.addDirectoryOrFileField("Select Directory of XML File", "Select Directory", 16)
gui.addCheckbox("View Table", True)
gui.addCheckbox("Auto Save", False)
gui.addStringField("Add extension to files when saving", "", 16)

# Create logger to output things
logger = Logger.IJ_LOGGER

gui.showDialog()

if gui.wasOKed():
    checkboxes = gui.getCheckboxes()
    path = gui.getNextString()
    output_extension = gui.getNextString()
    should_show = checkboxes[0].state
    should_save = checkboxes[1].state
    xml_files = get_xmls_to_analyze(path)
    for xml_file in xml_files:
        if xml_file is None:
            continue
        file = File(xml_file)
        reader = TmXmlReader(file)
        if not reader.isReadingOk():
            continue
        model = reader.getModel()
        trackModel = model.getTrackModel()
        table = create_table_for(trackModel)
        filename, extension = splitext(file.getAbsolutePath())
        if should_show:
            table.show("Tracks of file " + filename)
        if should_save:
            output_file = filename + output_extension + ".csv"
            table.save(output_file)
    