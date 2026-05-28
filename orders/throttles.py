from rest_framework.throttling import AnonRateThrottle


class CheckoutRateThrottle(AnonRateThrottle):
    scope = 'checkout'


class OrderTrackRateThrottle(AnonRateThrottle):
    scope = 'order_track'
