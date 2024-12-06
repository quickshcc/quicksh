from modules.paths import Path
from modules import timestamp
from modules import database
from modules.logs import Log
from modules import errors

from fastapi import UploadFile
from enum import IntEnum
import random
import hashlib
import os


TRANSFERS_PATH = Path("./data/shared/")
MAX_TRANSFER_SIZE = 150 * 1024 * 1024   # 150mb


if not TRANSFERS_PATH.exists():
    TRANSFERS_PATH.touch()


def get_max_data_size_b() -> int | float:
    return float(os.getenv("MAX_DATA_SIZE_MB")) * 1024 * 1024 or 1024 ** 3


def get_total_space_usage_b() -> int:
    """ Returns amount of bytes currently stored. """
    total_size = 0
    
    for model in transfers_db.get_all_models():
        total_size += model.size
        
    return total_size


def is_space_available(size: int) -> bool:
    """ Check if there is enough space to fit file with this size. """
    return get_total_space_usage_b() + size < get_max_data_size_b()


def can_create_code(ip_address: str) -> bool:
    MAX_SHARES = int(os.getenv("MAX_SHARES_PER_IP")) or 5
    
    current_count = 0
    for model in transfers_db.get_all_models():
        if model.owner_ip == ip_address:
            current_count += 1
        
    return current_count < MAX_SHARES


class TransferLifetime(IntEnum):
    MINUTES_15 = 0
    HOURS_1 = 1
    HOURS_12 = 2
    DAYS_1 = 3
    DAYS_3 = 4


LIFETIMES_TIMEDELTA = {
    TransferLifetime.MINUTES_15: timestamp.timedelta(minutes=15),
    TransferLifetime.HOURS_1: timestamp.timedelta(hours=1),
    TransferLifetime.HOURS_12: timestamp.timedelta(hours=12),
    TransferLifetime.DAYS_1: timestamp.timedelta(days=1),
    TransferLifetime.DAYS_3: timestamp.timedelta(days=3)
}


def generate_transfer_code() -> int:
    while True:
        code = random.randrange(10000, 99999)
        
        if str(code) not in transfers_db.get_all_keys():
            return code
    
    
def ensure_file_size(file: UploadFile) -> int:
    if file.size is not None:
        return file.size
    
    size = len(file.file.read())
    file.file.seek(0)
    
    return size
    
    
def hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()

    
@database.DBModel.model("shares", "!code")
class SharedFile:
    code: int
    name: str
    size: int
    date_created: int
    date_expire: int
    owner_ip: str
    
    @staticmethod
    def create_shared_file(file: UploadFile, lifetime: TransferLifetime, ip_address: str) -> "SharedFile | errors.T_Error":
        ip_address = hash_ip(ip_address)
        if not can_create_code(ip_address):
            return errors.MAX_SHARED_FILES
        
        size = ensure_file_size(file)
        if size > MAX_TRANSFER_SIZE:
            return errors.SIZE_ERROR
        
        if not is_space_available(size):
            return errors.SERVER_SIZE_ERROR
        
        if lifetime not in range(0, 5):
            return errors.INVALID_LIFETIME
        
        code = generate_transfer_code()
        date_created = timestamp.generate_timestamp()
        date_expire = timestamp.add_timedelta_to_timestamp(LIFETIMES_TIMEDELTA[lifetime], date_created)
        
        shared_file = SharedFile(
            code, file.filename, size, date_created, date_expire, ip_address
        )
        
        transfer_path = TRANSFERS_PATH / str(code)
        transfer_path.touch()
        
        with open(transfer_path.path, "wb+") as sh_file:
            sh_file.write(file.file.read())
        
        transfers_db.insert(shared_file)
        Log.info(f"Transfered new file: {code}  ({file.filename}, {size} b)")
        
        return shared_file
    
    def remove(self) -> None:
        os.remove(get_file_path(self))
        transfers_db.delete(str(self.code))
        Log.info(f"Removed share: {self.code} ({self.size}b)")
    
    def request_delete(self, ip_address: str) -> bool | errors.T_Error:
        ip_address = hash_ip(ip_address)
        if ip_address != self.owner_ip:
            return errors.NOT_OWNER
        
        self.remove()
        return True
    
    
def get_shared_file(code: int) -> SharedFile | errors.T_Error:
    try:
        shared_file = transfers_db.get(str(code))
        
        if shared_file.date_expire < timestamp.generate_timestamp():
            Log.error(f"Failed to receive shared file: ({code}) - File expired.")
            return errors.INVALID_CODE

        return shared_file

    except database.KeyNotFound:
        Log.error(f"Failed to receive shared file: ({code}) - Code not found.")
        return errors.INVALID_CODE
    

def get_file_path(file: SharedFile) -> str:
    return (TRANSFERS_PATH / str(file.code)).path
    
    
transfers_db = database.Database[SharedFile](SharedFile)

