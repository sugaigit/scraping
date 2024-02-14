from logging import DEBUG, FileHandler, Formatter, StreamHandler, getLogger


class StreamAndFileLogger:
    def __init__(self, log_file=None):
        self.prefix = None
        self.logger = getLogger(log_file)
        self.logger.setLevel(DEBUG)

        if log_file is not None:
            # handler1を作成
            handler1 = FileHandler(filename=log_file)
            handler1.setLevel(DEBUG)
            handler1.setFormatter(Formatter("%(asctime)s %(process)d %(levelname)s : %(message)s"))
            self.logger.addHandler(handler1)

        # handler2を作成
        handler2 = StreamHandler()
        handler2.setLevel(DEBUG)
        handler2.setFormatter(Formatter("%(asctime)s %(process)d %(levelname)s : %(message)s"))
        self.logger.addHandler(handler2)

    def kill(self):
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def exception(self, msg):
        self.logger.exception(msg)
