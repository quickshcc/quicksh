
class T_Error(str):
    pass


SIZE_ERROR = T_Error("File is too big.")
SERVER_SIZE_ERROR = T_Error("Server's usage limit exceeded. Try again later.")
INVALID_LIFETIME = T_Error("Invalid lifetime.")
INVALID_CODE = T_Error("Code not found or is expired.")
NOT_OWNER = T_Error("You are not the owner of the file.")
MAX_SHARED_FILES = T_Error("Cannot share more files. Remove exisitng…")
