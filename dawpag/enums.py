from dawpag.python import enum

class Direction(enum):
    (LEFT, RIGHT) = (1, -1)

class DataState(enum):
    (INSERTING, BROWSING, EDITING) = range(3)

class ColumnDraw(enum):
    (TEXT, TOGGLE, PIXBUF, PROGRESS, CUSTOM) = (0,1,2,3,4)