1. Added multiple calculation modes for velocity. You can switch between them by using the calculation_mode parameter.
        0: Strengh increases based on velocity and distacne to the proximity contact receiver
        1: Strength increases based on velocity only
2. Added osc parameter passthrough 
3. output_bool parameter now allows you to change the output to be a bool (useful for some haptic devices) <br>
        -1 = disabled, <br>
        0.0 - 1.0 threshold of the output value to be considered as 1