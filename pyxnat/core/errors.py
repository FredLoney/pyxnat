import re

import httplib2

# parsing functions

def is_xnat_error(message):
    return message.startswith('<!DOCTYPE') or message.startswith('<html>')

def parse_error_message(message):

    if message.startswith('<html>'):
        error = message.split('<h3>')[1].split('</h3>')[0]

    elif message.startswith('<!DOCTYPE'):
        if 'Not Found' in message.split('<title>')[1].split('</title>')[0]:
           error = message.split('<title>')[1].split('</title>')[0]
        else:
            error = message.split('<h1>')[1].split('</h1>')[0]

    else:
        error = message

    return error

def parse_put_error_message(message):
    if message.startswith('<html>'):
        error = message.split('<h3>')[1].split('</h3>')[0]

    required_fields = []

    for line in error.split('\n'):

        try:
            datatype_name = re.findall("\'.*?\'",line)[0].strip('\'')
            element_name = re.findall("\'.*?\'",line
                                      )[1].rsplit(':', 1)[1].strip('}\'')

            required_fields.append((datatype_name, element_name))
        except:
            continue

    return required_fields

def catch_error(msg_or_exception, **kwargs):
    # handle errors returned by the xnat server
    if isinstance(msg_or_exception, (str, unicode)):
        # parse the message
        msg = msg_or_exception
        if msg.startswith('<html>'):
            match = re.search('<h1>(?P<error>HTTP Status.+)</h1>', msg) or \
                re.search('<h3>(?P<error>.+)</h3>', msg)
        elif msg.startswith('<!DOCTYPE'):
            match = re.search('<title>(?P<error>.*Not Found.*)</title>', msg) or \
                re.search('<h1>(?P<error>.+)</h1>', msg)
        if match:
            error = match.group('error')
        else:
            error = 'Database error'
        # If there is additional information, then add it to the error message.
        # The replace strips out the dictionary formatting cruft resulting in a
        # clearer error message.
        if kwargs:
            error = error + '(%s)' % re.sub("[{'}]", "", str(kwargs))

        # choose the exception
        if re.search('The request(ed resource)? requires user authentication', error):
            raise OperationalError('Authentication failed')
        elif 'Not Found' in error:
            raise OperationalError('Connection failed')
        else:
            raise DatabaseError(error)

    # handle other errors, raised for instance by the http layer
    elif isinstance(msg_or_exception, httplib2.ServerNotFoundError):
        raise OperationalError('Connection failed')
    else:
        raise DatabaseError(str(msg_or_exception))
    

# Exceptions as defined in PEP-249, the module treats errors using thoses
# classes following as closely as possible the original definitions.

class Warning(StandardError):
    pass

class Error(StandardError):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class DataError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class InternalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass
