# src/application/exceptions.py
class InvalidCredentialsError(Exception):
    pass

class WebhookDeliveryError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass
class PitchNotFoundError(Exception):
    pass
