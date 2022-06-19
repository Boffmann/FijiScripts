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

g_custom_algorithm = "Custom Algorithm"

###################################
# Write custom spot analysis here #
###################################
# The 'analyse_spot()' function is#
# the entry point for custom spot #
# analysis algorithm. It gets a   #
# spot as input and must return   #
# a string to be shown in the     #
# result table.                   #
# The 'analyse_spot()' function   #
# is automatically invoked when   #
# the 'Custom Algorithm' feature  #
# is selected in the dropdown     #

def analyse_spot(spot):
	#anzahl=spots.getNSpots(True)
	# TODO Write algorithm to analyse spots here.
	# Must return a single value as string
	return "Not implemented"

###################################

class Track:
    
    def __init__(self, id, trackModel):
        self.id = id
        self.trackModel = trackModel
        track_spots = trackModel.trackSpots(id)
        self.spots = []
        for spot in track_spots:
        	self.spots.append(spot)

    def get_id(self):
        return self.id

    def get_spot(self, id):
        if len(self.spots) <= id:
            return None
        return self.spots[id]
    
    def get_features(self):
        features = []
        for spot in self.spots:
            features.append(spot.getFeatures().keys())
        return flat_map_get_common(features)

class TrackTable:

    def __init__(self, tracks, feature, spot_analyzer):
        self.spot_analyzer = spot_analyzer
        self.tracks = []
        self.feature = feature
        self.column_names = []
    	self.result_table = ResultsTable()
        for track in tracks:
            self.addTrack(track)

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
                if self.feature == g_custom_algorithm:
                    feature = self.spot_analyzer(spot)
                else:
                    feature = str(spot.getFeature(self.feature))
                self.result_table.addValue(column_name, str(feature))

    def to_results_table(self):
    	rows = self.__tracks_to_rows()
        self.__add_columns(rows)
        [self.__add_row(row) for row in rows[1:]]
    	return self.result_table

def flat_map_get_common(list_of_lists):
    result = set(list_of_lists[0])
    for l in list_of_lists[1:]:
        result.intersection_update(l)
    return result

def isXMLFile(file):
    """
    Checks whether a specific file is indeed a xml file
    """
    if not isfile(file):
        return False
    filename, extension = splitext(file)
    return extension == ".xml"

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

def create_table_for(tracks, feature):
	trackTable = TrackTable(tracks, feature, analyse_spot)
	return trackTable.to_results_table()

def get_tracks_for_files(xml_files):
    result = {}
    for xml_file in xml_files:
        if xml_file is None:
            continue
        result[xml_file] = []
        file = File(xml_file)
        reader = TmXmlReader(file)
        if not reader.isReadingOk():
            continue
        model = reader.getModel()
        trackModel = model.getTrackModel()
        track_ids = trackModel.trackIDs(True)
        for id in track_ids:
            track = Track(id, trackModel)
            result[xml_file].append(track)
    return result

def find_mutual_features(tracks_for_files):
    features_across_files = []
    for xml_file in tracks_for_files:
        features_in_file = []
        for track in tracks_for_files.get(xml_file):
            features_in_file.append(track.get_features())
        common_features_in_file = flat_map_get_common(features_in_file)
        features_across_files.append(common_features_in_file)
    commons_set = flat_map_get_common(features_across_files)
    commons_list = []
    for elem in commons_set:
        commons_list.append(elem)
    return commons_list

# Create logger to output things
logger = Logger.IJ_LOGGER

chooser = GenericDialogPlus("Please select File or Directory containing XMLs")
chooser.addDirectoryOrFileField("Select Directory or Single XML File", "Select Directory or File", 16)
chooser.showDialog()

if chooser.wasOKed():

    path = chooser.getNextString()
    xml_files = get_xmls_to_analyze(path)
    tracks_for_files = get_tracks_for_files(xml_files)
    available_features = find_mutual_features(tracks_for_files)
    available_features.append(g_custom_algorithm)

    # Create a GUI window and add required fields
    gui = GenericDialogPlus("TrackTable to CSV")
    gui.addCheckbox("View Table", True)
    gui.addCheckbox("Auto Save", False)
    gui.addStringField("Add extension to files when saving", "", 16)
    gui.addChoice("Choose a feature to extract.", available_features, available_features[0])

    gui.showDialog()

    if gui.wasOKed():
        checkboxes = gui.getCheckboxes()
        output_extension = gui.getNextString()
        feature = str(gui.getNextChoice())
        should_show = checkboxes[0].state
        should_save = checkboxes[1].state
        for xml_file in tracks_for_files:
            tracks = tracks_for_files[xml_file]
            table = create_table_for(tracks, feature)
            file = File(xml_file)
            filename, extension = splitext(file.getAbsolutePath())
            if should_show:
                table.show("Tracks of file " + filename)
            if should_save:
                output_file = filename + output_extension + ".csv"
                table.save(output_file)