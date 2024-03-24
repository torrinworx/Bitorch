from abc import ABC, abstractmethod


COLLECTION = "models"


class Plugin(ABC):
    @abstractmethod
    def load_model(self):
        """
        Load the necessary model components.
        """
        raise NotImplementedError

    @abstractmethod
    def preprocess(self, input_data):
        """
        Preprocess input data suitable for the model.
        
        input_data: data coming in from the fastapi endpoint (tbd what this actually is though and how we will handle this here)
        
        """
        raise NotImplementedError

    @abstractmethod
    def inference(self, preprocessed_data, parameters):
        """
        Run inference on the preprocessed data using the model.
        """
        raise NotImplementedError

    @abstractmethod
    def postprocess(self, prediction):
        """
        Transform the model's raw output into a suitable format.
        """
        raise NotImplementedError


# class ModelManagerTasks:
#     @staticmethod
#     async def startup():
#         """
#         Initialize startup tasks for the model manager, things like loading default load models into memeory
#         checking model integrity and that the database is in sync with the file system.
        
        
#         """
#         pass
    
#     @staticmethod
#     def register_plugins():
#         """
#         Scan the plugins directory and mongodb and register plugins.
#         """
#         pass

# class ModelManagerMethods:
#     """
#     The ModelManagerMethods class contains a collection of static methods that correspond to
#     the public API endpoints defined in the backend/api/model_manager folder, which are exposed
#     through a FastAPI application interface. These methods are to be kept private and are only
#     to be used by the owner of the server, but it can be designed in the future to be configurable
#     to allow larger networks of the server to be managed, but this is not an immediate concern.
#     """


# class ModelManagerUtils:
#     """
#     is a utility class that provides miscellaneous static methods which
#     support the functionality of the ModelManger and it's interaction
#     endpoints.
#     """


# class ModelManagerMongo:
#     """
#     A utility class that serves as an interface to the MongoDB database
#     for operations related to managing models.
#     """
