from rest_framework.throttling import UserRateThrottle,AnonRateThrottle


class CustomUserThrottle(UserRateThrottle):
    rate = '3/min'

class CustomAnonRateTrottle(AnonRateThrottle):
    rate = '3/min'