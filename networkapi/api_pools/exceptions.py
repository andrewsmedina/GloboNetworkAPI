from rest_framework.exceptions import APIException
from rest_framework import status


class PoolDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Pool Does Not Exist.'


class PoolMemberDoesNotExistException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Pool Member Does Not Exist.'

class InvalidIdPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Pool.'

class InvalidIdEnvironmentException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Environment.'


class InvalidIdVipException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for VIP.'


class InvalidIdentifierPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Identifier ja existe'


class InvalidIdPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Pool Member.'

class ScriptRemovePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute remove script for pool.'


class ScriptCreatePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute create script for pool.'


class ScriptAddPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute add script for pool.'


class ScriptCheckStatusPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute status script for pool member.'


class ScriptDeletePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute delete script for pool.'


class ScriptEnablePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute enable script for pool.'


class ScriptDisablePoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute disable script for pool.'


class PoolConstraintVipException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Pool nao pode ser excluido pois esta associado com um VIP.'


class UpdateEnvironmentVIPException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ambiente nao pode ser alterado pois o server pool esta associado com um ou mais VIP.'


class UpdateEnvironmentServerPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ambiente nao pode ser alterado pois o server pool esta associado com um ou mais server pool member.'


class IpNotFoundByEnvironment(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'O ambiente do IP e diferente do ambiente do Server Pool.'


class InvalidRealPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Parametros invalidos do real.'


class InvalidIdPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid id for Pool.'


class ScriptManagementPoolException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Failed to execute management pool members script for pool.'


class InvalidStatusPoolMemberException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid status for Pool Member.'