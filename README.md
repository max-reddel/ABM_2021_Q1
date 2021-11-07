# ABM_2021_Q1
SEN1211 Agent-Based Modelling 2021/22 Q1. Final project

## Authors
This project was conducted by Max Reddel, Felicitas Reddel, and Sherman Lee.

## Structure

There are 4 main folders: Images, Notebooks, OutputData, and Scripts.

In Notebooks are three core notebooks, Main.ipynb to run the experiments without animation, Main_animation.ipynb to run experiments with animation, and Output_Visualisation for data merging and plotting.

The Scripts folder contains all Python scripts that are necessary to create the model, the experiment, and the animations.

The OutputData folder contains saved pickle files of simulation outputs from Main.ipynb, and are used for Output_Visualisation. Additionally, a timelapse video of Exit C is provided within this folder

The Images folder contains the relevant images that are converted to the map which the agents would navigate through.

## How to run the simulation (without animation)
In the Notebooks folder, in Main.ipynb is the code for the experiment runs. The first section, "Run Experiments" contains the code to run the experiments without animation (due to computational cost), and the next section contains code to run an experiment with animation.

## How to run a simulation (with animation)
In the Notebooks folder, in Main_animation.ipynb file, execute the code under "Run an animation", a visualization will be executed, and the animation is projected in an internet browser tab. Take note that the runs are very slow (further details in the .ipynb file).

## How to view experiment outputs
In the Notebooks folder, in Output_Visualisation.ipynb is the code for visualising the outputs as numbers and graphs. The first section contains data-merging processes to merge multiple run results into one dataset, and the second shows a series of numeric and graphical outputs specifically for evacuation time per replication and average evacuation time per exit type. 