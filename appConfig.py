import configparser
import os

class AppConfig:
    data_dir = 'data'
    article_id_set = data_dir + os.sep +'article_id.txt'
    article_filename_set = data_dir + os.sep+'article_file_names.txt'

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        self.data_dir = self.get('DEFAULT', 'data_dir')
        self.article_id_set = self.data_dir + os.sep + self.get('DEFAULT', 'article_id')
        self.article_filename_set = self.data_dir+os.sep+self.get('DEFAULT', 'article_file_name')

    def get(self, section, key):
        return self.config[section][key]

    def set(self, section, key, value):
        self.config[section][key] = value
        with open(os.path.join(os.path.dirname(__file__), 'config.ini'), 'w') as configfile:
            self.config.write(configfile)

    def get_all(self, section):
        return self.config[section]

    def set_all(self, section, values):
        for key, value in values.items():
            self.config[section][key] = value
        with open(os.path.join(os.path.dirname(__file__), 'config.ini'), 'w') as configfile:
            self.config.write(configfile)

    def get_sections(self):
        return self.config.sections()

    def get_keys(self, section):
        return self.config[section].keys()

    def get_all_sections(self):
        return self.config.items()

if __name__ == '__main__':
    appConfig = AppConfig()
    print(appConfig.article_filename_set)
    print(appConfig.article_id_set)



