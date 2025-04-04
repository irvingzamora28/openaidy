"""
Filter warnings for tests.
"""
import warnings

# Filter out specific warnings from Google Protobuf
warnings.filterwarnings(
    "ignore", 
    message="Type google._upb._message.MessageMapContainer uses PyType_Spec with a metaclass that has custom tp_new",
    category=DeprecationWarning
)
warnings.filterwarnings(
    "ignore", 
    message="Type google._upb._message.ScalarMapContainer uses PyType_Spec with a metaclass that has custom tp_new",
    category=DeprecationWarning
)
