# Energy Map

Energy Map identifies energy-hungry software modules by combining:

- energy measurements (RAPL)
- testcase execution
- static analysis (AST)

## Current Scope

1. Run testcases
2. Measure energy consumption
3. Map testcases to modules
4. Compute energy statistics per module

## Architecture

Backend:
- energy measurement
- test runner
- static analysis
- aggregation

Frontend:
- visualization dashboard

## Setup

1. Run "python server/init_db.py && python server/populate_db.py".
2. Start the server using command "uvicorn server.api:app --port 8080".
3. Start frontend by change directory to lib ("cd lib" from root) then using command "npm install" 
followed by "npm run dev".