# AS (Autonomous System) State Machine

Reference: FS Rules 2026 v1.1, Section T14.8, Figure 15 (page 68)

## States

| State | ASSI Color | Description |
|-------|-----------|-------------|
| AS Off | off | System inactive, no autonomous capability |
| AS Ready | yellow continuous | Mission selected, all checks passed, brakes engaged, waiting for RES Go |
| AS Driving | yellow flashing (2-5 Hz) | Vehicle is in R2D, autonomous driving active |
| AS Finished | blue continuous | Mission completed, vehicle at standstill |
| AS Emergency | blue flashing (2-5 Hz) | EBS activated, emergency state |

## State Determination (Figure 15 - Continuous Decision Tree)

The AS status is **continuously evaluated** based on current conditions, not discrete event-driven transitions:

```
Entry → EBS activated?
├─ YES → Mission finished AND Vehicle at Standstill?
│  ├─ YES → SDC open at RES?
│  │  ├─ YES → AS Emergency
│  │  └─ NO  → AS Finished
│  └─ NO  → AS Emergency
└─ NO  → Mission Selected AND ASMS On AND ASB checks OK AND TS Active?
   ├─ NO  → AS Off
   └─ YES → R2D (Ready-to-Drive)?
      ├─ YES → AS Driving
      └─ NO  → Brakes engaged?
         ├─ YES → AS Ready
         └─ NO  → AS Off
```

## Key Timing Requirements

- **T14.8.4**: R2D mode may only be entered by the RES "Go" signal, after the system has remained in "AS Ready" for **at least 5 seconds**
- **T14.8.5**: The vehicle must not start moving until the system has remained in "AS Driving" for **at least 3 seconds**

## Conditions for Each State

### AS Off
- EBS not activated AND (no mission selected OR ASMS off OR ASB checks failed OR TS not active OR brakes not engaged)

### AS Ready
- EBS not activated AND mission selected AND ASMS on AND ASB checks OK AND TS active AND brakes engaged AND NOT in R2D

### AS Driving
- EBS not activated AND all AS Ready conditions met AND R2D active (via RES Go after 5s in AS Ready)

### AS Finished
- EBS activated AND mission finished AND vehicle at standstill AND SDC NOT open at RES

### AS Emergency
- EBS activated AND (vehicle not at standstill OR mission not finished OR SDC open at RES)

## Required Missions (T14.10)

- Acceleration
- Skidpad
- Autocross (DC only)
- Trackdrive (DC only)
- EBS Test
- Inspection
- Manual Driving

## Hardware Interfaces

- **RES (Remote Emergency System)**: Physical remote with Go button and emergency stop (T14.3)
- **ASMS (Autonomous System Master Switch)**: Physical rotary switch, must have lockout/tagout (T14.5)
- **ASSI (Autonomous System Status Indicator)**: 3x lights showing AS state (T14.9)
- **AMI (Autonomous Mission Indicator)**: Displays selected mission, readable from outside (T14.10)
- **ASB (Autonomous System Brake)**: Emergency braking with EBS (T15)

## Our Implementation Notes

Our kart (APC entry) doesn't have all the ADS-DV hardware (no physical RES, no ASMS switch).
We simulate these via dashboard buttons. The state machine in `state_machine_node.py` maps:

- Dashboard "start" button → RES "Go" signal
- Dashboard "stop" button → returns to `AS_READY` and **stays armed**; it is not equivalent to ASMS off. Switching to the manual mission is what reaches `AS_OFF` (see [state machine](../software/state_machine.md)).
- Dashboard "ebs" button → EBS activation (AS Emergency)
- Dashboard mission selector → mission selection + simulated ASMS on

The 5s AS_READY wait and 3s AS_DRIVING delay are NOT currently implemented but are
required for competition compliance.
