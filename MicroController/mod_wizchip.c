// mod_wizchip.c
//
// Minimal MicroPython module wrapping selected functions from the official
// WIZnet driver for the W6100-EVB-Pico2.  This code is based on the driver
// implementation in the WIZnet-PICO-v6-C repository.
//
// Copyright (c) 2019, WIZnet Co., LTD.
// Released under the MIT License.

#include "py/obj.h"
#include "py/runtime.h"
#include "wizchip_conf.h"  // This header should be provided by the official driver

#include <string.h>
#include <stdio.h>

//------------------------------------------------------------------------------
// wizchip.reset()
// Wrap the software reset function from the driver
//------------------------------------------------------------------------------
STATIC mp_obj_t wizchip_reset(void) {
    wizchip_sw_reset();   // Call the official driver function to perform a software reset
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(wizchip_reset_obj, wizchip_reset);

//------------------------------------------------------------------------------
// wizchip.init()
// Wrap the initialization function from the driver.
//------------------------------------------------------------------------------
STATIC mp_obj_t wizchip_init(void) {
    // Call the official initialization function.
    // Assume wizchip_init() returns 0 on success.
    int ret = wizchip_init();
    if (ret != 0) {
        mp_raise_OSError(ret);
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(wizchip_init_obj, wizchip_init);

//------------------------------------------------------------------------------
// wizchip.get_ip()
// Wrap the function that retrieves the current IP address.
//------------------------------------------------------------------------------
STATIC mp_obj_t wizchip_get_ip(void) {
    uint8_t ip[4] = {0,0,0,0};
    wizchip_get_ip(ip);  // Official function: fills the ip array with the current IP address
    char ip_str[16];
    snprintf(ip_str, sizeof(ip_str), "%d.%d.%d.%d", ip[0], ip[1], ip[2], ip[3]);
    return mp_obj_new_str(ip_str, strlen(ip_str));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(wizchip_get_ip_obj, wizchip_get_ip);

//------------------------------------------------------------------------------
// wizchip.set_ip(ip)
// Wrap the function that sets the device IP address.
//------------------------------------------------------------------------------
STATIC mp_obj_t wizchip_set_ip(mp_obj_t ip_obj) {
    const char *ip_str = mp_obj_str_get_str(ip_obj);
    uint8_t ip[4];
    if (sscanf(ip_str, "%hhu.%hhu.%hhu.%hhu", &ip[0], &ip[1], &ip[2], &ip[3]) != 4) {
        mp_raise_ValueError("Invalid IP format");
    }
    wizchip_set_ip(ip);  // Official function to set the IP address
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(wizchip_set_ip_obj, wizchip_set_ip);

//------------------------------------------------------------------------------
// Module Globals Table
//------------------------------------------------------------------------------
STATIC const mp_rom_map_elem_t wizchip_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_wizchip) },
    { MP_ROM_QSTR(MP_QSTR_reset), MP_ROM_PTR(&wizchip_reset_obj) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&wizchip_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_ip), MP_ROM_PTR(&wizchip_get_ip_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_ip), MP_ROM_PTR(&wizchip_set_ip_obj) },
};

STATIC MP_DEFINE_CONST_DICT(wizchip_module_globals, wizchip_module_globals_table);

//------------------------------------------------------------------------------
// Module Definition
//------------------------------------------------------------------------------
const mp_obj_module_t wizchip_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&wizchip_module_globals,
};

// This macro registers the module and makes it available in MicroPython as "wizchip".
// The third argument (MODULE_WIZCHIP_ENABLED) is a macro that you can define in your build
// configuration to conditionally compile this module.
MP_REGISTER_MODULE(MP_QSTR_wizchip, wizchip_user_cmodule, MODULE_WIZCHIP_ENABLED);
