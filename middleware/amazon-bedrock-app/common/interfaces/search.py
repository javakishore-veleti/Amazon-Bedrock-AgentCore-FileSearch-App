from search.models.dtos import SearchReq, SearchResp


class SearchFacade:
    def search(self, req: SearchReq) -> SearchResp:
        raise NotImplementedError
