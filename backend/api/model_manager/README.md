The model manager handles the downloading, installation, and configuration of models. All functionality here is internal and private endpoints and by default should only be controlled and configured by the user as they handle read/write data to the drive directly.


Definition of a plugin:
bitorch/plugins/hello_world/

each plugin will have
1. ./__init__.py
2. ./model directory, containing the model repo/binaries. The actual model.
3. ./plugin.json file, containing metadata about the plugin like version, description, creator, training data info, date, name, display name, etc to be displayed in the app and info returned from /list-models endpoint.
4. requirnments.txt/pipfile, dependencies needed to run this plugin.
4. any other python files/directory structure needed to run the model.

The way the plugin system will work dependency wise:
Each plugin will have it's own Pipfile, it's deps will be installed locally in the plugins folder and loaded in a separate environment to the app as to avoid dependency conflicts.
