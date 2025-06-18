import googlemaps
import pandas as pd
import time
import json
from typing import List, Dict, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessScraper:
    def __init__(self, api_key: str):
        """Initialize the scraper with Google Maps API key."""
        self.gmaps = googlemaps.Client(key=api_key)
        self.all_businesses = []
        self.selected_business_type = None
        
    def get_business_types(self) -> Dict[str, Dict]:
        """
        Returns a comprehensive dictionary of business types with their search parameters.
        """
        return {
            # PERSONAL CARE & BEAUTY
            "1": {"name": "Barbershops", "keywords": ["barbershop", "barber shop", "mens haircut"], "type": "hair_care"},
            "2": {"name": "Hair Salons", "keywords": ["hair salon", "beauty salon", "hairdresser"], "type": "hair_care"},
            "3": {"name": "Nail Salons", "keywords": ["nail salon", "manicure", "pedicure"], "type": "beauty_salon"},
            "4": {"name": "Spas & Wellness", "keywords": ["spa", "massage", "wellness center"], "type": "spa"},
            "5": {"name": "Tattoo Parlors", "keywords": ["tattoo", "tattoo parlor", "ink"], "type": "establishment"},
            "6": {"name": "Piercing Studios", "keywords": ["piercing", "body piercing", "ear piercing"], "type": "establishment"},
            "7": {"name": "Tanning Salons", "keywords": ["tanning salon", "tanning", "suntan"], "type": "beauty_salon"},
            "8": {"name": "Eyebrow Threading", "keywords": ["eyebrow threading", "threading", "brow bar"], "type": "beauty_salon"},
            
            # FOOD & DINING
            "9": {"name": "Restaurants", "keywords": ["restaurant", "dining", "eatery"], "type": "restaurant"},
            "10": {"name": "Fast Food", "keywords": ["fast food", "quick service", "drive thru"], "type": "meal_takeaway"},
            "11": {"name": "Pizza Places", "keywords": ["pizza", "pizzeria", "pizza delivery"], "type": "meal_delivery"},
            "12": {"name": "Coffee Shops", "keywords": ["coffee shop", "cafe", "espresso"], "type": "cafe"},
            "13": {"name": "Bars & Pubs", "keywords": ["bar", "pub", "tavern"], "type": "bar"},
            "14": {"name": "Bakeries", "keywords": ["bakery", "bread", "pastry"], "type": "bakery"},
            "15": {"name": "Ice Cream Shops", "keywords": ["ice cream", "gelato", "frozen yogurt"], "type": "establishment"},
            "16": {"name": "Food Trucks", "keywords": ["food truck", "mobile food", "street food"], "type": "meal_takeaway"},
            "17": {"name": "Juice Bars", "keywords": ["juice bar", "smoothie", "fresh juice"], "type": "establishment"},
            "18": {"name": "Donut Shops", "keywords": ["donut", "doughnut", "donut shop"], "type": "bakery"},
            
            # AUTOMOTIVE
            "19": {"name": "Gas Stations", "keywords": ["gas station", "fuel", "petrol"], "type": "gas_station"},
            "20": {"name": "Auto Repair", "keywords": ["auto repair", "mechanic", "car service"], "type": "car_repair"},
            "21": {"name": "Car Washes", "keywords": ["car wash", "auto wash", "detailing"], "type": "car_wash"},
            "22": {"name": "Tire Shops", "keywords": ["tire shop", "tires", "tire service"], "type": "establishment"},
            "23": {"name": "Oil Change", "keywords": ["oil change", "lube", "quick lube"], "type": "car_repair"},
            "24": {"name": "Car Dealerships", "keywords": ["car dealer", "auto dealer", "car sales"], "type": "car_dealer"},
            "25": {"name": "Auto Parts", "keywords": ["auto parts", "car parts", "automotive"], "type": "establishment"},
            
            # RETAIL & SHOPPING
            "26": {"name": "Grocery Stores", "keywords": ["grocery", "supermarket", "food store"], "type": "grocery_or_supermarket"},
            "27": {"name": "Convenience Stores", "keywords": ["convenience store", "corner store", "mini mart"], "type": "convenience_store"},
            "28": {"name": "Pharmacies", "keywords": ["pharmacy", "drugstore", "medicine"], "type": "pharmacy"},
            "29": {"name": "Clothing Stores", "keywords": ["clothing store", "fashion", "apparel"], "type": "clothing_store"},
            "30": {"name": "Shoe Stores", "keywords": ["shoe store", "footwear", "shoes"], "type": "shoe_store"},
            "31": {"name": "Electronics Stores", "keywords": ["electronics", "computer store", "tech"], "type": "electronics_store"},
            "32": {"name": "Furniture Stores", "keywords": ["furniture", "home decor", "furnishing"], "type": "furniture_store"},
            "33": {"name": "Hardware Stores", "keywords": ["hardware store", "tools", "home improvement"], "type": "hardware_store"},
            "34": {"name": "Pet Stores", "keywords": ["pet store", "pet shop", "animal supplies"], "type": "pet_store"},
            "35": {"name": "Florists", "keywords": ["florist", "flower shop", "flowers"], "type": "florist"},
            "36": {"name": "Bookstores", "keywords": ["bookstore", "book shop", "books"], "type": "book_store"},
            "37": {"name": "Jewelry Stores", "keywords": ["jewelry", "jeweler", "watches"], "type": "jewelry_store"},
            "38": {"name": "Thrift Stores", "keywords": ["thrift store", "second hand", "consignment"], "type": "establishment"},
            
            # HEALTH & FITNESS
            "39": {"name": "Gyms & Fitness", "keywords": ["gym", "fitness", "workout"], "type": "gym"},
            "40": {"name": "Yoga Studios", "keywords": ["yoga", "yoga studio", "meditation"], "type": "establishment"},
            "41": {"name": "Martial Arts", "keywords": ["martial arts", "karate", "dojo"], "type": "establishment"},
            "42": {"name": "Dance Studios", "keywords": ["dance studio", "dance", "ballet"], "type": "establishment"},
            "43": {"name": "Doctors Offices", "keywords": ["doctor", "physician", "medical"], "type": "doctor"},
            "44": {"name": "Dentists", "keywords": ["dentist", "dental", "orthodontist"], "type": "dentist"},
            "45": {"name": "Veterinarians", "keywords": ["veterinarian", "vet", "animal hospital"], "type": "veterinary_care"},
            "46": {"name": "Chiropractors", "keywords": ["chiropractor", "chiropractic", "spine"], "type": "establishment"},
            "47": {"name": "Physical Therapy", "keywords": ["physical therapy", "physiotherapy", "rehab"], "type": "physiotherapist"},
            
            # PROFESSIONAL SERVICES
            "48": {"name": "Law Firms", "keywords": ["lawyer", "attorney", "law firm"], "type": "lawyer"},
            "49": {"name": "Real Estate", "keywords": ["real estate", "realtor", "property"], "type": "real_estate_agency"},
            "50": {"name": "Insurance Agencies", "keywords": ["insurance", "insurance agency", "coverage"], "type": "insurance_agency"},
            "51": {"name": "Accounting Firms", "keywords": ["accountant", "tax", "bookkeeping"], "type": "accounting"},
            "52": {"name": "Banks", "keywords": ["bank", "banking", "financial"], "type": "bank"},
            "53": {"name": "Credit Unions", "keywords": ["credit union", "financial", "banking"], "type": "establishment"},
            "54": {"name": "Travel Agencies", "keywords": ["travel agency", "travel", "vacation"], "type": "travel_agency"},
            
            # HOME SERVICES
            "55": {"name": "Plumbers", "keywords": ["plumber", "plumbing", "pipes"], "type": "plumber"},
            "56": {"name": "Electricians", "keywords": ["electrician", "electrical", "wiring"], "type": "electrician"},
            "57": {"name": "HVAC Services", "keywords": ["hvac", "heating", "air conditioning"], "type": "establishment"},
            "58": {"name": "Roofing Contractors", "keywords": ["roofing", "roof repair", "contractor"], "type": "roofing_contractor"},
            "59": {"name": "Landscaping", "keywords": ["landscaping", "lawn care", "gardening"], "type": "establishment"},
            "60": {"name": "Cleaning Services", "keywords": ["cleaning", "maid service", "janitorial"], "type": "establishment"},
            "61": {"name": "Pest Control", "keywords": ["pest control", "exterminator", "bug control"], "type": "establishment"},
            "62": {"name": "Locksmiths", "keywords": ["locksmith", "keys", "locks"], "type": "locksmith"},
            
            # ENTERTAINMENT & RECREATION
            "63": {"name": "Movie Theaters", "keywords": ["movie theater", "cinema", "movies"], "type": "movie_theater"},
            "64": {"name": "Bowling Alleys", "keywords": ["bowling", "bowling alley", "lanes"], "type": "bowling_alley"},
            "65": {"name": "Pool Halls", "keywords": ["pool hall", "billiards", "snooker"], "type": "establishment"},
            "66": {"name": "Casinos", "keywords": ["casino", "gambling", "gaming"], "type": "casino"},
            "67": {"name": "Amusement Parks", "keywords": ["amusement park", "theme park", "rides"], "type": "amusement_park"},
            "68": {"name": "Mini Golf", "keywords": ["mini golf", "miniature golf", "putt putt"], "type": "establishment"},
            "69": {"name": "Arcade", "keywords": ["arcade", "video games", "game room"], "type": "establishment"},
            "70": {"name": "Escape Rooms", "keywords": ["escape room", "puzzle room", "escape game"], "type": "establishment"},
            
            # EDUCATION & CHILDCARE
            "71": {"name": "Schools", "keywords": ["school", "education", "academy"], "type": "school"},
            "72": {"name": "Daycares", "keywords": ["daycare", "childcare", "preschool"], "type": "establishment"},
            "73": {"name": "Tutoring Centers", "keywords": ["tutoring", "learning center", "education"], "type": "establishment"},
            "74": {"name": "Music Schools", "keywords": ["music school", "music lessons", "instrument"], "type": "establishment"},
            "75": {"name": "Art Schools", "keywords": ["art school", "art classes", "art studio"], "type": "establishment"},
            "76": {"name": "Language Schools", "keywords": ["language school", "language classes", "ESL"], "type": "establishment"},
            
            # LODGING & TRAVEL
            "77": {"name": "Hotels", "keywords": ["hotel", "motel", "lodging"], "type": "lodging"},
            "78": {"name": "Bed & Breakfasts", "keywords": ["bed and breakfast", "B&B", "inn"], "type": "lodging"},
            "79": {"name": "Hostels", "keywords": ["hostel", "backpacker", "budget"], "type": "lodging"},
            "80": {"name": "RV Parks", "keywords": ["RV park", "campground", "camping"], "type": "rv_park"},
            
            # SPECIALTY SERVICES
            "81": {"name": "Laundromats", "keywords": ["laundromat", "laundry", "wash"], "type": "laundry"},
            "82": {"name": "Dry Cleaners", "keywords": ["dry cleaner", "dry cleaning", "alterations"], "type": "establishment"},
            "83": {"name": "Photo Studios", "keywords": ["photo studio", "photography", "portrait"], "type": "establishment"},
            "84": {"name": "Copy & Print", "keywords": ["copy center", "printing", "office services"], "type": "establishment"},
            "85": {"name": "Storage Units", "keywords": ["storage", "self storage", "mini storage"], "type": "storage"},
            "86": {"name": "Pawn Shops", "keywords": ["pawn shop", "pawn", "second hand"], "type": "establishment"},
            "87": {"name": "Funeral Homes", "keywords": ["funeral home", "mortuary", "cremation"], "type": "funeral_home"},
            
            # SPECIALTY FOOD
            "88": {"name": "Butcher Shops", "keywords": ["butcher", "meat market", "deli"], "type": "establishment"},
            "89": {"name": "Seafood Markets", "keywords": ["seafood", "fish market", "fresh fish"], "type": "establishment"},
            "90": {"name": "Wine Shops", "keywords": ["wine shop", "liquor store", "spirits"], "type": "liquor_store"},
            "91": {"name": "Specialty Food", "keywords": ["gourmet", "specialty food", "organic"], "type": "establishment"},
            "92": {"name": "Farmers Markets", "keywords": ["farmers market", "fresh produce", "local"], "type": "establishment"},
            
            # TECHNOLOGY & REPAIR
            "93": {"name": "Phone Repair", "keywords": ["phone repair", "cell phone", "mobile repair"], "type": "establishment"},
            "94": {"name": "Computer Repair", "keywords": ["computer repair", "IT services", "tech support"], "type": "establishment"},
            "95": {"name": "TV Repair", "keywords": ["TV repair", "television", "electronics repair"], "type": "establishment"},
            "96": {"name": "Appliance Repair", "keywords": ["appliance repair", "washer", "dryer"], "type": "establishment"},
            
            # TRANSPORTATION
            "97": {"name": "Taxi Services", "keywords": ["taxi", "cab", "ride"], "type": "establishment"},
            "98": {"name": "Parking Lots", "keywords": ["parking", "parking lot", "garage"], "type": "parking"},
            "99": {"name": "Public Transit", "keywords": ["bus station", "train", "transit"], "type": "transit_station"},
            "100": {"name": "Bike Shops", "keywords": ["bike shop", "bicycle", "cycling"], "type": "bicycle_store"},
        }
    
    def display_business_types(self):
        """Display all available business types for user selection."""
        business_types = self.get_business_types()
        
        print("\n" + "="*80)
        print("🏢 COMPREHENSIVE BUSINESS TYPE SCRAPER")
        print("="*80)
        print("Choose from the following business types to scrape:\n")
        
        # Group by categories for better display
        categories = {
            "PERSONAL CARE & BEAUTY": list(range(1, 9)),
            "FOOD & DINING": list(range(9, 19)),
            "AUTOMOTIVE": list(range(19, 26)),
            "RETAIL & SHOPPING": list(range(26, 39)),
            "HEALTH & FITNESS": list(range(39, 49)),
            "PROFESSIONAL SERVICES": list(range(48, 55)),
            "HOME SERVICES": list(range(55, 63)),
            "ENTERTAINMENT & RECREATION": list(range(63, 71)),
            "EDUCATION & CHILDCARE": list(range(71, 77)),
            "LODGING & TRAVEL": list(range(77, 81)),
            "SPECIALTY SERVICES": list(range(81, 88)),
            "SPECIALTY FOOD": list(range(88, 93)),
            "TECHNOLOGY & REPAIR": list(range(93, 97)),
            "TRANSPORTATION": list(range(97, 101)),
        }
        
        for category, numbers in categories.items():
            print(f"\n📂 {category}:")
            for num in numbers:
                if str(num) in business_types:
                    print(f"  {num:2d}. {business_types[str(num)]['name']}")
        
        print("\n" + "="*80)
        return business_types
    
    def get_user_selection(self) -> Optional[Dict]:
        """Get user's business type selection."""
        business_types = self.display_business_types()
        
        while True:
            try:
                choice = input("\nEnter the number of the business type you want to scrape (1-100): ").strip()
                
                if choice in business_types:
                    selected = business_types[choice]
                    print(f"\n✅ You selected: {selected['name']}")
                    print(f"   Keywords: {', '.join(selected['keywords'])}")
                    
                    confirm = input("\nProceed with this selection? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        self.selected_business_type = selected
                        return selected
                    else:
                        continue
                else:
                    print("❌ Invalid selection. Please enter a number between 1 and 100.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Scraping cancelled by user.")
                return None
            except Exception as e:
                print(f"❌ Error: {e}. Please try again.")
    
    def get_north_american_cities(self) -> List[tuple]:
        """
        Returns a comprehensive list of major cities in USA, Mexico, and Canada with their coordinates.
        """
        cities = [
            # === UNITED STATES ===
            # Major metropolitan areas
            (40.7128, -74.0060),  # New York, NY
            (34.0522, -118.2437), # Los Angeles, CA
            (41.8781, -87.6298),  # Chicago, IL
            (29.7604, -95.3698),  # Houston, TX
            (33.4484, -112.0740), # Phoenix, AZ
            (39.9526, -75.1652),  # Philadelphia, PA
            (29.4241, -98.4936),  # San Antonio, TX
            (32.7767, -96.7970),  # Dallas, TX
            (37.2431, -115.7918), # Las Vegas, NV
            (37.7749, -122.4194), # San Francisco, CA
            (47.6062, -122.3321), # Seattle, WA
            (39.7392, -104.9903), # Denver, CO
            (42.3601, -71.0589),  # Boston, MA
            (25.7617, -80.1918),  # Miami, FL
            (33.7490, -84.3880),  # Atlanta, GA
            (39.2904, -76.6122),  # Baltimore, MD
            (36.1627, -86.7816),  # Nashville, TN
            (35.2271, -80.8431),  # Charlotte, NC
            (44.9778, -93.2650),  # Minneapolis, MN
            (32.7157, -117.1611), # San Diego, CA
            
            # Additional major US cities
            (30.2672, -97.7431),  # Austin, TX
            (35.2131, -106.6500), # Albuquerque, NM
            (61.2181, -149.9003), # Anchorage, AK
            (33.5207, -86.8025),  # Birmingham, AL
            (42.3314, -83.0458),  # Detroit, MI
            (39.7391, -75.5406),  # Wilmington, DE
            (26.1224, -80.1373),  # Fort Lauderdale, FL
            (30.3322, -81.6557),  # Jacksonville, FL
            (27.9506, -82.4572),  # Tampa, FL
            (28.5383, -81.3792),  # Orlando, FL
            (32.0835, -81.0998),  # Savannah, GA
            (21.3099, -157.8581), # Honolulu, HI
            (43.6150, -116.2023), # Boise, ID
            (40.7589, -89.6501),  # Peoria, IL
            (39.7910, -86.1480),  # Indianapolis, IN
            (41.5868, -93.6250),  # Des Moines, IA
            (39.0458, -76.6413),  # Annapolis, MD
            (39.0458, -94.5786),  # Kansas City, MO
            (38.6270, -90.1994),  # St. Louis, MO
            (46.8772, -96.7898),  # Fargo, ND
            (41.2033, -95.9920),  # Omaha, NE
            (36.1699, -115.1398), # Las Vegas, NV
            (43.2081, -71.5376),  # Manchester, NH
            (40.2206, -74.7567),  # Princeton, NJ
            (40.0583, -74.4057),  # Trenton, NJ
            (35.6870, -105.9378), # Santa Fe, NM
            (43.1566, -77.6088),  # Rochester, NY
            (42.8864, -78.8784),  # Buffalo, NY
            (36.0726, -79.7920),  # Greensboro, NC
            (35.7796, -78.6382),  # Raleigh, NC
            (46.8083, -100.7837), # Bismarck, ND
            (39.9612, -82.9988),  # Columbus, OH
            (41.4993, -81.6944),  # Cleveland, OH
            (39.3210, -84.5120),  # Cincinnati, OH
            (35.4676, -97.5164),  # Oklahoma City, OK
            (36.1540, -95.9928),  # Tulsa, OK
            (45.5152, -122.6784), # Portland, OR
            (40.2732, -76.8839),  # Harrisburg, PA
            (40.4406, -79.9959),  # Pittsburgh, PA
            (41.8240, -71.4128),  # Providence, RI
            (32.7765, -80.0517),  # Charleston, SC
            (34.0000, -81.0348),  # Columbia, SC
            (44.9537, -93.0900),  # Saint Paul, MN
            (44.9778, -93.2650),  # Minneapolis, MN
            (36.1627, -86.7816),  # Nashville, TN
            (35.1495, -90.0490),  # Memphis, TN
            (36.1540, -86.7836),  # Nashville, TN
            (30.2672, -97.7431),  # Austin, TX
            (32.7767, -96.7970),  # Dallas, TX
            (31.7619, -106.4850), # El Paso, TX
            (29.4241, -98.4936),  # San Antonio, TX
            (29.7604, -95.3698),  # Houston, TX
            (32.7555, -97.3308),  # Fort Worth, TX
            (40.7608, -111.8910), # Salt Lake City, UT
            (44.2601, -72.5806),  # Montpelier, VT
            (37.4316, -78.6569),  # Richmond, VA
            (36.8508, -75.2859),  # Virginia Beach, VA
            (47.0379, -122.9015), # Olympia, WA
            (47.6587, -117.4260), # Spokane, WA
            (38.3498, -81.6326),  # Charleston, WV
            (43.0642, -87.9073),  # Milwaukee, WI
            (44.2619, -88.4054),  # Green Bay, WI
            (41.1400, -104.8197), # Cheyenne, WY
            
            # === CANADA ===
            (43.6532, -79.3832),  # Toronto, ON
            (45.5017, -73.5673),  # Montreal, QC
            (49.2827, -123.1207), # Vancouver, BC
            (51.0447, -114.0719), # Calgary, AB
            (53.5461, -113.4938), # Edmonton, AB
            (45.4215, -75.6972),  # Ottawa, ON
            (46.8139, -71.2080),  # Quebec City, QC
            (49.8951, -97.1384),  # Winnipeg, MB
            (43.2557, -79.8711),  # Hamilton, ON
            (42.9849, -81.2453),  # London, ON
            (43.4643, -80.5204),  # Kitchener, ON
            (46.4917, -84.3356),  # Sault Ste. Marie, ON
            (48.4284, -89.2477),  # Thunder Bay, ON
            (50.4452, -104.6189), # Regina, SK
            (52.1332, -106.6700), # Saskatoon, SK
            (44.6488, -63.5752),  # Halifax, NS
            (45.9636, -66.6431),  # Fredericton, NB
            (46.2382, -63.1311),  # Charlottetown, PE
            (47.5615, -52.7126),  # St. John's, NL
            (64.2008, -149.4937), # Fairbanks, AK (US but northern)
            (60.7212, -135.0568), # Whitehorse, YT
            (62.4540, -114.3718), # Yellowknife, NT
            (63.7467, -68.5170),  # Iqaluit, NU
            (49.6917, -112.8408), # Lethbridge, AB
            (54.7293, -113.2909), # Athabasca, AB
            (58.2348, -103.9968), # Fort McMurray, AB
            (50.6759, -120.3401), # Kamloops, BC
            (49.8880, -119.4960), # Kelowna, BC
            (54.0153, -122.5810), # Prince George, BC
            (48.4222, -123.3657), # Victoria, BC
            (53.9171, -122.7497), # Prince George, BC
            (58.8019, -111.4702), # Peace River, AB
            
            # === MEXICO ===
            (19.4326, -99.1332),  # Mexico City (Ciudad de México)
            (25.6866, -100.3161), # Monterrey, NL
            (20.6597, -103.3496), # Guadalajara, JAL
            (21.1619, -86.8515),  # Cancún, QR
            (32.5027, -117.0039), # Tijuana, BC
            (25.7903, -108.9850), # Mazatlán, SIN
            (20.9674, -89.5926),  # Mérida, YUC
            (22.2710, -97.8437),  # Tampico, TAM
            (19.0414, -98.2063),  # Puebla, PUE
            (21.8853, -102.2916), # Aguascalientes, AGS
            (20.5888, -100.3899), # Querétaro, QRO
            (19.7026, -101.1774), # Morelia, MICH
            (17.0732, -96.7266),  # Oaxaca, OAX
            (16.7569, -93.1292),  # Tuxtla Gutiérrez, CHIS
            (27.4858, -109.9309), # Ciudad Obregón, SON
            (28.6353, -106.0889), # Chihuahua, CHIH
            (31.3340, -106.4424), # Ciudad Juárez, CHIH
            (25.5428, -103.4068), # Torreón, COAH
            (22.1565, -100.9855), # San Luis Potosí, SLP
            (18.5204, -88.2956),  # Chetumal, QR
            (27.9654, -110.1090), # Hermosillo, SON
            (24.0277, -104.6532), # Durango, DGO
            (19.5398, -96.9106),  # Xalapa, VER
            (18.8464, -97.1131),  # Cuernavaca, MOR
            (19.2433, -103.7222), # Colima, COL
            (17.9895, -92.9475),  # Villahermosa, TAB
            (18.1465, -94.4558),  # Coatzacoalcos, VER
            (20.5230, -97.4589),  # Poza Rica, VER
            (22.7709, -102.5832), # Zacatecas, ZAC
            (16.8531, -99.8237),  # Acapulco, GRO
            (24.8092, -107.3940), # Culiacán, SIN
            (20.5217, -103.3111), # Tlaquepaque, JAL
            (19.0176, -98.2428),  # Cholula, PUE
            (25.5677, -103.5034), # Gómez Palacio, DGO
            (22.2738, -97.8677),  # Ciudad Madero, TAM
            (25.4232, -100.9962), # García, NL
            (19.3629, -99.2837),  # Naucalpan, MEX
            (19.4978, -99.1269),  # Tlalnepantla, MEX
            (19.2808, -99.1197),  # Coyoacán, CDMX
            (32.6419, -115.4718), # Mexicali, BC
            (22.8905, -109.9167), # La Paz, BCS
            (23.2494, -106.4114), # Mazatlán, SIN
            (18.9261, -99.2319),  # Taxco, GRO
            (19.8301, -90.5349),  # Campeche, CAM
            (27.4894, -99.5075),  # Nuevo Laredo, TAM
            (26.0756, -98.8019),  # Reynosa, TAM
            (25.9017, -97.4974),  # Matamoros, TAM
            (28.7004, -100.5217), # Piedras Negras, COAH
            (29.3667, -100.8833), # Ciudad Acuña, COAH
            (31.7367, -106.4890), # El Paso-Juárez border area
            (26.5263, -100.2175), # Saltillo, COAH
            (21.0190, -101.2574), # León, GTO
            (20.9737, -101.4677), # Celaya, GTO
            (20.5265, -100.8157), # San Juan del Río, QRO
            (20.2134, -87.4660),  # Playa del Carmen, QR
            (20.6296, -87.0739),  # Cozumel, QR
        ]
        return cities
    
    def search_businesses_in_area(self, lat: float, lng: float, radius: int = 50000) -> List[Dict]:
        """Search for businesses in a specific area."""
        businesses = []
        
        if not self.selected_business_type:
            logger.error("No business type selected")
            return businesses
        
        try:
            # Search for businesses using different keywords
            keywords = self.selected_business_type['keywords']
            business_type = self.selected_business_type['type']
            
            for keyword in keywords:
                logger.info(f"Searching for '{keyword}' near ({lat}, {lng})")
                
                # Initial search
                places_result = self.gmaps.places_nearby(
                    location=(lat, lng),
                    radius=radius,
                    type=business_type,
                    keyword=keyword
                )
                
                # Process results
                for place in places_result.get('results', []):
                    business_data = self.get_detailed_place_info(place['place_id'])
                    if business_data:
                        businesses.append(business_data)
                
                # Handle pagination (next_page_token)
                while 'next_page_token' in places_result:
                    time.sleep(2)  # Required delay for next_page_token
                    places_result = self.gmaps.places_nearby(
                        page_token=places_result['next_page_token']
                    )
                    
                    for place in places_result.get('results', []):
                        business_data = self.get_detailed_place_info(place['place_id'])
                        if business_data:
                            businesses.append(business_data)
                
                # Respectful API rate limiting
                time.sleep(0.1)  # 10 requests per second
        
        except Exception as e:
            logger.error(f"Error searching area ({lat}, {lng}): {str(e)}")
        
        return businesses
    
    def get_detailed_place_info(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a specific place."""
        try:
            # Request detailed place information
            place_details = self.gmaps.place(
                place_id=place_id,
                fields=[
                    'name', 'formatted_address', 'formatted_phone_number',
                    'website', 'rating', 'user_ratings_total', 'price_level',
                    'opening_hours', 'geometry', 'type', 'business_status',
                    'photo', 'review', 'url'
                ]
            )
            
            result = place_details.get('result', {})
            
            # Extract relevant information
            business_info = {
                'place_id': place_id,
                'name': result.get('name', ''),
                'address': result.get('formatted_address', ''),
                'phone': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'rating': result.get('rating', 0),
                'total_ratings': result.get('user_ratings_total', 0),
                'price_level': result.get('price_level', ''),
                'business_status': result.get('business_status', ''),
                'types': ', '.join(result.get('type', [])),
                'google_url': result.get('url', ''),
                'latitude': result.get('geometry', {}).get('location', {}).get('lat', ''),
                'longitude': result.get('geometry', {}).get('location', {}).get('lng', ''),
                'business_type': self.selected_business_type['name'],
            }
            
            # Extract opening hours
            opening_hours = result.get('opening_hours', {})
            if opening_hours:
                business_info['hours'] = '; '.join(opening_hours.get('weekday_text', []))
                business_info['open_now'] = opening_hours.get('open_now', False)
            else:
                business_info['hours'] = ''
                business_info['open_now'] = ''
            
            # Extract first photo reference
            photos = result.get('photo', [])
            business_info['photo_reference'] = photos[0].get('photo_reference', '') if photos else ''
            
            # Extract recent reviews
            reviews = result.get('review', [])
            if reviews:
                business_info['recent_review'] = reviews[0].get('text', '')
                business_info['recent_review_rating'] = reviews[0].get('rating', '')
            else:
                business_info['recent_review'] = ''
                business_info['recent_review_rating'] = ''
            
            # Determine country based on address
            address = business_info['address'].lower()
            if any(country in address for country in ['canada', 'ontario', 'quebec', 'alberta', 'british columbia']):
                business_info['country'] = 'Canada'
            elif any(country in address for country in ['mexico', 'méxico', 'guadalajara', 'monterrey']):
                business_info['country'] = 'Mexico'
            else:
                business_info['country'] = 'USA'
            
            return business_info
            
        except Exception as e:
            logger.error(f"Error getting details for place_id {place_id}: {str(e)}")
            return None
    
    def scrape_all_businesses(self, max_cities: Optional[int] = None) -> List[Dict]:
        """Scrape businesses from all major North American cities."""
        if not self.selected_business_type:
            logger.error("No business type selected. Please run get_user_selection() first.")
            return []
        
        cities = self.get_north_american_cities()
        
        if max_cities:
            cities = cities[:max_cities]
        
        business_name = self.selected_business_type['name']
        logger.info(f"Starting comprehensive North American scrape of {business_name} from {len(cities)} cities")
        
        for i, (lat, lng) in enumerate(cities, 1):
            logger.info(f"Processing city {i}/{len(cities)} - Coordinates: ({lat}, {lng})")
            businesses = self.search_businesses_in_area(lat, lng)
            self.all_businesses.extend(businesses)
            
            # Remove duplicates based on place_id
            seen_ids = set()
            unique_businesses = []
            for business in self.all_businesses:
                if business['place_id'] not in seen_ids:
                    seen_ids.add(business['place_id'])
                    unique_businesses.append(business)
            
            self.all_businesses = unique_businesses
            logger.info(f"Total unique {business_name.lower()} found so far: {len(self.all_businesses)}")
            
            # Progress checkpoint - save every 10 cities
            if i % 10 == 0:
                safe_name = business_name.lower().replace(' ', '_').replace('&', 'and')
                self.save_to_csv(f'{safe_name}_checkpoint_{i}.csv')
                logger.info(f"Checkpoint saved at city {i}")
            
            # Be respectful to the API
            time.sleep(0.2)  # 5 requests per second
        
        return self.all_businesses
    
    def save_to_csv(self, filename: str = None):
        """Save the scraped data to a CSV file."""
        if not self.all_businesses:
            logger.warning("No business data to save")
            return
        
        if not filename:
            safe_name = self.selected_business_type['name'].lower().replace(' ', '_').replace('&', 'and')
            filename = f'{safe_name}_north_america.csv'
        
        df = pd.DataFrame(self.all_businesses)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Saved {len(self.all_businesses)} businesses to {filename}")
        
        # Print summary statistics
        if 'country' in df.columns:
            country_counts = df['country'].value_counts()
            logger.info(f"Businesses by country: {dict(country_counts)}")
    
    def save_to_json(self, filename: str = None):
        """Save the scraped data to a JSON file."""
        if not self.all_businesses:
            logger.warning("No business data to save")
            return
        
        if not filename:
            safe_name = self.selected_business_type['name'].lower().replace(' ', '_').replace('&', 'and')
            filename = f'{safe_name}_north_america.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.all_businesses, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(self.all_businesses)} businesses to {filename}")

def main():
    # Replace with your actual Google Maps API key
    API_KEY = "AIzaSyBKIn6wT8Ytsv_cECB-GLKTliylypIHtuU"
    
    # Initialize scraper
    scraper = BusinessScraper(API_KEY)
    
    # Get user's business type selection
    selected_type = scraper.get_user_selection()
    
    if not selected_type:
        print("No business type selected. Exiting...")
        return
    
    # Ask for city limit
    print(f"\n🌍 Ready to scrape {selected_type['name']} across North America!")
    print("This will cover major cities in USA, Canada, and Mexico")
    
    while True:
        try:
            city_limit = input("\nEnter max number of cities to scrape (or press Enter for all cities): ").strip()
            if city_limit == "":
                city_limit = None
                break
            else:
                city_limit = int(city_limit)
                if city_limit > 0:
                    break
                else:
                    print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number or press Enter for all cities.")
    
    # Scrape businesses
    logger.info(f"Starting comprehensive North American {selected_type['name']} scraping...")
    businesses = scraper.scrape_all_businesses(max_cities=city_limit)
    
    # Save results
    safe_name = selected_type['name'].lower().replace(' ', '_').replace('&', 'and')
    scraper.save_to_csv(f'{safe_name}_north_america_complete.csv')
    scraper.save_to_json(f'{safe_name}_north_america_complete.json')
    
    print(f"\n🎉 Scraping complete! Found {len(businesses)} {selected_type['name'].lower()} across North America")
    
    # Display sample data and statistics
    if businesses:
        print(f"\n📊 Sample {selected_type['name'].lower()} data:")
        sample = businesses[0]
        for key, value in list(sample.items())[:8]:
            print(f"  {key}: {value}")
        
        # Country distribution
        countries = {}
        for business in businesses:
            country = business.get('country', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        
        print(f"\n🌍 Distribution by country:")
        for country, count in countries.items():
            print(f"  {country}: {count} {selected_type['name'].lower()}")
        
        print(f"\n💾 Data saved to:")
        print(f"  - {safe_name}_north_america_completeddd.csv")
        print(f"  - {safe_name}_north_america_completeddd.json")

if __name__ == "__main__":
    main()