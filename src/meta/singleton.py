from abc import ABCMeta


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)

        return cls.__instance


class ABCMetaSingleton(ABCMeta, Singleton):
    pass


class SportNameBasedSingleton(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__sport_names_to_instances = {}

    def __call__(cls, sport_name):
        if sport_name not in cls.__sport_names_to_instances:
            instance = super().__call__(sport_name)
            cls.__sport_names_to_instances[sport_name] = instance

        return cls.__sport_names_to_instances[sport_name]
