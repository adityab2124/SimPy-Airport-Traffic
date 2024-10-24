import simpy
from statistics import mean 
import random 


# Parameters
ID_CHECKERS = 3  # # of employees doing ID Check 
SCANNERS = 4     # # of scanners to scan travelers
ARRIVAL_RATE = 5  # Passengers per minute, Poisson rate 5/per min
ID_SERVICE_TIME = 0.75  # Exponential service time for ID check (mean = 0.75 minutes)
SCANNER_SERVICE_MIN = 0.5  # 
SCANNER_SERVICE_MAX = 1.0  #
SIM_TIME = 120  # Total simulation time (minutes) (2 hours)

wait_times = []

#passenger processing at ID check
def id_check(env, id_checker):
    yield env.timeout(random.expovariate(1.0 / ID_SERVICE_TIME))  # Exponentially distributed service time

#passenger processing at scanner
def scanner_process(env, scanner):
    yield env.timeout(random.uniform(SCANNER_SERVICE_MIN, SCANNER_SERVICE_MAX))  # Uniformly distributed service time

#passenger journey through ID check and scanner
def passenger(env, id_checker, scanners):
    # Passenger arrives at ID check
    arrival_time = env.now  # Record when the passenger arrives
    
    with id_checker.request() as request:
        yield request
        yield env.process(id_check(env, id_checker))
    
    # Passenger proceeds to one of the scanners
    with random.choice(scanners).request() as request:
        yield request
        yield env.process(scanner_process(env, random.choice(scanners)))
    
    #total time spent (arrival to finish)
    wait_time = env.now - arrival_time
    wait_times.append(wait_time)

# Passenger arrival process
def passenger_arrivals(env, id_checker, scanners):
    while True:
        yield env.timeout(random.expovariate(ARRIVAL_RATE))  #Random poisson-distributed arrival time
        env.process(passenger(env, id_checker, scanners))
# Setting up the environment
env = simpy.Environment()

# Creating resources for ID checkers and scanners
id_checker = simpy.Resource(env, capacity=ID_CHECKERS)  # Multiple ID checkers
scanners = [simpy.Resource(env, capacity=1) for _ in range(SCANNERS)]  # Each scanner has 1 capacity

# Start the passenger arrival process
env.process(passenger_arrivals(env, id_checker, scanners))

# Run the simulation
env.run(until=SIM_TIME)

# Calculate and print average wait time
average_wait_time = sum(wait_times) / len(wait_times)
print(f"Average wait time: {average_wait_time:.2f} minutes")