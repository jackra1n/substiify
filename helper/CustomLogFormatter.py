import logging

class CustomLogFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    dark_grey = "\x1b[30;1m"
    green = "\x1b[1;32m"
    light_blue = "\x1b[34;1m"
    yellow = "\x1b[1;33m"
    purple = "\x1b[1;35m"
    red = "\x1b[1;31m"
    bold_red = "\x1b[5m\x1b[1;31m"
    reset = "\x1b[0m"

    format_prefix = "["+green+"{asctime}"+reset+"] ["
    level_name = "{levelname:<7}"+reset+"] "
    source_line = purple+"line {lineno} in"+reset+" -> "
    format_suffix = light_blue+"{name}"+reset+": {message} "

    dt_fmt = '%Y-%m-%d %H:%M:%S'

    FORMATS = {
        logging.DEBUG: format_prefix + dark_grey + level_name + format_suffix,
        logging.INFO: format_prefix + dark_grey + level_name + format_suffix,
        logging.WARNING: format_prefix + yellow + level_name + source_line + format_suffix,
        logging.ERROR: format_prefix + red + level_name + source_line + format_suffix,
        logging.CRITICAL: format_prefix + bold_red + level_name + source_line + format_suffix
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.dt_fmt, style='{')
        return formatter.format(record)