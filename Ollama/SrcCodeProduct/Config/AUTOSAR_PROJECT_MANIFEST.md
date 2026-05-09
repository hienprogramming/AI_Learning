# AUTOSAR Project Manifest

This repository is organized as an AUTOSAR-like prototype for the digital key
application.

## Layering

| Layer | Folder | Responsibility |
| --- | --- | --- |
| Application SWC | `SrcCodeProduct/App` | Digital key logic and app runnables |
| Runtime Environment | `SrcCodeProduct/Rte` | RTE APIs, runnable wrappers, signal access |
| Basic Software | `SrcCodeProduct/ComStack` | COM, PduR, CanIf, CanTp communication services |
| OS | `SrcCodeProduct/Os` | Task activation and cyclic scheduling |
| Common | `SrcCodeProduct/Common` | AUTOSAR-style standard types |
| Bootloader | `SrcCodeProduct/BootLoader` | Boot, update, jump, and safety services |
| Configuration | `SrcCodeProduct/Config` | RTE-to-OS mapping and project manifest |

## RTE To OS Mapping

| OS task | Activation | Period | Runnable |
| --- | --- | ---: | --- |
| `OsTask_Init` | Autostart | once | `Rte_Runnable_App_Init` |
| `OsTask_App_10ms` | Alarm | 10 ms | `Rte_Runnable_App_10ms` |
| `OsTask_App_100ms` | Alarm | 100 ms | `Rte_Runnable_App_100ms` |
| `OsTask_Background` | Cooperative | idle | `Rte_Runnable_Background` |

The machine-readable version is stored in
`SrcCodeProduct/Config/Rte_Os_Task_Mapping.json`.

## Startup Flow

1. `Os_Init()` resets task states and the tick counter.
2. `Os_Start()` activates `OsTask_Init`.
3. `OsTask_Init` calls `Rte_Runnable_App_Init()`.
4. `Rte_Runnable_App_Init()` initializes application services and moves RTE to
   `RTE_MODE_RUN`.
5. `Os_Tick()` activates periodic 10 ms and 100 ms tasks.

## Notes

This is a compact AUTOSAR-style educational project, not generated ARXML output
from a commercial AUTOSAR toolchain. The important contracts are present:
standard types, RTE APIs, runnable wrappers, OS task mapping, and configuration
artifacts.
