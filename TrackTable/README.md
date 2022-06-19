# TrackTable
Extracts track features from a XML file and arranges them in tabular form. This happens in a two steps.

1. Select a file or directory. If a directory is chosen, all subsequent actions will be performed to all XML files in the selected directory.
2. In a second dialog, select the desired action. Your options and their implications are described in the following section

## Options
* **View Table**: If this is selected, the resulting table is shown in an extra window. Please notice that this can lead to multiple windows if you selected a directory with multiple XML files.
* **Auto Save**: If this is selected, each resulting table will be automatically saved as a CSV in the same directory as the XML file resides. The name will match the corresponding XML file.
* **Add extension to files when saving**: This allows you to provide a postfix to the saved CSV files. Thereby, you can distinguish multiple CSV files that contain different features.
* **Choose a feature to extract**: This dropdown menu provides a full list of all features that are available in the selected XML file. If a directory was chosen, the drop down contains a set of all common features. Please notice that this can lead to a feature not being shown in the drop down because it is not supported by one or multiple files in the selected directory. The drop down contains a special item called **Custom Algorithm**. Please see down below for further information.

## Custom Algorithm
With the **Custom Algorithm** feature, you can implement your own algorithm to analyse a track's spot. The script contains a special function *analyse_spot(spot)* that is automatically invoked with every spot for every track in the analysed XML files if the **Custom Algorithm** feature option is chosen. The function's only contract is that is must return a string. Feel free to combine multiple features and apply various mathematical functions to them as long as you stick to the simple contract. You can also write further functions and invoke them from *analyse_spot(spot)*. I recommend you to write your algoritm between the *###################################* lines to distinguish them from the framework code more easily.