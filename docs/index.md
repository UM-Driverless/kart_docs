# KART Documentation

## General Description

This project equips a standard competition kart with autonomous capabilities by integrating perception, control, and actuation systems. It serves as a modular platform for rapid development and testing of driverless technologies in outdoor environments.

## Motivation

In Driverless, our objective is to enable a single-seater vehicle to autonomously navigate a circuit delimited by cones.

Until now, teachers and researchers lacked a practical outdoor testbed for their algorithms. This year, Henakart donated a kart chassis, which we're converting to electric and equipping with autonomous systems. It's simpler and safer than the Formula car, making it ideal for early development and testing.

→ **[Learn more about Formula Student Driverless and our project](about.md)**

## Objectives

- Build a modular testbed for autonomous driving components (perception, planning, control).
- Enable outdoor algorithm validation for students, teachers, and researchers.
- Reuse and adapt developed components for the single-seater Formula vehicle.
- Maintain manual drive capability for supervised operation and data collection.

The autonomy stack runs on ROS 2. It replaced an earlier monolithic Python stack, which is kept for reference on the [2024 — Python](software/legacy.md) page.

## Current Status (2026-07-30)

- The kart is fully operational in manual mode.
- Steering actuation is built and running closed-loop; the kart has driven itself under its own control.
- An emergency brake and telemetry system are in development.
- The camera used for cone detection is mounted.
- Work is ongoing to improve cone detection accuracy and software speed.

## Regulatory Requirements and Limitations

This prototype is not intended to compete, so no specific racing regulations apply. Development follows general safety and engineering standards, and deviations are documented. Manual driving must be preserved. Standard kart components are preferred; custom parts are used only when justified.

---

## Follow the build

We're documenting the whole conversion from day one — motor, battery, steering, compute — one post at a time.

[:material-rocket-launch: Read the Build Journey](build-journey/index.md){ .md-button .md-button--primary }
