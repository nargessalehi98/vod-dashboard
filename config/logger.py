import logging
import traceback

logger = logging.getLogger(__name__)


def log_message(*, error, request):
    tb = traceback.extract_stack()[-3]
    line_no = None
    func = None
    if not tb.name.endswith('routing'):
        line_no = tb.lineno
        func = 'validate_input' if tb.name == 'wrap' else tb.name

    if request:
        message = '{ip} | {method} | {error} | {input}'.format(
            ip=request.remote_ip or '\t',
            input=request.api_data or '\t',
            method=f'{func}()[{line_no}]' if func else request.api_method or '\t',
            error=error
        )
    else:
        message = '{error}'.format(error=error)
    return message


def log_error(message, *, request):
    _log_message = log_message(error=message, request=request)
    logger.error(_log_message)


def log_warning(message, *, request):
    _log_message = log_message(error=message, request=request)
    logger.warning(_log_message)

