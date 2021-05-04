from cloud.cloud_interface import CloudProvider


class AWS_cloud(CloudProvider):
    def __init__(self) -> None:
        super().__init__()