from http11 import Http11StreamFormat, Http11MessageHandler

class Http2StreamFormat(http2.StreamFormat):
    connection_header = "505249202a20485454502f322e300d0a0d0a534d0d0a0d0a".decode("hex")


