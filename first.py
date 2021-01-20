import re
from itertools import cycle, tee

import pandas as pd

from util_func import description_extraction, pairwise, vessel_name, excel_extractor


excel_extractor('7065 MAERSK KAMPALA.xls')
