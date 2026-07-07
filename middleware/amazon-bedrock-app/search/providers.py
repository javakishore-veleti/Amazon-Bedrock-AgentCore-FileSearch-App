from common.interfaces.search import SearchFacade
from common.objects_factory import OBJECTS_FACTORY


def get_search_facade() -> SearchFacade:
    return OBJECTS_FACTORY.get("SearchFacade")
