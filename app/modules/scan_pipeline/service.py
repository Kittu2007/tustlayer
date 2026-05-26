import time
import json
import asyncio
from typing import Optional
from app.modules.scan_pipeline.schemas import FinalScanResponse, ScanMetadata
from app.modules.scan_pipeline.parallel_executor import ParallelTaskExecutor
from app.modules.scan_pipeline.aggregator import ResultAggregator
from app.modules.scan_pipeline.metadata import MetadataService
from app.integrations.supabase_client import save_scan_result_async

from app.modules.ocr.service import get_ocr_service
from app.modules.fraud_intelligence.service import get_fraud_intelligence_service
from app.modules.trust_score.service import get_final_decision_assembler

class ScanPipelineService:
    def __init__(self):
        self.executor = ParallelTaskExecutor(
            ocr_service=get_ocr_service(),
            fraud_service=get_fraud_intelligence_service()
        )
        self.aggregator = ResultAggregator()
        self.trust_engine = get_final_decision_assembler()
        self.metadata_service = MetadataService()

    async def execute_full_scan(self, image_bytes: bytes) -> FinalScanResponse:
        start_time = time.time()
        
        # 1. Parallel Execution
        ocr_result, fraud_result = await self.executor.execute_all(image_bytes)
        
        # 2. Synchronous Metadata Check
        metadata_anomalies = self.metadata_service.extract_anomalies(image_bytes)
        
        # 3. Normalize inputs for Trust Engine
        trust_input = self.aggregator.normalize_to_trust_input(ocr_result, fraud_result, metadata_anomalies)
        
        # 4. Final Trust Decision
        trust_result = await self.trust_engine.evaluate(trust_input)
        
        # 5. Cinematic Assembly
        execution_ms = int((time.time() - start_time) * 1000)
        
        final_response = FinalScanResponse(
            success=True,
            metadata=ScanMetadata(
                execution_time_ms=execution_ms,
                modules_executed=["OCR", "FraudIntelligence", "Metadata", "TrustScore"]
            ),
            trust_score_data=trust_result,
            ocr_data=ocr_result,
            fraud_intelligence_data=fraud_result
        )
        
        # Async background save to database (will instantly fail silently if no keys)
        asyncio.create_task(save_scan_result_async(final_response.model_dump()))
        
        return final_response
            metadata=ScanMetadata(
                execution_time_ms=execution_ms,
                modules_executed=["OCR", "FraudIntelligence", "Metadata", "TrustScore"]
            ),
            trust_score_data=trust_result,
            ocr_data=ocr_result,
            fraud_intelligence_data=fraud_result
        )
        
    async def stream_full_scan(
        self, 
        image_bytes: bytes, 
        session_id: Optional[str] = None, 
        remaining_scans: int = -1
    ):
        """Generator for Server-Sent Events (SSE)."""
        start_time = time.time()
        
        # Initial status
        yield f'data: {json.dumps({"status": "processing", "step": "starting", "message": "Initializing TrustLayer Pipeline..."})}\n\n'
        await asyncio.sleep(0.5) # Artificial delay for cinematic effect
        
        # 1. Run parallel tasks
        yield f'data: {json.dumps({"status": "processing", "step": "scanning", "message": "Running OCR and Fraud scans concurrently..."})}\n\n'
        ocr_result, fraud_result = await self.executor.execute_all(image_bytes)
        metadata_anomalies = self.metadata_service.extract_anomalies(image_bytes)
        
        yield f'data: {json.dumps({"status": "processing", "step": "scan_complete", "message": "Scans complete. Aggregating results..."})}\n\n'
        await asyncio.sleep(0.5)
        
        # 2. Final Trust Decision
        trust_input = self.aggregator.normalize_to_trust_input(ocr_result, fraud_result, metadata_anomalies)
        trust_result = await self.trust_engine.evaluate(trust_input)
        
        # 3. Assemble Final Payload
        execution_ms = int((time.time() - start_time) * 1000)
        final_response = FinalScanResponse(
            success=True,
            metadata=ScanMetadata(
                execution_time_ms=execution_ms,
                modules_executed=["OCR", "FraudIntelligence", "Metadata", "TrustScore"]
            ),
            trust_score_data=trust_result,
            ocr_data=ocr_result,
            fraud_intelligence_data=fraud_result,
            anonymous_session_id=session_id,
            remaining_scans=remaining_scans
        )
        
        yield f'data: {json.dumps({"status": "complete", "step": "finalized", "payload": final_response.model_dump()})}\n\n'
        
        # Async background save to database
        asyncio.create_task(save_scan_result_async(final_response.model_dump()))

def get_scan_pipeline_service() -> ScanPipelineService:
    return ScanPipelineService()
