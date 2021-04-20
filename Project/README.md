# Coordinated Multi-Robot Exploration Project
## Kenneth Alcineus - CAP4630
This project is based on the Wolfram Burgard's article, *Coordinated Multi-Robot Exploration*.

There are the following features:
* GUI with Adjustable Features
  * Frames
  * Framerate
  * Three Grid Display Profiles
  * Three Environments
* Coordination with Utility Calculations
  * A unique algorithm that calculates which frontier cells are explored and are going to be explored by other robots
  * Attempts to provide the optimal number of spaces in an environment becoming explored per unit of time
* Pathing to Frontier Grid Cells with the A* Algorithm
  * Based on my Assignment 1 submission with changes only being made to how neighbor cells are determined
* Time-Sensitive Movement
  * Each robot moves at a rate of exactly one unit of cost per frame
  * I.E. it will take a robot 1 frame to move to an adjacent cell and ~1.414 frames to move to a diagonal cell
  * Each robot's position on the grid is not updated until the integer frame counted from once it starts moving is higher than the cost

There are the following shortcomings:
* Spaghetti Code
  * This is programming, not cooking
  * Object-oriented design and scope management will make the code easier to read and likely run faster
* Long Utility Calculation Time
  * All the calculations for each environment of this program had to be done in advance
  * Using the run demonstrated in class, it took 1307 seconds (roughly 22 minutes!) until the GUI was displayed
* No Line-of-Sight Implementation
  * The robots are able to sense cells with objects in the way of the robots
* Non-Ideal Display Profile
  * The Discovery and Path Tracing display profiles are not visually ideal for environments with obstacles
  
There are six functional iterations of this project with 'burgardvi.py' being the most recent version and the version presented in class.