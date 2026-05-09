/**
 * Linker Script for STM32F103C8T6
 * Bootloader + Application Layout
 * 
 * Memory Layout:
 * - Flash: 64KB (0x08000000 - 0x0800FFFF)
 * - RAM: 20KB (0x20000000 - 0x20004FFF)
 * 
 * Partition:
 * - Bootloader: 0x08000000 - 0x08007FFF (32KB)
 * - Application: 0x08008000 - 0x0800FFFF (32KB)
 */

MEMORY
{
  BOOTLOADER_FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 32K
  APP_FLASH (rx)         : ORIGIN = 0x08008000, LENGTH = 32K
  RAM (xrw)              : ORIGIN = 0x20000000, LENGTH = 20K
}

SECTIONS
{
  /* Bootloader sections (if linked as bootloader) */
  .bootloader_text :
  {
    KEEP(*(.bootloader_entry))
    *(.bootloader_text)
    *(.bootloader_text*)
  } > BOOTLOADER_FLASH AT > BOOTLOADER_FLASH
  
  /* Application sections */
  .text :
  {
    KEEP(*(.vectors))
    KEEP(*(.init))
    *(.text)
    *(.text*)
    *(.rodata)
    *(.rodata*)
    KEEP(*(.fini))
    _etext = .;
  } > APP_FLASH AT > APP_FLASH
  
  /* Initialized data (RAM copy) */
  .data :
  {
    _sdata = .;
    *(.data)
    *(.data*)
    _edata = .;
  } > RAM AT > APP_FLASH
  
  _sidata = LOADADDR(.data);
  
  /* Uninitialized data (BSS) */
  .bss :
  {
    _sbss = .;
    *(.bss)
    *(.bss*)
    *(COMMON)
    _ebss = .;
  } > RAM AT > RAM
  
  /* Stabs debugging sections */
  .stab 0 (NOLOAD) : { *(.stab) }
  .stabstr 0 (NOLOAD) : { *(.stabstr) }
  
  /* DWARF debug sections */
  .debug_aranges 0 : { *(.debug_aranges) }
  .debug_info 0 : { *(.debug_info .gnu.linkonce.wi.*) }
  .debug_abbrev 0 : { *(.debug_abbrev) }
  .debug_line 0 : { *(.debug_line .debug_line.* .debug_line_end) }
  .debug_frame 0 : { *(.debug_frame) }
  .debug_str 0 : { *(.debug_str) }
  .debug_loc 0 : { *(.debug_loc) }
  .debug_macinfo 0 : { *(.debug_macinfo) }
  .debug_macro 0 : { *(.debug_macro) }
}

/* Define symbols for memory management */
_stack_end = ORIGIN(RAM) + LENGTH(RAM);
_heap_start = _ebss;
_heap_end = _stack_end - 128;  /* Reserve 128 bytes for stack */

/* Entry point */
ENTRY(Boot_Jump_ToApplication)
