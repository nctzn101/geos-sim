'''
classes and helper methods for the Gift Economies of Scale project
'''

import random 
from collections import defaultdict
from sklearn import preprocessing

REQUEST_SUBMITTED = "submitted"
DONATION_SUBMITTED = "submitted"
SOLVER_TYPES = ["breakdown", "matchmaking", "validation"]
AGENT_TYPES = ["decentralization-conscious", "honest", "rational"]

class Agent:
    '''
    any system user; holds an inventory
    submits requests, donation responses, donation receipts
    inventory updated with consumption, acquisition, donations/receipts of resources
    atype represents the type of agent (honest, rational, decentralization-conscious)
    '''
    
    def __init__(self, id, economies, atype, receipts):
        self.id = id
        self.atype = atype
        self.receipts = receipts
        self.economies = economies
        self.inventory = Inventory()


class Constraint:
    '''
    constraints to requests/donations such as location, time
    '''
    def __init__(self, ctype, content):
        self.ctype = ctype
        self.content = content

class Inventory:
    '''
    inventory holds resources with respective quantities
    '''
    def __init__(self):
        self.stock = {} 

    def add_resource(self, resource_id, resource, quantity, idle_stock):
        '''
        adds one resource to stock
        '''
        self.stock[resource_id] = {
                "resource": resource,
                "quantity": quantity, 
                "idle_stock": idle_stock,
                "locked": 0
            }

    def update_inventory_policy(self, resource_id, new_idle_stock):
        '''
        updates the inventory policy (i.e., how much of the current quantity is idle)
        '''
        self.stock[resource_id]["idle_stock"] = new_idle_stock

    def update_quantity(self, resource_id, new_quantity):
        ''' 
        updates the quantity of a given resource
        '''
        self.stock[resource_id]["quantity"] = new_quantity

    def make_copy(self):
        '''
        makes a copy of the inventory
        '''
        return self

class DonationReceipt:
    '''
    donation receipts are submitted by either a requestor or a donor upon a resource's donation
    rtype specifies the type of sender (requestor/donor) of the receipt
    '''
    def __init__(self, id, agent_id, request_id, rtype, solver_id, quantity, resource_id):
        self.id = id
        self.rtype = rtype
        self.agent_id = agent_id
        self.quantity = quantity
        self.solver_id = solver_id
        self.request_id = request_id
        self.resource_id = resource_id 

class DonationResponse:
    '''
    donation responses are donation intents/announcements
    agents with spare resources compile responses to requests
    '''
    def __init__(self, id, donor, request_id, quantity, constraints):
        self.id = id
        self.donor = donor
        self.quantity = quantity
        self.request_id = request_id
        self.constraints = constraints
        self.state = DONATION_SUBMITTED

class Request:
    '''
    requests are intents for acquiring resources
    agents submit requests by specifying the requested resource, quantity, and any applicable constraints
    complex requests (for resources with dependencies) are further divided into corresponding subrequests by solvers
    if a request is fulfilled, its state is FULFILLED
    if a request expires, its state is EXPIRED and is no longer viable for donations
    '''
    def __init__(self, id, resource_id, quantity, requestor, constraints, rtype, solver_id):
        self.id = id
        self.rtype = rtype # inherits the type of resource (complex (with dependent resources) or atomic)
        self.subrequests = []
        self.quantity = quantity
        self.requestor = requestor
        self.solver_id = solver_id
        self.strategy_added = False
        self.constraints = constraints
        self.resource_id = resource_id
        self.state = REQUEST_SUBMITTED

class Resource:
    '''
    resources; rtype is 'complex' for resources with dependent resources, atomic otherwise
    '''
    def __init__(self, id, rtype):
        self.id = id
        self.rtype = rtype
        self.dependencies = {}

class Solver:
    ''' 
    solvers are non-user system nodes tasked with one or more of three computational tasks
        - breaking down complex requests into atomic ones
        - request-donation matching
        - donation receipt validation
    solvers are assigned to one or more subeconomies and handle requests pertaining to that subeconomy 
    (and the donations corresponding to said requests)
    '''

    def __init__(self, id, solver_type, economies):
        self.id = id
        self.requests = []
        self.type = solver_type
        self.economies = economies

    def add_requests(self, requests):
        '''
        add request(s) to given solver
        '''
        for r_id in requests:
            self.requests.append(r_id) 
    
    def remove_requests(self, requests):
        ''' 
        remove request(s) from given solver
        '''
        for r_id in requests:
            self.requests.remove(r_id)

# helper methods
def init_agents(econs, num_agents, probabilities):
    ''' 
    initialize agents by assigning them to sub-economies and setting their type
    '''

    agents = {}

    for i in range(num_agents):

        # prepare data
        agent_id = "agent_" + str(i)
        econ_count = random.randint(1, len(econs))
        economies = random.sample(econs, econ_count)
        atype = random.choices(AGENT_TYPES, probabilities)[0]

        # set agent
        agent = Agent(agent_id, economies, atype, [])

        agents[agent_id] = agent

    return agents

