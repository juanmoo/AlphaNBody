# Particle
### Properties: 
* Particle ID: Stirng
* Mass: scalar - kilograms (Only accounts for non-varying weight)

# Particle State
### Properties:
* particle: Particle
* Location: n-dimensional vector - meter^n 
* Velocity: n-dimensional vector 
* fuel weight: scalar - kilograms


# Thrust Action
### Properties:
* magnitude: scalar - kilograms ?
* orientation: radians | degrees | unit vector
* OR
* n-dimensional vector - kg * m^2 ?


# Scene
### Properties:
* Particle List: Particle []
* State List:
  * List of (time, particle-state [])
    * State List[0] are the initial conditions

### Metohds:
Simulate | Args: (Particle State[], (Thrust Action, Particle)[]): 
    * Appends new entry (time, Particle State[]) to State List.

