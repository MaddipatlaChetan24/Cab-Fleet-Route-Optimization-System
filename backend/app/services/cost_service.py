class CostService:

    def calculate_cost(self, routes, fuel_price=100, km_per_liter=15, driver_cost_per_km=5):

        total_distance = sum(r.distance for r in routes)

        fuel_cost = (total_distance / km_per_liter) * fuel_price
        driver_cost = total_distance * driver_cost_per_km

        total_cost = fuel_cost + driver_cost

        return {
            "total_distance": round(total_distance,2),
            "fuel_cost": round(fuel_cost,2),
            "driver_cost": round(driver_cost,2),
            "total_cost": round(total_cost,2)
        }