# Practical Considerations

## Sample Rate 

Observations by Daniel Gierse.

## Time Drift

Measurements using RuuviTag *C7:22:C6:A1:0D:DA* have shown that the average time drift over one day is linear, with the RuuviTag time running ahead of the gateway time by 2.7 seconds. The drift increases linearly throughout the day.  

Temperature effects were not considered. It can not be guaranteed that this observation is valid for other tags due to hardware differences.  

More information about the data collection and analysis process can be found in the IPython notebook *analyze_timedrift.ipynb* and the associated elaboration.

## Time Synchronisation 

The function *set_time()* of class *Tag* does not set the RuuviTag time as expected. Mentioned measurements with tag *C7:22:C6:A1:0D:DA* show that even when the time is set, the existing time drift persists. To synchronize video and acceleration data during data labeling, targeted mechanical actions such as three quick strokes can be used to mark acceleration peaks.  

The time drift must be considered in any case. Filming at 30 fps means one frame every 33.3 ms. With a time drift of 2.7 s per day, it can be calculated that the RuuviTag clock drifts by a half frame every 8.9 minutes on average. To ensure that most of the data is correctly associated with the frame, a synchronization should be performed at least after this period of time. A higher synchronization rate increases accuracy. For other applications, a lower synchronization rate may be sufficient. The following formula is used for the calculation and can be adapted to other conditions.

$$
T_{sync} = \frac{0.5 \cdot \frac{1}{f}}{\Delta t_{day}} \cdot T_{day} 
= \frac{0.5 \cdot T_{day}}{\Delta t_{day} \cdot f} 
= \frac{0.5 \cdot 1440~min}{2.7 s \cdot 30 \frac{1}{s}} 
= 8.9~min
$$