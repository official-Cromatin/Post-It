import configparser
import logging
from os.path import isfile, split
from pathlib import Path
from shutil import copy

class Advanced_ConfigParser(configparser.ConfigParser):
    """Utility class to ease the use of the configparser libary"""
    VERSION = "2.0"
    number_of_instances = 0

    def __init__(self, path:str, allow_template:bool = True) -> None:
        super().__init__()
        self.__instance_number = self.__class__.number_of_instances
        self.__class__.number_of_instances += 1
        self.__from_template = False

        self.logger = logging.getLogger(f"utils.config.{self.__instance_number}")
        self.logger.debug(f"New instance {self.__instance_number} of class created")

        # Check existence of provided file
        self.__template_path = self.__get_template_path(path)
        if isfile(path):
            self.logger.debug(f"Opening existing file at path: '{path}'")
        else:
            # Check if it is allowed to use an existing template
            if allow_template:
                if isfile(self.__template_path):
                    self.logger.info(f"Using existing template file {self.__template_path}")
                    copy(self.__template_path, path)
                    self.__from_template = True
                else:
                    self.logger.warning("No potential template found, starting with empty file")
        
        # Load the configfile
        self.__file_path = path
        self.__pending_changes = 0

        try:
            self.read_file(open(path))
        except:
            pass
        else:
            self.logger.info(f"Successfully opened config file at path {path}")
    
    def __get_template_path(self, path:str) -> str | None:
        """Looks for a existing template and returns the path to it
        
        If no config file was found, None is returned"""
        path_to_file, file_name = split(path)
        file_name = file_name.split(".")[0]
        path_to_temp = Path(path_to_file) / f".{file_name}.template"

        return path_to_temp
    
    def __has_all_template_options(self, template:configparser.ConfigParser):
        """Check if config contains all sections and options from the template"""
        for section in template.sections():
            if section not in self:
                return False
            template_options = set(template.options(section))
            config_options = set(config.options(section))
            if not template_options.issubset(config_options):
                return False
        return True

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

    def get_config_file_path(self) -> str:
        """Returns the path to the config file"""
        return self.__file_path
    
    def get_template_file_path(self) -> str:
        """Returns the path to the template file, a config could be created from
        
        Returns None if the is no template file"""
        return self.__template_path
    
    def compare_to_template(self) -> str:
        """Returns one of multiple possible keywords depending on the relation of both files

        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | Return Keyword  |                                                       Description                                                        |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+
        | not_found       | No template file found                                                                                                   |
        | equal           | Both files contain the same sections and options                                                                         |
        | config_plus     | Config contains additional sections and/or options compared to template                                                   |
        | config_options  | Config contains additional options but same sections                                                                     |
        | config_base     | Same as "config_plus" but additionally config contains all sections and options from the template                         |
        | config_minus    | Config contains fewer sections and/or options as template                                                                |
        +-----------------+--------------------------------------------------------------------------------------------------------------------------+"""

        # Check existence of template
        if self.__template_path is None:
            return "not_found"

        # Open template file
        template_config = configparser.ConfigParser()
        template_config.read_file(open(self.__template_path))

        # Get sections of both config and template
        config_sections = set(self.sections())
        template_sections = set(template_config.sections())

        # Compare sections
        if config_sections == template_sections:
            # Same sections, now compare options within each section
            config_plus_found = False  # For tracking additional options in config
            config_minus_found = False  # For tracking missing options in config
            
            for section in config_sections:
                config_options = set(self.options(section))
                template_options = set(template_config.options(section))

                if config_options > template_options:
                    config_plus_found = True  # More options in config than template
                elif config_options < template_options:
                    config_minus_found = True  # Fewer options in config than template
            
            if config_plus_found and config_minus_found:
                return "config_plus"
            elif config_plus_found:
                return "config_options"
            elif config_minus_found:
                return "config_minus"
            else:
                return "equal"

        elif config_sections > template_sections:
            # Config has additional sections
            return "config_plus"

        elif config_sections < template_sections:
            # Config has fewer sections
            return "config_minus"


    def created_from_template(self) -> bool:
        """Will ONLY return `True` if the config file has been created from template at the first run"""
        return self.__from_template

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
    print(config.compare_to_template())
    # config["DEFAULT"]["Compression"] = "no"
    # config.save()