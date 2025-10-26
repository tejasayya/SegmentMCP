from models.schemas import ActivationResult
from database.kaggle_connector import KaggleConnector
import uuid
import time
from datetime import datetime
from typing import List

class ActivationAgent:
    def __init__(self, db_connector: KaggleConnector):
        self.db_connector = db_connector
        self.active_segments = {}
        # Import here to avoid circular imports
        from config import Config
        self.config = Config.get_agent_config("activation")
    
    async def activate_segment(self, query: str, segment_name: str = None) -> ActivationResult:
        """Execute the final query and activate the segment"""
        start_time = time.time()
        
        try:
            # Execute the query
            results = await self.db_connector.execute_query(query)
            customer_count = len(results)
            
            # Generate segment ID
            segment_id = f"SEG_{uuid.uuid4().hex[:8].upper()}"
            
            # Store segment (in production, this would go to a database)
            self.active_segments[segment_id] = {
                "query": query,
                "results": results,
                "customer_count": customer_count,
                "name": segment_name or f"Segment_{segment_id}",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Simulate downstream system activation
            downstream_systems = await self._activate_downstream_systems(segment_id, results)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return ActivationResult(
                success=True,
                segment_id=segment_id,
                customer_count=customer_count,
                downstream_systems=downstream_systems,
                query_used=query,
                processing_time_ms=processing_time,
                issues=[]  # No issues on success
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            
            return ActivationResult(
                success=False,
                segment_id=None,
                customer_count=0,
                downstream_systems=[],
                query_used=query,
                processing_time_ms=processing_time,
                issues=[f"Activation failed: {str(e)}"]  # Now properly defined in schema
            )
    
    async def _activate_downstream_systems(self, segment_id: str, results: List[dict]) -> List[str]:
        """Simulate activation in downstream systems"""
        # In production, this would integrate with actual marketing systems
        # For now, we'll simulate successful activations
        
        simulated_systems = [
            "CRM_System",
            "Email_Marketing_Platform", 
            "Ad_Platform",
            "Analytics_Dashboard"
        ]
        
        print(f"Segment {segment_id} activated in downstream systems: {simulated_systems}")
        return simulated_systems