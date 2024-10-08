import configparser
import logging
from os.path import isfile, split
from pathlib import Path
from shutil import copy

class Advanced_ConfigParser(configparser.ConfigParser):
    """Utility class to ease the use of the configparser libary
    
    Version 1.0"""
    number_of_instances = 0

    def __init__(self, path:str, allow_template:bool = True) -> None:
        super().__init__()
        self.__instance_number = self.__class__.number_of_instances
        self.__class__.number_of_instances += 1

        self.logger = logging.getLogger(f"utils.config.{self.__instance_number}")
        self.logger.debug(f"New instance {self.__instance_number} of class created")

        # Check existence of provided file
        if isfile(path):
            self.logger.debug(f"Opening existing file at path: '{path}'")
        else:
            # Check if it is allowed to use an existing template
            if allow_template:
                path_to_file, file_name = split(path)
                file_name = file_name.split(".")[0]
                path_to_temp = Path(path_to_file) / f".{file_name}.template"
                # Check for the existence of the file
                if isfile(path_to_temp):
                    self.logger.info(f"Using existing template file {path_to_temp}")
                    copy(path_to_temp, path)
                else:
                    self.logger.warning("No potential template found, starting with empty file")
        
        # Load the configfile
        self.__file_path = path
        self.__pending_changes = 0
        self.read_file(open(path))
    
    def set(self, section: str, option: str, value: str | None = None) -> None:
        old_value = self.get(section, option, fallback=None)
        if old_value:
            self.logger.debug(f"New value in section '{section}' at option '{option}' added: '{value}'")
            self.__pending_changes += 1
        else:
            self.logger.debug(f"Value in section '{section}' at option '{option}' changed: '{self[section][option]}' -> '{value}'")
            if old_value != value:
                self.__pending_changes += 1
        
        return super().set(section, option, value)
    
    def remove_option(self, section, option):
        if self.has_option(section, option):
            value = self.get(section, option)
            self.logger.debug(f"Option removed in section '{section}' for '{option}': '{value}'")
            self.__pending_changes += 1
        
        return super().remove_option(section, option)
    
    def remove_section(self, section):
        if self.has_section(section):
            self.logger.info(f"Section removed: '{section}'")
            self.__pending_changes += 1

        return super().remove_section(section)
    
    def save(self):
        """Saves changes to disk"""
        with open(self.__file_path, 'w') as configfile:
            self.write(configfile)
        self.logger.debug(f"Contents ({self.__pending_changes} changes) have been saved to disk")

if __name__ == "__main__":
    # Dummy logger
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logger = logging.getLogger("utils")
    logger.addHandler(console)
    logger.setLevel(logging.DEBUG)

    file_path = Path(__file__).resolve()

    base_path = file_path.parents[2]
    print(f"Base path of the program: {base_path}")

    config = Advanced_ConfigParser(Path.joinpath(base_path, "config", "bot.ini"))
    config["DEFAULT"]["Compression"] = "no"
    config.save()