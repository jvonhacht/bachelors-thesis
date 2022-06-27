# Bachelor's project Spring 2019 - Intelligent control systems


## Abstract

Effective scheduling of traffic is vital for a city to function optimally. For high-density traffic in urban areas, intersections and how they schedule traffic plays an integral part in preventing congestion. Current traffic light scheduling methods predominantly consist of using fixed time intervals to schedule traffic, a method not taking advantage of the technological leaps of recent years. With the unpredictable characteristic of traffic and urban population ever-expanding, conventional traffic scheduling becomes less effective due to them being non-adaptive. Therefore, the study sought out to investigate if a traffic scheduler utilising reinforcement learning could perform better than traditional traffic scheduling policies used today, more specifically fixed-interval scheduling. A solution involving a reinforcement agent choosing different predefined scheduling methods with varied characteristics was implemented. This implementation was successful in lowering the average waiting time of cars passing the intersection compared to fixed-interval scheduling. This was made possible by the agent regularly applying suitable scheduling method for the present traffic conditions. Reinforcement learning could, therefore, be a viable approach to scheduling traffic in intersections. However, the reinforcement agent had a limited overview of the current traffic environment at its disposal which could have consequences for the result.


## Problem statement

- `Can a traffic scheduler utilising reinforcement learning reduce the average waiting time in a 4-way intersection compared to a traditional method in the form of fixed-time scheduling?`

Please read the full report found in file dkand19.pdf.

## Versions

There are multiple iterations of the project as it developed over time and methods were changed. 

- **V1** contains a program for simulating the intersection where the intersection is divided into 9 occupation squares. A car can move from one square to the other and two cars can never be on the same square. This simulation was scrapped in order to simplify the problem due to time constraints.

- **V2** utilises a simplified simulation where cars are logical occupiers and where each lane is simply a queue that can be emptied. However, in this version a DQN was used to schedule each indpendent lane in the intersection. This method did not end up getting used since the results were worse than a normal fixed scheduler and there was not enough time to research and improve it.

- **V3** utilises the same simulation from V2 but instead of a DQN a QTable was used instead. The QTable could then choose between a few different pre-defined scheduling methods for the current traffic environment. The report is based on this version of the project.
