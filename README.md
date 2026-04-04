Make me a simple Home Layout CAD software.  It should look/feel similar to a block diagram tool except that there will be no connection wires just rigid part-to-part connections.

Requirements:
* Create/Hide/Remove named layers
* A canvas area displaying the visible layers  
* Series: A list of available component collections
* Components: A list of available parts in the series that can be placed on the canvas layer
* Component Properties: Each component has properties associated with it.  They may be common or unique to the component
* Component Ports: Each component has a number of ports which can be used as for position assignments
    * Example: We have a Position property group that has a source and destination and an offset
        * Position
            * Source: [port]
            * Destination: [component.port]
            * Offset: [x,y,orientation]
        The source is always the component this property belongs to, so in this case source would be this component, port2.
        The destination might be component2.port1.
        The offset might be [0,4,90].
        In this case it would connect port2 of this component to port1 of component2 but with an offset in the y-axis of 4.

Example Drain Layer
    * Series: SCH40 PVC
    * Components: Straight, Elbow, Wye, Double Wye, Sanitary Tee, Cleanout Cap ...
    * Component Ports: 
        * Elbow: 2 ports, one at each end of the pipe
        * Wye: 3 ports one at each end of the pipe
        * Cleanout Cap: 1 port
    * Component Properties:
        * Elbow:
            * Diameter: 2"
            * Angle: 1/4 turn
            * Sweep: Long
        * Straight:
            * Diameter: 2"
            * Length: 36"

Example: Electrical layer
    * Series: Electrical
    * Components: Wire, Breaker Panel, Breaker, Switch, Fixture, Outlet
    * Ports: 
        * Breaker Panel: 1 for each Breaker (representing the slot), 1 for Neutral, 1 for GND
        * Breaker: 1 port
        * Outlet: 3 ports: 1 for Hot, 1 for Neutral, 1 for GND
        * Wire: 6 ports: 1 at each end for Hot, 1 at each end for Neutral, 1 at each end for GND
    * Properties:
        * Wire:
            * Length: 40"
            * Turn: [None,Right,Left]        
        * Breaker:
            * Limit: 15 Amps
    
Example: Floorplan Layer
    * Series: Floorplan
    * Components: Wall, Window, Door
    * Ports:
        * Wall: 3 ports, one at each end and one in the center
        * Window: 1 port, one port in the center
    * Properties:
        * Wall:
            * Visible: true
            * Length: 60"
            * Width: 3.5"
        * Door:
            * Orientation: [Up,Down,Left,Right]

