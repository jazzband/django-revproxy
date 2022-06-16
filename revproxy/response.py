import logging

from .utils import cookie_from_string, should_stream, set_response_headers

from django.http import HttpResponse, StreamingHttpResponse

logger = logging.getLogger('revproxy.response')


def get_django_response(
    proxy_response, strict_cookies=False, streaming_amount=None
):
    """This method is used to create an appropriate response based on the
    Content-Length of the proxy_response. If the content is bigger than
    MIN_STREAMING_LENGTH, which is found on utils.py,
    than django.http.StreamingHttpResponse will be created,
    else a django.http.HTTPResponse will be created instead

    :param proxy_response: An Instance of urllib3.response.HTTPResponse that
                           will create an appropriate response
    :param strict_cookies: Whether to only accept RFC-compliant cookies
    :param streaming_amount: The amount for streaming HTTP response, if not
                             given, use a dynamic value -- 1("no-buffering")
                             for "text/event-stream" content type, 65535 for
                             other types.
    :returns: Returns an appropriate response based on the proxy_response
              content-length
    """
    status = proxy_response.status
    headers = proxy_response.headers

    logger.debug('Proxy response headers: %s', headers)

    content_type = headers.get('Content-Type')

    logger.debug('Content-Type: %s', content_type)

    if should_stream(proxy_response):
        if streaming_amount is None:
            amt = get_streaming_amt(proxy_response)
        else:
            amt = streaming_amount

        logger.info(('Starting streaming HTTP Response, buffering amount='
                     '"%s bytes"'), amt)
        response = StreamingHttpResponse(proxy_response.stream(amt),
                                         status=status,
                                         content_type=content_type)
    else:
        content = proxy_response.data or b''
        response = HttpResponse(content, status=status,
                                content_type=content_type)

    logger.info('Normalizing response headers')
    set_response_headers(response, headers)

    cookies = proxy_response.headers.getlist('set-cookie')
    logger.info('Checking for invalid cookies')
    for cookie_string in cookies:
        cookie_dict = cookie_from_string(cookie_string,
                                         strict_cookies=strict_cookies)
        # if cookie is invalid cookie_dict will be None
        if cookie_dict:
            response.set_cookie(**cookie_dict)

    logger.debug('Response cookies: %s', response.cookies)

    return response


# Default number of bytes that are going to be read in a file lecture
DEFAULT_AMT = 2**16
# The amount of chunk being used when no buffering is needed: return every byte
# eagerly, which might be bad in performance perspective, but is essential for
# some special content types, e.g. "text/event-stream". Without disabling
# buffering, all events will pending instead of return in realtime.
NO_BUFFERING_AMT = 1

NO_BUFFERING_CONTENT_TYPES = set(['text/event-stream', ])


def get_streaming_amt(proxy_response):
    """Get the value of streaming amount(in bytes) when streaming response

    :param proxy_response: urllib3.response.HTTPResponse object
    """
    content_type = proxy_response.headers.get('Content-Type', '')
    # Disable buffering for "text/event-stream"(or other special types)
    if content_type.lower() in NO_BUFFERING_CONTENT_TYPES:
        return NO_BUFFERING_AMT
    return DEFAULT_AMT
