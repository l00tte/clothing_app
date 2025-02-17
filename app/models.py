from dataclasses import dataclass, field
import pandas as pd
import uuid
from typing import List 
from datetime import datetime
import numpy as np

@dataclass 

class Clothing_Item:
    id: str
    name: str
    clothing_type: str
    season: str
    colour: str
    material: str

    def __post_init__(self):
        # Generate id if not provided
        if self.id == None:
            object.__setattr__(self, 'id', str(uuid.uuid4()))  


@dataclass
class Outfit:
    id: str
    name: str = "Unnamed Outfit"
    weather: str = "Any"
    occasion: str = "Casual"
    clothing_items: List[Clothing_Item] = field(default_factory=list)
    date_selected: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


    def __post_init__(self):
        # Generate id if not provided
        if self.id == None:
            object.__setattr__(self, 'id', str(uuid.uuid4()))  


@dataclass
class OutfitSelection:
    name: str
    date_selected: str

    def __post_init__(self):
        # If date is not provided, set it to the current date
        if not self.date_selected:
            self.date_selected = datetime.now().strftime("%Y-%m-%d")
