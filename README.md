# Rhythm Game Database Schema

This repository contains a database schema for an osu!-style rhythm game, written in dbdiagram.io syntax.

## Overview
The schema covers the core data needed for a rhythm game, including:

- Player accounts and countries  
- Game modes and beatmap metadata  
- Beatmaps with difficulty settings  
- Plays with scores, accuracy, ranks, and mods  
- Player stats per mode  
- Medals and achievements  

## Structure
Key parts of the schema:

- Countries and Players  
- GameModes, Statuses, and Ranks (enums)  
- BeatmapSets and Beatmaps  
- Plays and PlayMods (many-to-many)  
- Medals and PlayerMedals  
- PlayerStats  
