class RTSADecoderException(Exception):
    """
    Exception which is thrown if something went wrong decoding a RTSA file
    """

    def __init__(self, message):
        super().__init__(message)
