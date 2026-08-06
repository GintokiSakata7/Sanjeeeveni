# SANJEEVANI

## AI-Powered Emergency Response & Medical Coordination Platform

> **Tagline:** Turning Fragmented Emergency Care Into One Coordinated
> Response

------------------------------------------------------------------------

# Vision

Sanjeevani is an AI-orchestrated emergency coordination platform that
connects citizens, hospitals, ambulances, doctors, ASHA workers, blood
banks and emergency responders into a single intelligent ecosystem. The
objective is to reduce delays during the "golden minutes" of a medical
emergency through real-time coordination.

# Problem Statement

Medical emergencies such as road accidents, cardiac arrest, stroke,
trauma, pregnancy complications and other life-threatening conditions
require rapid and coordinated intervention. Existing emergency systems
primarily operate as isolated services such as ambulance dispatch,
hospital management and telemedicine. Citizens often spend valuable time
searching for hospitals, verifying specialist availability, arranging
ambulances and repeatedly communicating the same medical information.

There is a need for an integrated emergency coordination system capable
of improving communication, resource visibility and emergency response
across the healthcare ecosystem.

# Existing System

-   Ambulance booking apps
-   Hospital directories
-   Telemedicine platforms
-   Separate hospital management systems
-   No unified coordination

# Proposed Solution

Sanjeevani serves as an orchestration layer instead of replacing
existing hospitals.

It: 1. Accepts voice or text emergencies. 2. Understands multilingual
input. 3. Classifies emergency severity. 4. Selects the most appropriate
hospital. 5. Coordinates hospitals and responders. 6. Provides
evidence-based first aid. 7. Generates a structured medical handoff.

# Major Features

-   SOS emergency activation
-   Voice + text emergency reporting
-   Multilingual support
-   AI emergency classification
-   Hospital recommendation
-   Ambulance coordination
-   Doctor consultation
-   ASHA worker integration
-   Blood bank discovery
-   Live tracking
-   Emergency timeline
-   Family notification
-   Command center dashboard

# Users

-   Citizens
-   Hospital Admin
-   Doctors
-   Ambulance Drivers
-   ASHA Workers
-   Volunteers
-   Emergency Operators
-   System Administrators

# Hybrid Hospital Architecture

## Large Hospitals

-   API Integration
-   Hospital keeps internal doctor scheduling
-   Hospital manages beds, ICU and ambulances
-   Sanjeevani submits standardized emergency requests

## Small Hospitals

-   Managed directly through Sanjeevani Dashboard
-   Staff use Sanjeevani Staff App
-   Internal doctor and ambulance management

# Applications

## Citizen App

-   SOS
-   Voice Assistant
-   Live Status
-   Medical Profile
-   Emergency History

## Staff App

Role-based interface: - Doctor - Ambulance Driver - ASHA Worker -
Hospital Admin

## Command Center

-   Live emergencies
-   GIS map
-   Hospital status
-   Ambulance status
-   Analytics

# Core AI Pipeline

Voice/Text → Whisper STT → Gemini/Groq reasoning → Emergency
Classification → Severity Analysis → Hospital Matching → Resource
Allocation → Notifications → First Aid Guidance → Medical Summary

# Technology Stack

## Frontend

-   React Native
-   React
-   TypeScript
-   Tailwind CSS

## Backend

-   FastAPI
-   Python
-   WebSockets
-   REST APIs

## AI

-   Gemini
-   Groq
-   Whisper (Speech-to-Text)

## Database

-   Supabase PostgreSQL
-   Supabase Auth
-   Supabase Storage
-   Supabase Realtime

## Notifications

-   Firebase Cloud Messaging
-   WebSockets

## Maps

-   Google Maps API
-   OpenStreetMap

## Deployment

-   Docker
-   Vercel
-   Render
-   Supabase

# Architecture

Citizen App → AI Orchestrator → Emergency Gateway → Hospital Adapter

Hospital Adapter routes to: - API Hospitals - Dashboard Hospitals

Hospital manages: - Doctors - Ambulances - Beds

Dashboard hospitals use Sanjeevani Staff App.

# Integration Pattern

Adapter Pattern: - API Adapter - Dashboard Adapter - Future FHIR
Adapter - Government Adapter

# Security

-   JWT Authentication
-   Role-Based Access Control
-   HTTPS
-   Encrypted sensitive data
-   Audit logs

# Future Scope

-   108 Integration
-   HL7 FHIR
-   Wearable integration
-   Drone medicine delivery
-   Smart city emergency systems

# Repository Structure

/apps - citizen-app - staff-app - command-center

/backend - api - ai - websocket - integrations

/docs - architecture - api - diagrams

# Conclusion

Sanjeevani is designed as an emergency coordination platform rather than
a hospital management system. By combining AI, multilingual
communication, real-time coordination and hybrid hospital integration,
it aims to improve emergency response efficiency while allowing
hospitals to continue using their existing infrastructure.

> This document is a condensed project README. It can be expanded into
> full technical documentation with detailed APIs, database schema, UML,
> ER diagrams and deployment guides.
