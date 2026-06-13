from datetime import datetime, timezone
from app.models.schemas import CarbonInputFull, CategoryBreakdown, CarbonResult

TRANSPORT_FACTORS = {
    "car": {"petrol": 0.192, "diesel": 0.171, "hybrid": 0.110, "electric": 0.053, "none": 0.000},
    "public_transit_per_km": 0.089,
    "flight_short_haul": 255.0,
    "flight_long_haul": 1050.0,
}
HOME_FACTORS = {"electricity_india": 0.716, "gas_per_unit": 2.03}
DIET_FACTORS = {
    "base": {"vegan": 1500.0, "vegetarian": 1700.0, "pescatarian": 2000.0, "omnivore": 2500.0},
    "extra_meat_meal": 3.5,
    "waste_multiplier": {"low": 1.00, "medium": 1.15, "high": 1.30},
}
SHOPPING_FACTORS = {"clothing_item": 10.0, "electronics_item": 300.0, "online_order": 0.5}

def calculate_transport(transport) -> float:
    annual_car_km = transport.car_km_per_week * 52
    car_factor = TRANSPORT_FACTORS["car"].get(transport.car_fuel_type, 0.192)
    car_emissions = annual_car_km * car_factor
    transit_emissions = transport.public_transport_km_per_week * 52 * TRANSPORT_FACTORS["public_transit_per_km"]
    flight_emissions = (transport.flights_per_year * 0.5 * TRANSPORT_FACTORS["flight_short_haul"] + transport.flights_per_year * 0.5 * TRANSPORT_FACTORS["flight_long_haul"])
    return round(car_emissions + transit_emissions + flight_emissions, 2)

def calculate_home(home) -> float:
    annual_kwh = home.electricity_kwh_per_month * 12
    effective_factor = HOME_FACTORS["electricity_india"] * (1 - home.renewable_energy_percent / 100)
    electricity_emissions = annual_kwh * effective_factor
    gas_emissions = home.gas_units_per_month * 12 * HOME_FACTORS["gas_per_unit"]
    return round((electricity_emissions + gas_emissions) / max(home.num_people_in_home, 1), 2)

def calculate_diet(diet) -> float:
    base = DIET_FACTORS["base"].get(diet.diet_type, 2500.0)
    excess_meat = max(0.0, diet.meat_meals_per_week - 7)
    meat_adjustment = excess_meat * 52 * DIET_FACTORS["extra_meat_meal"]
    waste_mult = DIET_FACTORS["waste_multiplier"].get(diet.food_waste_level, 1.15)
    return round((base + meat_adjustment) * waste_mult, 2)

def calculate_shopping(shopping) -> float:
    return round(shopping.new_clothes_per_year * SHOPPING_FACTORS["clothing_item"] + shopping.electronics_per_year * SHOPPING_FACTORS["electronics_item"] + shopping.online_shopping_orders_per_month * 12 * SHOPPING_FACTORS["online_order"], 2)

def get_rating(total_kg: float) -> str:
    if total_kg < 1500: return "excellent"
    elif total_kg < 2500: return "good"
    elif total_kg < 4000: return "average"
    elif total_kg < 7000: return "high"
    else: return "critical"

def get_percentile(total_kg: float) -> float:
    if total_kg < 1000: return 5.0
    elif total_kg < 2000: return 20.0
    elif total_kg < 3000: return 40.0
    elif total_kg < 4500: return 60.0
    elif total_kg < 7000: return 80.0
    elif total_kg < 10000: return 90.0
    else: return 97.0

def calculate_full_footprint(data: CarbonInputFull, user_id: int = None) -> CarbonResult:
    transport_kg = calculate_transport(data.transport)
    home_kg = calculate_home(data.home_energy)
    diet_kg = calculate_diet(data.diet)
    shopping_kg = calculate_shopping(data.shopping)
    total_kg = round(transport_kg + home_kg + diet_kg + shopping_kg, 2)
    breakdown = CategoryBreakdown(transport=transport_kg, home_energy=home_kg, diet=diet_kg, shopping=shopping_kg, total=total_kg)
    return CarbonResult(user_id=user_id, footprint=breakdown, global_avg_kg=4000.0, india_avg_kg=1800.0, percentile=get_percentile(total_kg), rating=get_rating(total_kg), calculated_at=datetime.now(timezone.utc))
