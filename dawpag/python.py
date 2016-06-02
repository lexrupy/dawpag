# Got this from kiwi framework
class ClassInittableMetaType(type):
    # pylint fails to understand this is a metaclass
    def __init__(self, name, bases, namespace):
        type.__init__(self, name, bases, namespace)
        self.__class_init__(namespace)

# Got this from kiwi framework
class enum(int):
    """
    enum is an enumered type implementation in python.

    To use it, define an enum subclass like this:

    >>> from dawpag.python import enum
    >>>
    >>> class Status(enum):
    >>>     OPEN, CLOSE = range(2)
    >>> Status.OPEN
    '<Status value OPEN>'

    All the integers defined in the class are assumed to be enums and
    values cannot be duplicated
    """

    __metaclass__ = ClassInittableMetaType

    #@classmethod
    def __class_init__(cls, ns):
        cls.names = {} # name -> enum
        cls.values = {} # value -> enum

        for key, value in ns.items():
            if isinstance(value, int):
                cls(value, key)
    __class_init__ = classmethod(__class_init__)

    #@classmethod
    def get(cls, value):
        """
        Lookup an enum by value
        @param value: the value
        """
        if not value in cls.values:
            raise ValueError("There is no enum for value %d" % (value,))
        return cls.values[value]
    get = classmethod(get)

    def __new__(cls, value, name):
        """
        Create a new Enum.

        @param value: value of the enum
        @param name: name of the enum
        """
        if name in cls.names:
            raise ValueError("There is already an enum called %s" % (name,))

        if value in cls.values:
            raise ValueError(
                "Error while creating enum %s of type %s, "
                "it has already been created as %s" % (
                value, cls.__name__, cls.values[value]))

        self = super(enum, cls).__new__(cls, value)
        self.name = name

        cls.values[value] = self
        cls.names[name] = self
        setattr(cls, name, self)

        return self

    def __str__(self):
        return '<%s value %s>' % (
            self.__class__.__name__, self.name)
    __repr__ = __str__