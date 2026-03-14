class ReroutingService:

    def should_reroute(self, old_time, new_time):
        """
        trigger reroute if delay > 15%
        """
        return new_time > old_time * 1.15

    def reroute(self, routing_service, cab):
        return routing_service.optimize_route_for_cab(cab)