def calc_dir_mode(mode):
    R_OWN = int("0400",8)
    R_GRP = int("0040",8)
    R_OTH = int("0004",8)
    W_OWN = int("0200",8)
    W_GRP = int("0020",8)
    W_OTH = int("0002",8)
    X_OWN = int("0100",8)
    X_GRP = int("0010",8)
    X_OTH = int("0001",8)
    
    if mode & R_OWN:
        mode |= X_OWN
    if mode & R_GRP:
        mode |= X_GRP
    if mode & R_OTH:
        mode |= X_OTH
    return mode
