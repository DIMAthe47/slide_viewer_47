class SlideTile:
    def __init__(self, slide_path=None, downsample=None, rect=None) -> None:
        super().__init__()
        self.slide_path = slide_path
        self.downsample = downsample
        self.rect = rect
