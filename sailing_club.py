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
    # Sort bookings by start time to process them chronologically
    sorted_bookings = sorted(bookings, key=lambda x: x[0])
    
    merged_slots = []
    if sorted_bookings:
        current_start, current_end = sorted_bookings[0]
        
        for next_start, next_end in sorted_bookings[1:]:
            if next_start <= current_end:
                # Overlap exists: extend the current merged interval
                current_end = max(current_end, next_end)
            else:
                # No overlap: the current merged interval is complete
                merged_slots.append([current_start, current_end])
                # Start a new merged interval with the next booking
                current_start, current_end = next_start, next_end
        
        # Add the very last merged slot
        merged_slots.append([current_start, current_end])

    # Part 2: Find minimum number of boats needed using a sweep-line algorithm
    # Create a list of events: a start event (+1) and an end event (-1) for each booking
    events = []
    for start, end in bookings:
        events.append((start, 1))  # +1 boat needed at the start of a booking
        events.append((end, -1))   # -1 boat needed at the end of a booking
    
    # Sort events by time. 
    # For events at the same time, process start events (+1) before end events (-1)
    # This is crucial for correctly handling bookings like [6, 10] and [10, 15]
    # where the boat is freed just as another is needed.
    events.sort(key=lambda x: (x[0], -x[1]))
    
    min_boats_needed = 0
    current_boats = 0
    
    # Sweep through the timeline of events
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
        # Catch unexpected errors and return a 500 error to prevent a crash.
        # This is good practice for production APIs.
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
