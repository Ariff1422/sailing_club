import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Pydantic models to handle the request and response structures
class TestCase(BaseModel):
    id: str
    input: List[List[int]]

class Solution(BaseModel):
    id: str
    sortedMergedSlots: List[List[int]]
    minBoatsNeeded: Optional[int] = None

class RequestBody(BaseModel):
    testCases: List[TestCase]

class ResponseBody(BaseModel):
    solutions: List[Solution]

def solve_sailing_club(bookings: List[List[int]]):
    """
    Solves both parts of the Sailing Club problem.

    Part 1: Merges overlapping time slots.
    Part 2: Calculates the minimum number of boats needed.
    """
    if not bookings:
        return [], 0

    # Part 1: Merge overlapping time slots
    # Sort bookings by start time
    sorted_bookings = sorted(bookings, key=lambda x: x[0])
    
    merged_slots = []
    if sorted_bookings:
        current_start, current_end = sorted_bookings[0]
        
        for next_start, next_end in sorted_bookings[1:]:
            if next_start <= current_end:
                # Overlap, merge the slots
                current_end = max(current_end, next_end)
            else:
                # No overlap, add the merged slot and start a new one
                merged_slots.append([current_start, current_end])
                current_start, current_end = next_start, next_end
        
        # Add the last merged slot
        merged_slots.append([current_start, current_end])

    # Part 2: Find minimum number of boats needed
    # Create a timeline of events (start and end times)
    events = []
    for start, end in bookings:
        events.append((start, 1))  # 1 for a boat becoming busy
        events.append((end, -1))   # -1 for a boat becoming free
    
    # Sort events by time. If times are equal, process start events before end events.
    # This is crucial for cases like [1, 8] and [8, 10] where boat 1 becomes free and a new boat is needed at the same time.
    events.sort(key=lambda x: (x[0], x[1]))
    
    min_boats_needed = 0
    current_boats = 0
    
    for _, event_type in events:
        current_boats += event_type
        min_boats_needed = max(min_boats_needed, current_boats)
    
    return merged_slots, min_boats_needed

@app.post("/sailing-club", response_model=ResponseBody)
async def submit_sailing_solutions(request_body: RequestBody):
    """
    Handles the POST request for the Sailing Club challenge.
    Processes each test case and returns the merged slots and minimum boats needed.
    """
    solutions = []
    try:
        for test_case in request_body.testCases:
            merged_slots, min_boats = solve_sailing_club(test_case.input)
            solutions.append(Solution(
                id=test_case.id,
                sortedMergedSlots=merged_slots,
                minBoatsNeeded=min_boats
            ))
        
        return ResponseBody(solutions=solutions)
    
    except Exception as e:
        # This will catch any unexpected errors and return a 500 error
        # to prevent your server from crashing.
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
