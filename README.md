# Salsa Simulator

(I'm a complete beginner in the world of salsa and am probably wrong in some of my assumptions and definitions in the code)

This repo contains a NetworkX graph with some beginner couples cuban salsa moves.

It also contains code that performs a random walk on the graph and calls callbacks.  Available callbacks are:

* Printing human-readable instructions, containing the "signs" for the partner and the moves.
* Collecting beats and moves to generate a track with a metronome and overlayed real-time audio instructions. Can be used to generate training sessions of any length.

Example instructions:

```
Wait for beat 7, For 2 beats, Pull hand then release (with spin) into Vacilala (4 beats)
For 4 beats, Hands not touching into Suelta position
Wait for beat 7, For 2 beats, Hand on back into Dile Que No (8 beats)
For 5 beats, Make way into Guapea position
Wait for beat 7, For 2 beats, Pull hand into Prima Con La Hermana (8 beats)
Perform Enchufala (4 beats)
Touch Shuolder with right hand into Doble (4 beats)
Perform Enchufala (4 beats)
Touch Shuolder with right hand into Doble (4 beats)
Perform Enchufala (4 beats)
Take left hand with right into Complicado (4 beats)
Perform Enchufala (4 beats)
For 4 beats, Complete into Closed position
Wait for beat 7, For 2 beats, Turn upper body of partner into Exhibala (8 beats)
You are now in Closed position
Step forward into Dile Que No (8 beats)
For 5 beats, Make way into Guapea position
Wait for beat 1, Make way into Dile Que Si (8 beats)
You are now in Closed position
Turn partner to the left and raise hand into Vamos Abajo (8 beats)
You are now in Closed position
Step forward into Dile Que No (8 beats)
For 5 beats, Make way into Guapea position
Wait for beat 7, For 2 beats, Hold both hands into Kentucky (16 beats)
Perform Dile Que No (8 beats)
For 5 beats, Make way into Guapea position
Wait for beat 7, For 2 beats, Pull hand then release (with spin) into Vacilala (4 beats)
For 4 beats, Hands not touching into Suelta position
Wait for beat 7, For 2 beats, Hand on back into Dile Que No (8 beats)
For 5 beats, Make way into Guapea position
```