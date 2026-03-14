from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.services.optimization_service import OptimizationService
from backend.app.core.exceptions import InsufficientCapacityError
import json

router = APIRouter()
optimizer = OptimizationService()


@router.websocket("/ws/optimize")
async def realtime_optimizer(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            data = await ws.receive_text()
            payload = json.loads(data)

            try:
                employees = payload["employees"]
                n_a = payload["n_a"]
                n_b = payload["n_b"]

                routes, total, avg = optimizer.process_optimization(
                    n_a=n_a,
                    n_b=n_b,
                    employee_data=employees
                )

                result = {
                    "status": "success",
                    "total_distance": total,
                    "average_distance": avg,
                    "routes": [
                        {
                            "cab_id": r.cab_id,
                            "type": r.cab_type,
                            "distance": r.distance,
                            "stops": [
                                {"id": e.id, "x": e.x, "y": e.y}
                                for e in r.stops
                            ]
                        }
                        for r in routes
                    ]
                }

            except InsufficientCapacityError as e:
                result = {"status": "error", "message": str(e)}

            except Exception as e:
                result = {"status": "error", "message": f"Server error: {str(e)}"}

            await ws.send_json(result)

    except WebSocketDisconnect:
        print("Client disconnected")