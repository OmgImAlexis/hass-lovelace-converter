"""Lovelace JSON config converter"""
import os
import glob
import logging
import simplejson as json
import yaml
from slugify import slugify

DOMAIN = "lovelace_converter"
_LOGGER = logging.getLogger(__name__)

INPUT = "/config/.storage/lovelace"
OUTPUT = "/config/ui-lovelace"


def setup(hass, config):
    """Load lovelace JSON config from disk."""
    def loadLoveLaceConfig(filePath):
        lovelaceFile = open(filePath, "r+")
        data = json.load(lovelaceFile)
        lovelaceFile.close()

        return data

    def without(d, key):
        new_d = d.copy()
        new_d.pop(key)
        return new_d

    """Write config to YAML file(s) to disk."""
    def convertToYaml(lovelaceJson, directory):
        lovelaceConfig = lovelaceJson["data"]["config"]
        lovelaceMainConfig = without(lovelaceConfig, "views")

        # Write the main lovelace file
        lovelaceYaml = open(directory + ".yaml", "w+")
        yaml.dump(lovelaceMainConfig,
                  lovelaceYaml,
                  default_flow_style=False)
        # Add views include
        lovelaceYaml.write("\nviews: !include_dir_list ui-lovelace/")
        lovelaceYaml.close()

        # Make the directory if it doesn't exist yet
        try:
            os.mkdir(directory)
        except Exception:
            pass

        # Delete all the views incase they deleted a single view
        fileList = glob.glob(directory + "/*.yaml")
        for filePath in fileList:
            try:
                os.remove(filePath)
            except Exception:
                pass

        # Write the views
        views = lovelaceConfig["views"]
        for index, view in enumerate(views, start=1):
            filename = str(index).zfill(2) + "-" + \
                slugify(view["title"]) + ".yaml"
            lovelaceYaml = open(directory + "/" + filename, "w+")
            yaml.dump(view,
                      lovelaceYaml,
                      default_flow_style=False)
            lovelaceYaml.close()

    """Convert config to YAML."""
    def convert(call):
        try:
            # Load the current lovelace config from disk
            lovelaceJson = loadLoveLaceConfig(INPUT)
            # Write yaml conversion to directory
            convertToYaml(lovelaceJson, OUTPUT)

            _LOGGER.info("Convertion done!")
        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.error("Something went wrong - {}".format(error))

    # Register our service with Home Assistant
    hass.services.register(DOMAIN, 'convert', convert)

    # Return boolean to indicate that initialization was successful
    return True
