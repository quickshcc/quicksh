from modules import timestamp
from modules.logs import Log

from fastapi.responses import JSONResponse
from dataclasses import dataclass
from functools import wraps

RATE_LIMITED_RESPONSE = JSONResponse({"status": False, "error": "Try again later."}, 429)


@dataclass
class _EndpointCall:
    caller_id: str
    call_timestamp: int
    forget_after_m: int
    
    def is_forgot(self) -> bool:
        forget_timestamp = timestamp.add_minutes_to_timestamp(self.forget_after_m, self.call_timestamp)
        return forget_timestamp < timestamp.generate_timestamp()
  

class ClientRateLimiter:
    """
    Limits access for unique IDs or IPs.
    
    call_slots: How many times can unique id call endpoint before being rate limited.
    call_expiration_m: Call made X minutes ago will be forgotten and call slot will be freed.
    limit_punishment_m: When call slots limit is met, id will be rate limited for X minutes.
    """
    def __init__(self, endpoint: str, call_slots: int, call_expiration_m: int, limit_punishment_m: int) -> None:
        self.endpoint = endpoint
        self.call_slots = call_slots
        self.call_expiration_m = call_expiration_m
        self.limit_punishment_m = limit_punishment_m
        
        self._calls_cache: dict[str, list[_EndpointCall]] = {} # ID: [_EndpointCall, _EndpointCall...]
        self._rate_limited: dict[str, int] = {} # ID: <int:punishment_end_timestamp>        

    def is_rate_limited(self, caller_id: str) -> bool:
        """ Can client's call be proceeded. """
        if caller_id in self._rate_limited:
            rate_limit_until = self._rate_limited[caller_id]
            if rate_limit_until < timestamp.generate_timestamp():
                Log.info(f"/{self.endpoint} -> {caller_id} - Client's rate limit passed.")
                self._rate_limited.pop(caller_id)
                return False
        
            else:
                Log.warn(f"/{self.endpoint} -> {caller_id} - Rate limited caller cannot proceed.")
                return True
            
        return False
        
    def register_call(self, caller_id: str) -> None:
        """ Register client's call. Punish if needed. Forget expired calls. """
        call_object = _EndpointCall(caller_id, timestamp.generate_timestamp(), self.call_expiration_m)
        
        cleaned_client_cache = [call_object]
        for previous_call in self._calls_cache.get(caller_id, []):
            if not previous_call.is_forgot():
                cleaned_client_cache.append(previous_call)
        self._calls_cache[caller_id] = cleaned_client_cache

        if len(self._calls_cache[caller_id]) > self.call_slots:
            Log.warn(f"/{self.endpoint} -> {caller_id} - Rate limited client for: {self.limit_punishment_m} minutes.")
            rate_limit_until = timestamp.add_minutes_to_timestamp(self.limit_punishment_m, timestamp.generate_timestamp())
            self._calls_cache.pop(caller_id)
            self._rate_limited.update({caller_id: rate_limit_until})
        
    def gate(self, function) -> None:
        limiter_obj = self
        
        @wraps(function)
        async def wrapper(*args, **kwargs):
            request = kwargs["request"]
            client_id = request.client.host

            if limiter_obj.is_rate_limited(client_id):
                return RATE_LIMITED_RESPONSE
            limiter_obj.register_call(client_id)
    
            return await function(*args, **kwargs)
        return wrapper
        