#
# Copyright 2025 ExFrame Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Patch file for adding exframe domain exception handling to app.py

This patch contains the modified _process_query_impl function that includes
special handling for the exframe domain.
"""

# Modified _process_query_impl function
MODIFIED_PROCESS_QUERY_IMPL = '''
async def _process_query_impl(
    query: str,
    domain_id: Optional[str],
    context: Optional[Dict[str, Any]],
    include_trace: Optional[bool],
    format_type: Optional[str]
) -> Response:
    """
    Internal implementation for query processing.

    Used by both GET and POST endpoints.
    """
    domain_id = domain_id or "llm_consciousness"
    
    if domain_id not in engines:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")
    
    # SPECIAL HANDLING FOR EXFRAME DOMAIN
    # ExFrame domain uses two-stage search: document store → local patterns → reply
    if domain_id == "exframe":
        engine = engines[domain_id]
        
        try:
            # Extract llm_confirmed from context if present
            llm_confirmed = False
            if context and isinstance(context, dict):
                llm_confirmed = context.get('llm_confirmed', False)
            
            # Process query with exframe specialist (two-stage search)
            result = await engine.process_query(
                query,
                context,
                include_trace=include_trace,
                llm_confirmed=llm_confirmed
            )
            
            # If format is specified, use formatter and return formatted response
            if format_type:
                # Prepare response data for formatter
                response_data = {
                    "query": result.get("query", query),
                    "patterns": result.get("patterns_used", []),
                    "documents_used": result.get("documents_used", []),
                    "specialist_id": result.get("specialist", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "raw_answer": result.get("response", ""),
                    "domain_id": domain_id,
                    "timestamp": result.get("timestamp", datetime.utcnow().isoformat()),
                    "processing_time_ms": result.get("processing_time_ms")
                }
                
                # Format → response
                formatted = await engine.domain.format_response(response_data, format_type=format_type)
                
                # Determine Content-Type based on formatter
                content_type = f"{formatted.mime_type}; charset={formatted.encoding}"
                
                # Return appropriate response type based on MIME type
                if formatted.mime_type == "application/json":
                    return JSONResponse(
                        content=formatted.content,
                        media_type=content_type
                    )
                else:
                    # For markdown, text, etc.
                    return PlainTextResponse(
                        content=formatted.content,
                        media_type=content_type
                    )
            else:
                # No format specified - return default structured JSON response (backward compatible)
                return QueryResponse(**result)
            
        except Exception as e:
            logger.error(f"[EXFRAME] Error processing query for exframe domain: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # REGULAR HANDLING FOR OTHER DOMAINS
    # Other domains use standard single-stage search
    engine = engines[domain_id]
    
    try:
        # Extract llm_confirmed from context if present
        llm_confirmed = False
        if context and isinstance(context, dict):
            llm_confirmed = context.get('llm_confirmed', False)
        
        # Process → query
        result = await engine.process_query(
            query,
            context,
            include_trace=include_trace,
            llm_confirmed=llm_confirmed
        )
        
        # If format is specified, use formatter and return formatted response
        if format_type:
            # Prepare response data for formatter
            response_data = {
                "query": result.get("query", query),
                "patterns": result.get("patterns_used", []),  # Note: engine returns pattern IDs
                "specialist_id": result.get("specialist", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "raw_answer": result.get("response", ""),
                "domain_id": domain_id,
                "timestamp": result.get("timestamp", datetime.utcnow().isoformat()),
                "processing_time_ms": result.get("processing_time_ms")
            }
            
            # Get patterns from knowledge base for formatter
            domain = engine.domain
            if hasattr(domain, '_knowledge_base'):
                kb = domain._knowledge_base
                # Get full pattern objects
                patterns_with_details = []
                pattern_ids = result.get("patterns_used", [])
                for pid in pattern_ids:
                    pattern = await kb.get_by_id(pid)
                    if pattern:
                        patterns_with_details.append(pattern)
                response_data["patterns"] = patterns_with_details
            
            # Format → response
            formatted = await domain.format_response(response_data, format_type=format_type)
            
            # Determine Content-Type based on formatter
            content_type = f"{formatted.mime_type}; charset={formatted.encoding}"
            
            # Return appropriate response type based on MIME type
            if formatted.mime_type == "application/json":
                return JSONResponse(
                    content=formatted.content,
                    media_type=content_type
                )
            else:
                # For markdown, text, etc.
                return PlainTextResponse(
                    content=formatted.content,
                    media_type=content_type
                )
        else:
            # No format specified - return default structured JSON response (backward compatible)
            return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

# Instructions for applying the patch:
# 1. Find the _process_query_impl function in generic_framework/api/app.py
# 2. Replace the entire function with the modified version above
# 3. Test the changes
