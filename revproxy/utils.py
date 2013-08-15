
def normalize_headers(request):
    norm_headers = {}
    for header, value in request.META.items():
        if header.startswith('HTTP_'):
            norm_header = header[5:].title().replace('_', '-')
            norm_headers[norm_header] = value

    return norm_headers
