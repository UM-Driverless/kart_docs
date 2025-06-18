# KART Documentation

## General Description

This project equips a standard competition kart with autonomous capabilities by integrating perception, control, and actuation systems. It serves as a modular platform for rapid development and testing of driverless technologies in outdoor environments.

## Motivation

In Driverless, our objective is to enable a single-seater vehicle to autonomously navigate a circuit delimited by cones.

Until now, teachers and researchers lacked a practical outdoor testbed for their algorithms. This year, Henakart donated a kart chassis, which we’re converting to electric and equipping with autonomous systems. It’s simpler and safer than the Formula car, making it ideal for early development and testing.

## Objectives

- Build a modular testbed for autonomous driving components (perception, planning, control).
- Enable outdoor algorithm validation for students, teachers, and researchers.
- Reuse and adapt developed components for the single-seater Formula vehicle.
- Maintain manual drive capability for supervised operation and data collection.

We are currently migrating from a Python-based stack to a ROS-based architecture to ensure compatibility with more complex vehicle platforms.

## Current Status (2025-06-18)

- The kart is fully operational in manual mode.
- Actuation systems for steering and braking are ordered.
- An emergency brake and telemetry system are in development.
- The camera used for cone detection is mounted.
- Work is ongoing to improve cone detection accuracy and software speed.

## Regulatory Requirements and Limitations

This prototype is not intended to compete, so no specific racing regulations apply. Development follows general safety and engineering standards, and deviations are documented. Manual driving must be preserved. Standard kart components are preferred; custom parts are used only when justified.
