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
- **New Set** button to create sets from selected bones (prompts for a name).
- **Tools Box** – All editing controls are now grouped in a collapsible "Tools" box for a cleaner interface.
- **Four Toggle Modes** (checkboxes inside the Tools box):
  - **Add/Rem** – Shows **+** and **−** buttons next to each set to add or remove selected bones.
  - **Rename** – Shows a pencil icon to rename a set (dialog pre‑filled with current name).
  - **Move** – Shows ▲ and ▼ arrows to reorder sets.
  - **Del** – Shows an ✕ button to delete a set (with confirmation).
- **Export** – Saves all selection sets to a `.json` file (includes rig name and timestamp).
- **Import** – Loads sets from a `.json` file.
- **Remove All** – Deletes every selection set at once.

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

All new tools are located in the **"Tools"** box at the bottom of the panel.

- **New Set** – Select bones in Pose Mode, click **New Set**, enter a name, and a set is created.
- **Toggle Modes** – Use the checkboxes to reveal extra buttons next to each set:
  - **Add/Rem** – Click **+** to add selected bones to that set, or **−** to remove them.
  - **Rename** – Click the pencil icon, type a new name, and press OK.
  - **Move** – Use ▲ and ▼ to change the order of sets in the list.
  - **Del** – Click the ✕ to delete that set (a confirmation popup appears).
- **Export** – Save all sets to a `.json` file. The file name defaults to `[rig_name]_selection_sets.json`.
- **Import** – Choose a `.json` file to add its sets to the current rig.
- **Remove All** – Clear every selection set from the rig (warning shown if none exist).

**Tip:** Toggle modes on only when you need them to keep the list clean. The checkboxes have icons that fill when active.

## Contributing
Contributions are welcome! If you have ideas for improvements or find any bugs, please create an issue or submit a pull request on [GitHub](https://github.com/DANOverkill/selectionSet_GUI).

## License
This addon is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Contact
If you have any questions or need further assistance, feel free to reach out to me at [danielz.nas@gmail.com].