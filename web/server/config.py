__author__ = 'ross'

import ConfigParser


class config:

    def __init__(self):
        self.site_refresh_time = 10  # 10 seconds default
        self.hb_danger_time = 60  # 60 seconds default
        self.hb_warning_time = 30  # 30 seconds default
        self.hb_dead_time = 86400  # 1 day default (86400 seconds)
        self.cpu_fine = 0  # 0% default
        self.cpu_warning = 50  # 50% default
        self.cpu_danger = 75  # 75% default
        self.ram_fine = 0  # 0% default
        self.ram_warning = 50  # 50% default
        self.ram_danger = 75  # 75% default
        self.temp_fine = 0  # 0 degrees C default
        self.temp_warning = 30  # 30 degrees C default
        self.temp_danger = 40  # 40 degrees C default
        self.refresh_config()

    def refresh_config(self):
        parser = ConfigParser.SafeConfigParser()
        try:
            parser.read("server.cfg")
            self.hb_warning_time = parser.getint("heartbeat_visualisation", "warning_time")
            self.hb_danger_time = parser.getint("heartbeat_visualisation", "danger_time")
            self.site_refresh_time = parser.getint("website", "refresh_time")
            self.hb_dead_time = parser.getint("heartbeat_visualisation", "dead_time")
            self.cpu_fine = parser.getint("resource_visual", "cpu_fine")
            self.cpu_warning = parser.getint("resource_visual", "cpu_warning")
            self.cpu_danger = parser.getint("resource_visual", "cpu_danger")
            self.ram_fine = parser.getint("resource_visual", "ram_fine")
            self.ram_warning = parser.getint("resource_visual", "ram_warning")
            self.ram_danger = parser.getint("resource_visual", "ram_danger")
            self.temp_fine = parser.getint("resource_visual", "temp_fine")
            self.temp_warning = parser.getint("resource_visual", "temp_warning")
            self.temp_danger = parser.getint("resource_visual", "temp_danger")
        except ConfigParser.ParsingError, e:
            print "[ERROR] parsing config failed"
            print e
            return
        except ConfigParser.NoSectionError, e:
            print "[ERROR] parsing config, section not found"
            print e
            return
