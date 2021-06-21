import logging


class GutenTagLogger:
    def __init__(self):
        self.logger = logging.getLogger("GutenTAG")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())

    def warn_false_combination(self, anomaly: str, base_oscillation: str):
        self.logger.warning(f"You tried to generate '{anomaly}' on '{base_oscillation}'. That doesn't work! Guten Tag!")


if __name__ == "__main__":
    logger = GutenTagLogger()
    logger.warn_false_combination("test", "test2")
