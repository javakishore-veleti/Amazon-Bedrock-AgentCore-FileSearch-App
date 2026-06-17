from common.end_points_dtos import EndPointReqDto, EndPointRespDto


class EndPointService:
    def __init__(self, end_point_repo):
        self.end_point_repo = end_point_repo

    def create_end_point(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_end_point(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_end_points_list(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        raise NotImplementedError("This method should be implemented by subclasses")


class EndPointsDao:
    def create_end_point(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_end_point(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_end_points_list(self, end_point_data: EndPointReqDto, resp: EndPointRespDto):
        raise NotImplementedError("This method should be implemented by subclasses")
