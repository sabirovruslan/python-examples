from rest_framework import authentication
from rest_framework import exceptions
from jwt.exceptions import (
    DecodeError, InvalidSignatureError, ExpiredSignatureError
)

from user.models import User
import config.utils.jwt as jwt


class JWTAuthentication(authentication.BaseAuthentication):

    HEADER = 'OTUS'

    def authenticate(self, request):
        hash_string = request.META.get(self.HEADER)
        if not hash_string:
            return None

        try:
            user = jwt.decode(hash_string)
            user = User.objects.get(id=user.get('id'))
        except DecodeError:
            raise exceptions.AuthenticationFailed('Cannot decode give token')
        except ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                'Authentication token has expired'
            )
        except InvalidSignatureError:
            raise exceptions.AuthenticationFailed(
                'Does not match with a signature'
            )
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