def init_solvers(econs, num_solvers, probabilities):
    '''
    initialize solvers by assigning them to sub-economies and setting their type
    '''

    solvers = {}

    for i in range(num_solvers):

        # prepare data
        id = "solver_" + str(i)
        econ_count = random.randint(1, len(econs))
        economies = random.sample(econs, econ_count)
        is_global = random.choices([0, 1], probabilities)[0] # select if global
        
        if is_global:
            economies.append("global")

        types_count = random.randint(1, 3)
        types = random.sample(SOLVER_TYPES, types_count)
        
        # set solver
        solver = Solver(id, types, economies) 

        solvers[id] = solver

    return solvers

def init_resources(resources1, resources2, probabilities):
    '''
    initialize resources 
    first initialize complex resources then dependencies
    '''

    resources = {}
    resource_counter = 0
    resources_level_1 = {}
    resources_level_2 = {}

    for i in range(resources1):

        resource_id = "resource_" + str(resource_counter)
        resource = Resource(resource_id, "complex")
        resources[resource_id] = resource

        # set resource
        resources_level_1[resource_id] = resource
        resource_counter += 1

    for i in range(resources2):

        resource_id = "resource_" + str(resource_counter)
        resource = Resource(resource_id, "atomic")
        resources_level_2[resource_id] = resource 

        # set resource
        resources[resource_id] = resource
        resource_counter += 1

    # add (random) dependencies if level 1 resource is parent
    for r_id in resources_level_1.keys():
        for r_id_j in resources_level_2.keys():

            is_parent = random.choices([0, 1], probabilities)[0] # determine dependency
            if is_parent: 
                resources[r_id].dependencies[r_id_j] = r_id_j

    return resources

def calculate_cumulative_idling_capacity(inv, agents):
    ''' 
    compute overall and by-resource idling capacity
    '''

    cumulative_idling_capacity_by_resource = {}
    idle_stock_overall, total_stock_overall = 0, 0

    idle_stock_by_resource = defaultdict(lambda: 0)
    total_stock_by_resource = defaultdict(lambda: 0)

    for agent_id, agent in agents.items():
        for resource_id, resource_data in agent.inventory.stock.items():

            idle_stock_overall += resource_data["idle_stock"]
            idle_stock_by_resource[resource_id] += resource_data["idle_stock"]

            total_stock_overall += resource_data["quantity"]
            total_stock_by_resource[resource_id] += resource_data["quantity"]
    
    for resource_id, resource in inv.stock.items():

        idle_stock_overall += resource["idle_stock"]
        idle_stock_by_resource[resource_id] += resource["idle_stock"]

        total_stock_overall += resource["quantity"]
        total_stock_by_resource[resource_id] += resource["quantity"]

    cumulative_idling_capacity_overall = round(idle_stock_overall / total_stock_overall, 2)

    for resource_id in inv.stock.keys():
        
        cumulative_idling_capacity_by_resource[resource_id] = round(idle_stock_by_resource[resource_id] / total_stock_by_resource[resource_id], 2)

    return cumulative_idling_capacity_overall, cumulative_idling_capacity_by_resource


def calculate_concentration_index(resource_id, net):
    '''
    compute the concentration index of a resource
    metric is invariant to idle system stock
    '''
    
    stock_per_agent = []
    fraction_per_agent = []

    for agent_id, agent in net.items():
        if resource_id in agent.inventory.stock.keys():
            stock_per_agent.append(agent.inventory.stock[resource_id]["quantity"])

    total_stock = sum(stock_per_agent)
    
    if total_stock == 0:
        return 0.0
    
    for s in stock_per_agent:
        fraction_per_agent.append(s / total_stock)

    # #normalized = preprocessing.normalize([fraction_per_agent])[0]
    
    concentration_index = 1.0 - (max(fraction_per_agent) - min(fraction_per_agent))

    return round(concentration_index, 2), min(fraction_per_agent), max(fraction_per_agent)

def calculate_distribution_index(resource_id, net, num_agents):
    '''
    compute the distribution index of a resource
    '''

    holders = 0 

    for agent_id, agent in net.items():
        if resource_id in agent.inventory.stock.keys():
            holders += 1

    return round(holders / num_agents, 2)


def calculate_decentralization_index(di, ci):
    '''
    compute the decentralization index of a resource based on its distribution and concentration indices
    '''
    return round((di + ci) / 2, 2)


def distribute_inventory(agents, min_count, max_count, inventory):
    '''
    distribute global inventory to agents before simulation begins
    '''

    for agent_id, agent in agents.items(): # for each agent

        resources_count = random.randint(min_count, max_count) # determine its resource count
        agent_resources = random.sample(inventory.stock.keys(), resources_count) # select resources

        for resource_id in agent_resources:

            # determine quantity, currently set to available resource qty in global stock
            # TODO -1 now set so that global inventory never goes to 0
            if inventory.stock[resource_id]["quantity"] > 2:
                qty = random.randint(1, inventory.stock[resource_id]["quantity"] - 1)
            
            else:
                continue

            # determine idle stock for the agent (can be updated with inventory policy in first round)
            idle_stock = random.randint(0, qty)

            # add resource to agents' inventory
            agents[agent_id].inventory.add_resource(resource_id, inventory.stock[resource_id]["resource"], qty, idle_stock)

            # decrease global stocks
            inventory.stock[resource_id]["quantity"] -= qty 
            inventory.stock[resource_id]["idle_stock"] -= qty

    return agents, inventory