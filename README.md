# Selection Set GUI

## Welcome!
Thank you for checking out my first Blender addon created with Python!

Selection Set GUI is an addon designed to simplify the management, creation, editing, and ease of access of selection sets within Blender. Some of these features are still not implemented but will be coming soon. 

## Features
- Recognizes any selection sets already created in a rig
- Automatically creates buttons to select each set individually
- Easily select multiple selection sets by SHIFT-clicking
- Remove all bones from a selection by CTRL-clicking
- Compatible with Blender 4.0 and above
## New Features - Added in Version 2.0.0
- Redesigned UI panel under the "Selection Sets - DEV" tab in the 3D View sidebar.
- **New Set** button to create sets from selected bones.
- **Edit toggle** (checkbox) to show reorder arrows (▲/▼) for each set.
- **Remove toggle** (red checkbox) to show delete buttons (✕) for individual sets.
- **Export** all sets to a `.json` file (includes rig name and timestamp in a comment).
- **Import** sets from a `.json` file.
- **Remove All** button to clear every set at once.

## Installation
1. **Download**: Download the ZIP file of the addon from the [releases page](https://github.com/DANOverkill/selectionSet_GUI)
2. **Open Blender**: Launch Blender and go to `Edit` > `Preferences`.
3. **Install the Addon**:
   - Navigate to the `Add-ons` tab.
   - Click `Install...` at the top of the preferences window.
   - Select the downloaded ZIP file and click `Install Add-on`.
4. **Activate the Addon**: After installation, enable the addon by checking the box next to "Selection Set GUI".

## Usage
1. **Open the Tool Panel**: Press `N` to open the `View3D` tool panel.
2. **Navigate to the Tool Tab**: Find the "Selection Set GUI" panel within the `Tool` tab.
3. **Manage Selection Sets**: Make sure you are in pose mode. Use the provided buttons and options to select the bones from selection sets present in the rig. 

## Usage – New Features in Version 2.0.0
- **New Set** – Creates a new selection set from the currently selected bones. You will be prompted to name the set.
- **Edit Toggle (checkbox next to New Set)** – Shows ▲ and ▼ arrows next to each set, allowing you to reorder them.
- **Remove Toggle (red checkbox)** – Shows an ✕ button next to each set. Click it to delete that specific set (with confirmation).
- **Export** – Saves all selection sets to a `.json` file. The file includes a header with the rig name and timestamp for team tracking.
- **Import** – Loads selection sets from a previously exported `.json` file and adds them to the current rig.
- **Remove All** – Deletes every selection set on the current rig (with a warning if none exist).

**Tip:** The toggles let you show/hide the editing controls to keep the UI clean when you don't need them.

## Contributing
Contributions are welcome! If you have ideas for improvements or find any bugs, please create an issue or submit a pull request on [GitHub](https://github.com/DANOverkill/selectionSet_GUI).

## License
This addon is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Contact
If you have any questions or need further assistance, feel free to reach out to me at [danielz.nas@gmail.com].
