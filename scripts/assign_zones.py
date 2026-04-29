#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assign TDWG/Kew Gardens geographic zones to each plant.

Zone assignments are hardcoded from botanical knowledge (not LLM-generated),
based on the TDWG World Geographical Scheme for Recording Plant Distributions
(WGSRPD) used by Kew Gardens / POWO.

Usage:
  cd <project_root>
  python scripts/assign_zones.py [--dry-run]
  --dry-run   Print what would be written without touching the DB
"""
import sqlite3
import sys
import io
import os
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'androidApp', 'src', 'main', 'assets', 'plants.db')

# ---------------------------------------------------------------------------
# 22 TDWG Geographic Zones (WGSRPD — Kew Gardens standard)
# ---------------------------------------------------------------------------
ZONES = [
    ('zone_northern_europe',     'Northern Europe'),
    ('zone_central_europe',      'Central Europe'),
    ('zone_southern_europe',     'Southern Europe & Mediterranean'),
    ('zone_eastern_europe',      'Eastern Europe'),
    ('zone_northern_africa',     'North Africa'),
    ('zone_western_africa',      'West & Central Africa'),
    ('zone_eastern_africa',      'East Africa'),
    ('zone_southern_africa',     'Southern Africa'),
    ('zone_western_asia',        'Middle East & Western Asia'),
    ('zone_central_asia',        'Central Asia'),
    ('zone_south_asia',          'South Asia (Indian Subcontinent)'),
    ('zone_southeast_asia',      'Southeast Asia'),
    ('zone_east_asia',           'East Asia'),
    ('zone_siberia',             'Siberia & Russian Far East'),
    ('zone_north_america_east',  'Eastern North America'),
    ('zone_north_america_west',  'Western North America'),
    ('zone_central_america',     'Central America & Caribbean'),
    ('zone_south_america_north', 'Northern South America'),
    ('zone_south_america_south', 'Southern South America'),
    ('zone_australia_oceania',   'Australia & Oceania'),
    ('zone_arctic',              'Arctic & Subarctic'),
    ('zone_tropical_africa',     'Tropical Africa'),
]

# Short aliases
NE = 'zone_northern_europe'
CE = 'zone_central_europe'
SE = 'zone_southern_europe'
EE = 'zone_eastern_europe'
NA = 'zone_northern_africa'
WA = 'zone_western_africa'
EA = 'zone_eastern_africa'
SA = 'zone_southern_africa'
WAS = 'zone_western_asia'
CA = 'zone_central_asia'
SAS = 'zone_south_asia'
SEA = 'zone_southeast_asia'
EAS = 'zone_east_asia'
SIB = 'zone_siberia'
NAE = 'zone_north_america_east'
NAW = 'zone_north_america_west'
CAM = 'zone_central_america'
SAN = 'zone_south_america_north'
SSA = 'zone_south_america_south'
AO = 'zone_australia_oceania'
ARC = 'zone_arctic'
TA = 'zone_tropical_africa'

# ---------------------------------------------------------------------------
# Plant zone assignments keyed by DB id (integer)
# Source: TDWG/WGSRPD via Kew Gardens POWO database knowledge
# Multiple zones = plant grows natively OR is widely naturalized across these
# ---------------------------------------------------------------------------
PLANT_ZONES = {
    # ---- Acai / Tropical America ----
    0:   [SAN],                              # Acai palm — Amazon basin
    # ---- A ----
    1:   [CA, WAS, SE, NAE, NAW, AO],        # Alfalfa — Central Asian origin, worldwide
    2:   [EA, SA, NA, WAS],                  # Aloe Vera — NE Africa, Arabian Peninsula
    3:   [CE, NE, NAW],                      # Arnica montana — Alpine/sub-alpine Europe
    4:   [SAS],                              # Ashoka Tree — Indian Subcontinent
    5:   [SAS, SEA, EAS, TA],               # Garden Spurge — pantropical Asia/Africa
    6:   [CE, SE, EE, NA, WAS, CA, EAS],    # Astragalus — Eurasia (wide genus)
    7:   [CE, SE, NA, WAS],                  # Common Barberry — C.Europe, Med, W.Asia
    8:   [SE, CE, EE, NA, WAS],              # Belladonna — S+C Europe, W.Asia
    10:  [SAS, SEA, EAS, TA],               # Bitter melon — Tropical Asia & Africa
    11:  [WA, TA],                           # Bitter leaf — West Africa
    12:  [SEA, SAS, SE, NA, CAM, SAN],      # Bitter orange — SE Asia origin, Med
    13:  [NAE],                              # Black cohosh — E.North America
    14:  [SE, NA, WAS],                      # Cnicus benedictus — Med & SW Asia
    15:  [NE, CE, NAE, NAW, ARC],           # Blueberry — N.Hemisphere boreal
    16:  [CE, EE, SE, WAS, CA, EAS, SIB],  # Burdock — Eurasia
    17:  [SAN, CAM],                         # Cat's Claw — Amazon/Andes
    18:  [SAN, CAM],                         # Cayenne Pepper — Tropical Americas (origin)
    19:  [SE, CE, NA, WAS],                  # Celery — Mediterranean, W.Asia
    20:  [SSA],                              # Cinchona — Andes (Peru/Ecuador/Bolivia)
    21:  [SEA],                              # Clove — Maluku Islands, SE Asia
    22:  [TA, SAN, SEA, SAS],              # Coffee Senna — pantropical
    23:  [CE, EE, WAS],                      # Comfrey — C+E Europe, W.Asia
    24:  [NE, CE, NAE, ARC],                # Cranberry — N.Hemisphere bogs
    25:  [NE, CE, EE, SE, WAS, EAS, NAE, NAW],  # Dandelion — N.Hemisphere widespread
    26:  [CE, SE, WAS, NA],                  # Woolly Foxglove — S+C Europe, W.Asia
    27:  [EAS],                              # Dong Quai — China/Japan/Korea
    28:  [NE, CE, SE, EE, WAS],             # Elderberry — Europe, W.Asia
    29:  [EAS, CA],                          # Chinese Ephedra — China, C.Asia
    30:  [AO],                               # Eucalyptus — Australia
    31:  [CE, NE, SE, EE, WAS],             # Mistletoe — Europe, W.Asia
    32:  [NAE, NAW],                         # Evening Primrose — N.America
    33:  [SE, NA, WAS, SAS, CA],            # Fenugreek — Med, India origin
    34:  [SE, CE, WAS],                      # Feverfew — SE Europe, Caucasus
    35:  [SE, CE, WAS, CA],                  # Flax — Med, W.Asia (domesticated)
    36:  [CA, WAS, SE, EE, SAS],            # Garlic — C.Asia origin, worldwide
    37:  [SAS, SEA],                         # Ginger — S+SE Asia (India/SE Asia)
    38:  [EAS],                              # Ginkgo — China (endemic)
    39:  [EAS],                              # Ginseng (Panax ginseng) — Korea/China/Russia
    40:  [NAE],                              # Goldenseal — E.North America
    41:  [SE, WAS, CA, NA],                  # Grape — Caucasus, Med, W.Asia
    42:  [SAN, CAM],                         # Guava — C+S America, now pantropical
    43:  [CE, SE, EE, WAS, NAE, NAW],       # Hawthorn — N.Hemisphere wide
    44:  [NA, WAS, SAS],                     # Henna — N.Africa, W.Asia, India
    45:  [SE, EE],                           # Horse Chestnut — Balkans origin
    46:  [NE, CE, EE, NAE, NAW, ARC],       # Horsetail — Circumboreal
    47:  [CAM],                              # Jamaican Dogwood — Caribbean
    48:  [AO, SEA],                          # Kava — Pacific Islands, Oceania
    49:  [EA, WAS],                          # Khat — Horn of Africa, SW Arabia
    50:  [EAS, SEA],                         # Konjac — China, SE Asia
    51:  [SEA],                              # Kratom — SE Asia (Thailand, Indonesia)
    52:  [SE, NA],                           # Lavender — Mediterranean
    53:  [SAS, SE, NA],                      # Lemon — India origin, Med widespread
    54:  [SE, NA, WAS, CA],                  # Liquorice — Med, C.Asia, W.Asia
    55:  [SAS, SEA, EAS],                    # Lotus — Asia (India, China, SE Asia)
    56:  [SE, CE, EE, WAS, NA],             # Pot Marigold — Med, W.Asia
    57:  [SE, WAS, CA, NA],                  # Marshmallow — Med, W.Asia
    58:  [SE, CE, NA, WAS],                  # Milk Thistle — Med, S+C Europe
    59:  [WAS, CA, SAS, SE],                 # Opium Poppy — W.Asia, C.Asia (origin)
    60:  [SE, WAS, NA],                      # Oregano — Mediterranean
    61:  [CAM, SAN, SEA],                    # Papaya — Central America origin
    62:  [NE, CE, EE],                       # Peppermint — Europe hybrid (garden origin)
    63:  [NAE],                              # Eastern purple coneflower — E.N.America
    64:  [SE, NA, WAS],                      # Rosemary — Mediterranean
    65:  [SE, NA, WAS],                      # Sage — Mediterranean
    66:  [CE, NE, SE, EE, WAS],             # Common Saint John's wort — Europe, W.Asia
    67:  [SE, WAS, NA],                      # Summer savory — Mediterranean
    68:  [SE, CE, WAS, NA],                  # Thyme — Mediterranean, S.Europe
    69:  [CE, EE, NE, WAS],                  # Valerian — Europe, W.Asia
    70:  [CE, EE, WAS, NA],                  # White willow — C+E Europe, W.Asia
    80:  [NAW, CAM],                         # Creosote Bush — SW N.America, Mexico
    81:  [CE, SE, EE, NA, WAS],             # Chamomile — C+S Europe, W.Asia
    82:  [SE, WAS, NA],                      # Chaste Tree — Med, W.Asia
    87:  [NA, EA, WA, TA],                   # Gum arabic — Sub-Saharan Africa
    88:  [SA],                               # Hoodia — Southern Africa (Kalahari)
    90:  [SAS],                              # Neem — India, S.Asia
    91:  [SEA, AO],                          # Noni — SE Asia, Pacific
    92:  [SAN, CAM],                         # Passiflora — Tropical Americas
    93:  [NE, CE, SE, EE, NAE, NAW],        # Red Clover — Europe, N.America
    94:  [WAS, NA, CA],                      # Syrian Rue — W.Asia, N.Africa, C.Asia
    95:  [AO],                               # Tea tree oil — Australia
    96:  [EAS],                              # Thunder God Vine — China (E.Asia)
    97:  [SAS, SEA],                         # Holy Basil — India, S+SE Asia
    98:  [SAS, SEA],                         # Turmeric — India, SE Asia
    99:  [CE, NE, EE, NAE, NAW],            # Watercress — Europe, N.America
    100: [NE, CE, NAE, NAW, ARC],           # Wheatgrass — Boreal N.Hemisphere
    101: [CAM],                              # Hoja Santa — Mexico, Central America
    102: [CE, NE, SE, EE, WAS, NA],         # Dog Rose — Europe, W.Asia, N.Africa
    103: [SE, NA, WAS],                      # Fennel — Mediterranean
    104: [CE, SE, EE, NA, WAS],             # Cornflower — C+SE Europe, W.Asia
    105: [CE, EE, WAS, NA],                  # Greater Celandine — Europe, W.Asia
    106: [SE, EE, WAS],                      # Birthwort (Aristolochia) — S+E Europe, W.Asia
    107: [NE, CE, SE, NAE, NAW, WAS],       # Juniper — N.Hemisphere wide
    108: [SE, NA, WAS, SAS],                 # Castor Bean — E.Africa/W.Asia origin, tropical worldwide
    109: [SE, CE, WAS, NA],                  # Mandrake — Med, W.Asia
    110: [CE, NE, SE, EE, WAS, NAE, NAW],  # Blackberry — N.Hemisphere wide
    111: [CE, SE, NE, EE, WAS, NA],         # Oak — Europe, W.Asia, N.Africa
    112: [SE, WAS, NA, CA],                  # Hyssop — Med, W.Asia, C.Asia
    114: [SE, CE, WAS, NA],                  # Parsley — Mediterranean
    115: [SE, CE, WAS, NA],                  # Borage — Mediterranean
    117: [SAS, SEA, EAS],                    # Basil — Asia origin (India/SE Asia)
    118: [CE, EE, SE, WAS],                  # Cabbage — Europe, W.Asia (wild origin)
    119: [WAS, NA, SE, SAS],                 # Pomegranate — W.Asia, N.Africa, India
    120: [CE, SE, EE, WAS, NA],             # Chicory — C+S Europe, W.Asia, N.Africa
    122: [SE, WAS, NA],                      # Rue (Ruta graveolens) — Med, W.Asia
    123: [WAS, CA, SE, SAS],                 # Saffron — W.Asia, C.Asia (Iran/Kashmir)
    125: [NE, CE, EE, SE, WAS, NAE, NAW],  # Yarrow — N.Hemisphere wide
    126: [NE, CE, EE, NAE, NAW, ARC],       # Silverweed — Circumboreal
    127: [SE, CE, WAS, NA],                  # White horehound — Med, W.Asia, N.Africa
    128: [CE, EE, WAS, EAS],                 # Mugwort — Eurasia
    129: [EA, WAS, NA],                      # Myrrh — NE Africa, Arabia, W.Asia
    130: [SE, WAS, NA, CA],                  # Anise — Mediterranean, W.Asia
    131: [SE, CE, WAS, NA],                  # Marigold — Med, W.Asia
    132: [CE, EE, SE, WAS, CA, EAS, SIB],  # Greater Burdock — Eurasia
    137: [SAS, SEA],                         # Cardamom — India, SE Asia (W.Ghats)
    138: [SEA],                              # Thai Ginger — SE Asia (Galangal)
    141: [WAS, NA, SE, SAS],                 # Coriander — W.Asia, Med, India
    142: [CE, WAS, CA, SE],                  # Dill — C+SE Europe, W.Asia
    143: [NE, CE, EE, WAS],                  # Angelica — N+C Europe, W.Asia
    151: [EAS],                              # Chinese Goldthread — China, E.Asia
    155: [SE, NA, WAS],                      # Seville Orange — SE Asia origin, now Med
    156: [CE, NE, SE, EE, WAS, NA, CA],    # Rosehip — N.Hemisphere
    180: [CE, SE, WAS, NA],                  # Corn Poppy — C+S Europe, W.Asia
    181: [CE, NE, EE, NAE, NAW],            # Common Plantain — Europe, N.America
    182: [CE, SE, EE, WAS, NAE, NA],        # Vervain — Europe, W.Asia, N.Africa
    183: [CE, SE, EE, WAS],                  # Mezereum — C+S Europe, W.Asia
    184: [SAS, SEA, EAS],                    # Bitter Melon — Tropical Asia
    187: [NAE],                              # Sugar Maple — E.North America
    189: [WAS, CA, SE, CE, EE, NA, SAS],   # Onion — C.Asia/W.Asia origin, widespread
    190: [SE, WAS],                          # Mastic — Med (Chios, Greece), W.Asia
    191: [CAM, SAN],                         # Soursop — Tropical Americas
    192: [SE, WAS, NA, SAS, EAS],           # Periwinkle — Med/Indian origin
    193: [EAS],                              # Asian Ginseng — Korea, China, Russia
    194: [NAE],                              # American Ginseng — E.North America
    195: [SE, EE, CE, WAS],                  # Birthwort — S+E Europe, W.Asia
    196: [NE, CE, EE, WAS, SIB],            # Silver Birch — N+C Europe, Russia
    198: [SAN, CAM, SEA],                    # Pineapple — Brazil origin, tropical
    200: [WAS, EA, NA],                      # Frankincense — NE Africa, Arabia
    201: [CA, SAS, CE, WAS],                 # Hemp — C.Asia origin, widespread
    202: [SAS, EA, WA, TA],                  # Moringa — N.India, NE Africa
    204: [SAS, SEA, EAS],                    # Cinnamon — Sri Lanka, SE Asia
    205: [SE, CE, WAS, NA],                  # Autumn Crocus — Med, S.Europe, W.Asia
    206: [CE, SE, EE, WAS, NA],             # Houseleek — Mountains of S+C Europe
    207: [SEA, EAS, SAS],                    # Sago Palm — SE Asia
    208: [NAE, CAM, SAN],                    # Wild Yam — E.N.America, Caribbean
    209: [EAS, SE, WAS],                     # Persimmon — E.Asia, also Med
    210: [NE, CE, EE, WAS, SIB, ARC],       # Bilberry — N.Hemisphere boreal
    212: [CE, NE, SE, EE, WAS, NA],         # English Oak — Europe, W.Asia
    213: [CE, SE, EE, WAS, SAS],            # Yellow Gentian — S+C Europe, W.Asia
    214: [SA],                               # Umckaloabo — S.Africa (Cape)
    215: [EAS],                              # Chinese Foxglove — China, E.Asia
    216: [AO, SE, NA],                       # Scaevola — Australia/Pacific origin
    217: [NE, CE, EE, NAE, NAW, SIB],       # Blackcurrant — N.Hemisphere
    218: [NAE],                              # Witch Hazel — E.North America
    220: [NAW, NAE],                         # Phacelia — N.America
    221: [NAE, NAW],                         # Blue Flag — N.America
    222: [NAE],                              # Black Walnut — E.North America
    223: [SE, WAS, NA, EAS],                 # Bay Laurel — Med, W.Asia
    224: [CAM, SAN, SE, NA],                 # Avocado — C.America origin, now tropical
    225: [SE, WAS, NA, SAS],                 # Madonna Lily — Med, W.Asia
    227: [EAS],                              # Magnolia Bark — China, Japan
    229: [TA, EA, WA, SEA, SAS, CAM, SAN],  # Hibiscus — pantropical (wide genus)
    230: [SAS, SEA],                         # Indian Rhododendron — India, SE Asia
    232: [SAS],                              # Guduchi — India, S.Asia
    234: [SE, WAS, NA, SAS],                 # Common Fig — Med, W.Asia
    235: [SEA, SAS, EAS, TA, SAN],          # Banana — SE Asia origin, tropical
    236: [SEA, SAS],                         # Nutmeg — Maluku Islands, SE Asia
    239: [SE, NA, WAS, EA],                  # Olive — Mediterranean, N.Africa
    240: [WAS, CA, SE, EE],                  # Ephedra — W.Asia, C.Asia, Med, E.Europe
    241: [CAM],                              # Vanilla — Mexico, C.America
    242: [CE, NE, EE, NAE, NAW, AO],        # Wood Sorrel — Cosmopolitan
    243: [NAE, SE],                          # Saw Palmetto — SE North America
    244: [SAN, CAM],                         # Passion Fruit — S+C America
    245: [SE, NA, WAS, SAS, EA, EAS, SEA],  # Sesame — Old World tropical
    246: [CE, SE, WAS],                      # Mock Orange — S+C Europe, W.Asia
    247: [NAE],                              # Pokeroot — E.North America
    248: [SAS, SEA, EAS],                    # Black Pepper — India, SE Asia
    250: [AO, SAS, EAS],                     # Pittosporum — Australasia, Asia
    251: [WAS, NA, SAS, CA],                 # Psyllium — W.Asia, India
    252: [CE, SE, EE, WAS, NA],             # Sycamore — C+S Europe, W.Asia
    253: [SE, WAS, SAS, NA, TA],            # Leadwort — Pantropical/subtropical
    254: [WAS, CA, CE, SE],                  # Wheat — W.Asia/Fertile Crescent origin
    255: [SAS, SEA, EAS, SAN, TA],          # Sugarcane — SE Asia/India origin
    256: [NE, CE, EE, WAS, SIB],            # Bistort — N.Hemisphere cool temperate
    257: [CA, EAS, CE, EE],                  # Rhubarb — C.Asia, China
    258: [CE, NE, EE, WAS],                  # Cowslip — C+N Europe, W.Asia
    259: [SA],                               # Protea — S.Africa (Cape)
    260: [CE, SE, EE, WAS],                  # Pulsatilla — C+S Europe, W.Asia
    261: [CE, NE, EE, WAS],                  # Buckthorn — Europe, W.Asia
    262: [SE, NA, TA, SEA, SAN, CAM, AO],  # Mangrove — tropical/subtropical coasts
    263: [CE, NE, EE, WAS, NAE, SIB],       # Wild Strawberry — N.Hemisphere
    264: [CE, NE, EE, WAS],                  # Meadowsweet — C+N Europe, W.Asia
    266: [SE, WAS, NA],                      # Rue — Mediterranean
    267: [NE, CE, EE, WAS, SIB, NAE, NAW, ARC],  # Aspen — Circumboreal
    268: [SAS, SEA, EA],                     # Sandalwood — India, SE Asia, E.Africa
    269: [SAS, SEA, EA],                     # Soapnuts — India, SE Asia
    270: [EAS, SEA, SAS],                    # Houttuynia — E+SE Asia
    271: [CA, EAS, SAS, CE],                 # Bergenia — C.Asia, Himalayas, Siberia
    272: [CE, NE, SE, EE, WAS],             # Foxglove — W+C Europe (mainly)
    273: [CE, SE, EE, NA, WAS, NAE],        # Mullein — C+S Europe, N.Africa, W.Asia
    274: [NA, WAS, CA],                      # Resurrection Plant — N.Africa, W.Asia
    275: [SAN, CAM],                         # Quassia — Tropical Americas (Suriname)
    276: [CE, SE, EE, WAS, SAS, TA],        # Black Nightshade — Old World widespread
    277: [CE, SE, EE, WAS],                  # Bladdernut — S+C Europe, W.Asia
    278: [SAN, CAM],                         # Cacao — Tropical Americas
    279: [SEA, SAS],                         # Benzoin — SE Asia (Sumatra, Java)
    280: [EAS, SEA, SAS],                    # Symplocos — E+SE Asia
    281: [SE, NA, WAS, CA],                  # Tamarisk — Med, N.Africa, C.Asia
    282: [CE, NE, SE, EE, WAS],             # English Yew — Europe, W.Asia
    283: [EAS, SAS, SEA],                    # Tea Plant — China, S+SE Asia
    284: [CE, EE, NE, WAS, SIB],            # Linden — C+E Europe, W.Asia
    285: [SAN, CAM, SE, NA],                 # Nasturtium — S.America origin
    286: [CAM, NAW],                         # Damiana — Mexico, SW N.America
    287: [NE, CE, EE, NAE, NAW, ARC],       # Cattail — Circumboreal/cosmopolitan
    288: [NAE],                              # Slippery Elm — E.North America
    289: [WAS, NA, SE, CA, SAS],            # Cumin — Med, W.Asia
    290: [CE, NE, EE, WAS, SIB, NAE, NAW], # Stinging Nettle — Circumboreal/cosmopolitan
    291: [SAS, CA, WAS],                     # Spikenard — Himalayas, India
    292: [SE, NA, SAN],                      # Lemon Verbena — S.America origin, Med grown
    293: [CE, NE, EE, WAS, SE],             # Sweet Violet — Europe, W.Asia
    295: [SA],                               # Cape Aloe — S.Africa
    296: [EAS],                              # Mioga Ginger — Japan, E.Asia
    297: [SAS],                              # Malabar Nut — India
    298: [EAS, CE, SE],                      # Kiwifruit — China (Yangtze) origin
    299: [NE, CE, SE, EE, WAS],             # Black Elderberry — Europe, W.Asia
    300: [NAE],                              # Sweet Gum — E.North America
    301: [SAS, SEA, TA],                     # Prickly Chaff Flower — S.Asia, tropical
    302: [SAN, CAM, SEA, SAS, TA],          # Cashew — Brazil origin, now pantropical
    303: [SAS, SEA, EAS, TA],               # Mango — S.Asia origin
    304: [SE, NA, WAS, SAS, EAS, NAE, NAW], # Sumac — Med/W.Asia, N.America
    306: [CAM, SAN, SEA],                    # Sapodilla — C.America, pantropical
    307: [SE, NA, WAS],                      # Khella — N.Africa, Med, W.Asia
    308: [WAS, SAS, NA, SE],                 # Ajowan — W.Asia, India, N.Africa
    309: [CE, SE, EE, WAS, NA],             # Lovage — S+C Europe, W.Asia
    312: [NAE],                              # American Spikenard — E.North America
    314: [EAS, SIB],                         # Siberian Ginseng — E.Russia, NE China, Korea
    315: [EAS],                              # Japanese Aralia — Japan, E.Asia
    318: [SAS, SEA],                         # Areca Nut — India, SE Asia
    320: [SEA, SAS, AO],                     # Coconut — SE Asia/Pacific
    322: [CAM, NAW],                         # Century Plant — Mexico, SW N.America
    324: [CE, SE, EE, WAS],                  # Butcher's Broom — S+C Europe, W.Asia
    327: [CE, EE, WAS, CA, NA],             # Wormwood — C+E Europe, W.Asia, C.Asia
    331: [EAS, SAS, SEA],                    # Sweet Wormwood — China, S+SE Asia
    341: [SE, NA, CE, EE, WAS],             # Artichoke — Med, W.Asia (wild origin Canary Is.)
    344: [NAE],                              # Narrow-leaved Coneflower — E.N.America
    347: [NAE, NAW],                         # Jerusalem Artichoke — N.America
    349: [SE, CE, WAS, NA],                  # Immortelle — Med, S.Europe
    351: [CE, EE, WAS, NA, SAS, CA],        # Elecampane — C+E Europe, W.Asia, India
    357: [CE, NE, SE, EE, NAE, NAW, AO],   # Tansy Ragwort — Europe, naturalized N.America
    363: [CE, NE, EE, WAS, NAE, NAW],       # Coltsfoot — C+N Europe, W.Asia
    366: [CE, NE, EE, SAS],                  # Touch-me-not — C+N Europe, Himalayas
    369: [CE, SE, EE, WAS, NA, CA, EAS],   # Barberry — Europe, W.Asia, E.Asia
    372: [NE, CE, EE, WAS, NA, SIB],        # Common Alder — N+C Europe, Russia
    375: [CE, SE, NE, EE, WAS, NA, SIB],   # Hazelnut — Europe, W.Asia
    387: [SAN, CAM],                         # Annatto — Tropical Americas
    400: [CE, NE, EE, WAS, SIB],            # Hound's Tongue — C+N Europe, W.Asia
    405: [CE, SE, EE, WAS, NA],             # Viper's Bugloss — C+S Europe, W.Asia
    410: [CE, NE, EE, WAS, SIB],            # Gromwell — C+N Europe, W.Asia
    421: [CE, NE, EE, WAS, SIB],            # Lungwort — C+N Europe, W.Asia
    438: [CE, EE, WAS, SE, NA, SAS],        # Horseradish — E.Europe, W.Asia
    451: [CE, SE, EE, WAS, NA],             # Woad — S+C Europe, W.Asia
    461: [CE, SE, EE, WAS, CA, SAS],        # Radish — W.Asia/S.Asia origin, widespread
    470: [CAM],                              # Pinguin — Central America / Caribbean
    482: [SEA],                              # Elemi — Philippines, SE Asia
    494: [CAM, NAW],                         # Night-blooming Cereus — C.America, Mexico
    502: [CAM, NAW, NA, WAS, SE],           # Prickly Pear — Americas, now Med/N.Africa
    512: [NAE],                              # Sweetshrub — E.North America
    521: [NAE],                              # Indian Tobacco — E.North America
    530: [EAS],                              # Balloon Flower — China, Korea, Japan
    551: [EAS, SAS],                         # Japanese Honeysuckle — China, Japan, Korea
    571: [NAE, NAW],                         # American Elderberry — N.America
    574: [CE, NE, EE, WAS, NAE, NAW],       # Guelder Rose — Europe, W.Asia, N.America
    577: [NAE],                              # Blackhaw — E.North America
    582: [SE, CE, NA, WAS],                  # Carnation — Med, S.Europe
    585: [CE, SE, EE, WAS, NA],             # Soapwort — C+S Europe, W.Asia
    588: [NAE],                              # Wahoo — E.North America
    592: [CE, SE, NE, EE, WAS, NA],         # English Holly — W+C Europe, W.Asia
    595: [NAE],                              # American Holly — E.North America
    598: [SSA, SAN],                         # Yerba Mate — S.Brazil, Paraguay, Argentina
    601: [SSA, SAN],                         # Mayten — Chile, Argentina, Patagonia
    603: [CAM, SAN, TA, SEA],               # Mexican Tea — Tropical Americas, pantropical
    605: [EAS, SAS, SEA],                    # Sarcandra — E+SE Asia
    607: [SE, NA, WAS],                      # Labdanum — Mediterranean
    609: [NAE, NAW],                         # Pepperbush — N.America
    611: [SEA, AO, SAS],                     # Alexandrian Laurel — SE Asia, Oceania
    613: [SEA],                              # Mangosteen — SE Asia (Thailand, Malaysia)
    615: [CAM, SAN, SEA],                    # Chicle Tree — C.America, pantropical
    617: [TA, EA, SA, SAS],                  # Flame Lily — Sub-Saharan Africa, India
    619: [CE, SE, EE, WAS],                  # White Hellebore — C+S Europe, W.Asia
    621: [SAS, SEA, EAS, TA, SAN],          # Spreading Dayflower — pantropical
    623: [CE, SE, EE, WAS, NAE, NAW, CA],   # Field Bindweed — Eurasia, cosmopolitan
    625: [CAM, SAN],                         # Jalap — Mexico, C.America
    627: [SAS, SEA],                         # Turpeth Root — India, SE Asia
    629: [NAE, CE, EE, WAS, NE, SIB],       # Red Dogwood — N.Hemisphere
    633: [SE, WAS, NA],                      # Tree Aeon — Med, W.Asia
    635: [CE, SE, EE, WAS, NE],             # Biting Stonecrop — C+S Europe
    637: [NE, ARC, SIB, CA, EE],            # Roseroot — Arctic, Subarctic, montane
    639: [CE, NE, EE, WAS, SIB],            # Orpine — C+N Europe, W.Asia
    641: [SE, CE, WAS],                      # Cobweb Houseleek — Alps/S.Europe
    643: [EAS, SEA, SAS],                    # Wax Gourd — E+SE Asia, S.Asia
    645: [WA, TA, SAN, CAM, SAS],           # Watermelon — W.Africa (Kalahari) origin
    647: [WAS, NA, CA, SAS],                 # Melon — C.Asia/Iran origin
    649: [SAS, EAS, SEA, WAS],              # Cucumber — S.Asia origin
    651: [SAN, CAM],                         # Pumpkin — C/S.Americas
    653: [SAS, SEA, EAS, TA],               # Luffa — S.Asia, SE Asia, Trop.Africa
    655: [CAM, SAN],                         # Chayote — C.America (Mexico)
    657: [EAS],                              # Hinoki Cypress — Japan, E.Asia
    659: [SE, WAS, NA],                      # Italian Cypress — Mediterranean
    661: [CE, NE, SE, EE, NAE, NAW, WAS],  # Common Juniper — N.Hemisphere wide
    663: [NA, SE, WAS],                      # Sandarac Tree — N.Africa, Mediterranean
    665: [NAE, NAW],                         # Eastern Arborvitae — N.America
    667: [EAS],                              # Oriental Arborvitae — China, E.Asia
    669: [NE, CE, EE, WAS, SAS, SEA, AO, NAE],  # Common Dodder — cosmopolitan
    671: [AO, SEA, SAS],                     # Black Tree Fern — Australasia, SE Asia
    673: [CAM, SEA, EAS, TA],               # Cardboard Palm — tropical
    675: [NA, SE, WAS, EAS, TA, SEA, SAS], # Tiger Nut — N.Africa/Med, Old World tropical
    677: [NA, WAS, SEA, SAS, TA, EAS],     # Galingale — Old World tropical
    679: [NE, CE, EE, WAS, SIB, ARC],       # Black Bog Rush — N.Hemisphere boreal
    681: [CE, SE, EE, WAS, NE],             # Spurge Laurel — C+S Europe, W.Asia
    683: [EAS, SE, CE, WAS],                 # Winter Daphne — China, Japan, S.Europe
    685: [CA, EE, CE, EAS, SIB],            # False Hemp — C.Asia, Russia, E.Europe
    687: [SEA, AO],                          # Ube — Philippines, SE Asia, Pacific
    689: [EAS, SAS, SEA],                    # Chinese Yam — China, S+SE Asia
    691: [SEA, EAS, SAS, TA],               # Air Potato — SE Asia, trop.worldwide
    693: [CAM, SAN],                         # Mexican Yam — C+S Americas
    697: [NE, CE, NAE, NAW, ARC, SIB, AO], # Sundew — Circumboreal/cosmopolitan bogs
    699: [EA, SE, WAS, SAS, EAS, SEA, TA], # Ebony — tropical Old World
    701: [SAS, SEA],                         # Malabar Ebony — India, SE Asia
    703: [NAE],                              # American Persimmon — E.North America
    705: [WAS, CA, EE, CE],                  # Russian Olive — C.Asia, W.Asia
    707: [WAS, SAS, CA, EAS],               # Autumn Olive — E.Asia, W.Asia, Himalayas
    709: [CA, SIB, NE, EE, WAS, EAS],       # Sea Buckthorn — C.Asia, Siberia, Europe
    711: [NE, ARC, SIB, NAE, NAW, AO, CE], # Crowberry — Circumboreal/sub-Antarctic
    713: [SAS, CA],                          # Himalayan Ephedra — Himalayas, C.Asia
    715: [EAS, CA],                          # Major Ephedra — China, C.Asia
    717: [NAW, CAM],                         # Nevada Ephedra — SW N.America, Mexico
    719: [SE, NA, WAS, CA],                  # Common Ephedra — Med, W.Asia, C.Asia
    721: [CE, EE, WAS, NA, SIB],            # Lesser Burdock — Europe, W.Asia
    723: [WAS, CA, CE, EE, EAS, SIB],       # Tarragon — C+E Europe, C.Asia, W.Asia
    725: [NAW, CAM],                         # White Sage — California, Mexico
    727: [NE, CE, EE, WAS, ARC, SIB, NAE, NAW],  # Bearberry — Circumboreal
    729: [CE, SE, EE, WAS, EAS, NAE],       # Aster — N.Hemisphere (wide genus)
    731: [NAW, CAM],                         # Coyote Brush — Pacific N.America, Mexico
    733: [SAN, CAM, TA, SEA],               # Spanish Needles — pantropical
    735: [SAS, SEA, TA, EAS],               # Blumea — S+SE Asia, trop.Africa
    737: [EAS, CA, WAS, CE],                 # Chinese Thorowax — E.Asia, C.Asia
    739: [NAE],                              # Pale Indian Plantain — E.North America
    741: [CE, SE, EE, WAS, NA],             # Welted Thistle — C+S Europe, W.Asia
    743: [CE, SE, EE, WAS, NA],             # Bristly Thistle — C+S Europe, W.Asia
    745: [CE, SE, EE, WAS, NA, ARC],        # Carline Thistle — C+S Europe, W.Asia, Arctic
    747: [CE, SE, EE, WAS],                  # Mountain Bluet — C+S Europe, W.Asia
    749: [CE, SE, EE, WAS, NA],             # Greater Knapweed — C+S Europe, W.Asia
    753: [NE, CE, EE, NAE, NAW, ARC],       # Canada Thistle — N.Hemisphere
    755: [CE, NE, EE, NAE, NAW, WAS],       # Bull Thistle — Europe, N.America
    757: [SE, NA, WAS, CE],                  # Blessed Thistle — Med, W.Asia
    759: [NAE, NAW],                         # Plains Coreopsis — N.America
    761: [SE, WAS, NA, CE],                  # Basil Thyme — Med, W.Asia
    763: [CE, SE, EE, WAS, NE],             # Bugle — C+S Europe, W.Asia
    765: [CE, SE, EE, WAS, NA],             # Black Horehound — C+S Europe, W.Asia
    767: [CE, SE, EE, WAS, NA],             # Betony — C+S Europe, W.Asia
    769: [SE, CE, WAS, NA],                  # Calamint — Med, S.Europe, W.Asia
    771: [CE, SE, EE, WAS, NA],             # Wild Basil — C+S Europe, W.Asia
    773: [EE, CE, WAS, EAS],                 # Moldavian Balm — E.Europe, C.Asia
    775: [CE, NE, EE, WAS, SE, NA],         # Common Hemp Nettle — Europe, W.Asia
    777: [CE, NE, EE, WAS, SE],             # Ground Ivy — C+N Europe, W.Asia
    781: [CE, NE, EE, WAS, SE, SIB],        # White Dead Nettle — C+N Europe, W.Asia
    783: [SE, WAS, NA],                      # Spanish Lavender — W.Mediterranean
    787: [CE, NE, EE, WAS, SE, SIB, NAE],  # Water Mint — Europe, W.Asia
    789: [CE, NE, EE, WAS, SE, NA, EAS, SIB], # Corn Mint — Eurasia
    791: [CE, NE, SE, EE, WAS, NAE, NAW],  # Horse Mint — N.Hemisphere
    793: [CE, SE, EE, WAS, NA, NE],         # Pennyroyal — Med, Europe, W.Asia
    795: [CE, NE, EE, WAS, SE, NAE, NAW, SIB], # Spearmint — Europe, N.Hemisphere wide
    797: [SE, WAS, NA],                      # Cretan Thyme — Crete/E.Med
    799: [CE, SE, EE, WAS, NA],             # Fool's Parsley — C+S Europe, W.Asia
    801: [SE, NA, WAS],                      # Ammi — Mediterranean
    803: [NAE, NAW],                         # American Angelica — N.America
    805: [CE, SE, EE, WAS, NE],             # Chervil — C+S Europe, W.Asia
    809: [CE, SE, EE, WAS],                  # Master Of The Wood — C+S Europe, W.Asia
    811: [CE, NE, EE, WAS, SE, CA],         # Caraway — C+N Europe, W.Asia, C.Asia
    813: [CE, SE, EE, WAS, NA],             # Spreading Hedge Parsley — C+S Europe, W.Asia
    815: [SE, CE, WAS, NA],                  # Turnip-rooted Chervil — Med, W.Asia
    817: [CE, SE, EE, WAS],                  # Rough Chervil — C+S Europe, W.Asia
    819: [NAW, NAE],                         # Douglas' Waterhemlook — N.America
    821: [NE, CE, EE, NAE, NAW, ARC, SIB], # Cowbane — Circumboreal
    823: [EAS, SE, WAS],                     # Cnidium — E.Asia, C+S Europe, W.Asia
    825: [WA, EA, TA],                       # Grains Of Paradise — W+E Africa
    829: [SEA, SAS],                         # Cluster Cardamom — SE Asia, India
    831: [SAS, EAS, SEA],                    # Black Cardamom — Himalayas, China, SE Asia
    833: [SEA],                              # Fingerroot — SE Asia (Thailand, Indonesia)
    835: [EAS],                              # Chinese Fringe Tree — China, E.Asia
    837: [SAS, SEA],                         # Wild Turmeric — India, SE Asia
    839: [SAS, SEA],                         # Zedoary — India, SE Asia
    841: [SEA, AO],                          # Red Ginger — SE Asia, Pacific
    843: [SEA, EAS, SAS],                    # Lesser Galangal — SE Asia, China
    845: [SAS],                              # White Ginger Lily — India, Himalayas
    847: [SAS, SEA],                         # Spiked Ginger Lily — India, SE Asia
    849: [NAE],                              # Zanthorhiza — E.North America
    851: [SEA],                              # Kacip Fatimah — Malaysia, SE Asia
    855: [AO, SSA, SE, NAE, NAW],           # Biddy-Biddy — Australasia, cosmopolitan
    857: [CE, NE, EE, WAS, SE, NA],         # Agrimony — C+N Europe, W.Asia
    859: [CE, SE, EE, WAS],                  # Fragrant Agrimony — C+S Europe, W.Asia
    861: [CE, NE, EE, WAS, SE, ARC],        # Lady's Mantle — C+N Europe, W.Asia
    863: [CE, NE, EE, WAS, SE],             # Common Lady's Mantle — C+N Europe, W.Asia
    865: [CE, SE, EE, WAS],                  # Bastard Agrimony — C+S Europe, W.Asia
    867: [CE, NE, EE, WAS, SE, NAE, NAW],  # Garden Strawberry — N.Hemisphere
    869: [SE, WAS, NA, SAS],                 # Musk Strawberry — Med, W.Asia, India
    871: [CE, NE, EE, WAS, SE, NAE],        # Herb Bennet — C+N Europe, W.Asia
    873: [CE, NE, EE, WAS, SE, NAE],        # Water Avens — C+N Europe, W.Asia
    875: [NAE],                              # Indian Physic — E.North America
    877: [CE, NE, EE, WAS, ARC, SIB],       # White Cinquefoil — C+N Europe, Siberia
    881: [CE, NE, EE, WAS, SE, NA],         # Tormentil — C+N Europe, W.Asia
    883: [CE, NE, EE, WAS, SE, NAE, ARC],  # Creeping Cinquefoil — N.Hemisphere
    885: [NE, ARC, SIB, NAE, NAW, AO],     # Cloudberry — Circumboreal/sub-Antarctic
    889: [CE, NE, EE, WAS, SE, NAE, NAW, SIB], # Red Raspberry — N.Hemisphere wide
    891: [CE, NE, EE, WAS, SE, NA],         # Salad Burnet — C+N Europe, W.Asia
    893: [CE, NE, EE, WAS, SE, NA],         # Great Burnet — C+N Europe, W.Asia
    894: [SAS, SEA, EAS],                    # Catechu — S+SE Asia
    895: [NA, WA, EA, TA, WAS],             # Gum Acacia — Africa, W.Asia
    896: [NAE, NAW],                         # False Indigo — N.America
    897: [NAE, NAW],                         # Wild Indigo — N.America (SE USA)
    898: [SAS, TA, SEA],                     # Pigeon Pea — S.Asia, pantropical
    899: [SA, EA, TA],                       # Golden Shower — S.Africa, E.Africa, pantropical
    900: [NA, WAS, SE, SAS, TA],            # Senna — N.Africa, W.Asia, pantropical
    901: [SE, NA, WAS, CA],                  # Carob — Mediterranean, W.Asia
    902: [WAS, SE, NA, SAS, CA],            # Chickpea — W.Asia/Med origin
    903: [SE, CE, EE, WAS, CA],             # Bladder Senna — S+C Europe, W.Asia
    904: [SAS, SEA, TA],                     # Sunn Hemp — S.Asia, pantropical
    905: [SAS, WAS, CA, NA],                 # Guar — India, NW India/Pakistan origin
    906: [SAS, SE, NA, CA],                  # Sissoo — India, SE Europe, N.Africa
    907: [SAS, SEA, TA],                     # Desmodium — S.Asia, pantropical
    908: [SAN],                              # Tonka Bean — Venezuela, N.S.America
    909: [TA, SAS],                          # Coral Tree — E.Africa, India, tropical
    910: [TA, SE, SAS],                      # Variegated Coral Tree — Trop.Africa, India
    912: [CE, SE, EE, WAS, NA],             # Goat's Rue — C+S Europe, W.Asia
    913: [CE, SE, EE, WAS, NA],             # Dyer's Greenweed — C+S Europe, W.Asia
    914: [CE, NE, EE, WAS, SE, SAS, CA],   # Monkshood — C+N Europe, Asia montane
    917: [CE, NE, EE, NAE],                 # Red Baneberry — C+N Europe, N.America
    918: [EAS, SIB, CA],                     # Amur Adonis — E.Russia, Siberia, C.Asia
    919: [NAE],                              # Rue Anemone — E.North America
    920: [NAE, NAW],                         # Canada Anemone — N.America
    921: [CE, NE, EE, WAS, SE],             # Wood Anemone — C+N Europe, W.Asia
    923: [NAE],                              # Eastern Columbine — E.North America
    924: [CE, SE, EE, WAS],                  # European Columbine — C+S Europe, W.Asia
    925: [CE, NE, EE, WAS, SE, NAE, NAW, SIB, ARC],  # Marsh Marigold — Circumboreal
    926: [NAE],                              # Black Cohosh — E.North America
    927: [CE, EE, SE, WAS, NA, CA],         # Upright Clematis — C+S Europe, W.Asia
    928: [CE, SE, EE, WAS, NA],             # Traveler's Joy — S+C Europe, W.Asia
    929: [NAE, NAW],                         # Larkspur — N.America (garden species)
    930: [NAE, NAW, CE, SE, EE],            # Rocket Larkspur — Europe, N.America
    931: [CE, SE, EE, WAS],                  # Winter Aconite — C+S Europe, W.Asia
    932: [CAM, SAN, SE, NA],                 # Key Lime — SE Asia origin, now C.America/Med
    933: [EAS, SAS, SE, NA],                 # Citron — E.Asia/India origin, now Med
    934: [SE, NA, CAM, SAN, SEA, SAS],      # Grapefruit — SE Asia hybrid, Med
    935: [EAS, SAS, SE, NA, CAM, SAN],      # Sweet Orange — China/India origin
    936: [EAS, SAS, SE, NA, CAM, SAN],      # Tangerine — China/SE Asia origin
    937: [SE, WAS, CE, EE, NA, CA],         # Gas Plant — Med, W.Asia, C.Asia
    938: [EAS, SAS, SEA],                    # Evodia — E+SE Asia
    939: [EAS],                              # Marumi Kumquat — China, Japan
    940: [NAE, NAW],                         # Hop Tree — N.America
    941: [EAS],                              # Japanese Skimmia — Japan, E.Asia
    942: [SEA, SAS],                         # Pepper Elemi — SE Asia, India
    943: [SAS, SEA, EAS],                    # Timut — Nepal Himalayas, SE Asia
    944: [NAE],                              # Northern Prickly Ash — E.N.America
    945: [EAS],                              # Sichuan Pepper — China, E.Asia
    946: [NAE],                              # Southern Prickly Ash — SE N.America
    947: [EAS],                              # Japanese Pepper — Japan, E.Asia
    949: [SE, EE, CE, WAS, NA],             # Deadly Nightshade — S+C Europe, W.Asia
    950: [CAM, SAN],                         # Scotch Bonnet — Caribbean, S.America
    951: [SEA, SAS],                         # Bird's Eye Chili — SE Asia, India
    952: [SAS, SEA, EAS],                    # Day Jasmine — S+SE Asia
    953: [SAS, SEA, EAS],                    # Night Jasmine — India, SE Asia
    954: [WAS, SAS, CA, NA, SE],            # Datura — W.Asia, India (disputed; now worldwide)
    956: [NAE, NAW, CAM],                    # Jimsonweed — N.America, C.America (now worldwide)
    957: [AO],                               # Pituri — Australia (Aboriginal)
    958: [CE, SE, EE, WAS, NA, CA],         # Henbane — C+S Europe, W.Asia, N.Africa
    959: [SAN, CAM],                         # Tomato — S+C Americas (Andes origin)
    961: [SAN, CAM],                         # Apple Of Peru — S.America, C.America
    962: [SAN, CAM],                         # Winged Tobacco — S.America
    963: [NAW, CAM],                         # Coyote Tobacco — W.N.America, Mexico
    964: [SAN, CAM],                         # Tobacco — Tropical Americas
    965: [SAN, CAM],                         # Ground Cherry — C+S Americas
    966: [CAM, SAN],                         # Pequanillo — C.America, Caribbean
    967: [CE, EE, WAS, CA, SIB],            # Scopolia — C+E Europe, W.Asia
    968: [NAE, NAW],                         # Carolina Horsenettle — N.America
    969: [CE, NE, EE, WAS, SE],             # Bittersweet — C+N Europe, W.Asia
    970: [SE, NA, WAS, SAS, TA],            # Prickly Nightshade — Med, trop.widespread
    971: [SAS, SEA],                         # Jasmine Nightshade — S.Asia, SE Asia
    972: [SAS, SEA, EAS, WAS],              # Eggplant — S+SE Asia, W.Asia
    973: [SE, EAS, TA, SAN, CAM],           # Jerusalem Cherry — Med, E.Asia, trop.
    974: [SAN, CA, WAS, SE, NA],            # Potato — Andes (Peru/Bolivia) origin
    975: [SAS, WAS, NA],                     # Ashwagandha — India, W.Asia, N.Africa
    978: [NAE],                              # Bloodroot — E.North America
    979: [NAE],                              # Wood Poppy — E.North America
    980: [CE, SE, EE, WAS, NE],             # Solid-rooted Corydalis — C+S Europe, W.Asia
    981: [NAE],                              # Squirrel Corn — E.North America
    982: [NAE],                              # Dutchman's Breeches — E.North America
    983: [NAE],                              # Wild Bleeding Heart — E.North America
    984: [EAS, SAS, SE],                     # Bleeding Heart — E.Asia, Himalayas
    985: [CE, SE, EE, WAS, NA, NE],         # Common Fumitory — Europe, W.Asia, N.Africa
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true',
                        help='Print what would be written without touching the DB')
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA encoding = "UTF-8"')
    conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
    cur = conn.cursor()

    # ------------------------------------------------------------------
    # Step 1: Insert zone rows into authors table
    # ------------------------------------------------------------------
    print('Step 1: Inserting zone rows into authors table...')
    existing_ids = {row[0] for row in cur.execute('SELECT id FROM authors').fetchall()}
    inserted = 0
    for zone_id, zone_name in ZONES:
        if zone_id not in existing_ids:
            cur.execute('INSERT INTO authors (id, name) VALUES (?, ?)', (zone_id, zone_name))
            inserted += 1
    if not args.dry_run:
        conn.commit()
    print(f'  {inserted} zone rows inserted ({len(ZONES) - inserted} already existed).')

    # ------------------------------------------------------------------
    # Step 2: Apply zone assignments to plants
    # ------------------------------------------------------------------
    cur.execute('SELECT id, paintingname FROM museum_item ORDER BY id')
    plants = cur.fetchall()
    print(f'\nStep 2: Assigning zones to {len(plants)} plants...\n')

    updated = 0
    skipped = 0
    for plant_id, name in plants:
        zones = PLANT_ZONES.get(plant_id)
        if not zones:
            print(f'  [NO DATA] id={plant_id} ({name}) — no zone assignment, skipping')
            skipped += 1
            continue
        zone_str = ','.join(zones)
        print(f'  id={plant_id:4d} ({name:<40s}) → {zone_str}')
        if not args.dry_run:
            cur.execute('UPDATE museum_item SET author=? WHERE id=?', (zone_str, plant_id))
            updated += 1

    if not args.dry_run:
        conn.commit()
        print(f'\n=== Done: {updated} plants updated, {skipped} skipped (no data) ===')
    else:
        print(f'\n=== DRY RUN: {len(plants) - skipped} would be updated, {skipped} skipped ===')

    # Verification
    if not args.dry_run:
        cur.execute("SELECT COUNT(*) FROM museum_item WHERE author LIKE 'zone_%'")
        zone_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM authors WHERE id LIKE 'zone_%'")
        zone_rows = cur.fetchone()[0]
        print(f'Verification: {zone_rows} zone rows in authors table, {zone_count} plants with zone assignments.')

    conn.close()


if __name__ == '__main__':
    main()
