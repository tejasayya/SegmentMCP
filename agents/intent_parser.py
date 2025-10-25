from openai import OpenAI
from models.schemas import IntentResult, SegmentCriteria
import json
import re
from typing import List, Dict, Any

class IntentParserAgent:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-3.5-turbo"  # Use a model that's available with most API keys
    
    async def parse_intent(self, natural_language_query: str) -> IntentResult:
        """Parse natural language into structured segment criteria"""
        
        prompt = f"""
        Parse the following marketing segment query into structured criteria:
        Query: "{natural_language_query}"
        
        The dataset contains bank customer information with these columns:
        - age: Customer age
        - job: Type of job
        - marital: Marital status
        - education: Education level
        - default: Has credit in default?
        - balance: Average yearly balance
        - housing: Has housing loan?
        - loan: Has personal loan?
        - contact: Contact communication type
        - day: Last contact day of the month
        - month: Last contact month
        - duration: Last contact duration in seconds
        - campaign: Number of contacts performed during this campaign
        - pdays: Number of days since previous contact
        - previous: Number of contacts performed before this campaign
        - poutcome: Outcome of previous marketing campaign
        - y: Has the customer subscribed to a term deposit?
        
        Return JSON with:
        - conditions: List of conditions with field, operator, value
        - logical_operators: List of operators connecting conditions (usually ["AND"])
        
        Example output for "Customers with housing loan and balance over 1000":
        {{
            "conditions": [
                {{"field": "housing", "operator": "=", "value": "yes"}},
                {{"field": "balance", "operator": ">", "value": 1000}}
            ],
            "logical_operators": ["AND"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                criteria_data = json.loads(json_match.group())
            else:
                criteria_data = json.loads(content)
            
            criteria = SegmentCriteria(**criteria_data)
            
            return IntentResult(
                parsed_criteria=criteria,
                confidence=0.9,
                ambiguous_terms=self._find_ambiguous_terms(natural_language_query)
            )
            
        except Exception as e:
            raise Exception(f"Intent parsing failed: {str(e)}")
    
    def _find_ambiguous_terms(self, query: str) -> List[str]:
        """Identify potentially ambiguous terms in the query"""
        ambiguous_terms = []
        common_ambiguous = ["premium", "active", "loyal", "high value", "regular"]
        
        for term in common_ambiguous:
            if term in query.lower():
                ambiguous_terms.append(term)
                
        return ambiguous_terms