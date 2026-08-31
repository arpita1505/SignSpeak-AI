"""WebSocket prediction endpoint."""
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.prediction import PredictionResponse
from app.services.inference_service import InferenceService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

@router.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    """WebSocket endpoint for real-time predictions."""
    await websocket.accept()
    inference_service = InferenceService()
    logger.info("WebSocket client connected")

    try:
        while True:
            # Receive message
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
            except json.JSONDecodeError:
                response = PredictionResponse(
                    type="error", message="Invalid JSON format"
                )
                await websocket.send_text(response.model_dump_json())
                continue

            # Validate message
            if "frame" not in message:
                response = PredictionResponse(
                    type="error", message="Missing 'frame' field"
                )
                await websocket.send_text(response.model_dump_json())
                continue

            # Process frame
            frame_base64 = message["frame"]

            # Check if model is loaded
            if not inference_service.model_service.is_model_loaded():
                response = PredictionResponse(
                    type="error", message="Model not loaded"
                )
                await websocket.send_text(response.model_dump_json())
                continue

            # Process frame
            try:
                prediction_dict, _, _ = inference_service.process_frame_from_base64(frame_base64)

                # Prepare response
                if prediction_dict["hands_detected"] == 0:
                    response = PredictionResponse(type="no_hand")
                elif prediction_dict["confidence"] < inference_service.smoothing.confidence_threshold:
                    response = PredictionResponse(
                        type="low_confidence",
                        confidence=prediction_dict["confidence"],
                    )
                else:
                    response = PredictionResponse(
                        type="prediction",
                        sign=prediction_dict["sign"],
                        confidence=prediction_dict["confidence"],
                        stable=prediction_dict["stable"],
                        commit=prediction_dict["commit"],
                        hands_detected=prediction_dict["hands_detected"],
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )

                await websocket.send_text(response.model_dump_json())

            except Exception as e:
                logger.error(f"Error processing frame: {e}")
                response = PredictionResponse(
                    type="error", message="Failed to process frame"
                )
                await websocket.send_text(response.model_dump_json())

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except Exception:
            pass
